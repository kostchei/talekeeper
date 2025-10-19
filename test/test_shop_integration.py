import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, os.path.join(str(project_root), 'src'))

from talekeeper.services.shop_service import ShopService, ShopSize


class ShopIntegrationTest:
    """Test shop system integration points"""

    def __init__(self):
        self.shop_service = ShopService()

    def test_shop_interface_signature(self):
        """Test that ShopInterface can be instantiated with correct parameters"""
        print("\n[TEST 1] ShopInterface Instantiation")

        try:
            from encounter_pane.town_encounter import ShopInterface
            from PyQt6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            test_character = {
                'id': 'test_char_123',
                'name': 'Test Character',
                'level': 5
            }

            shop = ShopInterface(test_character, ShopSize.MEDIUM)

            if shop is not None:
                print("  [PASS] ShopInterface instantiated successfully")
                return True
            else:
                print("  [FAIL] ShopInterface returned None")
                return False

        except TypeError as e:
            print(f"  [FAIL] TypeError in ShopInterface: {e}")
            return False
        except Exception as e:
            print(f"  [FAIL] Exception in ShopInterface: {e}")
            return False

    def test_vendor_encounter_compatibility(self):
        """Test that vendor encounter can create ShopInterface"""
        print("\n[TEST 2] Vendor Encounter Compatibility")

        try:
            from encounter_pane.town_encounter import ShopInterface
            from talekeeper.services.shop_service import ShopSize
            import random

            test_character = {
                'id': 'test_vendor_char',
                'name': 'Vendor Test',
                'level': 3
            }

            vendor_size = random.choice([ShopSize.SMALL, ShopSize.MEDIUM, ShopSize.LARGE])
            shop = ShopInterface(test_character, vendor_size)

            if shop is not None:
                print(f"  [PASS] Vendor shop created with size {vendor_size.size_name}")
                return True
            else:
                print("  [FAIL] Vendor shop creation failed")
                return False

        except Exception as e:
            print(f"  [FAIL] Vendor encounter compatibility failed: {e}")
            return False

    def test_shop_size_enum_values(self):
        """Test that all ShopSize enum values work"""
        print("\n[TEST 3] ShopSize Enum Values")

        try:
            sizes = [ShopSize.SMALL, ShopSize.MEDIUM, ShopSize.LARGE]

            for size in sizes:
                assert hasattr(size, 'size_name'), f"Missing size_name for {size}"
                assert hasattr(size, 'gold_limit'), f"Missing gold_limit for {size}"
                assert hasattr(size, 'base_items'), f"Missing base_items for {size}"
                assert hasattr(size, 'dice_count'), f"Missing dice_count for {size}"

            print(f"  [PASS] All {len(sizes)} ShopSize enum values valid")
            return True

        except AssertionError as e:
            print(f"  [FAIL] ShopSize enum validation failed: {e}")
            return False
        except Exception as e:
            print(f"  [FAIL] Unexpected error: {e}")
            return False

    def run_all_tests(self):
        print("\n" + "="*60)
        print("SHOP INTEGRATION TEST")
        print("="*60)

        test1 = self.test_shop_interface_signature()
        test2 = self.test_vendor_encounter_compatibility()
        test3 = self.test_shop_size_enum_values()

        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"ShopInterface Instantiation: {'PASS' if test1 else 'FAIL'}")
        print(f"Vendor Encounter Compatibility: {'PASS' if test2 else 'FAIL'}")
        print(f"ShopSize Enum Values: {'PASS' if test3 else 'FAIL'}")

        all_passed = test1 and test2 and test3

        print("\n" + "="*60)
        if all_passed:
            print("ALL TESTS PASSED [OK]")
        else:
            print("SOME TESTS FAILED [ERROR]")
        print("="*60 + "\n")

        return all_passed


if __name__ == '__main__':
    tester = ShopIntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)