"""
File: models/items_indexeddb.py
Path: /models/items_indexeddb.py

IndexedDB-compatible item and equipment models for TaleKeeper Desktop.
Handles weapons, armor, and general equipment without SQLAlchemy.

Pseudo Code:
1. Define Item dataclass with D&D properties (damage, AC, etc.)
2. Handle equipment slots and character inventory
3. Manage item properties and magical effects
4. Track weapon and armor statistics
5. Support equipment purchasing and selling

AI Agents: Equipment system and inventory management.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum


class ItemType(str, Enum):
    """D&D item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    TOOL = "tool"
    CONSUMABLE = "consumable"
    TREASURE = "treasure"
    WONDROUS = "wondrous"


@dataclass
class Item:
    """D&D Equipment and items for IndexedDB storage."""
    # Primary key (use name as ID)
    name: str = ""
    description: str = ""
    
    # Item properties
    item_type: str = "weapon"
    rarity: str = "common"  # common, uncommon, rare, etc.
    cost_gp: int = 0
    weight_lb: float = 0.0
    
    # Equipment properties
    armor_class: Optional[int] = None  # For armor/shields
    damage_dice: Optional[str] = None  # For weapons (e.g., "1d8")
    damage_type: Optional[str] = None  # slashing, piercing, etc.
    weapon_properties: List[str] = field(default_factory=list)  # finesse, versatile, etc.
    
    # Magical properties
    is_magical: bool = False
    magical_properties: Dict[str, Any] = field(default_factory=dict)
    attunement_required: bool = False
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create item from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'weapon_properties': [],
            'magical_properties': {},
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)


@dataclass
class Equipment:
    """Starting equipment packages for classes for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""  # "Fighter Starting Equipment"
    class_id: Optional[str] = None
    background_id: Optional[str] = None
    
    # Equipment contents
    items: List[Dict[str, Any]] = field(default_factory=list)  # List of {item_id, quantity}
    gold_pieces: int = 0
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment package to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """Create equipment package from dictionary from IndexedDB."""
        # Handle missing fields gracefully
        defaults = {
            'items': [],
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)


@dataclass
class EquipmentChoice:
    """Equipment choice options for classes/backgrounds for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""  # "Martial Weapon", "Armor Choice"
    class_id: Optional[str] = None
    background_id: Optional[str] = None
    choice_type: str = ""  # "weapon", "armor", "pack", "tool"
    
    # Choice options - list of item names
    options: List[str] = field(default_factory=list)
    max_selections: int = 1  # Usually 1, but could allow multiple
    is_required: bool = True
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment choice to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EquipmentChoice':
        """Create equipment choice from dictionary from IndexedDB."""
        defaults = {
            'options': [],
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)


@dataclass
class CharacterInventory:
    """Character's inventory items for IndexedDB storage."""
    # Primary key
    id: str = field(default_factory=lambda: str(uuid4()))
    character_id: str = ""
    item_id: str = ""
    
    # Inventory details
    quantity: int = 1
    equipped: bool = False
    equipment_slot: Optional[str] = None  # main_hand, off_hand, armor, etc.
    
    # Magical item state
    attuned: bool = False
    charges_remaining: Optional[int] = None
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character inventory to dictionary for IndexedDB storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterInventory':
        """Create character inventory from dictionary from IndexedDB."""
        defaults = {
            'created_at': datetime.now().isoformat()
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return cls(**data)