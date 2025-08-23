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
from core.dtos import CharacterDTO, MonsterDTO, RaceDTO, ClassDTO, BackgroundDTO, SaveSlotDTO
from sqlalchemy.orm import selectinload


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
    
    def _character_to_dto(self, character: Character) -> CharacterDTO:
        """
        Convert SQLAlchemy Character model to CharacterDTO.
        This method assumes all relationships are already loaded via selectinload.
        """
        return CharacterDTO(
            # Core Identity
            id=character.id,
            name=character.name,
            level=character.level,
            experience_points=character.experience_points,
            
            # Character Build
            race_id=character.race_id,
            race_name=character.race.name if character.race else "Unknown",
            class_id=character.class_id,
            class_name=character.character_class.name if character.character_class else "Unknown",
            subclass_id=character.subclass_id,
            subclass_name=character.subclass.name if character.subclass else None,
            background_id=character.background_id,
            background_name=character.background.name if character.background else "Unknown",
            
            # Ability Scores
            strength=character.strength,
            dexterity=character.dexterity,
            constitution=character.constitution,
            intelligence=character.intelligence,
            wisdom=character.wisdom,
            charisma=character.charisma,
            
            # Ability Modifiers
            strength_modifier=character.strength_modifier,
            dexterity_modifier=character.dexterity_modifier,
            constitution_modifier=character.constitution_modifier,
            intelligence_modifier=character.intelligence_modifier,
            wisdom_modifier=character.wisdom_modifier,
            charisma_modifier=character.charisma_modifier,
            
            # Combat Stats
            armor_class=character.armor_class,
            hit_points_max=character.hit_points_max,
            hit_points_current=character.hit_points_current,
            hit_points_temporary=character.hit_points_temporary,
            hit_dice_max=character.hit_dice_max,
            hit_dice_current=character.hit_dice_current,
            death_saves_successes=character.death_saves_successes,
            death_saves_failures=character.death_saves_failures,
            conditions=character.conditions or [],
            
            # Character Features
            proficiencies=character.proficiencies or [],
            features=character.features or {},
            
            # Equipment
            equipment_main_hand=character.equipment_main_hand,
            equipment_off_hand=character.equipment_off_hand,
            equipment_armor=character.equipment_armor,
            equipment_shield=character.equipment_shield,
            
            # Metadata
            created_at=character.created_at,
            updated_at=character.updated_at,
            notes=character.notes or "",
            
            # Save Slot Info
            save_slot_id=character.save_slot_id,
            save_slot_number=character.save_slot.slot_number if character.save_slot else None
        )
    
    def _monster_to_dto(self, monster: Monster) -> MonsterDTO:
        """Convert SQLAlchemy Monster model to MonsterDTO."""
        return MonsterDTO(
            # Core Identity
            id=monster.id,
            name=monster.name,
            size=monster.size,
            type=monster.type,
            alignment=monster.alignment,
            
            # Combat Stats
            armor_class=monster.armor_class,
            hit_points=monster.hit_points,
            speed=monster.speed,
            challenge_rating=monster.challenge_rating,
            
            # Ability Scores
            strength=monster.strength,
            dexterity=monster.dexterity,
            constitution=monster.constitution,
            intelligence=monster.intelligence,
            wisdom=monster.wisdom,
            charisma=monster.charisma,
            
            # Skills and Saves
            skills=monster.skills or {},
            saving_throws=monster.saving_throws or {},
            damage_resistances=monster.damage_resistances or [],
            damage_immunities=monster.damage_immunities or [],
            condition_immunities=monster.condition_immunities or [],
            senses=monster.senses or [],
            languages=monster.languages or [],
            
            # Actions and Abilities
            actions=monster.actions or {},
            legendary_actions=monster.legendary_actions or {},
            special_abilities=monster.special_abilities or {},
            
            # AI and Behavior
            ai_script=monster.ai_script
        )
    
    def _race_to_dto(self, race: Race) -> RaceDTO:
        """Convert SQLAlchemy Race model to RaceDTO."""
        return RaceDTO(
            id=race.id,
            name=race.name,
            description=race.description,
            size=race.size,
            speed=race.speed,
            ability_score_increases=race.ability_score_increases or {},
            languages=race.languages or [],
            proficiencies=race.proficiencies or [],
            traits=race.traits or {}
        )
    
    def _class_to_dto(self, cls: Class, subclasses: List[Subclass] = None) -> ClassDTO:
        """Convert SQLAlchemy Class model to ClassDTO."""
        subclass_data = []
        if subclasses:
            for subclass in subclasses:
                subclass_data.append({
                    "id": subclass.id,
                    "name": subclass.name,
                    "description": subclass.description,
                    "features": subclass.features or {}
                })
        
        return ClassDTO(
            id=cls.id,
            name=cls.name,
            description=cls.description,
            hit_die=cls.hit_die,
            primary_ability=cls.primary_ability,
            armor_proficiencies=cls.armor_proficiencies or [],
            weapon_proficiencies=cls.weapon_proficiencies or [],
            saving_throw_proficiencies=cls.saving_throw_proficiencies or [],
            skill_proficiencies=cls.skill_proficiencies or [],
            subclasses=subclass_data
        )
    
    def _background_to_dto(self, background: Background) -> BackgroundDTO:
        """Convert SQLAlchemy Background model to BackgroundDTO."""
        return BackgroundDTO(
            id=background.id,
            name=background.name,
            description=background.description or "",
            skill_proficiencies=background.skill_proficiencies or [],
            tool_proficiencies=background.tool_proficiencies or [],
            languages=background.language_proficiencies or [],  # Fixed: was .languages
            equipment=background.starting_equipment or [],  # Fixed: was .equipment
            feature_name=background.feature_name or "",
            feature_description=background.feature_description or ""
        )
    
    def _save_slot_to_dto(self, slot: SaveSlot) -> SaveSlotDTO:
        """Convert SQLAlchemy SaveSlot model to SaveSlotDTO."""
        return SaveSlotDTO(
            id=slot.id,
            slot_number=slot.slot_number,
            is_occupied=slot.is_occupied,
            save_name=slot.save_name,
            character_name=slot.character_name,
            character_level=slot.character_level,
            current_location=slot.current_location,
            play_time_hours=int((slot.play_time_minutes or 0) / 60),  # Convert minutes to hours
            last_played=slot.last_played,
            created_at=slot.created_at
        )
    
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
    
    def get_save_slots(self) -> List[SaveSlotDTO]:
        """Get all save slot information as DTOs."""
        with DatabaseSession() as db:
            slots = db.query(SaveSlot).order_by(SaveSlot.slot_number).all()
            return [self._save_slot_to_dto(slot) for slot in slots]
    
    def create_new_character(self, character_data: Dict[str, Any], save_slot: int) -> CharacterDTO:
        """
        Create a new character and assign to save slot.
        
        Args:
            character_data: Character creation data
            save_slot: Save slot number (1-10)
            
        Returns:
            Created character as DTO (no session dependencies)
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
            
            # Eagerly load all relationships using selectinload for clean approach
            character_with_relationships = db.query(Character).options(
                selectinload(Character.race),
                selectinload(Character.character_class),
                selectinload(Character.subclass),
                selectinload(Character.background),
                selectinload(Character.save_slot)
            ).filter_by(id=character.id).first()
            
            # Convert to DTO immediately - no more DetachedInstanceError!
            character_dto = self._character_to_dto(character_with_relationships)
            
            logger.info(f"Created new character: {character_dto.name} in slot {save_slot}")
            return character_dto
    
    def load_character(self, save_slot: int) -> Optional[CharacterDTO]:
        """
        Load character from save slot.
        
        Args:
            save_slot: Save slot number (1-10)
            
        Returns:
            Loaded character as DTO or None if slot empty
        """
        with DatabaseSession() as db:
            slot = db.query(SaveSlot).filter_by(slot_number=save_slot).first()
            if not slot or not slot.is_occupied:
                return None
            
            # Eagerly load all character relationships using selectinload
            character = db.query(Character).options(
                selectinload(Character.race),
                selectinload(Character.character_class),
                selectinload(Character.subclass),
                selectinload(Character.background),
                selectinload(Character.save_slot)
            ).filter_by(save_slot_id=slot.id).first()
            
            if character:
                # Load game state
                game_state = db.query(GameState).filter_by(character_id=character.id).first()
                
                # Convert to DTO before setting as current (avoids DetachedInstanceError)
                character_dto = self._character_to_dto(character)
                
                # Update current state with DTO
                self.current_character = character_dto
                self.current_save_slot = self._save_slot_to_dto(slot)  
                self.game_state = game_state  # Keep as SQLAlchemy object for now
                
                # Update last played
                slot.last_played = datetime.utcnow()
                db.commit()
                
                logger.info(f"Loaded character: {character_dto.name} from slot {save_slot}")
                return character_dto
            
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
    
    def get_available_races(self) -> List[RaceDTO]:
        """Get all available races for character creation as DTOs."""
        with DatabaseSession() as db:
            races = db.query(Race).all()
            return [self._race_to_dto(race) for race in races]
    
    def get_available_classes(self) -> List[ClassDTO]:
        """Get all available classes for character creation as DTOs."""
        with DatabaseSession() as db:
            classes = db.query(Class).all()
            class_dtos = []
            for cls in classes:
                # Load subclasses for this class
                subclasses = db.query(Subclass).filter_by(class_id=cls.id).all()
                class_dto = self._class_to_dto(cls, subclasses)
                class_dtos.append(class_dto)
            return class_dtos
    
    def get_available_backgrounds(self) -> List[BackgroundDTO]:
        """Get all available backgrounds for character creation as DTOs."""
        with DatabaseSession() as db:
            backgrounds = db.query(Background).all()
            return [self._background_to_dto(bg) for bg in backgrounds]
    
    
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
    
    def get_monsters_by_cr(self, min_cr: float, max_cr: float) -> List[MonsterDTO]:
        """
        Get monsters within CR range as DTOs.
        No DetachedInstanceError possible with DTOs!
        """
        with DatabaseSession() as db:
            monsters = db.query(Monster).filter(
                Monster.challenge_rating >= min_cr,
                Monster.challenge_rating <= max_cr
            ).all()
            
            # Convert all monsters to DTOs
            monster_dtos = [self._monster_to_dto(monster) for monster in monsters]
            
            return monster_dtos
    
    def auto_save(self):
        """Perform automatic save if enough time has passed."""
        if self.current_character and self.current_save_slot:
            self.save_game()
    
    def shutdown(self):
        """Clean shutdown of game engine."""
        logger.info("Game engine shutting down")
        self.save_game()
        self.save_settings()