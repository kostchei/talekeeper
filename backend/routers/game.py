"""
File: backend/routers/game.py
Path: /backend/routers/game.py

Pseudo Code:
1. Save game: store character state, location, progress to save slot
2. Load game: retrieve character and game state from save slot
3. Get save slots: list all available saves with metadata
4. Enter dungeon: start dungeon exploration, generate rooms
5. Random encounter: roll for monsters, create combat or event
6. Town actions: handle shop, rest, training activities
7. Game state: manage current location, progress, flags

Game Management Router
Handles save/load system, dungeon progression, and overall game state management.

AI Agents: Key endpoints:
- POST /save - Save current game state to slot
- GET /load/{slot} - Load game from save slot
- GET /save-slots - List available save slots
- POST /enter-dungeon - Start dungeon exploration
- POST /random-encounter - Generate random encounter
- GET /game-state/{character_id} - Get current game state
- POST /town-action - Handle town activities
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc, func
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
import json
from loguru import logger
from datetime import datetime, timedelta
from enum import Enum

from database import get_db, GameQueries
from models.character import Character
from models.game import (
    GameSave, GameState, DungeonRoom, GameEvent,
    GameSaveRequest, GameSaveResponse, GameStateResponse,
    DungeonEnterRequest, EncounterResult, TownActionRequest
)
from models.monsters import Monster
from services.dice import DiceRoller
from services.game_service import GameService

router = APIRouter()
dice = DiceRoller()

class LocationType(str, Enum):
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    COMBAT = "combat"

class TownActionType(str, Enum):
    LONG_REST = "long_rest"
    SHOP = "shop"
    TRAIN = "train"
    TAVERN = "tavern"

@router.post("/save", response_model=GameSaveResponse)
async def save_game(
    save_data: GameSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save current game state to a save slot.
    
    Stores character state, location, progress, and metadata.
    
    AI Agents: Extend for:
    - Multiple characters per save
    - Quest progress tracking
    - World state persistence
    """
    try:
        # Validate character exists
        character = db.get(Character, save_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Check if save slot is already used
        existing_save = db.execute(
            select(GameSave).where(
                and_(GameSave.slot_number == save_data.slot_number, GameSave.is_active == True)
            )
        ).scalar_one_or_none()
        
        if existing_save and not save_data.overwrite:
            raise HTTPException(
                status_code=400, 
                detail=f"Save slot {save_data.slot_number} is already in use. Set overwrite=true to replace."
            )
        
        # Deactivate existing save if overwriting
        if existing_save:
            existing_save.is_active = False
        
        # Get current game state
        game_state = db.execute(
            select(GameState).where(GameState.character_id == save_data.character_id)
        ).scalar_one_or_none()
        
        # Create comprehensive save data
        save_snapshot = {
            "character": {
                "id": str(character.id),
                "name": character.name,
                "race_id": character.race_id,
                "class_id": character.class_id,
                "background_id": character.background_id,
                "level": character.level,
                "experience_points": character.experience_points,
                "current_hit_points": character.current_hit_points,
                "max_hit_points": character.max_hit_points,
                "armor_class": character.armor_class,
                "proficiency_bonus": character.proficiency_bonus,
                "hit_dice_current": character.hit_dice_current,
                "hit_dice_max": character.hit_dice_max,
                "ability_scores": {
                    "strength": character.strength,
                    "dexterity": character.dexterity,
                    "constitution": character.constitution,
                    "intelligence": character.intelligence,
                    "wisdom": character.wisdom,
                    "charisma": character.charisma
                },
                "conditions": character.conditions or [],
                "death_saves": {
                    "successes": character.death_saves_successes,
                    "failures": character.death_saves_failures
                }
            },
            "game_state": {
                "current_location": game_state.current_location if game_state else "town",
                "location_type": game_state.location_type if game_state else "town",
                "dungeon_level": game_state.dungeon_level if game_state else 0,
                "room_number": game_state.room_number if game_state else 0,
                "short_rests_used": game_state.short_rests_used if game_state else 0,
                "last_long_rest": game_state.last_long_rest.isoformat() if game_state and game_state.last_long_rest else None,
                "flags": game_state.flags if game_state else {},
                "inventory_gold": game_state.inventory_gold if game_state else 0
            },
            "timestamp": datetime.utcnow().isoformat(),
            "playtime_minutes": game_state.playtime_minutes if game_state else 0,
            "version": "1.0.0"
        }
        
        # Create new save
        new_save = GameSave(
            id=uuid4(),
            slot_number=save_data.slot_number,
            character_id=save_data.character_id,
            save_name=save_data.save_name or f"{character.name} - Level {character.level}",
            save_data=save_snapshot,
            location_description=f"{game_state.current_location if game_state else 'Town'} (Level {character.level})",
            character_level=character.level,
            playtime_minutes=game_state.playtime_minutes if game_state else 0,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_save)
        db.commit()
        db.refresh(new_save)
        
        return GameSaveResponse(
            save_id=new_save.id,
            slot_number=new_save.slot_number,
            save_name=new_save.save_name,
            character_name=character.name,
            character_level=character.level,
            location_description=new_save.location_description,
            playtime_minutes=new_save.playtime_minutes,
            created_at=new_save.created_at,
            success=True,
            message=f"Game saved to slot {save_data.slot_number}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving game: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save game")

@router.get("/load/{slot_number}", response_model=Dict[str, Any])
async def load_game(
    slot_number: int,
    db: Session = Depends(get_db)
):
    """
    Load game from save slot.
    
    Restores character state and game progress.
    
    AI Agents: Extend for:
    - Save file validation
    - Version compatibility
    - Corrupted save recovery
    """
    try:
        # Find the save
        save = db.execute(
            select(GameSave).where(
                and_(GameSave.slot_number == slot_number, GameSave.is_active == True)
            )
        ).scalar_one_or_none()
        
        if not save:
            raise HTTPException(status_code=404, detail=f"No save found in slot {slot_number}")
        
        # Validate save data
        if not save.save_data:
            raise HTTPException(status_code=400, detail="Save data is corrupted")
        
        save_data = save.save_data
        character_data = save_data.get("character", {})
        game_state_data = save_data.get("game_state", {})
        
        # Restore character (this would update the existing character or create new one)
        character = db.get(Character, save.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found in database")
        
        # Update character from save data
        character.current_hit_points = character_data.get("current_hit_points", character.max_hit_points)
        character.hit_dice_current = character_data.get("hit_dice_current", character.hit_dice_max)
        character.conditions = character_data.get("conditions", [])
        character.death_saves_successes = character_data.get("death_saves", {}).get("successes", 0)
        character.death_saves_failures = character_data.get("death_saves", {}).get("failures", 0)
        
        # Restore or create game state
        game_state = db.execute(
            select(GameState).where(GameState.character_id == save.character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            game_state = GameState(
                character_id=save.character_id,
                current_location=game_state_data.get("current_location", "town"),
                location_type=game_state_data.get("location_type", "town"),
                dungeon_level=game_state_data.get("dungeon_level", 0),
                room_number=game_state_data.get("room_number", 0),
                short_rests_used=game_state_data.get("short_rests_used", 0),
                flags=game_state_data.get("flags", {}),
                inventory_gold=game_state_data.get("inventory_gold", 0),
                playtime_minutes=game_state_data.get("playtime_minutes", 0)
            )
            db.add(game_state)
        else:
            game_state.current_location = game_state_data.get("current_location", "town")
            game_state.location_type = game_state_data.get("location_type", "town")
            game_state.dungeon_level = game_state_data.get("dungeon_level", 0)
            game_state.room_number = game_state_data.get("room_number", 0)
            game_state.short_rests_used = game_state_data.get("short_rests_used", 0)
            game_state.flags = game_state_data.get("flags", {})
            game_state.inventory_gold = game_state_data.get("inventory_gold", 0)
            game_state.playtime_minutes = save_data.get("playtime_minutes", 0)
        
        # Parse last long rest if exists
        last_long_rest = game_state_data.get("last_long_rest")
        if last_long_rest:
            try:
                game_state.last_long_rest = datetime.fromisoformat(last_long_rest)
            except ValueError:
                game_state.last_long_rest = datetime.utcnow() - timedelta(hours=8)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Game loaded from slot {slot_number}",
            "character": {
                "id": str(character.id),
                "name": character.name,
                "level": character.level,
                "current_hp": character.current_hit_points,
                "max_hp": character.max_hit_points,
                "experience": character.experience_points
            },
            "game_state": {
                "current_location": game_state.current_location,
                "location_type": game_state.location_type,
                "dungeon_level": game_state.dungeon_level,
                "room_number": game_state.room_number,
                "gold": game_state.inventory_gold,
                "short_rests_used": game_state.short_rests_used,
                "playtime_minutes": game_state.playtime_minutes
            },
            "save_info": {
                "save_name": save.save_name,
                "created_at": save.created_at,
                "playtime": save.playtime_minutes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading game: {e}")
        raise HTTPException(status_code=500, detail="Failed to load game")

@router.get("/save-slots", response_model=List[Dict[str, Any]])
async def get_save_slots(
    db: Session = Depends(get_db)
):
    """
    Get all available save slots with metadata.
    
    AI Agents: Use for save selection UI.
    """
    try:
        from sqlalchemy import text
        
        # Query save slots with linked characters
        save_slots = []
        
        # Show all slots 1-10, check if they have characters
        for slot_num in range(1, 11):
            # Get save slot and character info
            result = db.execute(text("""
                SELECT 
                    s.id as slot_id,
                    s.character_name as slot_character_name,
                    s.last_played,
                    s.created_at as slot_created_at,
                    s.play_time,
                    c.id as character_id,
                    c.name as character_name,
                    c.level,
                    gs.current_location,
                    gs.inventory_gold
                FROM save_slots s
                LEFT JOIN characters c ON c.save_slot_id = s.id
                LEFT JOIN game_states gs ON gs.character_id = c.id
                WHERE s.slot_number = :slot_num
            """), {"slot_num": slot_num}).first()
            
            if result and result.character_id:
                # Slot has a character
                save_slots.append({
                    "slot_number": slot_num,
                    "is_empty": False,
                    "save_id": str(result.slot_id),
                    "character_id": str(result.character_id),
                    "save_name": f"{result.character_name} - {result.current_location or 'Unknown Location'}",
                    "character_name": result.character_name,
                    "character_level": result.level,
                    "location_description": result.current_location or "Unknown Location",
                    "gold": result.inventory_gold or 0,
                    "playtime_minutes": result.play_time or 0,
                    "playtime_display": f"{(result.play_time or 0) // 60}h {(result.play_time or 0) % 60}m",
                    "created_at": result.slot_created_at,
                    "last_played": result.last_played
                })
            elif result:
                # Slot exists but no character (orphaned slot)
                save_slots.append({
                    "slot_number": slot_num,
                    "is_empty": True,
                    "save_id": str(result.slot_id),
                    "character_id": None,
                    "save_name": f"Empty Slot {slot_num}",
                    "character_name": None,
                    "character_level": None,
                    "location_description": "Empty",
                    "gold": 0,
                    "playtime_minutes": 0,
                    "playtime_display": "0h 0m",
                    "created_at": result.slot_created_at,
                    "last_played": result.last_played
                })
            else:
                # No slot exists
                save_slots.append({
                    "slot_number": slot_num,
                    "is_empty": True,
                    "save_id": None,
                    "character_id": None,
                    "save_name": f"Empty Slot {slot_num}",
                    "character_name": None,
                    "character_level": None,
                    "location_description": "Empty",
                    "gold": 0,
                    "playtime_minutes": 0,
                    "playtime_display": "0h 0m",
                    "created_at": None,
                    "last_played": None
                })
        
        return save_slots
        
    except Exception as e:
        logger.error(f"Error getting save slots: {e}")
        raise HTTPException(status_code=500, detail="Failed to get save slots")

@router.post("/enter-dungeon", response_model=Dict[str, Any])
async def enter_dungeon(
    dungeon_data: DungeonEnterRequest,
    db: Session = Depends(get_db)
):
    """
    Enter dungeon and generate first room.
    
    Creates dungeon state and generates encounters.
    
    AI Agents: Extend for:
    - Procedural dungeon generation
    - Themed dungeons with lore
    - Multi-level dungeons
    """
    try:
        character = db.get(Character, dungeon_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get or create game state
        game_state = db.execute(
            select(GameState).where(GameState.character_id == dungeon_data.character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            game_state = GameState(
                character_id=dungeon_data.character_id,
                current_location="dungeon_entrance",
                location_type=LocationType.DUNGEON,
                dungeon_level=1,
                room_number=1,
                short_rests_used=0,
                flags={},
                inventory_gold=0,
                playtime_minutes=0
            )
            db.add(game_state)
        else:
            game_state.current_location = "dungeon_entrance"
            game_state.location_type = LocationType.DUNGEON
            game_state.dungeon_level = dungeon_data.dungeon_level or 1
            game_state.room_number = 1
        
        # Generate first room
        service = GameService(db)
        room = service.generate_dungeon_room(
            character_level=character.level,
            dungeon_level=game_state.dungeon_level,
            room_number=game_state.room_number
        )
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Entered {dungeon_data.dungeon_name or 'the dungeon'}",
            "dungeon_name": dungeon_data.dungeon_name or "Ancient Ruins",
            "current_location": game_state.current_location,
            "dungeon_level": game_state.dungeon_level,
            "room_number": game_state.room_number,
            "room": {
                "description": room["description"],
                "type": room["type"],
                "exits": room["exits"],
                "has_encounter": room["has_encounter"],
                "has_treasure": room["has_treasure"],
                "special_features": room.get("special_features", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error entering dungeon: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to enter dungeon")

@router.post("/random-encounter", response_model=Dict[str, Any])
async def generate_random_encounter(
    character_id: UUID,
    location_type: str = "dungeon",
    db: Session = Depends(get_db)
):
    """
    Generate a balanced encounter using D&D 2024 guidelines and random bag system.
    
    Uses XP budgets (50% easy, 40% medium, 10% hard) and CR constraints (max CR = levels/4).
    Ensures variety with random bag monster selection per location type.
    
    AI Agents: This replaces the old simple encounter system with proper D&D balance.
    """
    try:
        from services.encounter_service import get_encounter_service
        
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Use the encounter service for balanced generation
        encounter_service = get_encounter_service(db)
        encounter = encounter_service.generate_encounter(str(character_id), location_type)
        
        if encounter.get("error"):
            # Fallback to simple treasure/event if no monsters available
            encounter_roll = dice.roll("1d100")
            
            if encounter_roll <= 60:  # 60% chance of treasure
                treasure_roll = dice.roll("2d6") * character.level * 10
                
                return {
                    "type": "treasure",
                    "success": True,
                    "message": "You discover a hidden cache!",
                    "gold_found": treasure_roll,
                    "items_found": [],
                    "environment": location_type
                }
            else:  # 40% chance of special event
                events = [
                    "You find a mysterious inscription on the wall.",
                    "A gentle breeze carries the sound of distant music.",
                    "Strange symbols glow faintly on an ancient door.",
                    "You hear echoing footsteps from somewhere ahead.",
                    "A shaft of light illuminates a forgotten shrine."
                ]
                
                return {
                    "type": "event",
                    "success": True,
                    "message": dice.choice(events),
                    "requires_action": False,
                    "options": ["Continue exploring", "Investigate further", "Rest here"],
                    "environment": location_type
                }
        
        # Return the balanced encounter
        monsters_text = f"{encounter['monster_count']} monster{'s' if encounter['monster_count'] > 1 else ''}"
        difficulty_text = encounter['difficulty'].title()
        
        return {
            "type": "combat",
            "success": True,
            "message": f"You encounter {monsters_text}! ({difficulty_text} encounter)",
            "monsters": encounter["monsters"],
            "difficulty": encounter["difficulty"],
            "total_xp": encounter["total_xp"],
            "xp_budget": encounter["xp_budget"],
            "environment": location_type,
            "surprise": dice.roll("1d6") == 1,  # 16% chance of surprise
            "encounter_system": "balanced"  # Mark as using new system
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating encounter: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate encounter")

@router.get("/game-state/{character_id}", response_model=GameStateResponse)
async def get_game_state(
    character_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get current game state for character.
    
    AI Agents: Use for UI updates and state management.
    """
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        game_state = db.execute(
            select(GameState).where(GameState.character_id == character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            # Create default game state
            game_state = GameState(
                character_id=character_id,
                current_location="town",
                location_type=LocationType.TOWN,
                dungeon_level=0,
                room_number=0,
                short_rests_used=0,
                flags={},
                inventory_gold=0,
                playtime_minutes=0,
                last_long_rest=datetime.utcnow()
            )
            db.add(game_state)
            db.commit()
            db.refresh(game_state)
        
        return GameStateResponse(
            character_id=character_id,
            current_location=game_state.current_location,
            location_type=game_state.location_type,
            dungeon_level=game_state.dungeon_level,
            room_number=game_state.room_number,
            short_rests_used=game_state.short_rests_used,
            inventory_gold=game_state.inventory_gold,
            playtime_minutes=game_state.playtime_minutes,
            last_long_rest=game_state.last_long_rest,
            flags=game_state.flags or {},
            can_short_rest=game_state.short_rests_used < 2,  # Max 2 short rests per long rest
            can_long_rest=game_state.location_type in [LocationType.TOWN, LocationType.WILDERNESS],
            available_actions=_get_available_actions(game_state, character)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting game state: {e}")
        raise HTTPException(status_code=500, detail="Failed to get game state")

@router.post("/town-action", response_model=Dict[str, Any])
async def perform_town_action(
    action_data: TownActionRequest,
    db: Session = Depends(get_db)
):
    """
    Perform actions available in town.
    
    AI Agents: Extend for:
    - Shop interactions
    - Training and skill learning
    - Quest givers and NPCs
    """
    try:
        character = db.get(Character, action_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        game_state = db.execute(
            select(GameState).where(GameState.character_id == action_data.character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")
        
        if game_state.location_type != LocationType.TOWN:
            raise HTTPException(status_code=400, detail="Can only perform town actions while in town")
        
        result = {"success": True, "message": "", "effects": {}}
        
        if action_data.action_type == TownActionType.LONG_REST:
            # Perform long rest
            old_hp = character.current_hit_points
            character.current_hit_points = character.max_hit_points
            
            # Recover hit dice (half of max)
            hit_dice_recovered = max(1, character.level // 2)
            character.hit_dice_current = min(
                character.hit_dice_max,
                character.hit_dice_current + hit_dice_recovered
            )
            
            # Reset short rests and conditions
            game_state.short_rests_used = 0
            game_state.last_long_rest = datetime.utcnow()
            character.conditions = []
            character.death_saves_successes = 0
            character.death_saves_failures = 0
            
            result["message"] = "You rest at the inn and feel fully refreshed."
            result["effects"] = {
                "hp_restored": character.max_hit_points - old_hp,
                "hit_dice_recovered": hit_dice_recovered,
                "conditions_cleared": True,
                "short_rests_reset": True
            }
            
        elif action_data.action_type == TownActionType.SHOP:
            # Simple shop interaction
            shop_items = [
                {"name": "Health Potion", "cost": 50, "type": "consumable"},
                {"name": "Leather Armor", "cost": 100, "type": "armor"},
                {"name": "Shield", "cost": 100, "type": "armor"},
                {"name": "Sword", "cost": 150, "type": "weapon"}
            ]
            
            result["message"] = "Welcome to the general store!"
            result["effects"] = {"shop_items": shop_items, "player_gold": game_state.inventory_gold}
            
        elif action_data.action_type == TownActionType.TAVERN:
            # Tavern for information and rumors
            rumors = [
                "Strange lights have been seen in the old ruins to the north.",
                "A merchant caravan went missing on the eastern road.",
                "The local lord is offering a reward for clearing out the goblin caves.",
                "An ancient treasure is said to be hidden in the haunted mansion."
            ]
            
            selected_rumor = dice.choice(rumors)
            result["message"] = f"You overhear a conversation: '{selected_rumor}'"
            result["effects"] = {"rumor": selected_rumor, "cost": 5}
            
            # Deduct tavern cost
            if game_state.inventory_gold >= 5:
                game_state.inventory_gold -= 5
            
        elif action_data.action_type == TownActionType.TRAIN:
            # Training for ability score improvements (future feature)
            training_cost = character.level * 100
            
            if game_state.inventory_gold >= training_cost:
                result["message"] = f"Training available for {training_cost} gold."
                result["effects"] = {"training_cost": training_cost, "available": True}
            else:
                result["message"] = f"Training costs {training_cost} gold. You need {training_cost - game_state.inventory_gold} more gold."
                result["effects"] = {"training_cost": training_cost, "available": False}
        
        db.commit()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing town action: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to perform town action")

def _get_available_actions(game_state: GameState, character: Character) -> List[str]:
    """Get list of available actions based on current game state."""
    actions = []
    
    if game_state.location_type == LocationType.TOWN:
        actions.extend(["shop", "tavern", "long_rest", "enter_dungeon"])
        if character.level < 3:
            actions.append("train")
    
    elif game_state.location_type == LocationType.DUNGEON:
        actions.extend(["explore", "search", "exit_dungeon"])
        if game_state.short_rests_used < 2:
            actions.append("short_rest")
    
    elif game_state.location_type == LocationType.WILDERNESS:
        actions.extend(["travel", "make_camp", "long_rest"])
        if game_state.short_rests_used < 2:
            actions.append("short_rest")
    
    return actions