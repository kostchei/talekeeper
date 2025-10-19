# core
# core
import sqlite3
import random
from typing import Optional, List, Set, Tuple

class LootDropService:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def drop_loot(self, character_id: str, character_data: dict, rarity: str) -> Optional[dict]:
        class_build = self.get_character_build(character_data)
        owned_items = self.get_player_inventory(character_id)

        bis_items = self.get_bis_items_for_rarity(class_build, rarity)

        for slot_number, item_name in bis_items:
            if item_name not in owned_items:
                item = self._get_equipment_by_name(item_name)
                if item:
                    return item

        other_items = self.get_other_items_for_rarity(rarity, owned_items)
        if other_items:
            item_name = random.choice(other_items)
            item = self._get_equipment_by_name(item_name)
            if item:
                return item

        return None

    def get_character_build(self, character_data: dict) -> str:
        class_name = character_data.get('class_name', '').lower()

        if class_name == 'fighter':
            dex = character_data.get('dexterity', 10)
            strength = character_data.get('strength', 10)

            if dex > strength:
                return 'Fighter Dex higher than Str'
            return 'Fighter'

        elif class_name == 'barbarian':
            dex = character_data.get('dexterity', 10)
            strength = character_data.get('strength', 10)
            constitution = character_data.get('constitution', 10)

            if dex + constitution < 32:
                return 'Barbarian Dex + Con under 32'
            elif dex > strength:
                return 'Barbarian Dex higher than Str'
            return 'Barbarian'

        elif class_name == 'rogue':
            return 'Rogue'
        elif class_name == 'paladin':
            return 'Paladin'
        elif class_name == 'cleric':
            return 'Cleric'
        elif class_name == 'wizard':
            return 'Wizard'
        elif class_name == 'warlock':
            return 'Warlock'

        return 'Other'

    def get_player_inventory(self, character_id: str) -> Set[str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT item_name
                FROM character_inventory
                WHERE character_id = ?
            """, (character_id,))

            items = set(row[0] for row in cursor.fetchall())

            cursor.execute("""
                SELECT equipment_main_hand, equipment_off_hand, equipment_armor,
                       equipment_shield, equipment_helmet, equipment_gloves,
                       equipment_boots, equipment_cloak, equipment_ring_1,
                       equipment_ring_2, equipment_amulet, equipment_belt
                FROM characters
                WHERE id = ?
            """, (character_id,))

            row = cursor.fetchone()
            if row:
                for equipped_item in row:
                    if equipped_item:
                        items.add(equipped_item)

            conn.close()

            return items
        except Exception as e:
            print(f"[LOOT] Error fetching player inventory: {e}")
            return set()

    def get_bis_items_for_rarity(self, class_build: str, rarity: str) -> List[Tuple[int, str]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT slot_number, item_name
                FROM best_in_slot_items
                WHERE class_build = ? AND rarity = ?
                ORDER BY slot_number ASC
            """, (class_build, rarity))

            items = cursor.fetchall()
            conn.close()

            return items
        except Exception as e:
            print(f"[LOOT] Error fetching BiS items: {e}")
            return []

    def get_other_items_for_rarity(self, rarity: str, owned_items: Set[str]) -> List[str]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT item_name
                FROM best_in_slot_items
                WHERE class_build = 'Other' AND rarity = ?
            """, (rarity,))

            items = [row[0] for row in cursor.fetchall() if row[0] not in owned_items]
            conn.close()

            return items
        except Exception as e:
            print(f"[LOOT] Error fetching Other items: {e}")
            return []

    def _get_equipment_by_name(self, item_name: str) -> Optional[dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description, item_type, rarity, cost_gp, weight_lb,
                       weapon_category, damage_dice, damage_type, weapon_properties,
                       weapon_mastery, range_normal, range_long, versatile_damage,
                       ammunition, armor_class, armor_type, dex_bonus_max,
                       strength_requirement, stealth_disadvantage, is_magical
                FROM equipment
                WHERE name = ?
                LIMIT 1
            """, (item_name,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                print(f"[LOOT] Warning: Item '{item_name}' not found in equipment table")
                return None

            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'item_type': row[3],
                'rarity': row[4],
                'cost_gp': row[5],
                'weight_lb': row[6],
                'weapon_category': row[7],
                'damage_dice': row[8],
                'damage_type': row[9],
                'weapon_properties': row[10],
                'weapon_mastery': row[11],
                'range_normal': row[12],
                'range_long': row[13],
                'versatile_damage': row[14],
                'ammunition': row[15],
                'armor_class': row[16],
                'armor_type': row[17],
                'dex_bonus_max': row[18],
                'strength_requirement': row[19],
                'stealth_disadvantage': row[20],
                'is_magical': row[21]
            }
        except Exception as e:
            print(f"[LOOT] Error fetching equipment by name: {e}")
            return None

    def cr_to_rarity(self, cr_numeric: float) -> str:
        if cr_numeric < 1:
            return 'Common'
        elif cr_numeric < 4:
            return 'Uncommon'
        elif cr_numeric < 8:
            return 'Rare'
        elif cr_numeric < 12:
            return 'Very Rare'
        else:
            return 'Legendary'