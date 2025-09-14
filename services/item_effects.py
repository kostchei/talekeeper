import sqlite3
import json
from typing import Dict, Any, List, Optional

class ItemEffectsService:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure magical bonuses table exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create character_magical_bonuses table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS character_magical_bonuses (
                        character_id TEXT PRIMARY KEY,
                        ac_bonus INTEGER DEFAULT 0,
                        save_bonus INTEGER DEFAULT 0,
                        attack_bonus INTEGER DEFAULT 0,
                        damage_bonus INTEGER DEFAULT 0,
                        str_bonus INTEGER DEFAULT 0,
                        dex_bonus INTEGER DEFAULT 0,
                        con_bonus INTEGER DEFAULT 0,
                        int_bonus INTEGER DEFAULT 0,
                        wis_bonus INTEGER DEFAULT 0,
                        cha_bonus INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                    )
                """)

                # Create character_attunements table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS character_attunements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        character_id TEXT NOT NULL,
                        item_key TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                        UNIQUE(character_id, item_key)
                    )
                """)

                print("[ITEM_EFFECTS] Tables ensured")

        except Exception as e:
            print(f"Error ensuring item effects tables: {e}")

    def calculate_bonuses_for_character(self, character_id: str, equipped_items: Dict) -> Dict[str, int]:
        """Calculate magical bonuses from all equipped items for a character."""
        bonuses = {
            'ac_bonus': 0,
            'save_bonus': 0,
            'attack_bonus': 0,
            'damage_bonus': 0,
            'str_bonus': 0,
            'dex_bonus': 0,
            'con_bonus': 0,
            'int_bonus': 0,
            'wis_bonus': 0,
            'cha_bonus': 0
        }

        try:
            # Get attunement status
            attuned_items = self._get_attuned_items(character_id)

            # Process each equipped item
            for slot, item in equipped_items.items():
                if not item:
                    continue

                item_key = self._get_item_key(item)
                is_attuned = item_key in attuned_items

                # Apply item effects based on item properties
                item_bonuses = self._get_item_bonuses(item, is_attuned)

                for bonus_type, bonus_value in item_bonuses.items():
                    if bonus_type in bonuses:
                        bonuses[bonus_type] += bonus_value

            # Save calculated bonuses to database
            self._save_bonuses_to_database(character_id, bonuses)

            return bonuses

        except Exception as e:
            print(f"Error calculating bonuses for character {character_id}: {e}")
            return bonuses

    def _get_attuned_items(self, character_id: str) -> set:
        """Get set of attuned item keys for character."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_key FROM character_attunements
                    WHERE character_id = ?
                """, (character_id,))

                return {row[0] for row in cursor.fetchall()}

        except Exception as e:
            print(f"Error getting attuned items: {e}")
            return set()

    def _get_item_key(self, item: Dict) -> str:
        """Generate unique key for item for attunement tracking."""
        item_id = item.get('id', '')
        item_name = item.get('name', item.get('item_name', ''))
        return f"{item_id}:{item_name}" if item_id else item_name

    def _get_item_bonuses(self, item: Dict, is_attuned: bool = False) -> Dict[str, int]:
        """Extract magical bonuses from an item."""
        bonuses = {
            'ac_bonus': 0,
            'save_bonus': 0,
            'attack_bonus': 0,
            'damage_bonus': 0,
            'str_bonus': 0,
            'dex_bonus': 0,
            'con_bonus': 0,
            'int_bonus': 0,
            'wis_bonus': 0,
            'cha_bonus': 0
        }

        try:
            item_name = item.get('name', item.get('item_name', ''))
            description = item.get('description', '')
            item_type = item.get('item_type', item.get('type', ''))

            # Basic magical item patterns
            magical_keywords = ['+1', '+2', '+3', 'magical', 'enchanted', 'blessed', 'cursed']
            is_magical = any(keyword.lower() in item_name.lower() or keyword.lower() in description.lower()
                           for keyword in magical_keywords)

            if is_magical:
                # Extract numerical bonuses from name/description
                import re

                # Look for +X patterns
                plus_match = re.search(r'\+(\d+)', item_name)
                if plus_match:
                    bonus_value = int(plus_match.group(1))

                    # Apply bonus based on item type
                    if item_type in ['weapon', 'sword', 'axe', 'bow', 'crossbow', 'dagger']:
                        bonuses['attack_bonus'] = bonus_value
                        bonuses['damage_bonus'] = bonus_value
                    elif item_type in ['armor', 'shield']:
                        bonuses['ac_bonus'] = bonus_value
                    elif item_type in ['amulet', 'ring', 'cloak']:
                        # Magical accessories typically provide various bonuses
                        if 'protection' in item_name.lower() or 'defense' in item_name.lower():
                            bonuses['ac_bonus'] = bonus_value
                        elif 'strength' in item_name.lower():
                            bonuses['str_bonus'] = bonus_value
                        elif 'dexterity' in item_name.lower():
                            bonuses['dex_bonus'] = bonus_value
                        elif 'constitution' in item_name.lower():
                            bonuses['con_bonus'] = bonus_value
                        elif 'intelligence' in item_name.lower():
                            bonuses['int_bonus'] = bonus_value
                        elif 'wisdom' in item_name.lower():
                            bonuses['wis_bonus'] = bonus_value
                        elif 'charisma' in item_name.lower():
                            bonuses['cha_bonus'] = bonus_value

                # Special item effects (requires attunement)
                if is_attuned:
                    # Enhanced bonuses for attuned items
                    if 'ring of protection' in item_name.lower():
                        bonuses['ac_bonus'] += 1
                        bonuses['save_bonus'] += 1
                    elif 'cloak of protection' in item_name.lower():
                        bonuses['ac_bonus'] += 1
                        bonuses['save_bonus'] += 1
                    elif 'amulet of health' in item_name.lower():
                        bonuses['con_bonus'] += 2
                    elif 'gauntlets of ogre power' in item_name.lower():
                        bonuses['str_bonus'] += 2
                    elif 'boots of elvenkind' in item_name.lower():
                        bonuses['dex_bonus'] += 1

            return bonuses

        except Exception as e:
            print(f"Error extracting bonuses from item {item}: {e}")
            return bonuses

    def _save_bonuses_to_database(self, character_id: str, bonuses: Dict[str, int]):
        """Save calculated bonuses to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO character_magical_bonuses (
                        character_id, ac_bonus, save_bonus, attack_bonus, damage_bonus,
                        str_bonus, dex_bonus, con_bonus, int_bonus, wis_bonus, cha_bonus
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    character_id,
                    bonuses['ac_bonus'],
                    bonuses['save_bonus'],
                    bonuses['attack_bonus'],
                    bonuses['damage_bonus'],
                    bonuses['str_bonus'],
                    bonuses['dex_bonus'],
                    bonuses['con_bonus'],
                    bonuses['int_bonus'],
                    bonuses['wis_bonus'],
                    bonuses['cha_bonus']
                ))

                print(f"[ITEM_EFFECTS] Saved bonuses for {character_id}: {bonuses}")

        except Exception as e:
            print(f"Error saving bonuses to database: {e}")

    def set_attunement(self, character_id: str, item_key: str, attune: bool):
        """Set or remove attunement for an item."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if attune:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_attunements (character_id, item_key)
                        VALUES (?, ?)
                    """, (character_id, item_key))
                else:
                    cursor.execute("""
                        DELETE FROM character_attunements
                        WHERE character_id = ? AND item_key = ?
                    """, (character_id, item_key))

                print(f"[ITEM_EFFECTS] {'Set' if attune else 'Removed'} attunement: {character_id} -> {item_key}")

        except Exception as e:
            print(f"Error setting attunement: {e}")

    def get_character_bonuses(self, character_id: str) -> Dict[str, int]:
        """Get saved bonuses for a character from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ac_bonus, save_bonus, attack_bonus, damage_bonus,
                           str_bonus, dex_bonus, con_bonus, int_bonus, wis_bonus, cha_bonus
                    FROM character_magical_bonuses
                    WHERE character_id = ?
                """, (character_id,))

                row = cursor.fetchone()
                if row:
                    return {
                        'ac_bonus': row[0] or 0,
                        'save_bonus': row[1] or 0,
                        'attack_bonus': row[2] or 0,
                        'damage_bonus': row[3] or 0,
                        'str_bonus': row[4] or 0,
                        'dex_bonus': row[5] or 0,
                        'con_bonus': row[6] or 0,
                        'int_bonus': row[7] or 0,
                        'wis_bonus': row[8] or 0,
                        'cha_bonus': row[9] or 0
                    }
                else:
                    return {
                        'ac_bonus': 0, 'save_bonus': 0, 'attack_bonus': 0, 'damage_bonus': 0,
                        'str_bonus': 0, 'dex_bonus': 0, 'con_bonus': 0, 'int_bonus': 0,
                        'wis_bonus': 0, 'cha_bonus': 0
                    }

        except Exception as e:
            print(f"Error getting character bonuses: {e}")
            return {}