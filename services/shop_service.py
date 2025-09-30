import random
from enum import Enum
from typing import List, Dict, Any, Tuple
from services.equipment_database import EquipmentDatabase


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
    def __init__(self):
        self.equipment_db = EquipmentDatabase()

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