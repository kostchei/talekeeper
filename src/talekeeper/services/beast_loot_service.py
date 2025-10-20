# core
# category: core
import sqlite3
from typing import Dict, List, Optional

class BeastLootService:
    """
    Handles loot drops for beast-type monsters.

    Beasts drop standard rations instead of gold as individual treasure.
    Ration quantity is based on individual treasure value converted at 0.5 GP per ration.
    Uses "Rations (1 day)" from the equipment table so they stack with regular rations.
    """

    RATION_COST_GP = 0.5
    RATION_WEIGHT_LB = 2.0

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def is_beast(self, monster_id: str) -> bool:
        """Check if a monster is a beast type"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT type, drops_rations
                FROM monsters
                WHERE id = ?
            """, (monster_id,))

            row = cursor.fetchone()
            if not row:
                return False

            monster_type, drops_rations = row
            return monster_type == 'beast' or drops_rations == 1

        except Exception as e:
            print(f"[BEAST_LOOT] Error checking beast type: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_individual_treasure_value(self, monster_id: str) -> float:
        """
        Get individual treasure value for a monster.
        This is a placeholder - will use CR-based calculation.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT challenge_rating FROM monsters WHERE id = ?", (monster_id,))
            row = cursor.fetchone()

            if not row:
                return 0.0

            cr_text = row[0]
            cr_numeric = self._parse_cr(cr_text)

            individual_treasure_gp = self._cr_to_individual_treasure(cr_numeric)
            return individual_treasure_gp

        except Exception as e:
            print(f"[BEAST_LOOT] Error getting treasure value: {e}")
            return 0.0
        finally:
            if conn:
                conn.close()

    def _parse_cr(self, cr_text: str) -> float:
        """Parse CR string to numeric value"""
        if not cr_text:
            return 0.0

        cr_text = cr_text.strip().lower()

        if cr_text == '1/8':
            return 0.125
        elif cr_text == '1/4':
            return 0.25
        elif cr_text == '1/2':
            return 0.5

        try:
            return float(cr_text)
        except ValueError:
            return 0.0

    def _cr_to_individual_treasure(self, cr: float) -> float:
        """
        Convert CR to individual treasure GP value.
        Based on DMG treasure tables - individual treasure per monster.
        """
        if cr < 0.25:
            return 0.5
        elif cr < 1:
            return 1.0
        elif cr < 2:
            return 2.0
        elif cr < 4:
            return 5.0
        elif cr < 6:
            return 10.0
        elif cr < 8:
            return 15.0
        elif cr < 10:
            return 25.0
        elif cr < 12:
            return 50.0
        elif cr < 15:
            return 75.0
        elif cr < 20:
            return 100.0
        else:
            return 150.0

    def calculate_ration_drop(self, monster_id: str) -> int:
        """
        Calculate how many rations a beast drops.

        Formula: individual_treasure_gp / 0.5 GP per ration
        Minimum: 1 ration
        """
        treasure_value = self.get_individual_treasure_value(monster_id)
        ration_count = max(1, int(treasure_value / self.RATION_COST_GP))
        return ration_count

    def generate_beast_loot(self, monster_id: str) -> List[Dict]:
        """
        Generate loot for a defeated beast.

        Returns:
            List of loot items (standard rations instead of gold)
        """
        if not self.is_beast(monster_id):
            return []

        ration_count = self.calculate_ration_drop(monster_id)

        # Return individual rations from the equipment table so they stack properly
        loot_items = []
        for _ in range(ration_count):
            ration_item = self._get_ration_from_equipment()
            if ration_item:
                loot_items.append(ration_item)

        return loot_items

    def _get_ration_from_equipment(self) -> Dict:
        """Get a single ration (1 day) from the equipment table."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, description, item_type, rarity, cost_gp, weight_lb
                FROM equipment
                WHERE name = 'Rations (1 day)'
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            if not row:
                print("[BEAST_LOOT] Warning: 'Rations (1 day)' not found in equipment table")
                # Fallback to creating a basic ration dict
                return {
                    'name': 'Rations (1 day)',
                    'item_type': 'gear',
                    'rarity': 'common',
                    'cost_gp': self.RATION_COST_GP,
                    'weight_lb': self.RATION_WEIGHT_LB,
                    'description': 'One day of food'
                }

            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'item_type': row[3],
                'rarity': row[4],
                'cost_gp': row[5],
                'weight_lb': row[6]
            }
        except Exception as e:
            print(f"[BEAST_LOOT] Error fetching ration from equipment: {e}")
            # Return fallback ration
            return {
                'name': 'Rations (1 day)',
                'item_type': 'gear',
                'rarity': 'common',
                'cost_gp': self.RATION_COST_GP,
                'weight_lb': self.RATION_WEIGHT_LB,
                'description': 'One day of food'
            }

    def add_rations_to_inventory(self, character_id: str, quantity: int) -> bool:
        """Add rations to character inventory"""
        if quantity <= 0:
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Use standard "Rations (1 day)" from equipment table
            cursor.execute("""
                SELECT quantity, item_type
                FROM character_inventory
                WHERE character_id = ? AND item_name = 'Rations (1 day)'
            """, (character_id,))

            existing = cursor.fetchone()

            if existing:
                new_quantity = existing[0] + quantity
                cursor.execute("""
                    UPDATE character_inventory
                    SET quantity = ?
                    WHERE character_id = ? AND item_name = 'Rations (1 day)'
                """, (new_quantity, character_id))
            else:
                cursor.execute("""
                    INSERT INTO character_inventory
                    (character_id, item_name, item_type, quantity)
                    VALUES (?, 'Rations (1 day)', 'gear', ?)
                """, (character_id, quantity))

            conn.commit()
            return True

        except Exception as e:
            print(f"[BEAST_LOOT] Error adding rations to inventory: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_monster_name(self, monster_id: str) -> str:
        """Get monster name for logging"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM monsters WHERE id = ?", (monster_id,))
            row = cursor.fetchone()

            return row[0] if row else "Unknown Beast"

        except Exception:
            return "Unknown Beast"
        finally:
            if conn:
                conn.close()
