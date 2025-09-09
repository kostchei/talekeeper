#!/usr/bin/env python3
"""
Qt6 Combat System Test
Tests the D&D 2024 combat system using the Qt6 testing framework
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from testing.test_framework import EncounterTester
from PyQt6.QtCore import QPoint
import time

class CombatSystemTester(EncounterTester):
    def __init__(self):
        super().__init__()
        
    def test_combat_flow(self):
        """Test complete combat flow with Qt6 interface"""
        self.log("=== COMBAT SYSTEM TEST ===")
        
        # Wait for application to fully load
        time.sleep(2)
        
        # Take screenshot of initial state
        self.take_screenshot("01_initial_state")
        
        # Navigate to encounter pane
        encounter_pane = self.find_widget_by_name("encounter_pane")
        if not encounter_pane:
            self.log("ERROR: Could not find encounter pane")
            return False
            
        # Click on encounter pane to focus it
        self.click_widget(encounter_pane)
        time.sleep(1)
        
        self.take_screenshot("02_encounter_pane_focused")
        
        # Look for monster buttons to target
        monster_buttons = []
        for child in encounter_pane.findChildren(object):
            if hasattr(child, 'objectName') and 'monster' in str(child.objectName()).lower():
                monster_buttons.append(child)
                
        if not monster_buttons:
            # Try to find any clickable elements in encounter pane
            clickables = encounter_pane.findChildren(object)
            for widget in clickables:
                if hasattr(widget, 'click') or 'button' in str(type(widget)).lower():
                    monster_buttons.append(widget)
        
        if monster_buttons:
            self.log(f"Found {len(monster_buttons)} potential monster targets")
            # Click the first monster to target it
            target_monster = monster_buttons[0]
            self.log(f"Targeting: {target_monster}")
            self.click_widget(target_monster)
            time.sleep(1)
            
            self.take_screenshot("03_monster_targeted")
        else:
            self.log("No monster buttons found, creating mock combat")
        
        # Find action panel
        action_panel = self.find_widget_by_name("action_panel")
        if not action_panel:
            self.log("ERROR: Could not find action panel")
            return False
            
        self.take_screenshot("04_action_panel_ready")
        
        # Look for attack action cards
        attack_buttons = []
        for child in action_panel.findChildren(object):
            widget_text = str(child)
            if 'attack' in widget_text.lower() or 'longsword' in widget_text.lower():
                attack_buttons.append(child)
                
        if attack_buttons:
            self.log(f"Found {len(attack_buttons)} attack options")
            
            # Click the first attack button
            attack_button = attack_buttons[0]
            self.log(f"Using attack: {attack_button}")
            self.click_widget(attack_button)
            time.sleep(2)  # Wait for combat to process
            
            self.take_screenshot("05_after_attack")
            
            # Check combat log for results
            self.check_combat_log()
            
        else:
            self.log("No attack buttons found")
            
        self.take_screenshot("06_final_state")
        
        return True
    
    def check_combat_log(self):
        """Check the combat log for D&D 2024 compliance"""
        # Find log panel
        log_panel = self.find_widget_by_name("log_panel")
        if not log_panel:
            self.log("Could not find log panel")
            return
            
        # Try to get log text
        log_text = ""
        if hasattr(log_panel, 'toPlainText'):
            log_text = log_panel.toPlainText()
        elif hasattr(log_panel, 'text'):
            log_text = log_panel.text()
            
        self.log("=== COMBAT LOG ANALYSIS ===")
        self.log(f"Log content length: {len(log_text)}")
        
        # Check for D&D 2024 combat markers
        markers = [
            "[DICE] ROLLING INITIATIVE",
            "Initiative:",
            "Initiative Order:",
            "It's not your turn!",
            "[COMBAT]",
            "Extra Attack",
            "Making 2 attack(s)"
        ]
        
        found_markers = []
        for marker in markers:
            if marker in log_text:
                found_markers.append(marker)
                
        self.log(f"D&D 2024 combat markers found: {len(found_markers)}/{len(markers)}")
        for marker in found_markers:
            self.log(f"  ✓ {marker}")
            
        missing_markers = [m for m in markers if m not in found_markers]
        for marker in missing_markers:
            self.log(f"  ✗ {marker}")

def main():
    """Run combat system test"""
    print("TaleKeeper D&D 2024 Combat System - Qt6 Test")
    print("=" * 50)
    
    tester = CombatSystemTester()
    
    try:
        if tester.setup():
            print("Qt6 application launched successfully")
            
            # Run combat test
            success = tester.test_combat_flow()
            
            if success:
                print("✓ Combat test completed")
            else:
                print("✗ Combat test failed")
                
            # Keep application open for manual inspection
            print("\nApplication will remain open for manual testing...")
            print("Close the application window when done.")
            tester.wait_for_close()
            
        else:
            print("✗ Failed to launch Qt6 application")
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        tester.cleanup()

if __name__ == '__main__':
    main()