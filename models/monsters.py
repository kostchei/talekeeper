"""
File: models/monsters.py
Path: /models/monsters.py

Monster models for D&D Desktop game.
Ported from web version with SQLite compatibility.

Pseudo Code:
1. Define Monster model with complete D&D stat block (HP, AC, stats, saves)
2. Store AI behavior scripts for different monster types
3. Handle special abilities, attacks, and spellcasting
4. Manage encounter difficulty and challenge rating
5. Process monster actions during combat turns

AI Agents: Combat encounters with full stat blocks and AI behavior patterns.
"""

from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from uuid import uuid4
from datetime import datetime
from enum import Enum
from core.database import Base


class MonsterType(str, Enum):
    """D&D monster types."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"


class MonsterSize(str, Enum):
    """D&D monster sizes."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"


class Monster(Base):
    """
    D&D Monster with complete stat block.
    AI Agents: Extend with new monster abilities and AI behaviors.
    """
    __tablename__ = "monsters"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    challenge_rating = Column(Numeric(3, 2), nullable=True)
    size = Column(String(20), nullable=True)
    type = Column(String(50), nullable=True)
    alignment = Column(String(50), nullable=True)
    armor_class = Column(Integer, nullable=True)
    hit_points = Column(Integer, nullable=True)
    hit_dice = Column(String(20), nullable=True)
    speed = Column(JSON, nullable=True)
    strength = Column(Integer, nullable=True)
    dexterity = Column(Integer, nullable=True)
    constitution = Column(Integer, nullable=True)
    intelligence = Column(Integer, nullable=True)
    wisdom = Column(Integer, nullable=True)
    charisma = Column(Integer, nullable=True)
    saving_throws = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    damage_vulnerabilities = Column(JSON, nullable=True)
    damage_resistances = Column(JSON, nullable=True)
    damage_immunities = Column(JSON, nullable=True)
    condition_immunities = Column(JSON, nullable=True)
    senses = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    actions = Column(JSON, nullable=True)
    reactions = Column(JSON, nullable=True)
    legendary_actions = Column(JSON, nullable=True)
    special_abilities = Column(JSON, nullable=True)
    ai_script = Column(String(50), nullable=True)
    loot_table = Column(JSON, nullable=True)
    xp_value = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @property
    def strength_modifier(self) -> int:
        return (self.strength - 10) // 2 if self.strength else 0
    
    @property
    def dexterity_modifier(self) -> int:
        return (self.dexterity - 10) // 2 if self.dexterity else 0
    
    @property
    def constitution_modifier(self) -> int:
        return (self.constitution - 10) // 2 if self.constitution else 0
    
    @property
    def intelligence_modifier(self) -> int:
        return (self.intelligence - 10) // 2 if self.intelligence else 0
    
    @property
    def wisdom_modifier(self) -> int:
        return (self.wisdom - 10) // 2 if self.wisdom else 0
    
    @property
    def charisma_modifier(self) -> int:
        return (self.charisma - 10) // 2 if self.charisma else 0
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on CR."""
        if not self.challenge_rating:
            return 2
        cr = float(self.challenge_rating)
        if cr <= 4:
            return 2
        elif cr <= 8:
            return 3
        elif cr <= 12:
            return 4
        elif cr <= 16:
            return 5
        else:
            return 6
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert monster to dictionary for display."""
        return {
            "id": self.id,
            "name": self.name,
            "challenge_rating": float(self.challenge_rating) if self.challenge_rating else 0,
            "size": self.size,
            "type": self.type,
            "alignment": self.alignment,
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "hit_dice": self.hit_dice,
            "speed": self.speed or {},
            "ability_scores": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "modifiers": {
                "strength": self.strength_modifier,
                "dexterity": self.dexterity_modifier,
                "constitution": self.constitution_modifier,
                "intelligence": self.intelligence_modifier,
                "wisdom": self.wisdom_modifier,
                "charisma": self.charisma_modifier
            },
            "saving_throws": self.saving_throws or {},
            "skills": self.skills or {},
            "damage_vulnerabilities": self.damage_vulnerabilities or [],
            "damage_resistances": self.damage_resistances or [],
            "damage_immunities": self.damage_immunities or [],
            "condition_immunities": self.condition_immunities or [],
            "senses": self.senses or {},
            "languages": self.languages or [],
            "actions": self.actions or [],
            "reactions": self.reactions or [],
            "legendary_actions": self.legendary_actions or [],
            "special_abilities": self.special_abilities or [],
            "ai_script": self.ai_script,
            "loot_table": self.loot_table or {},
            "xp_value": self.xp_value,
            "proficiency_bonus": self.proficiency_bonus
        }