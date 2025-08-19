"""
File: backend/models/__init__.py
Path: /backend/models/__init__.py

Models package for D&D game.
AI Agents: Import all models here for proper database initialization.

Pseudo Code:
1. Import all SQLAlchemy models to register with Base.metadata
2. Ensure proper database table creation order with relationships
3. Export models for use in services and routers
4. Handle any model-level initialization or configuration
"""

from .character import Character
from .items import Item, CharacterInventory, ShopInventory, LootTable
from .monsters import Monster
from .combat import CombatEncounter, CombatAction, CombatLog, CombatState
from .game import GameState, SaveSlot, GameSave, DungeonRoom, GameEvent
from .races import Race
from .classes import Class, Subclass
from .backgrounds import Background

__all__ = [
    'Character',
    'Item', 'CharacterInventory', 'ShopInventory', 'LootTable',
    'Monster',
    'CombatEncounter', 'CombatAction', 'CombatLog', 'CombatState',
    'GameState', 'SaveSlot', 'GameSave', 'DungeonRoom', 'GameEvent',
    'Race',
    'Class', 'Subclass',
    'Background'
]