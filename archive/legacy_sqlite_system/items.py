"""
File: models/items.py
Path: /models/items.py

Item and equipment models for D&D Desktop game.
Handles weapons, armor, and general equipment.

Pseudo Code:
1. Define Item model with D&D properties (damage, AC, etc.)
2. Handle equipment slots and character inventory
3. Manage item properties and magical effects
4. Track weapon and armor statistics
5. Support equipment purchasing and selling

AI Agents: Equipment system and inventory management.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum
from core.database import Base


class ItemType(str, Enum):
    """D&D item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    TOOL = "tool"
    CONSUMABLE = "consumable"
    TREASURE = "treasure"
    WONDROUS = "wondrous"


class Item(Base):
    """D&D Equipment and items."""
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Item properties
    item_type = Column(String(50), nullable=False)
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    cost_gp = Column(Integer, default=0)
    weight_lb = Column(Numeric(5, 2), default=0.0)
    
    # Equipment properties
    armor_class = Column(Integer, nullable=True)  # For armor/shields
    damage_dice = Column(String(20), nullable=True)  # For weapons (e.g., "1d8")
    damage_type = Column(String(20), nullable=True)  # slashing, piercing, etc.
    weapon_properties = Column(JSON, default=lambda: [])  # finesse, versatile, etc.
    
    # Magical properties
    is_magical = Column(Boolean, default=False)
    magical_properties = Column(JSON, default=lambda: {})
    attunement_required = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Equipment(Base):
    """Starting equipment packages for classes."""
    __tablename__ = "equipment_packages"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)  # "Fighter Starting Equipment"
    class_id = Column(String, ForeignKey("classes.id"), nullable=True)
    background_id = Column(String, ForeignKey("backgrounds.id"), nullable=True)
    
    # Equipment contents
    items = Column(JSON, default=lambda: [])  # List of {item_id, quantity}
    gold_pieces = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CharacterInventory(Base):
    """Character's inventory items."""
    __tablename__ = "character_inventory"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    item_id = Column(String, ForeignKey("items.id"), nullable=False)
    
    # Inventory details
    quantity = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)
    equipment_slot = Column(String(50), nullable=True)  # main_hand, off_hand, armor, etc.
    
    # Magical item state
    attuned = Column(Boolean, default=False)
    charges_remaining = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    character = relationship("Character")  # Removed back_populates since Character.inventory is commented out
    item = relationship("Item")