"""
File: backend/routers/character.py
Path: /backend/routers/character.py

Pseudo Code:
1. Get races/classes/backgrounds: return available options from database
2. Create character: validate choices, calculate stats, assign equipment
3. Get character: fetch character with all related data (race, class, equipment)
4. Update character: modify attributes, recalculate derived stats
5. Level up: check XP, increase level, add HP, apply features
6. Rest: recover HP/abilities, reset conditions, manage hit dice

Character Management Router
Handles character creation, updates, and progression.

AI Agents: Key endpoints:
- POST /create - Create new character
- GET /{character_id} - Get character details
- PATCH /{character_id} - Update character
- POST /{character_id}/level-up - Level up character
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
from loguru import logger

from database import get_db, GameQueries
from models.character import Character, CharacterCreate, CharacterUpdate, CharacterResponse
from models.races import Race
from models.classes import Class, Subclass
from models.backgrounds import Background
from services.character_service import CharacterService
from services.dice import DiceRoller

router = APIRouter()
dice = DiceRoller()

@router.get("/races", response_model=List[Dict])
async def get_races(db: Session = Depends(get_db)):
    """
    Get all available races.
    AI Agents: Extend with subraces when implementing.
    """
    try:
        races = db.execute(select(Race)).scalars().all()
        return [
            {
                "id": race.id,
                "name": race.name,
                "size": race.size,
                "speed": race.speed,
                "ability_score_increase": race.ability_score_increase,
                "traits": race.traits,
                "description": race.description
            }
            for race in races
        ]
    except Exception as e:
        logger.error(f"Error fetching races: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch races")

@router.get("/classes", response_model=List[Dict])
async def get_classes(db: Session = Depends(get_db)):
    """Get all available classes."""
    try:
        classes = db.execute(select(Class)).scalars().all()
        return [
            {
                "id": cls.id,
                "name": cls.name,
                "hit_die": cls.hit_die,
                "primary_ability": cls.primary_ability,
                "saving_throws": cls.saving_throw_proficiencies,
                "skill_proficiencies": cls.skill_proficiencies,
                "starting_equipment": cls.starting_equipment,
                "features_by_level": cls.features_by_level
            }
            for cls in classes
        ]
    except Exception as e:
        logger.error(f"Error fetching classes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch classes")

@router.get("/backgrounds", response_model=List[Dict])
async def get_backgrounds(db: Session = Depends(get_db)):
    """Get all available backgrounds."""
    try:
        backgrounds = db.execute(select(Background)).scalars().all()
        return [
            {
                "id": bg.id,
                "name": bg.name,
                "skill_proficiencies": bg.skill_proficiencies,
                "tool_proficiencies": bg.tool_proficiencies,
                "languages": bg.language_proficiencies,
                "equipment": bg.starting_equipment,
                "feature_name": bg.feature_name,
                "feature_description": bg.feature_description
            }
            for bg in backgrounds
        ]
    except Exception as e:
        logger.error(f"Error fetching backgrounds: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch backgrounds")

@router.get("/classes/{class_id}/subclasses", response_model=List[Dict])
async def get_subclasses(class_id: int, db: Session = Depends(get_db)):
    """Get subclasses for a specific class."""
    try:
        subclasses = db.execute(
            select(Subclass).where(Subclass.class_id == class_id)
        ).scalars().all()
        
        return [
            {
                "id": sub.id,
                "name": sub.name,
                "choice_level": sub.choice_level,
                "features": sub.features,
                "description": sub.description
            }
            for sub in subclasses
        ]
    except Exception as e:
        logger.error(f"Error fetching subclasses: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subclasses")

@router.post("/create", response_model=CharacterResponse)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new character.
    
    AI Agents: This handles:
    - Ability score generation/assignment
    - HP calculation
    - Starting equipment
    - Skill/proficiency selection
    """
    try:
        service = CharacterService(db)
        
        # Create character (service handles validation)
        result = service.create_character(character_data)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to create character"))
        
        character = result["character"]
        return character  # Return the character dict directly
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create character")

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    db: Session = Depends(get_db)
):
    """Get character by ID with all details."""
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Load related data
        service = CharacterService(db)
        character_data = service.get_character_full(character_id)
        
        return character_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching character: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch character")

@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    updates: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update character attributes.
    AI Agents: Use for HP changes, condition updates, etc.
    """
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(character, field, value)
        
        # Recalculate derived stats if needed
        if any(field in update_data for field in 
               ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']):
            service = CharacterService(db)
            service.recalculate_stats(character)
        
        db.commit()
        db.refresh(character)
        
        return CharacterResponse.from_orm(character)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating character: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update character")

@router.post("/{character_id}/level-up")
async def level_up_character(
    character_id: UUID,
    choices: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Level up a character.
    
    Choices include:
    - hp_roll: Result of hit die roll
    - ability_score_improvements: Dict of ability increases
    - feat: Selected feat (if applicable)
    - new_spells: Selected spells (for casters)
    
    AI Agents: Extend for:
    - Multiclassing
    - Feat selection (level 4+)
    - Spell selection
    """
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        service = CharacterService(db)
        
        # Check if character can level up
        required_xp = service.get_xp_for_level(character.level + 1)
        if character.experience_points < required_xp:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient XP. Need {required_xp}, have {character.experience_points}"
            )
        
        # Process level up
        old_level = character.level
        character.level += 1
        
        # Increase HP
        char_class = db.get(Class, character.class_id)
        con_mod = GameQueries.ability_modifier(character.constitution)
        
        if 'hp_roll' in choices:
            hp_increase = choices['hp_roll'] + con_mod
        else:
            # Average HP increase
            hp_increase = (char_class.hit_die // 2 + 1) + con_mod
        
        character.max_hit_points += max(1, hp_increase)
        character.current_hit_points += max(1, hp_increase)
        
        # Update proficiency bonus
        character.proficiency_bonus = GameQueries.get_proficiency_bonus(character.level)
        
        # Handle ability score improvements (level 4, 8, 12, 16, 19)
        if character.level in [4, 8, 12, 16, 19]:
            if 'ability_score_improvements' in choices:
                for ability, increase in choices['ability_score_improvements'].items():
                    current = getattr(character, ability)
                    setattr(character, ability, min(20, current + increase))
        
        # Apply class features for new level
        if char_class.features_by_level:
            features = json.loads(char_class.features_by_level) if isinstance(
                char_class.features_by_level, str
            ) else char_class.features_by_level
            
            level_features = features.get(str(character.level), [])
            logger.info(f"Character gained features: {level_features}")
            # AI Agents: Apply specific feature mechanics here
        
        # Handle subclass features (if level 3)
        if character.level == 3 and character.subclass_id:
            subclass = db.get(Subclass, character.subclass_id)
            if subclass:
                logger.info(f"Character gained subclass: {subclass.name}")
                # AI Agents: Apply subclass features
        
        db.commit()
        db.refresh(character)
        
        return {
            "success": True,
            "old_level": old_level,
            "new_level": character.level,
            "hp_gained": hp_increase,
            "new_features": level_features if 'level_features' in locals() else [],
            "character": CharacterResponse.from_orm(character)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error leveling up character: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to level up character")

@router.post("/{character_id}/rest")
async def rest_character(
    character_id: UUID,
    rest_type: str,  # "short" or "long"
    hit_dice_used: int = 0,
    db: Session = Depends(get_db)
):
    """
    Process a rest for the character.
    
    Short Rest:
    - Spend hit dice to recover HP
    - Recover some abilities (Second Wind, etc.)
    
    Long Rest:
    - Recover all HP
    - Recover all hit dice (up to half total)
    - Recover all abilities
    - Remove exhaustion (1 level)
    
    AI Agents: Extend for:
    - Spell slot recovery
    - Exhaustion mechanics
    - Condition removal
    """
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        service = CharacterService(db)
        result = {}
        
        if rest_type == "short":
            # Short rest
            hp_healed = 0
            
            # Use hit dice
            if hit_dice_used > 0 and character.hit_dice_current > 0:
                dice_to_use = min(hit_dice_used, character.hit_dice_current)
                char_class = db.get(Class, character.class_id)
                con_mod = GameQueries.ability_modifier(character.constitution)
                
                for _ in range(dice_to_use):
                    heal = dice.roll(f"1d{char_class.hit_die}") + con_mod
                    hp_healed += max(1, heal)
                
                character.hit_dice_current -= dice_to_use
                old_hp = character.current_hit_points
                character.current_hit_points = min(
                    character.max_hit_points,
                    character.current_hit_points + hp_healed
                )
                actual_healed = character.current_hit_points - old_hp
                
                result = {
                    "type": "short",
                    "hit_dice_used": dice_to_use,
                    "hp_healed": actual_healed,
                    "hit_dice_remaining": character.hit_dice_current
                }
            
            # Recover short rest abilities
            # AI Agents: Add class-specific short rest recovery here
            
        elif rest_type == "long":
            # Long rest
            old_hp = character.current_hit_points
            character.current_hit_points = character.max_hit_points
            
            # Recover hit dice (half of max)
            hit_dice_recovered = max(1, character.level // 2)
            character.hit_dice_current = min(
                character.hit_dice_max,
                character.hit_dice_current + hit_dice_recovered
            )
            
            # Reset death saves
            character.death_saves_successes = 0
            character.death_saves_failures = 0
            
            # Clear conditions
            character.conditions = []
            
            # Recover all abilities
            # AI Agents: Reset daily abilities, spell slots, etc.
            
            # Update game state - reset short rests counter
            from models.game import GameState
            game_state = db.execute(
                select(GameState).where(GameState.character_id == character_id)
            ).scalar_one_or_none()
            
            if game_state:
                game_state.short_rests_used = 0
                game_state.last_long_rest = db.func.current_timestamp()
            
            result = {
                "type": "long",
                "hp_healed": character.max_hit_points - old_hp,
                "hit_dice_recovered": hit_dice_recovered,
                "hit_dice_current": character.hit_dice_current,
                "conditions_cleared": True
            }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid rest type. Use 'short' or 'long'")
        
        db.commit()
        db.refresh(character)
        
        result["character"] = CharacterResponse.from_orm(character)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing rest: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process rest")

@router.get("/{character_id}/inventory")
async def get_character_inventory(
    character_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get character's inventory with equipped items marked.
    AI Agents: Extend with encumbrance calculation.
    """
    try:
        from models.items import CharacterInventory, Item
        
        inventory = db.execute(
            select(CharacterInventory, Item)
            .join(Item, CharacterInventory.item_id == Item.id)
            .where(CharacterInventory.character_id == character_id)
        ).all()
        
        return [
            {
                "item": {
                    "id": item.id,
                    "name": item.name,
                    "type": item.type,
                    "subtype": item.subtype,
                    "rarity": item.rarity,
                    "weight": float(item.weight) if item.weight else 0,
                    "cost_gp": float(item.cost_gp) if item.cost_gp else 0,
                    "description": item.description,
                    "properties": item.properties
                },
                "quantity": inv.quantity,
                "equipped": inv.equipped,
                "equipped_slot": inv.equipped_slot,
                "identified": inv.identified,
                "notes": inv.notes
            }
            for inv, item in inventory
        ]
        
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch inventory")