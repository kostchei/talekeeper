# core
# category: utility
"""
Subclass Definitions Package

This package contains all subclass definitions for TaleKeeper.
Each class has its own module containing its subclass definitions.

Structure:
- barbarian/
  - berserker.py
  - totem_warrior.py
  - ancestral_guardian.py
  - wild_heart.py
- fighter/
  - champion.py
  - battle_master.py
  - eldritch_knight.py
  - psi_warrior.py
- rogue/
  - thief.py
  - assassin.py
  - arcane_trickster.py
  - swashbuckler.py
etc...

Each subclass module exports a create() function that returns a SubclassDefinition.
"""

from talekeeper.services.enhanced_subclass_manager import SubclassDefinition

# Import all subclass modules when available
__all__ = ['SubclassDefinition']