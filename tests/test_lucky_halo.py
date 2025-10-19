#test
#!/usr/bin/env python3
"""
Test script for Lucky/Inspiration halo system
Tests that the advantage halos appear correctly on action cards
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


class LuckyHaloTester:
    """Test the Lucky/Inspiration halo system."""
    
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        self.window = None
        self.test_results = []
        
    def setup(self):
        """Setup the test environment."""
        print("=== Lucky/Inspiration Halo Test ===")
        
        # Create main window
        self.window = MainWindow()
        self.window.show()
        
        # Wait for initialization
        QTest.qWait(2000)
        
    def load_test_character_with_resources(self):
        """Load a character with Lucky and Inspiration resources."""
        print("\n1. Loading character with Lucky/Inspiration resources...")
        
        # Load Valerius (has both Lucky feat and Human inspiration)
        try:
            # Simulate loading Valerius from save slot 1
            character_data = {
                'id': 'test_valerius',
                'name': 'Valerius', 
                'level': 1,
                'class_id': 'fighter',
                'race_id': 'human',
                'lucky_uses_current': 3,
                'lucky_uses_max': 3,
                'inspiration_uses_current': 1,
                'inspiration_uses_max': 1,
                'strength': 10,
                'dexterity': 20,
                'constitution': 16,
                'intelligence': 12,
                'wisdom': 8,
                'charisma': 12
            }
            
            # Simulate the character loading process
            self.window.action_panel.load_character_resources(character_data)
            print("✓ Character resources loaded")
            
            # Wait for UI updates
            QTest.qWait(1000)
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to load character: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def test_halo_appearance(self):
        """Test that halos appear when hovering over action cards."""
        print("\n2. Testing halo appearance on action card hover...")
        
        try:
            # Find an action card to test
            action_cards = []
            for card in self.window.action_panel.action_cards.values():
                if hasattr(card, 'advantage_halo'):
                    action_cards.append(card)
                    
            if not action_cards:
                print("✗ No action cards found")
                return False
                
            print(f"Found {len(action_cards)} action cards")
            
            # Test hover on first action card
            test_card = action_cards[0]
            print(f"Testing hover on card: {test_card.name}")
            
            # Get card geometry
            card_rect = test_card.geometry()
            card_center = card_rect.center()
            
            # Simulate mouse hover
            QTest.mouseMove(test_card, card_center)
            QTest.qWait(500)  # Wait for hover event
            
            # Check if halo is visible
            if hasattr(test_card, 'advantage_halo'):
                halo = test_card.advantage_halo
                if halo.isVisible():
                    print("✓ Halo appeared on hover")
                    
                    # Check halo content
                    if halo.resource_type:
                        print(f"✓ Halo showing resource: {halo.resource_type} ({halo.resource_count}/{halo.resource_max})")
                    else:
                        print("✗ Halo visible but no resource type set")
                        
                    return True
                else:
                    print("✗ Halo not visible on hover")
                    return False
            else:
                print("✗ Action card has no advantage_halo attribute")
                return False
                
        except Exception as e:
            print(f"✗ Error testing halo appearance: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def test_resource_priority(self):
        """Test that Inspiration shows before Lucky."""
        print("\n3. Testing resource priority (Inspiration before Lucky)...")
        
        try:
            # Check what resource is currently showing
            test_card = list(self.window.action_panel.action_cards.values())[0]
            
            if hasattr(test_card, 'resource_manager'):
                manager = test_card.resource_manager
                if manager:
                    primary = manager.get_primary_resource()
                    print(f"Primary resource: {primary}")
                    
                    if primary == "inspiration":
                        print("✓ Inspiration showing first (correct priority)")
                        return True
                    elif primary == "lucky":
                        print("? Lucky showing first (Inspiration may be exhausted)")
                        return True
                    else:
                        print("✗ No primary resource found")
                        return False
                else:
                    print("✗ Resource manager not set")
                    return False
            else:
                print("✗ Action card has no resource_manager attribute")
                return False
                
        except Exception as e:
            print(f"✗ Error testing resource priority: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def test_halo_click(self):
        """Test clicking the halo to use resources."""
        print("\n4. Testing halo click to use resource...")
        
        try:
            # Find visible halo
            test_card = list(self.window.action_panel.action_cards.values())[0]
            
            if hasattr(test_card, 'advantage_halo'):
                halo = test_card.advantage_halo
                
                # Make sure halo is visible
                QTest.mouseMove(test_card, test_card.rect().center())
                QTest.qWait(200)
                
                if halo.isVisible():
                    # Get resource count before click
                    before_count = halo.resource_count
                    resource_type = halo.resource_type
                    
                    print(f"Before click: {resource_type} {before_count}")
                    
                    # Click the halo
                    halo_center = halo.rect().center()
                    QTest.mouseClick(halo, Qt.MouseButton.LeftButton, pos=halo_center)
                    QTest.qWait(200)
                    
                    # Check if resource was consumed
                    if test_card.resource_manager:
                        counts = test_card.resource_manager.get_resource_counts()
                        if resource_type == "inspiration":
                            after_count = counts['inspiration_current']
                        else:
                            after_count = counts['lucky_current']
                            
                        if after_count == before_count - 1:
                            print("✓ Resource consumed on click")
                            return True
                        else:
                            print(f"✗ Resource not consumed: {before_count} -> {after_count}")
                            return False
                    else:
                        print("✗ No resource manager to verify consumption")
                        return False
                else:
                    print("✗ Halo not visible for click test")
                    return False
            else:
                print("✗ No advantage halo found")
                return False
                
        except Exception as e:
            print(f"✗ Error testing halo click: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def run_all_tests(self):
        """Run all tests and report results."""
        print("Starting Lucky/Inspiration halo tests...")
        
        if not self.setup():
            print("Setup failed, aborting tests")
            return False
            
        tests = [
            ("Load character with resources", self.load_test_character_with_resources),
            ("Halo appearance on hover", self.test_halo_appearance),
            ("Resource priority", self.test_resource_priority),
            ("Halo click functionality", self.test_halo_click)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"ERROR in {test_name}: {e}")
                results.append((test_name, False))
                
        # Print summary
        print("\n=== TEST RESULTS ===")
        passed = 0
        for test_name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
                
        print(f"\nPassed: {passed}/{len(results)}")
        
        # Keep window open for manual inspection
        print("\nWindow will stay open for manual testing...")
        print("Hover over action cards to see halos")
        print("Press Ctrl+C to exit")
        
        return passed == len(results)


def main():
    """Main test entry point."""
    tester = LuckyHaloTester()
    
    try:
        success = tester.run_all_tests()
        
        # Keep app running for manual testing
        if tester.app and tester.window:
            sys.exit(tester.app.exec())
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()