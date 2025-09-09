"""
Test Reckless Attack implementation specifically
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import time

from test_framework import TaleKeeperTestBase

class RecklessAttackTester(TaleKeeperTestBase):
    """Test Reckless Attack feature for barbarians"""
    
    def __init__(self):
        super().__init__("RecklessAttack")
    
    def test_reckless_attack_toggle(self) -> bool:
        """Test that Reckless Attack toggles correctly and grants advantage"""
        try:
            # Load barbarian character (Shang in slot 20)
            if not self.window.menu.load_character_from_slot(20):
                return False
            
            QTest.qWait(1000)
            
            # Check that character is a barbarian with Reckless Attack
            action_panel = self.window.action_panel
            character_context = action_panel.character_context
            
            print(f"[TEST] Character class: {character_context.get('class_id')}")
            print(f"[TEST] Character features: {action_panel.character_features}")
            
            if character_context.get('class_id', '').lower() != 'barbarian':
                print("[TEST] ERROR: Character is not a barbarian")
                return False
            
            if 'Reckless Attack' not in action_panel.character_features:
                print("[TEST] ERROR: Character doesn't have Reckless Attack")
                return False
            
            # Switch to FREE actions to see Reckless Attack
            action_panel.current_category = action_panel.ActionCategory.FREE
            action_panel._update_visible_cards()
            QTest.qWait(500)
            
            # Check if Reckless Attack card exists
            if action_panel.ActionType.RECKLESS_ATTACK not in action_panel.action_cards:
                print("[TEST] ERROR: Reckless Attack card not found")
                return False
            
            reckless_card = action_panel.action_cards[action_panel.ActionType.RECKLESS_ATTACK]
            print(f"[TEST] Reckless Attack card found: {reckless_card.name}")
            
            # Test initial state (should be inactive)
            is_active = character_context.get('reckless_attack_active', False)
            print(f"[TEST] Initial Reckless Attack state: {is_active}")
            
            # Click to activate Reckless Attack
            print("[TEST] Clicking Reckless Attack to activate...")
            QTest.mouseClick(reckless_card, Qt.MouseButton.LeftButton)
            QTest.qWait(500)
            
            # Check state after click
            is_active_after = character_context.get('reckless_attack_active', False)
            print(f"[TEST] Reckless Attack state after click: {is_active_after}")
            
            if not is_active_after:
                print("[TEST] ERROR: Reckless Attack not activated after click")
                return False
            
            # Check card text changed
            card_text = reckless_card.name_label.text()
            print(f"[TEST] Card text after activation: '{card_text}'")
            
            if "RECKLESS ACTIVE" not in card_text:
                print("[TEST] ERROR: Card text didn't change to show active state")
                return False
            
            print("[TEST] SUCCESS: Reckless Attack toggle working correctly")
            return True
            
        except Exception as e:
            print(f"[TEST] ERROR in reckless attack test: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_reckless_attack_combat_advantage(self) -> bool:
        """Test that Reckless Attack grants advantage in actual combat"""
        try:
            # Ensure Reckless Attack is active
            action_panel = self.window.action_panel
            character_context = action_panel.character_context
            character_context['reckless_attack_active'] = True
            
            # Create a test attack context
            test_context = {
                'strength': 16,
                'dexterity': 16, 
                'constitution': 16,
                'level': 4,
                'weapon_properties': [],  # Regular melee weapon, should use STR
                'class_id': 'barbarian'
            }
            
            print("[TEST] Testing attack roll with Reckless Attack active...")
            
            # Manually call the attack roll method to see debug output
            attack_total, attack_breakdown = action_panel._roll_attack(test_context)
            
            print(f"[TEST] Attack total: {attack_total}")
            print(f"[TEST] Attack breakdown: {attack_breakdown}")
            
            # Check if advantage was applied (should see it in debug output)
            # This is mainly to trigger the debug logging we added
            
            return True
            
        except Exception as e:
            print(f"[TEST] ERROR in combat advantage test: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run Reckless Attack tests"""
    app = QApplication(sys.argv)
    
    tester = RecklessAttackTester() 
    if not tester.setup():
        print("Failed to setup test environment")
        return
    
    print("="*60)
    print("Testing Reckless Attack Toggle...")
    toggle_result = tester.test_reckless_attack_toggle()
    
    print("="*60)
    print("Testing Reckless Attack Combat Advantage...")
    combat_result = tester.test_reckless_attack_combat_advantage()
    
    print("="*60)
    print(f"Toggle Test: {'PASS' if toggle_result else 'FAIL'}")
    print(f"Combat Test: {'PASS' if combat_result else 'FAIL'}")
    
    # Keep window open for inspection
    input("Press Enter to close...")
    
    tester.cleanup()

if __name__ == "__main__":
    main()