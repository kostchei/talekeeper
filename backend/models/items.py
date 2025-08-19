"""
File: backend/models/items.py
Path: /backend/models/items.py

Item and inventory models for D&D game.
AI Agents: Comprehensive item system with equipment, consumables, and inventory tracking.

Pseudo Code:
1. Define Item model with stats, rarity, type, and magical properties
2. Handle equipment slots and character inventory relationships
3. Manage shop inventory with pricing and availability
4. Create loot tables for random treasure generation
5. Process item effects (stat bonuses, damage, healing)
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum

from database import Base

class ItemType(str, Enum):
    """Categories of items."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    GEAR = "gear"
    CONSUMABLE = "consumable"
    TOOL = "tool"
    TREASURE = "treasure"
    QUEST_ITEM = "quest_item"

class ItemRarity(str, Enum):
    """Item rarity following D&D 5e standards."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class EquipmentSlot(str, Enum):
    """Equipment slots for characters."""
    HEAD = "head"
    NECK = "neck"
    CHEST = "chest"
    BACK = "back"
    ARMS = "arms"
    HANDS = "hands"
    WAIST = "waist"
    LEGS = "legs"
    FEET = "feet"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    TRINKET_1 = "trinket_1"
    TRINKET_2 = "trinket_2"

class Item(Base):
    """
    Base item model covering all item types.
    AI Agents: Extend with magical effects and crafting components.
    """
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="")
    
    # Item categorization
    type = Column(String(50), nullable=False)  # weapon, armor, gear, etc.
    subtype = Column(String(50), nullable=True)  # e.g., "longsword", "plate armor"
    rarity = Column(String(20), nullable=False, default="common")
    
    # Economic properties
    cost_gp = Column(Numeric(10, 2), nullable=True, default=0)
    weight = Column(Numeric(5, 2), nullable=True, default=0)
    
    # Equipment properties
    equipment_slot = Column(String(20), nullable=True)  # Primary slot when equipped
    armor_class = Column(Integer, nullable=True)  # For armor/shields
    max_dex_bonus = Column(Integer, nullable=True)  # For armor
    strength_requirement = Column(Integer, nullable=True)  # For heavy armor
    stealth_disadvantage = Column(Boolean, default=False)
    
    # Weapon properties
    damage_dice = Column(String(20), nullable=True)  # e.g., "1d8", "2d6"
    damage_type = Column(String(20), nullable=True)  # slashing, piercing, bludgeoning, etc.
    range_normal = Column(Integer, nullable=True)  # Normal range in feet
    range_long = Column(Integer, nullable=True)  # Long range in feet
    
    # Magic properties
    is_magical = Column(Boolean, default=False)
    attunement_required = Column(Boolean, default=False)
    charges_max = Column(Integer, nullable=True)  # For items with limited uses
    
    # Flexible properties for special items
    properties = Column(JSON, default=dict)  # Weapon properties, special abilities
    requirements = Column(JSON, default=dict)  # Class, race, level requirements
    effects = Column(JSON, default=dict)  # Stat bonuses, special effects
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory_items = relationship("CharacterInventory", back_populates="item")
    shop_items = relationship("ShopInventory", back_populates="item")

class CharacterInventory(Base):
    """
    Junction table tracking items owned by characters.
    AI Agents: Extend with item conditions, enhancement levels, and custom names.
    """
    __tablename__ = "character_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False, default=1)
    equipped = Column(Boolean, default=False)
    equipped_slot = Column(String(20), nullable=True)  # Actual slot when equipped
    
    # Item state
    identified = Column(Boolean, default=True)  # False for unidentified magic items
    attuned = Column(Boolean, default=False)  # For magic items requiring attunement
    charges_current = Column(Integer, nullable=True)  # Current charges if applicable
    condition = Column(String(20), default="normal")  # normal, damaged, broken
    
    # Metadata
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, default="")  # Custom notes about this specific item
    
    # Relationships
    character = relationship("Character", back_populates="inventory")
    item = relationship("Item", back_populates="inventory_items")

class ShopInventory(Base):
    """
    Shop inventory tracking for different vendors.
    AI Agents: Implement dynamic pricing and stock management.
    """
    __tablename__ = "shop_inventory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    shop_type = Column(String(50), nullable=False)  # general_store, weapon_smith, etc.
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    
    stock_quantity = Column(Integer, nullable=False, default=1)
    price_modifier = Column(Numeric(3, 2), default=1.0)  # Multiply base cost
    in_stock = Column(Boolean, default=True)
    restock_time = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    item = relationship("Item", back_populates="shop_items")

class LootTable(Base):
    """
    Loot generation tables for monsters and treasure.
    AI Agents: Create themed loot tables for different environments and enemy types.
    """
    __tablename__ = "loot_tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    
    # Loot table properties
    monster_cr_min = Column(Integer, nullable=True)  # Minimum CR for this table
    monster_cr_max = Column(Integer, nullable=True)  # Maximum CR for this table
    environment = Column(String(50), nullable=True)  # dungeon, forest, urban, etc.
    
    # Loot composition (JSON arrays of item weights and quantities)
    currency_tables = Column(JSON, default=list)  # Gold, silver, copper generation
    item_tables = Column(JSON, default=list)  # Item generation by rarity
    special_items = Column(JSON, default=list)  # Unique items for this table

# Pydantic Models for API
class ItemResponse(BaseModel):
    """Item data for API responses."""
    id: str
    name: str
    type: ItemType
    subtype: Optional[str]
    rarity: ItemRarity
    cost_gp: float
    weight: float
    description: str
    
    # Equipment properties
    armor_class: Optional[int]
    damage_dice: Optional[str]
    damage_type: Optional[str]
    range_normal: Optional[int]
    range_long: Optional[int]
    
    # Magic properties
    is_magical: bool
    attunement_required: bool
    
    # Flexible properties
    properties: Dict[str, Any]
    requirements: Dict[str, Any]
    effects: Dict[str, Any]
    
    class Config:
        from_attributes = True

class InventoryItemResponse(BaseModel):
    """Character inventory item for API responses."""
    inventory_id: str
    item_id: str
    name: str
    type: ItemType
    subtype: Optional[str]
    rarity: ItemRarity
    quantity: int
    equipped: bool
    equipped_slot: Optional[str]
    identified: bool
    attuned: bool
    condition: str
    weight_total: float
    value_total: float
    notes: str
    acquired_at: datetime
    
    class Config:
        from_attributes = True

class InventoryResponse(BaseModel):
    """Complete character inventory for API responses."""
    character_id: str
    equipped_items: Dict[str, InventoryItemResponse]
    unequipped_items: List[InventoryItemResponse]
    total_items: int
    total_weight: float
    total_value: float
    carrying_capacity: float
    encumbrance_status: str
    current_gold: int
    equipment_slots_used: int
    equipment_slots_available: List[str]
    
    class Config:
        from_attributes = True

class EquipItemRequest(BaseModel):
    """Request to equip/unequip an item."""
    character_id: str
    item_id: str
    equip: bool = True  # True to equip, False to unequip
    slot: Optional[str] = None  # Specific slot to equip to

class PurchaseItemRequest(BaseModel):
    """Request to purchase an item from a shop."""
    character_id: str
    item_id: str
    quantity: int = Field(default=1, gt=0)
    shop_type: Optional[str] = None

class SellItemRequest(BaseModel):
    """Request to sell an item to a shop."""
    character_id: str
    item_id: str
    quantity: int = Field(default=1, gt=0)

class LootGenerationRequest(BaseModel):
    """Request to generate loot."""
    character_level: int = Field(default=1, ge=1, le=20)
    monster_id: Optional[str] = None
    loot_table_id: Optional[str] = None
    treasure_type: str = Field(default="standard", description="standard, hoard, quest")