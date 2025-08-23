"""
File: core/game_engine.py
Path: /core/game_engine.py

Main game engine for TaleKeeper Desktop.
Coordinates all game systems and manages application state.

Pseudo Code:
1. Initialize all game services (combat, character, dice)
2. Manage active game state and current character
3. Coordinate between UI and game logic
4. Handle save/load operations
5. Process game events and state transitions

AI Agents: Central hub for all game mechanics coordination.
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from core.database import DatabaseSession
from services.dice import DiceRoller
from models.character import Character, Race, Class, Background, Subclass
from models.monsters import Monster
from models.game import SaveSlot, GameState
from models.combat import CombatSession


class GameEngine:
    """
    Central game engine managing all systems.
    
    AI Agents: Add new game systems and coordination logic here.
    """
    
    def __init__(self):
        """Initialize the game engine."""
        self.dice_roller = DiceRoller()
        self.current_character: Optional[Character] = None
        self.current_save_slot: Optional[SaveSlot] = None
        self.game_state: Optional[GameState] = None
        self.active_combat: Optional[CombatSession] = None
        
        # Game settings
        self.settings = self._load_settings()
        
        logger.info("Game engine initialized")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load game settings from config file."""
        settings_file = "config/settings.json"
        default_settings = {
            "auto_save_interval": 300,  # 5 minutes
            "difficulty": "normal",
            "sound_enabled": True,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "window_width": 1200,
            "window_height": 800,
            "theme": "dark"
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    default_settings.update(loaded_settings)
                    logger.info("Game settings loaded")
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}, using defaults")
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to config file."""
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Game settings saved")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get_save_slots(self) -> List[Dict[str, Any]]:
        """Get all save slot information."""
        with DatabaseSession() as db:
            slots = db.query(SaveSlot).order_by(SaveSlot.slot_number).all()
            return [self._save_slot_to_dict(slot) for slot in slots]
    
    def _save_slot_to_dict(self, slot: SaveSlot) -> Dict[str, Any]:
        """Convert save slot to dictionary."""
        return {
            "slot_number": slot.slot_number,
            "is_occupied": slot.is_occupied,
            "save_name": slot.save_name,
            "character_name": slot.character_name,
            "character_level": slot.character_level,
            "current_location": slot.current_location,
            "last_played": slot.last_played.isoformat() if slot.last_played else None,
            "play_time_minutes": slot.play_time_minutes
        }
    
    def create_new_character(self, character_data: Dict[str, Any], save_slot: int) -> Character:
        """
        Create a new character and assign to save slot.
        
        Args:
            character_data: Character creation data
            save_slot: Save slot number (1-10)
            
        Returns:
            Created character
        """
        with DatabaseSession() as db:
            # Get or create save slot
            slot = db.query(SaveSlot).filter_by(slot_number=save_slot).first()
            if not slot:
                slot = SaveSlot(slot_number=save_slot)
                db.add(slot)
                db.flush()
            
            # Create character
            character = Character(
                save_slot_id=slot.id,
                name=character_data["name"],
                race_id=character_data["race_id"],
                class_id=character_data["class_id"],
                background_id=character_data["background_id"],
                subclass_id=character_data.get("subclass_id"),
                strength=character_data.get("strength", 10),
                dexterity=character_data.get("dexterity", 10),
                constitution=character_data.get("constitution", 10),
                intelligence=character_data.get("intelligence", 10),
                wisdom=character_data.get("wisdom", 10),
                charisma=character_data.get("charisma", 10),
                notes=character_data.get("notes", "")
            )
            
            # Calculate derived stats
            self._calculate_character_stats(character, db)
            
            db.add(character)
            db.flush()
            
            # Create game state
            game_state = GameState(
                character_id=character.id,
                current_location="Starting Town",
                location_type="town"
            )
            db.add(game_state)
            
            # Update save slot
            slot.is_occupied = True
            slot.character_name = character.name
            slot.character_level = character.level
            slot.current_location = game_state.current_location
            slot.last_played = datetime.utcnow()
            slot.save_name = f"{character.name} - Level {character.level}"
            
            db.commit()
            
            logger.info(f"Created new character: {character.name} in slot {save_slot}")
            return character
    
    def load_character(self, save_slot: int) -> Optional[Character]:
        """
        Load character from save slot.
        
        Args:
            save_slot: Save slot number (1-10)
            
        Returns:
            Loaded character or None if slot empty
        """
        with DatabaseSession() as db:
            slot = db.query(SaveSlot).filter_by(slot_number=save_slot).first()
            if not slot or not slot.is_occupied:
                return None
            
            character = db.query(Character).filter_by(save_slot_id=slot.id).first()
            if character:
                # Load game state
                game_state = db.query(GameState).filter_by(character_id=character.id).first()
                
                self.current_character = character
                self.current_save_slot = slot
                self.game_state = game_state
                
                # Update last played
                slot.last_played = datetime.utcnow()
                db.commit()
                
                logger.info(f"Loaded character: {character.name} from slot {save_slot}")
                return character
            
            return None
    
    def save_game(self):
        """Save current game state."""
        if not self.current_character or not self.current_save_slot:
            return
        
        with DatabaseSession() as db:
            # Update save slot info
            slot = db.merge(self.current_save_slot)
            slot.last_played = datetime.utcnow()
            slot.character_level = self.current_character.level
            slot.current_location = self.game_state.current_location if self.game_state else "Unknown"
            
            # Update character
            character = db.merge(self.current_character)
            
            # Update game state
            if self.game_state:
                game_state = db.merge(self.game_state)
            
            db.commit()
            logger.info("Game saved")
    
    def get_available_races(self) -> List[Dict[str, Any]]:
        """Get all available races for character creation."""
        with DatabaseSession() as db:
            races = db.query(Race).all()
            return [self._race_to_dict(race) for race in races]
    
    def get_available_classes(self) -> List[Dict[str, Any]]:
        """Get all available classes for character creation."""
        with DatabaseSession() as db:
            classes = db.query(Class).all()
            return [self._class_to_dict(cls, db) for cls in classes]
    
    def get_available_backgrounds(self) -> List[Dict[str, Any]]:
        """Get all available backgrounds for character creation."""
        with DatabaseSession() as db:
            backgrounds = db.query(Background).all()
            return [self._background_to_dict(bg) for bg in backgrounds]
    
    def _race_to_dict(self, race: Race) -> Dict[str, Any]:
        """Convert race to dictionary."""
        return {
            "id": race.id,
            "name": race.name,
            "description": race.description,
            "size": race.size,
            "speed": race.speed,
            "ability_score_increases": race.ability_score_increases or {},
            "languages": race.languages or [],
            "proficiencies": race.proficiencies or [],
            "traits": race.traits or {}
        }
    
    def _class_to_dict(self, cls: Class, db) -> Dict[str, Any]:
        """Convert class to dictionary."""
        subclasses = db.query(Subclass).filter_by(class_id=cls.id).all()
        return {
            "id": cls.id,
            "name": cls.name,
            "description": cls.description,
            "hit_die": cls.hit_die,
            "primary_ability": cls.primary_ability,
            "saving_throw_proficiencies": cls.saving_throw_proficiencies or [],
            "armor_proficiencies": cls.armor_proficiencies or [],
            "weapon_proficiencies": cls.weapon_proficiencies or [],
            "skill_proficiencies": cls.skill_proficiencies or [],
            "skill_choices": cls.skill_choices,
            "subclasses": [{"id": sub.id, "name": sub.name, "description": sub.description} for sub in subclasses]
        }
    
    def _background_to_dict(self, bg: Background) -> Dict[str, Any]:
        """Convert background to dictionary."""
        return {
            "id": bg.id,
            "name": bg.name,
            "description": bg.description,
            "skill_proficiencies": bg.skill_proficiencies or [],
            "language_proficiencies": bg.language_proficiencies or [],
            "tool_proficiencies": bg.tool_proficiencies or [],
            "feature_name": bg.feature_name,
            "feature_description": bg.feature_description
        }
    
    def _calculate_character_stats(self, character: Character, db):
        """Calculate derived character statistics."""
        # Get race and class for calculations
        race = db.query(Race).filter_by(id=character.race_id).first()
        char_class = db.query(Class).filter_by(id=character.class_id).first()
        
        # Apply racial bonuses
        if race and race.ability_score_increases:
            for ability, bonus in race.ability_score_increases.items():
                current_score = getattr(character, ability.lower(), 10)
                setattr(character, ability.lower(), current_score + bonus)
        
        # Calculate AC (10 + Dex modifier)
        character.armor_class = 10 + character.dexterity_modifier
        
        # Calculate HP (class hit die + con modifier)
        if char_class:
            character.hit_points_max = char_class.hit_die + character.constitution_modifier
            character.hit_points_current = character.hit_points_max
            character.max_hit_points = character.hit_points_max  # Alternative field
            character.current_hit_points = character.hit_points_max
            character.hit_dice_max = character.level
            character.hit_dice_current = character.level
    
    def roll_dice(self, notation: str, advantage: bool = False, disadvantage: bool = False) -> int:
        """Roll dice using the game's dice roller."""
        return self.dice_roller.roll(notation, advantage, disadvantage)
    
    def get_monsters_by_cr(self, min_cr: float, max_cr: float) -> List[Monster]:
        """Get monsters within CR range."""
        with DatabaseSession() as db:
            return db.query(Monster).filter(
                Monster.challenge_rating >= min_cr,
                Monster.challenge_rating <= max_cr
            ).all()
    
    def auto_save(self):
        """Perform automatic save if enough time has passed."""
        if self.current_character and self.current_save_slot:
            self.save_game()
    
    def shutdown(self):
        """Clean shutdown of game engine."""
        logger.info("Game engine shutting down")
        self.save_game()
        self.save_settings()