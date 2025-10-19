# core
# core
"""
Warlock Patron implementations for TaleKeeper.

This module contains the various patron implementations for the Warlock class,
including their specific features, abilities, and spell expansions.
"""

from .patron_manager import PatronManager, get_patron_manager
from .fiend_patron import FiendPatron
from .sorcerer_king_patron import SorcererKingPatron

__all__ = [
    'PatronManager',
    'get_patron_manager',
    'FiendPatron',
    'SorcererKingPatron'
]