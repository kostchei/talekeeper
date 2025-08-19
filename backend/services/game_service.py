"""
File: backend/services/game_service.py
Path: /backend/services/game_service.py

Pseudo Code:
1. Save game: serialize character/game state to save slot with compression
2. Load game: deserialize and restore character/game state from save slot
3. Generate dungeons: create procedural rooms with monsters/treasures
4. Random encounters: roll encounter tables based on location/level
5. Town actions: handle rest, shopping, training, quest interactions
6. Story progression: track flags, unlock content, manage narrative flow

Game Management Service
Handles save/load system, procedural content generation, and game state management.

AI Agents: Core game loop management - extend with:
- Dynamic story generation based on character choices
- Procedural quest creation
- Adaptive difficulty scaling
- Rich narrative event generation
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from loguru import logger
import json
from datetime import datetime, timedelta

from models.character import Character
from models.game import GameState, GameSave, DungeonRoom, GameEvent
from models.monsters import Monster
from models.items import Item, CharacterInventory
from services.dice import DiceRoller

class GameService:
    """
    Service for game state management and procedural content.
    AI Agents: Central hub for game progression and narrative management.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dice = DiceRoller()
    
    def save_game(self, character_id: str, slot_number: int, save_name: str = "Quick Save") -> Dict[str, Any]:
        """Save complete game state to specified slot."""
        
        try:
            character = self.db.get(Character, character_id)
            if not character:
                return {
                    "success": False,
                    "message": "Character not found"
                }
            
            game_state = self.db.execute(
                select(GameState).where(GameState.character_id == character_id)
            ).scalar_one_or_none()
            
            if not game_state:
                return {
                    "success": False,
                    "message": "Game state not found"
                }
            
            # Serialize complete game state
            save_data = {
                "character": character.to_dict(),
                "game_state": {
                    "status": game_state.status,
                    "total_playtime_minutes": game_state.total_playtime_minutes,
                    "current_location": game_state.current_location,
                    "location_type": game_state.location_type,
                    "discovered_locations": game_state.discovered_locations,
                    "inventory_gold": game_state.inventory_gold,
                    "active_quests": game_state.active_quests,
                    "completed_quests": game_state.completed_quests,
                    "story_flags": game_state.story_flags,
                    "encounters_faced": game_state.encounters_faced,
                    "monsters_defeated": game_state.monsters_defeated,
                    "difficulty_level": game_state.difficulty_level
                },
                "save_timestamp": datetime.utcnow().isoformat(),
                "save_version": "1.0"
            }
            
            # Get character inventory
            inventory_items = self.db.execute(
                select(CharacterInventory).where(CharacterInventory.character_id == character_id)
            ).scalars().all()
            
            save_data["inventory"] = [
                {
                    "item_id": str(item.item_id),
                    "quantity": item.quantity,
                    "equipped": item.equipped,
                    "equipped_slot": item.equipped_slot,
                    "identified": item.identified,
                    "attuned": item.attuned
                }
                for item in inventory_items
            ]
            
            # Check for existing save in slot
            existing_save = self.db.execute(
                select(GameSave).where(
                    and_(
                        GameSave.character_id == character_id,
                        GameSave.slot_number == slot_number,
                        GameSave.is_active == True
                    )
                )
            ).scalar_one_or_none()
            
            if existing_save:
                # Update existing save
                existing_save.save_name = save_name
                existing_save.game_data = save_data["game_state"]
                existing_save.character_data = save_data["character"]
                existing_save.character_level = character.level
                existing_save.location = game_state.current_location
                existing_save.playtime_minutes = game_state.total_playtime_minutes
                save_id = str(existing_save.id)
            else:
                # Create new save
                new_save = GameSave(
                    character_id=character.id,
                    slot_number=slot_number,
                    save_name=save_name,
                    game_data=save_data["game_state"],
                    character_data=save_data["character"],
                    character_level=character.level,
                    location=game_state.current_location,
                    playtime_minutes=game_state.total_playtime_minutes
                )
                self.db.add(new_save)
                self.db.flush()
                save_id = str(new_save.id)
            
            self.db.commit()
            
            return {
                "success": True,
                "save_id": save_id,
                "slot_number": slot_number,
                "save_name": save_name,
                "message": f"Game saved to slot {slot_number}"
            }
            
        except Exception as e:
            logger.error(f"Error saving game: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to save game: {str(e)}"
            }
    
    def generate_random_encounter(self, character_level: int, location_type: str = "dungeon") -> Dict[str, Any]:
        """Generate a random encounter appropriate for character level and location."""
        
        try:
            encounter_roll = self.dice.roll("1d100")
            
            # Encounter type chances
            if location_type == "dungeon":
                if encounter_roll <= 60:
                    encounter_type = "combat"
                elif encounter_roll <= 75:
                    encounter_type = "trap"
                elif encounter_roll <= 85:
                    encounter_type = "treasure"
                else:
                    encounter_type = "event"
            elif location_type == "wilderness":
                if encounter_roll <= 40:
                    encounter_type = "combat"
                elif encounter_roll <= 50:
                    encounter_type = "trap"
                elif encounter_roll <= 70:
                    encounter_type = "treasure"
                else:
                    encounter_type = "event"
            else:  # town/safe areas
                if encounter_roll <= 10:
                    encounter_type = "combat"
                elif encounter_roll <= 20:
                    encounter_type = "event"
                else:
                    encounter_type = "social"
            
            if encounter_type == "combat":
                return self._generate_combat_encounter(character_level, location_type)
            elif encounter_type == "trap":
                return self._generate_trap_encounter(character_level)
            elif encounter_type == "treasure":
                return self._generate_treasure_encounter(character_level)
            else:
                return self._generate_story_event(character_level, location_type)
                
        except Exception as e:
            logger.error(f"Error generating encounter: {e}")
            return {
                "encounter_type": "event",
                "encounter_name": "Peaceful Moment",
                "description": "Nothing happens. You continue on your way.",
                "monsters": [],
                "experience_reward": 0,
                "gold_reward": 0,
                "items_reward": []
            }
    
    def _generate_combat_encounter(self, character_level: int, location_type: str) -> Dict[str, Any]:
        """Generate a combat encounter with appropriate monsters."""
        
        # Get monsters appropriate for level
        target_cr_min = max(0.25, character_level * 0.5 - 1)
        target_cr_max = character_level * 0.75 + 1
        
        suitable_monsters = self.db.execute(
            select(Monster).where(
                and_(
                    Monster.challenge_rating >= target_cr_min,
                    Monster.challenge_rating <= target_cr_max
                )
            )
        ).scalars().all()
        
        if not suitable_monsters:
            # Fallback to basic monsters
            suitable_monsters = self.db.execute(
                select(Monster).limit(5)
            ).scalars().all()
        
        if suitable_monsters:
            selected_monster = self.dice.choice(suitable_monsters)
            
            # Determine quantity based on CR vs character level
            if float(selected_monster.challenge_rating) < character_level * 0.5:
                quantity = self.dice.roll("1d4") + 1  # 2-5 weak monsters
            else:
                quantity = self.dice.roll("1d2")  # 1-2 appropriate monsters
            
            total_xp = int(selected_monster.experience_value * quantity)
            
            return {
                "encounter_type": "combat",
                "encounter_name": f"{quantity}x {selected_monster.name}",
                "description": f"You encounter {quantity} {selected_monster.name}{'s' if quantity > 1 else ''}!",
                "monsters": [
                    {
                        "monster_id": str(selected_monster.id),
                        "name": selected_monster.name,
                        "quantity": quantity,
                        "challenge_rating": float(selected_monster.challenge_rating)
                    }
                ],
                "experience_reward": total_xp,
                "gold_reward": self.dice.roll(f"{quantity}d6") * 5,
                "items_reward": []
            }
        else:
            return {
                "encounter_type": "event",
                "encounter_name": "Empty Corridor",
                "description": "The area seems quiet...",
                "monsters": [],
                "experience_reward": 0,
                "gold_reward": 0,
                "items_reward": []
            }
    
    def _generate_trap_encounter(self, character_level: int) -> Dict[str, Any]:
        """Generate a trap encounter."""
        
        trap_types = [
            "Pit Trap", "Poison Dart", "Falling Block", "Spike Trap", 
            "Alarm Rune", "Gas Trap", "Collapsing Ceiling"
        ]
        
        trap_name = self.dice.choice(trap_types)
        dc = 10 + character_level + self.dice.roll("1d4")
        damage = f"{character_level}d6"
        
        return {
            "encounter_type": "trap",
            "encounter_name": trap_name,
            "description": f"You spot a {trap_name.lower()}! DC {dc} to detect/disable. {damage} damage if triggered.",
            "monsters": [],
            "experience_reward": character_level * 25,
            "gold_reward": 0,
            "items_reward": [],
            "trap_data": {
                "detection_dc": dc,
                "disable_dc": dc + 2,
                "damage": damage,
                "damage_type": "piercing"
            }
        }
    
    def _generate_treasure_encounter(self, character_level: int) -> Dict[str, Any]:
        """Generate a treasure encounter."""
        
        gold_amount = self.dice.roll(f"{character_level}d10") * 10
        
        treasure_types = [
            "Hidden Cache", "Abandoned Chest", "Ancient Coffer", 
            "Forgotten Stash", "Treasure Hoard"
        ]
        
        treasure_name = self.dice.choice(treasure_types)
        
        return {
            "encounter_type": "treasure",
            "encounter_name": treasure_name,
            "description": f"You discover a {treasure_name.lower()} containing {gold_amount} gold pieces!",
            "monsters": [],
            "experience_reward": 0,
            "gold_reward": gold_amount,
            "items_reward": []
        }
    
    def _generate_story_event(self, character_level: int, location_type: str) -> Dict[str, Any]:
        """Generate a story event."""
        
        events = {
            "dungeon": [
                "Ancient Inscription", "Mysterious Portal", "Abandoned Camp",
                "Strange Echoes", "Magical Phenomenon"
            ],
            "wilderness": [
                "Traveling Merchant", "Wild Animal Sighting", "Weather Change",
                "Distant Smoke", "Ancient Ruins"
            ],
            "town": [
                "Local Gossip", "Festival Preparation", "Merchant Deal",
                "City Guard Patrol", "Street Performance"
            ]
        }
        
        event_list = events.get(location_type, events["dungeon"])
        event_name = self.dice.choice(event_list)
        
        descriptions = {
            "Ancient Inscription": "You find mysterious runes carved into the wall. They seem to tell a story...",
            "Traveling Merchant": "A friendly merchant offers to trade goods with you.",
            "Local Gossip": "You overhear interesting rumors about nearby adventures.",
            "Weather Change": "The weather shifts, affecting visibility and travel conditions."
        }
        
        description = descriptions.get(event_name, f"You encounter {event_name.lower()}.")
        
        return {
            "encounter_type": "event",
            "encounter_name": event_name,
            "description": description,
            "monsters": [],
            "experience_reward": 0,
            "gold_reward": 0,
            "items_reward": [],
            "story_impact": {
                "event_type": "discovery",
                "knowledge_gained": event_name
            }
        }
    
    def process_town_action(self, character_id: str, action_type: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process town actions like rest, shopping, training."""
        
        try:
            character = self.db.get(Character, character_id)
            if not character:
                return {
                    "success": False,
                    "message": "Character not found"
                }
            
            if action_type == "rest":
                return self._process_rest(character, action_data.get("rest_type", "long"))
            elif action_type == "shop":
                return self._process_shop_visit(character, action_data)
            elif action_type == "train":
                return self._process_training(character, action_data)
            elif action_type == "inn":
                return self._process_inn_stay(character, action_data)
            else:
                return {
                    "success": False,
                    "message": f"Unknown town action: {action_type}"
                }
                
        except Exception as e:
            logger.error(f"Error processing town action: {e}")
            return {
                "success": False,
                "message": f"Failed to process town action: {str(e)}"
            }
    
    def _process_rest(self, character: Character, rest_type: str) -> Dict[str, Any]:
        """Handle character rest in town."""
        
        if rest_type == "long":
            # Full heal
            character.hit_points_current = character.hit_points_max
            character.hit_points_temporary = 0
            
            # Update game state
            game_state = self.db.execute(
                select(GameState).where(GameState.character_id == character.id)
            ).scalar_one_or_none()
            
            if game_state:
                game_state.last_long_rest = datetime.utcnow()
                game_state.short_rests_today = 0
                # Reset spell slots if spellcaster
                if game_state.spell_slots_max:
                    game_state.spell_slots_remaining = game_state.spell_slots_max.copy()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "You rest peacefully and recover all your strength.",
                "health_restored": character.hit_points_max,
                "resources_restored": ["spell_slots", "abilities"]
            }
        
        else:  # short rest
            # Partial healing
            healing = self.dice.roll(f"{character.level}d6") + character.constitution_modifier
            old_hp = character.hit_points_current
            character.hit_points_current = min(character.hit_points_max, old_hp + healing)
            actual_healing = character.hit_points_current - old_hp
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"You take a short rest and recover {actual_healing} hit points.",
                "health_restored": actual_healing
            }
    
    def _process_shop_visit(self, character: Character, shop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shop interactions."""
        
        shop_type = shop_data.get("shop_type", "general_store")
        
        return {
            "success": True,
            "message": f"You visit the {shop_type.replace('_', ' ')}.",
            "shop_type": shop_type,
            "available_items": [],  # Would be populated by items service
            "merchant_greeting": "Welcome to my shop!"
        }
    
    def _process_training(self, character: Character, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle character training."""
        
        return {
            "success": True,
            "message": "Training facilities are not yet available.",
            "training_options": []
        }
    
    def _process_inn_stay(self, character: Character, inn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle inn stay."""
        
        cost = inn_data.get("room_quality", 1) * 10  # 10gp per quality level
        
        game_state = self.db.execute(
            select(GameState).where(GameState.character_id == character.id)
        ).scalar_one_or_none()
        
        if game_state and game_state.inventory_gold >= cost:
            game_state.inventory_gold -= cost
            
            # Inn provides guaranteed long rest
            character.hit_points_current = character.hit_points_max
            game_state.last_long_rest = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "success": True,
                "message": f"You stay at the inn for {cost} gold and wake up refreshed.",
                "cost": cost,
                "health_restored": character.hit_points_max,
                "remaining_gold": game_state.inventory_gold
            }
        else:
            return {
                "success": False,
                "message": f"You need {cost} gold to stay at the inn."
            }