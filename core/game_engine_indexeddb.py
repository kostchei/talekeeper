"""
File: core/game_engine_indexeddb.py
Path: /core/game_engine_indexeddb.py

IndexedDB-compatible game engine for TaleKeeper Desktop.
Coordinates all game systems using IndexedDB instead of SQLite/SQLAlchemy.

Pseudo Code:
1. Initialize all game services (combat, character, dice) with IndexedDB
2. Manage active game state and current character using dataclasses
3. Coordinate between UI and game logic without ORM dependencies
4. Handle save/load operations with IndexedDB async operations
5. Process game events and state transitions

AI Agents: Central hub for all game mechanics coordination using IndexedDB.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from core.database_indexeddb import indexeddb, get_indexeddb_session
from services.dice import DiceRoller
from models.character_indexeddb import Character, Race, Class, Background, Subclass
from models.monsters_indexeddb import Monster
from models.game_indexeddb import SaveSlot, GameState
from models.combat_indexeddb import CombatSession
from core.dtos import CharacterDTO, MonsterDTO, RaceDTO, ClassDTO, BackgroundDTO, SaveSlotDTO


class GameEngineIndexedDB:
    """
    Central game engine managing all systems with IndexedDB.
    
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
        
        logger.info("IndexedDB Game engine initialized")
    
    async def _ensure_connected(self):
        """Ensure IndexedDB connection is established."""
        if not indexeddb.is_connected:
            await indexeddb.connect()
    
    def _character_to_dto(self, character: Character) -> CharacterDTO:
        """Convert Character dataclass to CharacterDTO."""
        return CharacterDTO(
            # Core Identity
            id=character.id,
            name=character.name,
            level=character.level,
            experience_points=character.experience_points,
            
            # Character Build
            race_id=character.race_id,
            race_name="Unknown",  # Will be resolved separately
            class_id=character.class_id,
            class_name="Unknown",  # Will be resolved separately
            subclass_id=character.subclass_id,
            subclass_name=None,  # Will be resolved separately
            background_id=character.background_id,
            background_name="Unknown",  # Will be resolved separately
            
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
            created_at=datetime.fromisoformat(character.created_at) if character.created_at else None,
            updated_at=datetime.fromisoformat(character.updated_at) if character.updated_at else None,
            notes=character.notes or "",
            
            # Save Slot Info
            save_slot_id=character.save_slot_id,
            save_slot_number=None  # Will be resolved separately
        )
    
    def _monster_to_dto(self, monster: Monster) -> MonsterDTO:
        """Convert Monster dataclass to MonsterDTO."""
        return MonsterDTO(
            # Core Identity
            id=monster.name,  # Use name as ID for monsters
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
            senses=monster.senses or {},
            languages=monster.languages or [],
            
            # Actions and Abilities
            actions=monster.actions or [],
            legendary_actions=monster.legendary_actions or [],
            special_abilities=monster.special_abilities or [],
            
            # AI and Behavior
            ai_script=monster.ai_script
        )
    
    def _race_to_dto(self, race: Race) -> RaceDTO:
        """Convert Race dataclass to RaceDTO."""
        return RaceDTO(
            id=race.name,  # Use name as ID for races
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
        """Convert Class dataclass to ClassDTO."""
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
            id=cls.name,  # Use name as ID for classes
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
        """Convert Background dataclass to BackgroundDTO."""
        return BackgroundDTO(
            id=background.name,  # Use name as ID for backgrounds
            name=background.name,
            description=background.description or "",
            skill_proficiencies=background.skill_proficiencies or [],
            tool_proficiencies=background.tool_proficiencies or [],
            languages=background.language_proficiencies or [],
            equipment=background.starting_equipment or {},
            feature_name=background.feature_name or "",
            feature_description=background.feature_description or ""
        )
    
    def _save_slot_to_dto(self, slot: SaveSlot) -> SaveSlotDTO:
        """Convert SaveSlot dataclass to SaveSlotDTO."""
        last_played = None
        if slot.last_played:
            try:
                last_played = datetime.fromisoformat(slot.last_played)
            except:
                pass
        
        return SaveSlotDTO(
            id=slot.id,
            slot_number=slot.slot_number,
            is_occupied=slot.is_occupied,
            save_name=slot.save_name,
            character_name=slot.character_name,
            character_level=slot.character_level,
            current_location=slot.current_location,
            play_time_hours=int(slot.play_time_minutes / 60) if slot.play_time_minutes else 0,
            last_played=last_played,
            created_at=datetime.fromisoformat(slot.created_at) if slot.created_at else None
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
    
    async def get_save_slots(self) -> List[SaveSlotDTO]:
        """Get all save slot information as DTOs."""
        await self._ensure_connected()
        
        slots_data = await indexeddb.get_all('save_slots')
        slots = []
        for slot_data in slots_data:
            slot = SaveSlot.from_dict(slot_data)
            slots.append(self._save_slot_to_dto(slot))
        
        # Sort by slot number
        slots.sort(key=lambda s: s.slot_number)
        return slots
    
    def get_save_slots_sync(self) -> List[SaveSlotDTO]:
        """Synchronous version of get_save_slots."""
        return asyncio.run(self.get_save_slots())
    
    async def create_new_character(self, character_data: Dict[str, Any], save_slot: int) -> CharacterDTO:
        """
        Create a new character and assign to save slot.
        
        Args:
            character_data: Character creation data
            save_slot: Save slot number (1-10)
            
        Returns:
            Created character as DTO
        """
        await self._ensure_connected()
        
        # Get or create save slot
        slot_data = await indexeddb.query_index('save_slots', 'slot_number', save_slot)
        if slot_data:
            slot = SaveSlot.from_dict(slot_data[0])
        else:
            slot = SaveSlot(slot_number=save_slot)
            await indexeddb.put('save_slots', slot.to_dict(), slot.id)
        
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
        await self._calculate_character_stats(character)
        
        # Save character
        await indexeddb.put('characters', character.to_dict(), character.id)
        
        # Create game state
        game_state = GameState(
            character_id=character.id,
            current_location="Starting Town",
            location_type="town"
        )
        await indexeddb.put('game_states', game_state.to_dict(), game_state.id)
        
        # Update save slot
        slot.is_occupied = True
        slot.character_name = character.name
        slot.character_level = character.level
        slot.current_location = game_state.current_location
        slot.last_played = datetime.now().isoformat()
        slot.save_name = f"{character.name} - Level {character.level}"
        slot.updated_at = datetime.now().isoformat()
        
        await indexeddb.put('save_slots', slot.to_dict(), slot.id)
        
        # Convert to DTO
        character_dto = self._character_to_dto(character)
        
        logger.info(f"Created new character: {character_dto.name} in slot {save_slot}")
        return character_dto
    
    def create_new_character_sync(self, character_data: Dict[str, Any], save_slot: int) -> CharacterDTO:
        """Synchronous version of create_new_character."""
        return asyncio.run(self.create_new_character(character_data, save_slot))
    
    async def load_character(self, save_slot: int) -> Optional[CharacterDTO]:
        """
        Load character from save slot.
        
        Args:
            save_slot: Save slot number (1-10)
            
        Returns:
            Loaded character as DTO or None if slot empty
        """
        await self._ensure_connected()
        
        # Find save slot
        slot_data_list = await indexeddb.query_index('save_slots', 'slot_number', save_slot)
        if not slot_data_list:
            return None
        
        slot = SaveSlot.from_dict(slot_data_list[0])
        if not slot.is_occupied:
            return None
        
        # Find character
        characters_data = await indexeddb.get_all('characters')
        character_data = None
        for char_data in characters_data:
            if char_data.get('save_slot_id') == slot.id:
                character_data = char_data
                break
        
        if not character_data:
            return None
        
        character = Character.from_dict(character_data)
        
        # Load game state
        game_states_data = await indexeddb.get_all('game_states')
        game_state = None
        for gs_data in game_states_data:
            if gs_data.get('character_id') == character.id:
                game_state = GameState.from_dict(gs_data)
                break
        
        # Update current state
        self.current_character = character
        self.current_save_slot = slot
        self.game_state = game_state
        
        # Update last played
        slot.last_played = datetime.now().isoformat()
        await indexeddb.put('save_slots', slot.to_dict(), slot.id)
        
        # Convert to DTO
        character_dto = self._character_to_dto(character)
        
        logger.info(f"Loaded character: {character_dto.name} from slot {save_slot}")
        return character_dto
    
    def load_character_sync(self, save_slot: int) -> Optional[CharacterDTO]:
        """Synchronous version of load_character."""
        return asyncio.run(self.load_character(save_slot))
    
    async def save_game(self):
        """Save current game state."""
        if not self.current_character or not self.current_save_slot:
            return
        
        await self._ensure_connected()
        
        # Update save slot info
        self.current_save_slot.last_played = datetime.now().isoformat()
        self.current_save_slot.character_level = self.current_character.level
        self.current_save_slot.current_location = self.game_state.current_location if self.game_state else "Unknown"
        self.current_save_slot.updated_at = datetime.now().isoformat()
        
        await indexeddb.put('save_slots', self.current_save_slot.to_dict(), self.current_save_slot.id)
        
        # Update character
        self.current_character.updated_at = datetime.now().isoformat()
        await indexeddb.put('characters', self.current_character.to_dict(), self.current_character.id)
        
        # Update game state
        if self.game_state:
            self.game_state.updated_at = datetime.now().isoformat()
            await indexeddb.put('game_states', self.game_state.to_dict(), self.game_state.id)
        
        logger.info("Game saved")
    
    def save_game_sync(self):
        """Synchronous version of save_game."""
        asyncio.run(self.save_game())
    
    async def get_available_races(self) -> List[RaceDTO]:
        """Get all available races for character creation as DTOs."""
        await self._ensure_connected()
        
        races_data = await indexeddb.get_all('races')
        races = []
        for race_data in races_data:
            race = Race.from_dict(race_data)
            races.append(self._race_to_dto(race))
        
        return sorted(races, key=lambda r: r.name)
    
    def get_available_races_sync(self) -> List[RaceDTO]:
        """Synchronous version of get_available_races."""
        return asyncio.run(self.get_available_races())
    
    async def get_available_classes(self) -> List[ClassDTO]:
        """Get all available classes for character creation as DTOs."""
        await self._ensure_connected()
        
        classes_data = await indexeddb.get_all('classes')
        subclasses_data = await indexeddb.get_all('subclasses')
        
        class_dtos = []
        for class_data in classes_data:
            cls = Class.from_dict(class_data)
            
            # Find subclasses for this class
            subclasses = []
            for subclass_data in subclasses_data:
                if subclass_data.get('class_id') == cls.name:
                    subclass = Subclass.from_dict(subclass_data)
                    subclasses.append(subclass)
            
            class_dto = self._class_to_dto(cls, subclasses)
            class_dtos.append(class_dto)
        
        return sorted(class_dtos, key=lambda c: c.name)
    
    def get_available_classes_sync(self) -> List[ClassDTO]:
        """Synchronous version of get_available_classes."""
        return asyncio.run(self.get_available_classes())
    
    async def get_available_backgrounds(self) -> List[BackgroundDTO]:
        """Get all available backgrounds for character creation as DTOs."""
        await self._ensure_connected()
        
        backgrounds_data = await indexeddb.get_all('backgrounds')
        backgrounds = []
        for bg_data in backgrounds_data:
            background = Background.from_dict(bg_data)
            backgrounds.append(self._background_to_dto(background))
        
        return sorted(backgrounds, key=lambda b: b.name)
    
    def get_available_backgrounds_sync(self) -> List[BackgroundDTO]:
        """Synchronous version of get_available_backgrounds."""
        return asyncio.run(self.get_available_backgrounds())
    
    async def _calculate_character_stats(self, character: Character):
        """Calculate derived character statistics."""
        await self._ensure_connected()
        
        # Get race and class for calculations
        race_data = await indexeddb.get('races', character.race_id)
        class_data = await indexeddb.get('classes', character.class_id)
        
        if race_data:
            race = Race.from_dict(race_data)
            # Apply racial bonuses
            if race.ability_score_increases:
                for ability, bonus in race.ability_score_increases.items():
                    current_score = getattr(character, ability.lower(), 10)
                    setattr(character, ability.lower(), current_score + bonus)
        
        # Calculate AC (10 + Dex modifier)
        character.armor_class = 10 + character.dexterity_modifier
        
        # Calculate HP (class hit die + con modifier)
        if class_data:
            char_class = Class.from_dict(class_data)
            character.hit_points_max = char_class.hit_die + character.constitution_modifier
            character.hit_points_current = character.hit_points_max
            character.max_hit_points = character.hit_points_max  # Alternative field
            character.current_hit_points = character.hit_points_max
            character.hit_dice_max = character.level
            character.hit_dice_current = character.level
    
    def roll_dice(self, notation: str, advantage: bool = False, disadvantage: bool = False) -> int:
        """Roll dice using the game's dice roller."""
        return self.dice_roller.roll(notation, advantage, disadvantage)
    
    async def get_monsters_by_cr(self, min_cr: float, max_cr: float) -> List[MonsterDTO]:
        """Get monsters within CR range as DTOs."""
        await self._ensure_connected()
        
        monsters_data = await indexeddb.get_all('monsters')
        matching_monsters = []
        
        for monster_data in monsters_data:
            monster = Monster.from_dict(monster_data)
            if min_cr <= monster.challenge_rating <= max_cr:
                matching_monsters.append(self._monster_to_dto(monster))
        
        return matching_monsters
    
    def get_monsters_by_cr_sync(self, min_cr: float, max_cr: float) -> List[MonsterDTO]:
        """Synchronous version of get_monsters_by_cr."""
        return asyncio.run(self.get_monsters_by_cr(min_cr, max_cr))
    
    def auto_save(self):
        """Perform automatic save if enough time has passed."""
        if self.current_character and self.current_save_slot:
            self.save_game_sync()
    
    def shutdown(self):
        """Clean shutdown of game engine."""
        logger.info("IndexedDB Game engine shutting down")
        if self.current_character and self.current_save_slot:
            self.save_game_sync()
        self.save_settings()