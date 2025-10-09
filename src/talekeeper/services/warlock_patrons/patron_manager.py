import sqlite3
from typing import Dict, List, Optional, Any
from .fiend_patron import FiendPatron
from .sorcerer_king_patron import SorcererKingPatron


class PatronManager:
    """Manages Warlock patron implementations."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.patrons = {
            'Fiend': FiendPatron(db_path),
            'Sorcerer-King': SorcererKingPatron(db_path),
            'Templar': SorcererKingPatron(db_path)  # Alias for Sorcerer-King
        }

    def get_available_patrons(self) -> List[str]:
        """Get list of available patron names."""
        return list(self.patrons.keys())

    def get_patron(self, patron_name: str):
        """Get patron implementation by name."""
        return self.patrons.get(patron_name)

    def initialize_patron_features(self, character_id: str, patron_name: str, level: int, cursor=None):
        """Initialize patron features for a character."""
        patron = self.get_patron(patron_name)
        if patron:
            patron.initialize_patron_features(character_id, level, cursor)

    def get_expanded_spells(self, patron_name: str) -> Dict[int, List[str]]:
        """Get expanded spells for a patron."""
        patron = self.get_patron(patron_name)
        if patron:
            return patron.get_expanded_spells()
        return {}

    def short_rest_recovery(self, character_id: str, patron_name: str):
        """Handle short rest recovery for patron features."""
        patron = self.get_patron(patron_name)
        if patron and hasattr(patron, 'short_rest_recovery'):
            patron.short_rest_recovery(character_id)

    def long_rest_recovery(self, character_id: str, patron_name: str):
        """Handle long rest recovery for patron features."""
        patron = self.get_patron(patron_name)
        if patron and hasattr(patron, 'long_rest_recovery'):
            patron.long_rest_recovery(character_id)

    def get_patron_features(self, character_id: str, patron_name: str) -> List[Dict[str, Any]]:
        """Get all patron features for a character."""
        patron = self.get_patron(patron_name)
        if patron and hasattr(patron, 'get_patron_features'):
            return patron.get_patron_features(character_id)
        return []

    def use_patron_feature(self, character_id: str, patron_name: str, feature_name: str, **kwargs) -> Dict[str, Any]:
        """Use a specific patron feature."""
        patron = self.get_patron(patron_name)
        if not patron:
            return {'success': False, 'reason': 'Patron not found'}

        # Map feature names to patron methods
        feature_methods = {
            # Fiend Patron
            'dark_ones_blessing': 'dark_ones_blessing',
            'dark_ones_own_luck': 'use_dark_ones_own_luck',
            'fiendish_resilience': 'set_fiendish_resilience',
            'hurl_through_hell': 'use_hurl_through_hell',

            # Sorcerer-King Patron
            'voice_of_tyranny': 'use_voice_of_tyranny',
            'decisive_edict': 'use_decisive_edict',
            'vindictive_rebuke': 'use_vindictive_rebuke',
            'absolute_tyranny': 'enhance_command_spell'
        }

        method_name = feature_methods.get(feature_name)
        if method_name and hasattr(patron, method_name):
            method = getattr(patron, method_name)
            try:
                return method(character_id, **kwargs)
            except Exception as e:
                return {'success': False, 'reason': str(e)}

        return {'success': False, 'reason': 'Feature method not found'}


def get_patron_manager(db_path: str = 'talekeeper.db') -> PatronManager:
    """Factory function to get a PatronManager instance."""
    return PatronManager(db_path)