import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shop_service import ShopService, ShopSize, format_currency


class ShopSystemTest:
    def __init__(self):
        self.shop_service = ShopService()

    def test_small_shop_inventory(self):
        print("\n[TEST 1] Small Shop Inventory Generation")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.SMALL)

        print(f"  Generated {len(inventory)} items")
        print(f"  Expected: 10 + 1d10 (11-20 items)")

        if not (11 <= len(inventory) <= 20):
            print(f"  [WARN] Item count {len(inventory)} outside expected range")

        max_price_gp = max((item['shop_price_gp'] for item in inventory), default=0)
        max_price_display, _ = format_currency(max_price_gp)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.SMALL.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 20 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.SMALL.gold_limit} GP limit (max: {max_price_display})")
        return True

    def test_medium_shop_inventory(self):
        print("\n[TEST 2] Medium Shop Inventory Generation")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        print(f"  Generated {len(inventory)} items")
        print(f"  Expected: 10 + 2d10 (12-30 items)")

        if not (12 <= len(inventory) <= 30):
            print(f"  [WARN] Item count {len(inventory)} outside expected range")

        max_price_gp = max((item['shop_price_gp'] for item in inventory), default=0)
        max_price_display, _ = format_currency(max_price_gp)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.MEDIUM.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 200 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.MEDIUM.gold_limit} GP limit (max: {max_price_display})")
        return True

    def test_large_shop_inventory(self):
        print("\n[TEST 3] Large Shop Inventory Generation")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.LARGE)

        print(f"  Generated {len(inventory)} items")
        print(f"  Expected: 10 + 3d10 (13-40 items)")

        if not (13 <= len(inventory) <= 40):
            print(f"  [WARN] Item count {len(inventory)} outside expected range")

        max_price_gp = max((item['shop_price_gp'] for item in inventory), default=0)
        max_price_display, _ = format_currency(max_price_gp)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.LARGE.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 2000 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.LARGE.gold_limit} GP limit (max: {max_price_display})")
        return True

    def test_shop_markup(self):
        print("\n[TEST 4] Shop Markup (25%)")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        if not inventory:
            print("  [FAIL] No inventory generated")
            return False

        sample_item = inventory[0]
        base_cost = sample_item['base_cost']
        shop_price_gp = sample_item['shop_price_gp']
        expected_price_gp = base_cost * 1.25

        base_display, _ = format_currency(base_cost)
        shop_display = sample_item['shop_price_display']

        if abs(shop_price_gp - expected_price_gp) < 0.01:
            print(f"  [PASS] Markup correct: {base_display} -> {shop_display} (25%)")
            return True
        else:
            expected_display, _ = format_currency(expected_price_gp)
            print(f"  [FAIL] Markup incorrect: {base_display} -> {shop_display} (expected {expected_display})")
            return False

    def test_shop_sorting(self):
        print("\n[TEST 5] Shop Inventory Sorting (by price)")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        if not inventory:
            print("  [FAIL] No inventory generated")
            return False

        prices = [item['shop_price_gp'] for item in inventory]
        sorted_prices = sorted(prices)

        if prices == sorted_prices:
            first_display = inventory[0]['shop_price_display']
            last_display = inventory[-1]['shop_price_display']
            print(f"  [PASS] Inventory sorted by price ({first_display} - {last_display})")
            return True
        else:
            print(f"  [FAIL] Inventory not properly sorted")
            return False

    def test_fractional_currency(self):
        print("\n[TEST 6] Fractional Currency Display")
        test_cases = [
            (0.05, "5 cp"),
            (0.5, "5 sp"),
            (1.25, "1 gp 2 sp 5 cp"),
            (50, "50 gp"),
            (10.52, "10 gp 5 sp 2 cp")
        ]

        all_passed = True
        for gold_amount, expected_display in test_cases:
            display, _ = format_currency(gold_amount)
            if display == expected_display:
                print(f"  [PASS] {gold_amount} gp -> {display}")
            else:
                print(f"  [FAIL] {gold_amount} gp -> {display} (expected {expected_display})")
                all_passed = False

        return all_passed

    def test_low_cost_items(self):
        print("\n[TEST 7] Low-Cost Items Included (< 1 GP)")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.SMALL)

        low_cost_items = [item for item in inventory if item['base_cost'] < 1]

        if low_cost_items:
            print(f"  Found {len(low_cost_items)} items under 1 GP:")
            for item in low_cost_items[:3]:
                print(f"    - {item['name']}: {item['shop_price_display']}")
            print("  [PASS] Low-cost items included")
            return True
        else:
            print("  [WARN] No items under 1 GP found (may be random)")
            return True

    def run_all_tests(self):
        print("\n" + "="*60)
        print("SHOP SYSTEM REGRESSION TEST")
        print("="*60)

        test1 = self.test_small_shop_inventory()
        test2 = self.test_medium_shop_inventory()
        test3 = self.test_large_shop_inventory()
        test4 = self.test_shop_markup()
        test5 = self.test_shop_sorting()
        test6 = self.test_fractional_currency()
        test7 = self.test_low_cost_items()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Small Shop: {'PASS' if test1 else 'FAIL'}")
        print(f"Medium Shop: {'PASS' if test2 else 'FAIL'}")
        print(f"Large Shop: {'PASS' if test3 else 'FAIL'}")
        print(f"Shop Markup: {'PASS' if test4 else 'FAIL'}")
        print(f"Shop Sorting: {'PASS' if test5 else 'FAIL'}")
        print(f"Fractional Currency: {'PASS' if test6 else 'FAIL'}")
        print(f"Low-Cost Items: {'PASS' if test7 else 'FAIL'}")

        all_passed = test1 and test2 and test3 and test4 and test5 and test6 and test7

        print("\n" + "="*60)
        if all_passed:
            print("ALL TESTS PASSED [OK]")
        else:
            print("SOME TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = ShopSystemTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)