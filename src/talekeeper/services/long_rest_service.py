import random
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime


LIFESTYLE_COSTS = {
    'wretched': 0.0,
    'squalid': 0.1,
    'poor': 0.2,
    'modest': 1.0,
    'comfortable': 2.0,
    'wealthy': 4.0
}

LIFESTYLE_DESCRIPTIONS = {
    'wretched': 'Survive via chance and charity. Sleep outside exposed to elements.',
    'squalid': 'Bare minimum shelter. Unhealthy conditions, opportunistic criminals.',
    'poor': 'Frugal necessities. Basic inn or local hospitality.',
    'modest': 'Average standard. Clean room, basic amenities.',
    'comfortable': 'Modest spending with luxuries. Well-maintained inn.',
    'wealthy': 'Fine accommodations. Private rooms, servants.'
}

ENCOUNTER_TABLE = {
    1: {
        'name': 'Bandits',
        'description': 'A group of armed bandits emerges from the shadows, weapons drawn.',
        'type': 'combat',
        'cr_modifier': 0
    },
    2: {
        'name': 'Wild Animals',
        'description': 'Hungry wolves circle your resting place, eyes gleaming in the darkness.',
        'type': 'combat',
        'cr_modifier': -1
    },
    3: {
        'name': 'Cutpurses',
        'description': 'A nimble thief attempts to rifle through your belongings!',
        'type': 'skill_check',
        'ability': 'dexterity',
        'dc': 15,
        'on_fail': 'lose_gold',
        'gold_formula': '2d10'
    },
    4: {
        'name': 'Corrupt Guards',
        'description': 'Local guards demand a bribe, hands on sword hilts.',
        'type': 'choice',
        'options': ['pay', 'fight'],
        'pay_gold': '1d10',
        'fight_cr': 0
    },
    5: {
        'name': 'Desperate Beggar',
        'description': 'A ragged beggar pleads for coin, growing increasingly aggressive.',
        'type': 'skill_check',
        'ability': 'charisma',
        'dc': 12,
        'on_fail': 'lose_items',
        'gold_formula': '1d6',
        'rations': '1d4'
    },
    6: {
        'name': 'Thugs Shakedown',
        'description': 'Rough-looking thugs corner you, demanding protection money.',
        'type': 'skill_check',
        'ability': 'charisma',
        'skill': 'intimidation',
        'dc': 13,
        'on_fail_choice': ['pay', 'fight'],
        'pay_gold': '3d6',
        'fight_cr': 0
    }
}

HAZARD_TABLE = {
    1: {
        'name': 'Disease',
        'description': 'You wake feeling feverish. Something in the water or air has sickened you.',
        'save_ability': 'constitution',
        'dc': 12,
        'on_fail': 'condition',
        'condition': 'diseased',
        'duration_days': '1d4',
        'effect': 'Disadvantage on ability checks'
    },
    2: {
        'name': 'Theft',
        'description': 'You wake to find your belongings disturbed. A thief struck in the night!',
        'save_ability': 'wisdom',
        'skill': 'perception',
        'dc': 14,
        'on_fail': 'lose_items',
        'gold_formula': '2d10',
        'random_items': 1
    },
    3: {
        'name': 'Exposure',
        'description': 'The bitter cold seeps through your bedroll. Your teeth chatter uncontrollably.',
        'save_ability': 'constitution',
        'dc': 13,
        'on_fail': 'damage_and_exhaustion',
        'damage_formula': '1d6',
        'damage_type': 'cold',
        'exhaustion_levels': 1
    },
    4: {
        'name': 'Food Poisoning',
        'description': 'Your meager meal churns in your stomach. You feel violently ill.',
        'save_ability': 'constitution',
        'dc': 13,
        'on_fail': 'condition',
        'condition': 'poisoned',
        'duration_hours': 8
    },
    5: {
        'name': 'Structural Collapse',
        'description': 'The ceiling groans ominously. Debris rains down!',
        'save_ability': 'dexterity',
        'dc': 14,
        'on_fail': 'damage',
        'damage_formula': '2d6',
        'damage_type': 'bludgeoning'
    },
    6: {
        'name': 'Fire',
        'description': 'Flames erupt from a knocked-over lantern! Smoke fills the air!',
        'save_ability': 'dexterity',
        'dc': 15,
        'on_fail': 'damage_and_items',
        'damage_formula': '2d8',
        'damage_type': 'fire',
        'items_lost': '1d4'
    }
}


class LongRestService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_available_lifestyles(self, character_id: str, q: int, r: int) -> List[Dict]:
        """Get available lifestyle options for hex settlement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT settlement_type, settlement_name, accommodation_name
            FROM character_hex_map
            WHERE character_id = ? AND q = ? AND r = ?
        ''', (character_id, q, r))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return [self._create_lifestyle_option('wretched', None, None)]

        settlement_type, settlement_name, accommodation_name = row

        if settlement_type in [None, 'empty']:
            return [self._create_lifestyle_option('wretched', None, None)]

        rng = random.Random()
        lifestyle_order = ['squalid', 'poor', 'modest', 'comfortable', 'wealthy']
        order_lookup = {name: idx for idx, name in enumerate(lifestyle_order)}

        def roll_unique_lifestyles(pool: List[str], rolls: int) -> List[str]:
            """Return up to `rolls` unique lifestyles from pool."""
            selected = set()
            for _ in range(rolls):
                choice = rng.choice(pool)
                selected.add(choice)
            return sorted(selected, key=lambda name: order_lookup.get(name, len(lifestyle_order)))

        lifestyles: List[Dict] = []

        if settlement_type == 'hamlet':
            lifestyles.append(self._create_lifestyle_option('wretched', settlement_name, None))
            rolled = roll_unique_lifestyles(['squalid', 'poor', 'modest'], 2)
            for lifestyle in rolled:
                lifestyles.append(self._create_lifestyle_option(lifestyle, settlement_name, accommodation_name))

        elif settlement_type == 'village':
            lifestyles.append(self._create_lifestyle_option('wretched', settlement_name, None))
            rolled = roll_unique_lifestyles(['squalid', 'poor', 'modest', 'comfortable'], 2)
            for lifestyle in rolled:
                lifestyles.append(self._create_lifestyle_option(lifestyle, settlement_name, accommodation_name))

        else:
            for level in ['wretched', 'squalid', 'poor', 'modest', 'comfortable', 'wealthy']:
                lifestyles.append(self._create_lifestyle_option(level, settlement_name, accommodation_name))

        return lifestyles

    def _create_lifestyle_option(self, lifestyle: str, settlement_name: Optional[str], accommodation_name: Optional[str]) -> Dict:
        """Create lifestyle option dict."""
        option = {
            'lifestyle': lifestyle,
            'cost_gp': LIFESTYLE_COSTS[lifestyle],
            'description': LIFESTYLE_DESCRIPTIONS[lifestyle],
            'settlement_name': settlement_name,
            'accommodation_name': accommodation_name
        }

        if lifestyle == 'wretched':
            option['hazard_chance'] = 0.5
            option['warning'] = 'DANGER: 50% chance of encounter or hazard'
        elif lifestyle == 'squalid':
            option['hazard_chance'] = 0.25
            option['warning'] = 'CAUTION: 25% chance of encounter or hazard'
        else:
            option['hazard_chance'] = 0.0
            option['warning'] = None

        if lifestyle in ['modest', 'comfortable', 'wealthy'] and accommodation_name:
            option['location'] = accommodation_name
        elif lifestyle == 'squalid' and accommodation_name:
            option['location'] = f"{accommodation_name} (flophouse)"
        elif lifestyle == 'poor':
            option['location'] = "Common room with shared bunks"
        else:
            option['location'] = "Sleeping rough"

        return option

    def check_hazard_trigger(self, lifestyle: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """Check if wretched/squalid triggers hazard.

        Returns:
            (triggered, event_type, event_data)
            event_type: 'encounter' or 'hazard' or None
        """
        if lifestyle not in ['wretched', 'squalid']:
            return (False, None, None)

        chance = 0.5 if lifestyle == 'wretched' else 0.25
        roll = random.random()

        if roll > chance:
            return (False, None, None)

        event_type = 'encounter' if random.randint(1, 2) == 1 else 'hazard'

        if event_type == 'encounter':
            encounter_roll = random.randint(1, 6)
            event_data = ENCOUNTER_TABLE[encounter_roll].copy()
        else:
            hazard_roll = random.randint(1, 6)
            event_data = HAZARD_TABLE[hazard_roll].copy()

        return (True, event_type, event_data)

    def get_character_gold(self, character_id: str) -> float:
        """Get total gold (in gp) from the character's inventory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM(
                COALESCE(quantity, 0) *
                COALESCE(NULLIF(unit_value_gp, 0), 1)
            )
            FROM character_inventory
            WHERE character_id = ?
              AND item_name = 'Gold Pieces'
              AND item_type IN ('treasure', 'currency')
        ''', (character_id,))

        row = cursor.fetchone()
        conn.close()

        if not row or row[0] is None:
            return 0.0

        return float(round(row[0], 4))

    def get_character_rest_status(self, character_id: str) -> Dict[str, float]:
        """Return HP/Hit Dice snapshot for rest calculations (handles legacy schemas)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        column_sets = [
            ('hit_points_current', 'hit_points_max', 'hit_dice_current', 'hit_dice_max'),
            ('current_hit_points', 'max_hit_points', 'hit_dice_current', 'hit_dice_max'),
            ('current_hp', 'max_hp', 'hit_dice', 'max_hit_dice')
        ]

        status = {
            'current_hp': 0,
            'max_hp': 0,
            'level': 1,
            'hit_dice_current': 0,
            'hit_dice_max': 0
        }

        for hp_current, hp_max, hd_current, hd_max in column_sets:
            try:
                cursor.execute(f'''
                    SELECT
                        COALESCE({hp_current}, 0),
                        COALESCE({hp_max}, 0),
                        level,
                        COALESCE({hd_current}, 0),
                        COALESCE({hd_max}, 0)
                    FROM characters
                    WHERE id = ?
                ''', (character_id,))
                row = cursor.fetchone()
                if row:
                    status['current_hp'] = row[0]
                    status['max_hp'] = row[1]
                    status['level'] = row[2]
                    status['hit_dice_current'] = row[3]
                    status['hit_dice_max'] = row[4]
                    break
            except sqlite3.OperationalError:
                continue

        conn.close()
        return status

    def _spend_gold(self, cursor: sqlite3.Cursor, character_id: str, amount_gp: float) -> bool:
        """Internal helper to deduct gold without closing the connection."""
        if amount_gp <= 0:
            return True

        cursor.execute('''
            SELECT id, COALESCE(quantity, 0), COALESCE(unit_value_gp, 0)
            FROM character_inventory
            WHERE character_id = ?
              AND item_name = 'Gold Pieces'
              AND item_type IN ('treasure', 'currency')
            ORDER BY id
        ''', (character_id,))

        rows = cursor.fetchall()
        if not rows:
            return False

        total_gold = 0.0
        normalized_rows = []
        for inv_id, quantity, unit_value in rows:
            value_per = unit_value if unit_value and unit_value > 0 else 1.0
            row_total = quantity * value_per
            total_gold += row_total
            normalized_rows.append((inv_id, quantity, value_per))

        if total_gold + 1e-6 < amount_gp:
            return False

        remaining = amount_gp
        for inv_id, quantity, value_per in normalized_rows:
            row_total = quantity * value_per
            if row_total <= 0 or remaining <= 1e-6:
                continue

            deduction = min(row_total, remaining)
            new_total = row_total - deduction
            new_quantity = max(0.0, round(new_total / value_per, 4))

            cursor.execute('''
                UPDATE character_inventory
                SET quantity = ?
                WHERE id = ?
            ''', (new_quantity, inv_id))

            remaining -= deduction
            if remaining <= 1e-6:
                break

        return True

    def deduct_lifestyle_cost(self, character_id: str, lifestyle_cost: float) -> bool:
        """Deduct gold from character_inventory. Returns True if successful."""
        if lifestyle_cost <= 0:
            return True

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        success = self._spend_gold(cursor, character_id, lifestyle_cost)

        if success:
            conn.commit()
        else:
            conn.rollback()

        conn.close()
        return success

    def apply_long_rest_benefits(self, character_id: str) -> Dict:
        """Apply long rest benefits: restore HP, spell slots, abilities."""
        status = self.get_character_rest_status(character_id)

        max_hp = status['max_hp']
        current_hp = status['current_hp']
        level = status['level']
        hit_dice_current = status['hit_dice_current']
        hit_dice_max = status['hit_dice_max']

        if max_hp <= 0:
            return {'success': False, 'error': 'Character not found'}

        restored_hp = max(0, max_hp - current_hp)
        available_hit_dice = max(0, hit_dice_max - hit_dice_current)
        restored_hit_dice = min(level // 2, available_hit_dice)
        new_hit_dice = hit_dice_current + restored_hit_dice

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(characters)")
        column_names = {row[1] for row in cursor.fetchall()}

        update_fields = []
        params: List = []

        if 'hit_points_current' in column_names:
            update_fields.append('hit_points_current = ?')
            params.append(max_hp)
        if 'current_hit_points' in column_names:
            update_fields.append('current_hit_points = ?')
            params.append(max_hp)
        if 'current_hp' in column_names:
            update_fields.append('current_hp = ?')
            params.append(max_hp)
        if 'hit_dice_current' in column_names:
            update_fields.append('hit_dice_current = ?')
            params.append(new_hit_dice)
        if 'hit_dice' in column_names:
            update_fields.append('hit_dice = ?')
            params.append(new_hit_dice)

        update_fields.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        params.append(character_id)

        cursor.execute(f'''
            UPDATE characters
            SET {", ".join(update_fields)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

        return {
            'success': True,
            'hp_restored': restored_hp,
            'hit_dice_restored': restored_hit_dice,
            'new_hp': max_hp,
            'new_hit_dice': new_hit_dice
        }

    def record_rest(self, character_id: str, q: int, r: int, lifestyle: str, lifestyle_cost: float,
                    hazard_triggered: bool, hazard_type: Optional[str], hazard_result: Optional[str]) -> None:
        """Record long rest in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO character_long_rests
            (character_id, hex_q, hex_r, rest_date, lifestyle_type, lifestyle_cost_gp,
             hazard_triggered, hazard_type, hazard_result, rest_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (character_id, q, r, datetime.now().isoformat(), lifestyle, lifestyle_cost,
              1 if hazard_triggered else 0, hazard_type, hazard_result))

        conn.commit()
        conn.close()

    def roll_damage(self, formula: str) -> int:
        """Roll damage dice (e.g., '2d6', '1d8')."""
        if 'd' not in formula:
            return 0

        parts = formula.split('d')
        num_dice = int(parts[0])
        die_size = int(parts[1])

        total = 0
        for _ in range(num_dice):
            total += random.randint(1, die_size)

        return total

    def apply_damage(self, character_id: str, damage: int, damage_type: str) -> Dict:
        """Apply damage to character."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT current_hp FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return {'success': False}

        current_hp = row[0]
        new_hp = max(0, current_hp - damage)

        cursor.execute('UPDATE characters SET current_hp = ? WHERE id = ?', (new_hp, character_id))
        conn.commit()
        conn.close()

        return {
            'success': True,
            'damage': damage,
            'damage_type': damage_type,
            'old_hp': current_hp,
            'new_hp': new_hp,
            'unconscious': new_hp == 0
        }

    def apply_condition(self, character_id: str, condition: str, duration_hours: int) -> Dict:
        """Apply condition to character."""
        return {
            'success': True,
            'condition': condition,
            'duration_hours': duration_hours,
            'message': f"You are {condition} for {duration_hours} hours."
        }

    def apply_gold_loss(self, character_id: str, gold_formula: str) -> Dict:
        """Apply gold loss to character."""
        gold_lost = self.roll_damage(gold_formula)
        current_gold = self.get_character_gold(character_id)
        actual_loss = min(gold_lost, current_gold)

        if actual_loss <= 0:
            return {
                'success': True,
                'gold_lost': 0,
                'old_gold': current_gold,
                'new_gold': current_gold
            }

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        success = self._spend_gold(cursor, character_id, actual_loss)

        if success:
            conn.commit()
        else:
            conn.rollback()

        conn.close()

        new_gold = max(0.0, current_gold - actual_loss if success else current_gold)

        return {
            'success': success,
            'gold_lost': actual_loss if success else 0,
            'old_gold': current_gold,
            'new_gold': new_gold
        }
