import random
import sqlite3
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from talekeeper.services.equipment_database import EquipmentDatabase


def format_currency(gold_amount: float) -> Tuple[str, str]:
    """
    Convert gold amount to appropriate currency display.
    Returns (display_string, sort_key_string)

    Examples:
        0.05 -> ("5 cp", "00000.05")
        0.5 -> ("5 sp", "00000.50")
        1.25 -> ("1 gp 2 sp 5 cp", "00001.25")
        50 -> ("50 gp", "00050.00")
    """
    if gold_amount < 0.01:
        return ("0 cp", "00000.00")

    total_copper = round(gold_amount * 100)

    gp = total_copper // 100
    sp = (total_copper % 100) // 10
    cp = total_copper % 10

    parts = []
    if gp > 0:
        parts.append(f"{gp} gp")
    if sp > 0:
        parts.append(f"{sp} sp")
    if cp > 0:
        parts.append(f"{cp} cp")

    display = " ".join(parts) if parts else "0 cp"
    sort_key = f"{gold_amount:09.2f}"

    return (display, sort_key)


class ShopSize(Enum):
    SMALL = ("small", 20, 10, 1)
    MEDIUM = ("medium", 200, 10, 2)
    LARGE = ("large", 2000, 10, 3)

    def __init__(self, size_name: str, gold_limit: int, base_items: int, dice_count: int):
        self.size_name = size_name
        self.gold_limit = gold_limit
        self.base_items = base_items
        self.dice_count = dice_count


class ShopService:
    ECONOMY_TIERS = {
        25: {'base_pool': 10, 'base_cap': 10},
        75: {'base_pool': 25, 'base_cap': 25},
        150: {'base_pool': 50, 'base_cap': 50},
        200: {'base_pool': 75, 'base_cap': 75},
        500: {'base_pool': 200, 'base_cap': 100},
        1000: {'base_pool': 400, 'base_cap': 150},
        1500: {'base_pool': 700, 'base_cap': 200},
        2000: {'base_pool': 1000, 'base_cap': 250},
        5000: {'base_pool': 5000, 'base_cap': 5000},
        10000: {'base_pool': 10000, 'base_cap': 10000},
    }

    def __init__(self, db_path: str = "talekeeper.db"):
        self.equipment_db = EquipmentDatabase()
        self.db_path = db_path

    def generate_shop_inventory(self, shop_size: ShopSize, markup_percent: float = 25.0) -> List[Dict[str, Any]]:
        all_equipment = self.equipment_db.get_equipment_by_rarity(['common', 'uncommon'])

        eligible_items = []
        for item in all_equipment:
            base_cost = item.get('cost_gp', 0)
            if base_cost >= 0.01 and base_cost <= shop_size.gold_limit:
                eligible_items.append(item)

        if not eligible_items:
            return []

        num_additional_items = sum(random.randint(1, 10) for _ in range(shop_size.dice_count))
        total_items = min(shop_size.base_items + num_additional_items, len(eligible_items))

        selected_items = random.sample(eligible_items, total_items)

        shop_inventory = []
        for item in selected_items:
            shop_item = item.copy()
            base_cost = item.get('cost_gp', 0)
            shop_price_gp = base_cost * (1 + markup_percent / 100)
            shop_item['shop_price_gp'] = shop_price_gp
            shop_item['shop_price_display'], shop_item['shop_price_sort'] = format_currency(shop_price_gp)
            shop_item['base_cost'] = base_cost
            shop_inventory.append(shop_item)

        shop_inventory.sort(key=lambda x: x['shop_price_sort'])

        return shop_inventory

    def get_shop_size_by_name(self, size_name: str) -> ShopSize:
        size_map = {
            'small': ShopSize.SMALL,
            'medium': ShopSize.MEDIUM,
            'large': ShopSize.LARGE
        }
        return size_map.get(size_name.lower(), ShopSize.MEDIUM)

    def calculate_sell_price(self, item_cost: float) -> Tuple[float, str]:
        sell_price_gp = max(0.01, item_cost * 0.5)
        display, _ = format_currency(sell_price_gp)
        return (sell_price_gp, display)

    def get_charisma_skill_roll(self, character_data: Dict[str, Any]) -> int:
        character_id = character_data.get('id')
        if not character_id:
            return 0

        charisma_mod = self._calculate_ability_modifier(character_data.get('charisma', 10))
        proficiency_bonus = self._calculate_proficiency_bonus(character_data.get('level', 1))

        skills = ['Persuasion', 'Deception', 'Intimidation']
        rolls = []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for skill in skills:
            cursor.execute('''
                SELECT COUNT(*) FROM character_proficiencies
                WHERE character_id = ? AND proficiency_name = ? AND proficiency_type = 'skill'
            ''', (character_id, skill))

            is_proficient = cursor.fetchone()[0] > 0
            skill_bonus = charisma_mod + (proficiency_bonus if is_proficient else 0)

            cursor.execute('''
                SELECT COUNT(*) FROM character_proficiencies
                WHERE character_id = ? AND proficiency_name = ? AND proficiency_type = 'skill_expertise'
            ''', (character_id, skill))

            has_expertise = cursor.fetchone()[0] > 0
            if has_expertise:
                skill_bonus += proficiency_bonus

            roll = random.randint(1, 20) + skill_bonus
            rolls.append(roll)

        conn.close()
        return max(rolls)

    def has_crafter_feat(self, character_data: Dict[str, Any]) -> bool:
        character_id = character_data.get('id')
        if not character_id:
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM character_feats WHERE character_id = ? AND feat_name = 'Crafter'",
            (character_id,)
        )
        has_feat = cursor.fetchone()[0] > 0
        conn.close()
        return has_feat

    def _calculate_ability_modifier(self, ability_score: int) -> int:
        return (ability_score - 10) // 2

    def _calculate_proficiency_bonus(self, level: int) -> int:
        return ((level - 1) // 4) + 2

    def _settlement_to_shop_size(self, settlement_type: str) -> ShopSize:
        mapping = {
            'hamlet': ShopSize.SMALL,
            'village': ShopSize.MEDIUM,
            'town_small': ShopSize.LARGE,
            'town_medium': ShopSize.LARGE,
            'town_large': ShopSize.LARGE,
            'empty': ShopSize.SMALL
        }
        return mapping.get(settlement_type, ShopSize.MEDIUM)

    def _determine_population_tier(self, settlement_type: str, seed: int) -> int:
        rng = random.Random(seed)

        if settlement_type == 'hamlet':
            return rng.choice([25, 75, 150, 200])
        elif settlement_type == 'village':
            return rng.choice([200, 500, 1000, 1500])
        elif settlement_type == 'town_small':
            return 2000
        elif settlement_type == 'town_medium':
            return 5000
        elif settlement_type == 'town_large':
            return 10000
        else:
            return 150

    def generate_hex_shop_inventory(
        self,
        settlement_type: str,
        character_data: Dict[str, Any],
        hex_seed: int
    ) -> Dict[str, Any]:
        charisma_roll = self.get_charisma_skill_roll(character_data)
        has_crafter = self.has_crafter_feat(character_data)

        buy_discount = charisma_roll
        if has_crafter:
            buy_discount += 20

        population = self._determine_population_tier(settlement_type, hex_seed)
        economy_tier = self.ECONOMY_TIERS.get(population, {'base_pool': 100, 'base_cap': 100})

        import time
        variance_rng = random.Random(int(time.time() * 1000000))
        pool_variance = variance_rng.randint(1, 200) / 100.0
        cap_variance = variance_rng.randint(1, 200) / 100.0

        actual_pool = economy_tier['base_pool'] * pool_variance
        actual_cap = economy_tier['base_cap'] * cap_variance

        rarity_list = ['common', 'uncommon']
        if settlement_type in ['town_medium', 'town_large']:
            rarity_list.append('rare')

        markup = max(0, 25 - buy_discount)
        markup_multiplier = 1 + markup / 100.0

        all_equipment = self.equipment_db.get_equipment_by_rarity(rarity_list)
        eligible_items = []
        for item in all_equipment:
            base_cost = item.get('cost_gp', 0)
            final_price = base_cost * markup_multiplier
            if 0.01 <= final_price <= actual_cap:
                eligible_items.append(item)

        if not eligible_items:
            eligible_items = []

        cheap_items = []
        high_value_items = []
        for item in eligible_items:
            base_cost = item.get('cost_gp', 0)
            final_price = base_cost * markup_multiplier
            if final_price <= actual_cap * 0.5:
                cheap_items.append(item)
            elif final_price <= actual_cap:
                high_value_items.append(item)

        num_cheap = random.randint(1, 8) + 2
        num_high_value = random.randint(1, 8) + 2

        inventory = []
        if cheap_items:
            inventory.extend(random.sample(cheap_items, min(num_cheap, len(cheap_items))))
        if high_value_items:
            inventory.extend(random.sample(high_value_items, min(num_high_value, len(high_value_items))))

        seen = set()
        unique_inventory = []
        for item in inventory:
            if item['name'] not in seen:
                seen.add(item['name'])
                unique_inventory.append(item)

        for item in unique_inventory:
            base_cost = item.get('cost_gp', 0)
            buy_price = base_cost * markup_multiplier
            item['buy_price_gp'] = buy_price
            item['buy_price_display'], _ = format_currency(buy_price)
            item['buy_discount_applied'] = buy_discount

        unique_inventory.sort(key=lambda x: x.get('cost_gp', 0))

        shop_size_map = {
            'hamlet': 'small',
            'village': 'medium',
            'town_small': 'large',
            'town_medium': 'large',
            'town_large': 'large',
            'empty': 'small'
        }
        shop_size = shop_size_map.get(settlement_type, 'medium')

        return {
            'inventory': unique_inventory,
            'charisma_roll': charisma_roll,
            'has_crafter': has_crafter,
            'pool_variance': pool_variance,
            'cap_variance': cap_variance,
            'settlement_type': settlement_type,
            'population': population,
            'base_pool': economy_tier['base_pool'],
            'base_cap': economy_tier['base_cap'],
            'actual_pool': actual_pool,
            'actual_cap': actual_cap,
            'shop_size': shop_size
        }

    def calculate_sell_price_with_character(self, item_cost: float, character_data: Dict[str, Any]) -> Tuple[float, str, int]:
        charisma_roll = self.get_charisma_skill_roll(character_data)
        sell_rate = min(100, 40 + charisma_roll)
        sell_price = item_cost * (sell_rate / 100.0)
        display, _ = format_currency(sell_price)
        return (sell_price, display, charisma_roll)