import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shop_service import ShopService, ShopSize


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

        max_price = max((item['shop_price'] for item in inventory), default=0)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.SMALL.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 20 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.SMALL.gold_limit} GP limit (max: {max_price} GP)")
        return True

    def test_medium_shop_inventory(self):
        print("\n[TEST 2] Medium Shop Inventory Generation")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        print(f"  Generated {len(inventory)} items")
        print(f"  Expected: 10 + 2d10 (12-30 items)")

        if not (12 <= len(inventory) <= 30):
            print(f"  [WARN] Item count {len(inventory)} outside expected range")

        max_price = max((item['shop_price'] for item in inventory), default=0)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.MEDIUM.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 200 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.MEDIUM.gold_limit} GP limit (max: {max_price} GP)")
        return True

    def test_large_shop_inventory(self):
        print("\n[TEST 3] Large Shop Inventory Generation")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.LARGE)

        print(f"  Generated {len(inventory)} items")
        print(f"  Expected: 10 + 3d10 (13-40 items)")

        if not (13 <= len(inventory) <= 40):
            print(f"  [WARN] Item count {len(inventory)} outside expected range")

        max_price = max((item['shop_price'] for item in inventory), default=0)
        over_limit = [item for item in inventory if item['base_cost'] > ShopSize.LARGE.gold_limit]

        if over_limit:
            print(f"  [FAIL] {len(over_limit)} items exceed 2000 GP limit")
            return False

        print(f"  [PASS] All items under {ShopSize.LARGE.gold_limit} GP limit (max: {max_price} GP)")
        return True

    def test_shop_markup(self):
        print("\n[TEST 4] Shop Markup (25%)")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        if not inventory:
            print("  [FAIL] No inventory generated")
            return False

        sample_item = inventory[0]
        base_cost = sample_item['base_cost']
        shop_price = sample_item['shop_price']
        expected_price = int(base_cost * 1.25)

        if shop_price == expected_price:
            print(f"  [PASS] Markup correct: {base_cost} GP -> {shop_price} GP (25%)")
            return True
        else:
            print(f"  [FAIL] Markup incorrect: {base_cost} GP -> {shop_price} GP (expected {expected_price} GP)")
            return False

    def test_shop_sorting(self):
        print("\n[TEST 5] Shop Inventory Sorting (by price)")
        inventory = self.shop_service.generate_shop_inventory(ShopSize.MEDIUM)

        if not inventory:
            print("  [FAIL] No inventory generated")
            return False

        prices = [item['shop_price'] for item in inventory]
        sorted_prices = sorted(prices)

        if prices == sorted_prices:
            print(f"  [PASS] Inventory sorted by price ({prices[0]} GP - {prices[-1]} GP)")
            return True
        else:
            print(f"  [FAIL] Inventory not properly sorted")
            return False

    def run_all_tests(self):
        print("\n" + "="*60)
        print("SHOP SYSTEM REGRESSION TEST")
        print("="*60)

        test1 = self.test_small_shop_inventory()
        test2 = self.test_medium_shop_inventory()
        test3 = self.test_large_shop_inventory()
        test4 = self.test_shop_markup()
        test5 = self.test_shop_sorting()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Small Shop: {'PASS' if test1 else 'FAIL'}")
        print(f"Medium Shop: {'PASS' if test2 else 'FAIL'}")
        print(f"Large Shop: {'PASS' if test3 else 'FAIL'}")
        print(f"Shop Markup: {'PASS' if test4 else 'FAIL'}")
        print(f"Shop Sorting: {'PASS' if test5 else 'FAIL'}")

        all_passed = test1 and test2 and test3 and test4 and test5

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