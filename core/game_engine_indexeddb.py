"""
Game Engine - Central Coordinator for TaleKeeper Desktop

Manages all game systems and coordinates between UI and data layers.
Uses IndexedDB for data persistence with dataclass models.

Core Functions:
1. Character management: creation, loading, saving, progression
2. Save slot management: multiple character saves with metadata
3. Game data access: races, classes, backgrounds, monsters, equipment
4. Settings management: user preferences and configuration
5. State coordination: current character, active save slot, game state

Architecture:
- Controller layer between PyQt6 UI and IndexedDB data
- Synchronous and asynchronous operation support
- DTO pattern for data transfer to UI components
- Centralized game logic and business rules
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
        # Resolve names from IDs
        race_name = self._get_race_name_by_id(character.race_id)
        class_name = self._get_class_name_by_id(character.class_id)
        background_name = self._get_background_name_by_id(character.background_id)
        subclass_name = self._get_subclass_name_by_id(character.subclass_id) if character.subclass_id else None
        
        # Recalculate armor class to ensure it's current
        character.armor_class = self._calculate_armor_class(character)
        
        return CharacterDTO(
            # Core Identity
            id=character.id,
            name=character.name,
            level=character.level,
            experience_points=character.experience_points,
            
            # Character Build
            race_id=character.race_id,
            race_name=race_name,
            class_id=character.class_id,
            class_name=class_name,
            subclass_id=character.subclass_id,
            subclass_name=subclass_name,
            background_id=character.background_id,
            background_name=background_name,
            
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

    async def delete_character(self, save_slot: int) -> bool:
        """Delete a character and associated data from a save slot.

        Args:
            save_slot: Save slot number (1-10)

        Returns:
            bool indicating whether a character was deleted
        """
        await self._ensure_connected()

        # Locate the save slot
        slot_data_list = await indexeddb.query_index('save_slots', 'slot_number', save_slot)
        if not slot_data_list:
            return False

        slot = SaveSlot.from_dict(slot_data_list[0])

        # Find the character associated with this slot
        characters_data = await indexeddb.get_all('characters')
        character_id = None
        for char_data in characters_data:
            if char_data.get('save_slot_id') == slot.id:
                character_id = char_data.get('id')
                break

        # Delete character and game state if they exist
        if character_id:
            await indexeddb.delete('characters', character_id)

            game_states_data = await indexeddb.get_all('game_states')
            for gs_data in game_states_data:
                if gs_data.get('character_id') == character_id:
                    await indexeddb.delete('game_states', gs_data.get('id'))
                    break

        # Reset save slot
        slot.is_occupied = False
        slot.character_name = None
        slot.character_level = None
        slot.current_location = None
        slot.last_played = None
        slot.save_name = None
        slot.updated_at = datetime.now().isoformat()
        await indexeddb.put('save_slots', slot.to_dict(), slot.id)

        # Clear current references if deleting active slot
        if self.current_save_slot and self.current_save_slot.slot_number == save_slot:
            self.current_character = None
            self.current_save_slot = None
            self.game_state = None

        # Update settings if last slot was removed
        if self.settings.get('last_character_slot') == save_slot:
            self.settings['last_character_slot'] = None
            self.save_settings()

        logger.info(f"Deleted character from slot {save_slot}")
        return True

    def delete_character_sync(self, save_slot: int) -> bool:
        """Synchronous version of delete_character."""
        return asyncio.run(self.delete_character(save_slot))
    
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
    
    async def get_class_equipment_choices(self, class_id: str) -> List[Dict[str, Any]]:
        """Get equipment choices for a class."""
        await self._ensure_connected()
        
        class_data = await indexeddb.get('classes', class_id)
        if class_data and 'equipment_choices' in class_data:
            return class_data['equipment_choices']
        return []
    
    def get_class_equipment_choices_sync(self, class_id: str) -> List[Dict[str, Any]]:
        """Synchronous version of get_class_equipment_choices."""
        # Direct access to avoid async issues in UI context
        if not indexeddb.is_connected or not indexeddb.object_stores:
            return []
        
        classes_store = indexeddb.object_stores.get('classes', {})
        class_key = class_id.lower().replace(' ', '_')
        class_data = classes_store.get('data', {}).get(class_key)
        
        if class_data and 'equipment_choices' in class_data:
            return class_data['equipment_choices']
        return []
    
    async def get_equipment_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get equipment item details by name."""
        await self._ensure_connected()
        
        # Equipment is stored in 'items' object store
        items_data = await indexeddb.get_all('items')
        for item in items_data:
            if item.get('name', '').lower() == item_name.lower():
                return item
        return None
    
    def get_equipment_item_sync(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Synchronous version of get_equipment_item."""
        # Direct access to avoid async issues in UI context
        if not indexeddb.is_connected or not indexeddb.object_stores:
            return None
        
        items_store = indexeddb.object_stores.get('items', {})
        items_data = items_store.get('data', {})
        
        # Search through items by name
        for item_key, item_data in items_data.items():
            if item_data.get('name', '').lower() == item_name.lower():
                return item_data
        return None
    
    async def apply_equipment_choices(self, character_data: Dict[str, Any], 
                                     equipment_selections: Dict[str, str]) -> None:
        """Apply selected equipment choices to character data."""
        await self._ensure_connected()
        
        # This will be called during character creation
        # equipment_selections format: {"choice_name": "selected_item_name"}
        
        # For now, store the selections in character data
        # Later we can create CharacterInventory records
        if 'equipment_selections' not in character_data:
            character_data['equipment_selections'] = {}
        character_data['equipment_selections'].update(equipment_selections)
        
        # Apply selected items to equipment slots based on item type
        for choice_name, item_name in equipment_selections.items():
            item = await self.get_equipment_item(item_name)
            if item:
                item_type = item.get('item_type', '')
                if item_type == 'weapon':
                    if not character_data.get('equipment_main_hand'):
                        character_data['equipment_main_hand'] = item_name
                elif item_type == 'armor':
                    character_data['equipment_armor'] = item_name
                elif item_type == 'shield':
                    character_data['equipment_shield'] = item_name
    
    def apply_equipment_choices_sync(self, character_data: Dict[str, Any], 
                                    equipment_selections: Dict[str, str]) -> None:
        """Synchronous version of apply_equipment_choices."""
        return asyncio.run(self.apply_equipment_choices(character_data, equipment_selections))
    
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
        
        # Calculate AC with equipped armor
        character.armor_class = self._calculate_armor_class(character)
        
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
    
    def _get_race_name_by_id(self, race_id: str) -> str:
        """Get race name by ID from database."""
        try:
            # Direct access to avoid async issues
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return race_id if race_id else "Human"
                
            races_store = indexeddb.object_stores.get('races', {})
            race_key = race_id.lower().replace(' ', '_')
            race_data = races_store.get('data', {}).get(race_key)
            
            if race_data:
                return race_data.get('name', race_id)
            return race_id if race_id else "Human"  # Use the ID as fallback
        except:
            return race_id if race_id else "Human"  # Safe fallback
    
    def _get_class_name_by_id(self, class_id: str) -> str:
        """Get class name by ID from database.""" 
        try:
            # Direct access to avoid async issues
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return class_id if class_id else "Fighter"
                
            classes_store = indexeddb.object_stores.get('classes', {})
            class_key = class_id.lower().replace(' ', '_')
            class_data = classes_store.get('data', {}).get(class_key)
            
            if class_data:
                return class_data.get('name', class_id)
            return class_id if class_id else "Fighter"  # Use the ID as fallback
        except:
            return class_id if class_id else "Fighter"  # Safe fallback
    
    def _get_background_name_by_id(self, background_id: str) -> str:
        """Get background name by ID from database."""
        try:
            # Direct access to avoid async issues
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return background_id if background_id else "Folk Hero"
                
            backgrounds_store = indexeddb.object_stores.get('backgrounds', {})
            background_key = background_id.lower().replace(' ', '_').replace('-', '_')
            background_data = backgrounds_store.get('data', {}).get(background_key)
            
            if background_data:
                return background_data.get('name', background_id)
            return background_id if background_id else "Folk Hero"  # Use the ID as fallback
        except:
            return background_id if background_id else "Folk Hero"  # Safe fallback
    
    def _get_subclass_name_by_id(self, subclass_id: str) -> str:
        """Get subclass name by ID from database."""
        try:
            # Direct access to subclasses data
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return "Unknown"
                
            subclasses_store = indexeddb.object_stores.get('subclasses', {})
            subclass_data = subclasses_store.get('data', {}).get(subclass_id)
            
            if subclass_data:
                return subclass_data.get('name', 'Unknown')
            return "Unknown"
        except:
            return "Unknown"  # Safe fallback
    
    def _is_proficient_with_armor(self, character, armor_type: str) -> bool:
        """Check if character is proficient with a specific armor type."""
        try:
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return True  # Default to allowing armor
            
            classes_store = indexeddb.object_stores.get('classes', {})
            class_key = character.class_id.lower().replace(' ', '_')
            class_data = classes_store.get('data', {}).get(class_key)
            
            if class_data:
                armor_proficiencies = class_data.get('armor_proficiencies', [])
                # Handle shield special case
                if armor_type == 'shield':
                    return 'shields' in armor_proficiencies
                else:
                    return armor_type in armor_proficiencies
            
            return True  # Default to allowing armor if class not found
        except:
            return True  # Safe fallback
    
    def _has_feat(self, character, feat_name: str) -> bool:
        """Check if character has a specific feat."""
        return feat_name in getattr(character, 'feats', [])
    
    def _get_feat_data(self, feat_name: str) -> Dict[str, Any]:
        """Get feat data by name."""
        try:
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return {}
            
            feats_store = indexeddb.object_stores.get('feats', {})
            feat_data = None
            
            # Find feat by name
            for feat_key, feat_info in feats_store.get('data', {}).items():
                if feat_info.get('name', '').lower() == feat_name.lower():
                    feat_data = feat_info
                    break
            
            return feat_data or {}
        except:
            return {}
    
    def can_equip_item(self, character, item_name: str) -> tuple[bool, str]:
        """Check if character can equip a specific item. Returns (can_equip, reason)."""
        try:
            if not indexeddb.is_connected or not indexeddb.object_stores:
                return True, ""
            
            items_store = indexeddb.object_stores.get('items', {})
            item_data = None
            
            # Find item by name
            for item_key, item_info in items_store.get('data', {}).items():
                if item_info.get('name', '').lower() == item_name.lower():
                    item_data = item_info
                    break
            
            if not item_data:
                return False, f"Item '{item_name}' not found"
            
            item_type = item_data.get('item_type', '')
            
            if item_type == 'armor':
                # Handle both old flat structure and new nested structure
                armor_props = item_data.get('armor_properties', {})
                if armor_props:
                    armor_type = armor_props.get('armor_type', 'light')
                else:
                    armor_type = item_data.get('armor_type', 'light')
                
                if not self._is_proficient_with_armor(character, armor_type):
                    return False, f"Not proficient with {armor_type} armor"
                
                # Check Strength requirement
                strength_req = armor_props.get('strength_requirement') if armor_props else item_data.get('strength_requirement')
                if strength_req and character.strength < strength_req:
                    return False, f"Requires Strength {strength_req} (you have {character.strength})"
            elif item_type == 'shield':
                if not self._is_proficient_with_armor(character, 'shield'):
                    return False, "Not proficient with shields"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking equipment proficiency: {e}")
            return False, "Error checking proficiency"
    
    def _calculate_armor_class(self, character) -> int:
        """Calculate armor class based on equipped armor and dexterity."""
        base_ac = 10  # Unarmored AC
        dex_modifier = character.dexterity_modifier
        shield_bonus = 0
        
        try:
            # Check for equipped armor
            if character.equipment_armor:
                if not indexeddb.is_connected or not indexeddb.object_stores:
                    return base_ac + dex_modifier
                
                equipment_store = indexeddb.object_stores.get('items', {})
                armor_data = None
                
                # Try to find armor by name (case-insensitive)
                for item_key, item_data in equipment_store.get('data', {}).items():
                    if item_data.get('name', '').lower() == character.equipment_armor.lower():
                        armor_data = item_data
                        break
                
                if armor_data and armor_data.get('item_type') == 'armor':
                    # Handle both old flat structure and new nested structure
                    armor_props = armor_data.get('armor_properties', {})
                    if armor_props:
                        # New nested structure
                        armor_ac = armor_props.get('armor_class', 10)
                        armor_type = armor_props.get('armor_type', 'light')
                        dex_max = armor_props.get('dex_bonus_max')
                    else:
                        # Old flat structure (backward compatibility)
                        armor_ac = armor_data.get('armor_class', 10)
                        armor_type = armor_data.get('armor_type', 'light')
                        dex_max = armor_data.get('dex_bonus_max')
                    
                    # Check if character is proficient with this armor type
                    is_proficient = self._is_proficient_with_armor(character, armor_type)
                    
                    if armor_type == 'light':
                        # Light armor: full dex bonus
                        base_ac = armor_ac + dex_modifier
                    elif armor_type == 'medium':
                        # Medium armor: dex bonus max +2 (or +3 with Medium Armor Master feat)
                        base_dex_max = dex_max if dex_max is not None else 2
                        
                        # Check for Medium Armor Master feat
                        if self._has_feat(character, "Medium Armor Master"):
                            feat_data = self._get_feat_data("Medium Armor Master")
                            feat_mechanics = feat_data.get('mechanics', {}).get('armor_bonuses', {})
                            dex_requirement = feat_mechanics.get('medium_armor_dex_requirement', 16)
                            feat_dex_max = feat_mechanics.get('medium_armor_dex_max', 2)
                            
                            if character.dexterity >= dex_requirement:
                                base_dex_max = feat_dex_max
                        
                        dex_bonus = min(dex_modifier, base_dex_max)
                        base_ac = armor_ac + dex_bonus
                    elif armor_type == 'heavy':
                        # Heavy armor: no dex bonus
                        base_ac = armor_ac
                    
                    # Prevent equipping non-proficient armor
                    if not is_proficient:
                        logger.warning(f"Character {character.name} cannot equip {armor_type} armor - not proficient")
                        # Remove the armor from equipment
                        character.equipment_armor = None
                        # Use unarmored AC
                        base_ac = 10 + dex_modifier
                else:
                    # No armor or armor not found, use base AC + dex
                    base_ac = 10 + dex_modifier
            else:
                # No armor equipped
                base_ac = 10 + dex_modifier
            
            # Check for equipped shield
            if character.equipment_shield:
                equipment_store = indexeddb.object_stores.get('items', {})
                shield_data = None
                
                # Try to find shield by name (case-insensitive)
                for item_key, item_data in equipment_store.get('data', {}).items():
                    if item_data.get('name', '').lower() == character.equipment_shield.lower():
                        shield_data = item_data
                        break
                
                if shield_data and shield_data.get('item_type') == 'shield':
                    shield_bonus = shield_data.get('armor_class', 0)
                    
                    # Check shield proficiency
                    is_shield_proficient = self._is_proficient_with_armor(character, 'shield')
                    if not is_shield_proficient:
                        logger.warning(f"Character {character.name} cannot equip shield - not proficient")
                        # Remove the shield from equipment
                        character.equipment_shield = None
                        shield_bonus = 0
            
            return base_ac + shield_bonus
            
        except Exception as e:
            logger.warning(f"Error calculating armor class: {e}")
            # Fallback to base calculation
            return 10 + dex_modifier
    
    def shutdown(self):
        """Clean shutdown of game engine."""
        logger.info("IndexedDB Game engine shutting down")
        if self.current_character and self.current_save_slot:
            self.save_game_sync()
        self.save_settings()