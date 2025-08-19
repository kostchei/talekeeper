"""
File: backend/services/character_service.py
Path: /backend/services/character_service.py

Character creation and management service.
AI Agents: Complete character lifecycle with D&D 2024 rules integration.

Pseudo Code:
1. Create new characters with race/class/background selection
2. Calculate derived stats (AC, HP, modifiers, saves)
3. Handle character leveling and XP progression
4. Manage equipment and inventory changes
5. Process rest mechanics (short/long rest recovery)
6. Apply class features and abilities at appropriate levels
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from loguru import logger
import json

from models.character import Character, CharacterCreate
from models.races import Race
from models.classes import Class, Subclass
from models.backgrounds import Background
from models.game import GameState
from models.items import CharacterInventory, Item
from database import GameQueries
from services.dice import DiceRoller

class CharacterService:
    """
    Service for character creation and management.
    AI Agents: Extend with automated character generation and optimization suggestions.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dice = DiceRoller()
    
    def create_character(self, char_data: CharacterCreate) -> Dict[str, Any]:
        """
        Create a new D&D character with full setup.
        
        Returns:
            dict: Result with character data or error message
        """
        try:
            # Validate required references
            race = self.db.get(Race, char_data.race_id)
            character_class = self.db.get(Class, char_data.class_id)
            background = self.db.get(Background, char_data.background_id)
            
            if not all([race, character_class, background]):
                return {
                    "success": False,
                    "message": "Invalid race, class, or background ID"
                }
            
            # Apply racial ability score bonuses
            final_abilities = self._apply_racial_bonuses(
                char_data, race
            )
            
            # Calculate derived stats
            hit_points = self._calculate_starting_hit_points(
                character_class, final_abilities["constitution"]
            )
            
            armor_class = self._calculate_starting_ac(
                final_abilities["dexterity"]
            )
            
            # Create character
            character = Character(
                name=char_data.name,
                race_id=UUID(char_data.race_id),
                class_id=UUID(char_data.class_id),
                background_id=UUID(char_data.background_id),
                level=1,
                experience_points=0,
                **final_abilities,
                armor_class=armor_class,
                hit_points_max=hit_points,
                hit_points_current=hit_points,
                proficiencies=self._calculate_starting_proficiencies(
                    race, character_class, background
                ),
                features=self._calculate_starting_features(
                    race, character_class, background
                ),
                notes=char_data.notes
            )
            
            self.db.add(character)
            self.db.flush()  # Get character ID
            
            # Create game state
            game_state = self._create_initial_game_state(character)
            self.db.add(game_state)
            
            # Add starting equipment
            self._add_starting_equipment(character, character_class, background)
            
            self.db.commit()
            
            return {
                "success": True,
                "character": character.to_dict(),
                "message": f"Created character {character.name}"
            }
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to create character: {str(e)}"
            }
    
    def _apply_racial_bonuses(self, char_data: CharacterCreate, race: Race) -> Dict[str, int]:
        """Apply racial ability score increases to base scores."""
        
        abilities = {
            "strength": char_data.strength,
            "dexterity": char_data.dexterity,
            "constitution": char_data.constitution,
            "intelligence": char_data.intelligence,
            "wisdom": char_data.wisdom,
            "charisma": char_data.charisma
        }
        
        # Apply racial bonuses
        if race.ability_score_increase:
            for ability, bonus in race.ability_score_increase.items():
                if ability in abilities:
                    abilities[ability] += bonus
        
        # Ensure no ability goes above 20 or below 8
        for ability in abilities:
            abilities[ability] = max(8, min(20, abilities[ability]))
        
        return abilities
    
    def _calculate_starting_hit_points(self, character_class: Class, constitution: int) -> int:
        """Calculate starting hit points."""
        
        # Extract hit die size
        hit_die_size = int(character_class.hit_die.replace("d", ""))
        
        # Starting HP = max hit die + CON modifier
        con_modifier = GameQueries.ability_modifier(constitution)
        starting_hp = hit_die_size + con_modifier
        
        # Minimum 1 HP
        return max(1, starting_hp)
    
    def _calculate_starting_ac(self, dexterity: int) -> int:
        """Calculate starting AC (10 + DEX modifier)."""
        
        dex_modifier = GameQueries.ability_modifier(dexterity)
        return 10 + dex_modifier
    
    def _calculate_starting_proficiencies(self, race: Race, character_class: Class, 
                                        background: Background) -> List[str]:
        """Combine all starting proficiencies."""
        
        proficiencies = []
        
        # Racial proficiencies
        if race.proficiencies:
            for prof_type, prof_list in race.proficiencies.items():
                if isinstance(prof_list, list):
                    proficiencies.extend(prof_list)
        
        # Class proficiencies
        if character_class.armor_proficiencies:
            proficiencies.extend(character_class.armor_proficiencies)
        if character_class.weapon_proficiencies:
            proficiencies.extend(character_class.weapon_proficiencies)
        if character_class.tool_proficiencies:
            proficiencies.extend(character_class.tool_proficiencies)
        if character_class.saving_throw_proficiencies:
            proficiencies.extend([f"save_{save}" for save in character_class.saving_throw_proficiencies])
        
        # Background proficiencies
        if background.skill_proficiencies:
            proficiencies.extend([f"skill_{skill}" for skill in background.skill_proficiencies])
        if background.tool_proficiencies:
            proficiencies.extend(background.tool_proficiencies)
        if background.language_proficiencies:
            proficiencies.extend(background.language_proficiencies)
        
        return list(set(proficiencies))  # Remove duplicates
    
    def _calculate_starting_features(self, race: Race, character_class: Class, 
                                   background: Background) -> Dict[str, Any]:
        """Combine all starting features."""
        
        features = {}
        
        # Racial traits
        if race.traits:
            features["racial_traits"] = race.traits
        
        # Class features (level 1)
        if character_class.features_by_level and "1" in character_class.features_by_level:
            features["class_features"] = character_class.features_by_level["1"]
        
        # Background feature
        features["background_feature"] = {
            "name": background.feature_name,
            "description": background.feature_description
        }
        
        return features
    
    def _create_initial_game_state(self, character: Character) -> GameState:
        """Create initial game state for new character."""
        
        return GameState(
            character_id=character.id,
            current_location="Starting Town",
            inventory_gold=50,  # Starting gold
            last_long_rest=None,  # Will be set on first rest
            hit_dice_remaining={character.character_class.name.lower(): 1},
            spell_slots_max=self._calculate_spell_slots(character.character_class, 1),
            spell_slots_remaining=self._calculate_spell_slots(character.character_class, 1)
        )
    
    def _calculate_spell_slots(self, character_class: Class, level: int) -> Dict[str, int]:
        """Calculate spell slots for a class at given level."""
        
        if not character_class.is_spellcaster:
            return {}
        
        if (character_class.spell_slots_by_level and 
            str(level) in character_class.spell_slots_by_level):
            return character_class.spell_slots_by_level[str(level)]
        
        return {}
    
    def _add_starting_equipment(self, character: Character, character_class: Class, 
                              background: Background):
        """Add starting equipment to character inventory."""
        
        # Add class starting equipment (structured format)
        if character_class.starting_equipment:
            if isinstance(character_class.starting_equipment, dict):
                self._process_structured_equipment(character.id, character_class.starting_equipment)
            else:
                # Fallback for list format
                for equipment_name in character_class.starting_equipment:
                    self._add_equipment_by_name(character.id, equipment_name)
        
        # Add background starting equipment (list format)  
        if background.starting_equipment:
            for equipment_name in background.starting_equipment:
                self._add_equipment_by_name(character.id, equipment_name)
    
    def _process_structured_equipment(self, character_id: UUID, equipment_dict: dict):
        """Process structured starting equipment (from classes)."""
        
        for category, items in equipment_dict.items():
            if not items:  # Skip empty categories
                continue
                
            logger.debug(f"Processing {category} equipment: {items}")
            
            # Process each item in the category
            for item_desc in items:
                if isinstance(item_desc, str):
                    # Handle choice descriptions like "Chain Mail OR Leather Armor"
                    if " OR " in item_desc:
                        # Take the first option for simplicity
                        item_name = item_desc.split(" OR ")[0].strip()
                        if item_name != "no shield":  # Skip "no shield" options
                            self._add_equipment_by_name(character_id, item_name)
                    else:
                        # Skip generic descriptions
                        skip_generics = ["Simple and Martial weapons", "Simple weapons", 
                                       "Martial weapons with Finesse or Light property",
                                       "Explorers Pack", "Burglars Pack", "20 arrows if using ranged weapon"]
                        if item_desc not in skip_generics:
                            self._add_equipment_by_name(character_id, item_desc)
    
    def _add_equipment_by_name(self, character_id: UUID, equipment_name: str):
        """Add equipment to character by name (helper method)."""
        
        try:
            # Skip non-equipment items (like clothing, pouches, etc.)
            skip_items = ["Common Clothes", "Belt Pouch", "Insignia of Rank", "Trophy from Fallen Enemy", 
                         "Deck of Cards", "Shovel", "Iron Pot"]
            if any(skip_item in equipment_name for skip_item in skip_items):
                logger.debug(f"Skipping non-equipment item: {equipment_name}")
                return
            
            # Handle special name mappings
            name_mappings = {
                "Herbalism Kit": "Healers Kit",
                "Gaming Set": None,  # Skip generic gaming sets
                "Land Vehicles": None  # Skip vehicle proficiency
            }
            
            mapped_name = name_mappings.get(equipment_name)
            if mapped_name is None and equipment_name in name_mappings:
                logger.debug(f"Skipping mapped item: {equipment_name}")
                return
            
            search_name = mapped_name if mapped_name else equipment_name
            
            # Find item by exact name first, then partial match
            item = self.db.execute(
                select(Item).where(Item.name == search_name)
            ).scalar_one_or_none()
            
            if not item:
                item = self.db.execute(
                    select(Item).where(Item.name.ilike(f"%{search_name}%"))
                ).scalar_one_or_none()
            
            if item:
                # Check if character already has this item
                existing = self.db.execute(
                    select(CharacterInventory).where(
                        and_(
                            CharacterInventory.character_id == character_id,
                            CharacterInventory.item_id == item.id
                        )
                    )
                ).scalar_one_or_none()
                
                if existing:
                    existing.quantity += 1
                else:
                    inventory_item = CharacterInventory(
                        character_id=character_id,
                        item_id=item.id,
                        quantity=1,
                        identified=True,
                        notes=f"Starting equipment"
                    )
                    self.db.add(inventory_item)
                logger.debug(f"Added starting equipment: {equipment_name} -> {item.name}")
            else:
                logger.debug(f"Starting equipment not found in items table: {equipment_name}")
                
        except Exception as e:
            logger.error(f"Error adding starting equipment {equipment_name}: {e}")
            # Don't re-raise the exception to avoid aborting the entire transaction
    
    def level_up_character(self, character_id: str) -> Dict[str, Any]:
        """Handle character leveling up."""
        
        try:
            character = self.db.get(Character, character_id)
            if not character:
                return {
                    "success": False,
                    "message": "Character not found"
                }
            
            # Check if character has enough XP
            current_level = character.level
            required_xp = self._get_xp_for_level(current_level + 1)
            
            if character.experience_points < required_xp:
                return {
                    "success": False,
                    "message": f"Not enough XP to level up. Need {required_xp}, have {character.experience_points}"
                }
            
            old_level = character.level
            new_level = current_level + 1
            
            # Update character level
            character.level = new_level
            
            # Roll for hit points
            hit_die_size = int(character.character_class.hit_die.replace("d", ""))
            hp_roll = self.dice.roll(f"1d{hit_die_size}")
            con_modifier = character.constitution_modifier
            hp_gained = max(1, hp_roll + con_modifier)
            
            character.hit_points_max += hp_gained
            character.hit_points_current += hp_gained
            
            # Get new features
            new_features = self._get_features_for_level(character, new_level)
            
            # Update spell slots if spellcaster
            new_spell_slots = {}
            if character.character_class.is_spellcaster:
                new_spell_slots = self._calculate_spell_slots(character.character_class, new_level)
                
                # Update game state spell slots
                game_state = self.db.execute(
                    select(GameState).where(GameState.character_id == character.id)
                ).scalar_one_or_none()
                
                if game_state:
                    game_state.spell_slots_max = new_spell_slots
                    # Only increase current slots, don't reset them
                    for level, max_slots in new_spell_slots.items():
                        current_slots = game_state.spell_slots_remaining.get(level, 0)
                        old_max = game_state.spell_slots_max.get(level, 0) if hasattr(game_state, 'spell_slots_max') else 0
                        slots_gained = max_slots - old_max
                        game_state.spell_slots_remaining[level] = current_slots + max(0, slots_gained)
            
            # Check for ability score improvement
            asi_levels = [4, 8, 12, 16, 19]
            ability_score_improvement = new_level in asi_levels
            
            # Check for proficiency bonus increase
            old_prof_bonus = character.proficiency_bonus
            new_prof_bonus = GameQueries.get_proficiency_bonus(new_level)
            proficiency_bonus_increase = new_prof_bonus > old_prof_bonus
            
            self.db.commit()
            
            return {
                "success": True,
                "character_id": str(character.id),
                "old_level": old_level,
                "new_level": new_level,
                "hit_points_gained": hp_gained,
                "new_features": new_features,
                "new_spell_slots": new_spell_slots,
                "ability_score_improvement": ability_score_improvement,
                "proficiency_bonus_increase": proficiency_bonus_increase,
                "pending_choices": self._get_level_up_choices(character, new_level),
                "message": f"{character.name} reached level {new_level}!"
            }
            
        except Exception as e:
            logger.error(f"Error leveling up character: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to level up character: {str(e)}"
            }
    
    def _get_xp_for_level(self, level: int) -> int:
        """Get XP required for a specific level."""
        xp_table = {
            1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500,
            6: 14000, 7: 23000, 8: 34000, 9: 48000, 10: 64000,
            11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000,
            16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
        }
        return xp_table.get(level, 355000)
    
    def _get_features_for_level(self, character: Character, level: int) -> List[Dict[str, Any]]:
        """Get new features gained at a specific level."""
        
        features = []
        
        # Class features
        if (character.character_class.features_by_level and 
            str(level) in character.character_class.features_by_level):
            features.extend(character.character_class.features_by_level[str(level)])
        
        # Subclass features (if character has subclass)
        if (character.subclass and character.subclass.features_by_level and
            str(level) in character.subclass.features_by_level):
            features.extend(character.subclass.features_by_level[str(level)])
        
        return features
    
    def _get_level_up_choices(self, character: Character, level: int) -> List[Dict[str, Any]]:
        """Get choices that need to be made during level up."""
        
        choices = []
        
        # Subclass selection
        if (level == character.character_class.subclass_level and 
            not character.subclass_id):
            choices.append({
                "type": "subclass_selection",
                "description": f"Choose your {character.character_class.subclass_name}",
                "options": [
                    {"id": str(sc.id), "name": sc.name, "description": sc.description}
                    for sc in character.character_class.subclasses
                ]
            })
        
        # Ability Score Improvement
        asi_levels = [4, 8, 12, 16, 19]
        if level in asi_levels:
            choices.append({
                "type": "ability_score_improvement",
                "description": "Increase two ability scores by 1 each or one by 2",
                "options": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            })
        
        # Spell selection (if spellcaster)
        if character.character_class.is_spellcaster:
            # This would need spell system implementation
            pass
        
        return choices
    
    def apply_damage(self, character_id: str, damage_amount: int, 
                    damage_type: str = "untyped") -> Dict[str, Any]:
        """Apply damage to a character."""
        
        try:
            character = self.db.get(Character, character_id)
            if not character:
                return {
                    "success": False,
                    "message": "Character not found"
                }
            
            # Apply damage to temporary HP first
            damage_remaining = damage_amount
            temp_hp_lost = 0
            
            if character.hit_points_temporary > 0:
                temp_hp_lost = min(character.hit_points_temporary, damage_remaining)
                character.hit_points_temporary -= temp_hp_lost
                damage_remaining -= temp_hp_lost
            
            # Apply remaining damage to regular HP
            hp_lost = min(character.hit_points_current, damage_remaining)
            character.hit_points_current -= hp_lost
            
            # Check for death/unconsciousness
            status = "conscious"
            if character.hit_points_current <= 0:
                if abs(character.hit_points_current) >= character.hit_points_max:
                    status = "dead"
                else:
                    status = "unconscious"
            
            self.db.commit()
            
            return {
                "success": True,
                "damage_dealt": damage_amount,
                "damage_type": damage_type,
                "temp_hp_lost": temp_hp_lost,
                "hp_lost": hp_lost,
                "current_hp": character.hit_points_current,
                "temp_hp": character.hit_points_temporary,
                "status": status,
                "message": f"{character.name} took {damage_amount} {damage_type} damage"
            }
            
        except Exception as e:
            logger.error(f"Error applying damage: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to apply damage: {str(e)}"
            }
    
    def heal_character(self, character_id: str, healing_amount: int, 
                      healing_type: str = "magical") -> Dict[str, Any]:
        """Heal a character."""
        
        try:
            character = self.db.get(Character, character_id)
            if not character:
                return {
                    "success": False,
                    "message": "Character not found"
                }
            
            # Can't heal if dead
            if character.hit_points_current <= -character.hit_points_max:
                return {
                    "success": False,
                    "message": "Cannot heal a dead character"
                }
            
            old_hp = character.hit_points_current
            character.hit_points_current = min(
                character.hit_points_max,
                character.hit_points_current + healing_amount
            )
            
            actual_healing = character.hit_points_current - old_hp
            
            # If character was unconscious and now has HP, they're conscious
            status = "conscious" if character.hit_points_current > 0 else "unconscious"
            
            self.db.commit()
            
            return {
                "success": True,
                "healing_applied": actual_healing,
                "healing_type": healing_type,
                "current_hp": character.hit_points_current,
                "max_hp": character.hit_points_max,
                "status": status,
                "message": f"{character.name} healed for {actual_healing} HP"
            }
            
        except Exception as e:
            logger.error(f"Error healing character: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to heal character: {str(e)}"
            }