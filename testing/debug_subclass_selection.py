#!/usr/bin/env python3
"""
Automated Qt6 test to debug subclass selection in training hall
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QEventLoop
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow

class SubclassSelectionDebugger:
    def __init__(self):
        self.app = None
        self.main_window = None
        
    def setup(self):
        """Initialize the application"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Wait for window to be ready
        self.wait(1000)
        print("[DEBUG] Main window created and shown")
        
    def wait(self, ms):
        """Wait for specified milliseconds"""
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec()
        
    def load_theron(self):
        """Load Theron character"""
        print("[DEBUG] Loading Theron...")
        
        # Find and click save slot for Theron (slot 1)
        menu_panel = self.main_window.menu
        if hasattr(menu_panel, 'save_slot_buttons'):
            slot_button = menu_panel.save_slot_buttons.get(1)  # Theron is in slot 1
            if slot_button:
                print("[DEBUG] Clicking Theron's save slot")
                QTest.mouseClick(slot_button, Qt.MouseButton.LeftButton)
                self.wait(2000)  # Wait for character to load
            else:
                print("[DEBUG] Save slot button not found")
        else:
            print("[DEBUG] Save slot buttons not accessible")
            
    def open_training_hall(self):
        """Navigate to training hall"""
        print("[DEBUG] Opening training hall...")
        
        # Click on encounter panel to show town
        encounter_panel = self.main_window.encounter_panel
        if hasattr(encounter_panel, 'show_town_encounter'):
            encounter_panel.show_town_encounter()
            self.wait(1000)
            print("[DEBUG] Town encounter shown")
            
        # Find and click training hall card
        if hasattr(encounter_panel, 'town_encounter') and encounter_panel.town_encounter:
            town = encounter_panel.town_encounter
            if hasattr(town, 'training_hall'):
                print("[DEBUG] Found training hall widget")
                training_hall = town.training_hall
                
                # Click the training hall card
                QTest.mouseClick(training_hall, Qt.MouseButton.LeftButton)
                self.wait(1000)
                print("[DEBUG] Training hall clicked")
                
                return training_hall
        
        print("[DEBUG] Training hall not found")
        return None
        
    def test_subclass_selection(self):
        """Test the subclass selection logic"""
        print("[DEBUG] Testing subclass selection...")
        
        training_hall = self.open_training_hall()
        if not training_hall:
            print("[FAIL] Could not access training hall")
            return False
            
        # Check if Fighter radio button exists and select it
        if hasattr(training_hall, 'class_button_group'):
            buttons = training_hall.class_button_group.buttons()
            fighter_button = None
            
            for button in buttons:
                if 'Fighter' in button.text():
                    fighter_button = button
                    break
                    
            if fighter_button:
                print(f"[DEBUG] Found Fighter button: {fighter_button.text()}")
                QTest.mouseClick(fighter_button, Qt.MouseButton.LeftButton)
                self.wait(500)
                print("[DEBUG] Fighter selected")
                
                # Check if subclass frame is now visible
                if hasattr(training_hall, 'subclass_frame'):
                    is_visible = training_hall.subclass_frame.isVisible()
                    print(f"[DEBUG] Subclass frame visible: {is_visible}")
                    
                    if is_visible:
                        print("[SUCCESS] Subclass selection UI appeared!")
                        
                        # Check subclass options
                        if hasattr(training_hall, 'subclass_button_group'):
                            subclass_buttons = training_hall.subclass_button_group.buttons()
                            print(f"[DEBUG] Found {len(subclass_buttons)} subclass options:")
                            for btn in subclass_buttons:
                                print(f"  - {btn.text()}")
                        
                        return True
                    else:
                        print("[FAIL] Subclass frame not visible")
                        
                        # Debug the values
                        if hasattr(training_hall, 'selected_class'):
                            print(f"[DEBUG] Selected class: {training_hall.selected_class}")
                        if hasattr(training_hall, 'is_subclass_level'):
                            print(f"[DEBUG] Is subclass level: {training_hall.is_subclass_level}")
                            
                        return False
                else:
                    print("[DEBUG] No subclass_frame attribute found")
            else:
                print("[DEBUG] Fighter button not found")
                for button in buttons:
                    print(f"  Available: {button.text()}")
        else:
            print("[DEBUG] No class_button_group found")
            
        return False
        
    def run_test(self):
        """Run the complete test"""
        print("=== Subclass Selection Debug Test ===")
        
        try:
            self.setup()
            self.load_theron()
            
            # Test subclass selection
            success = self.test_subclass_selection()
            
            if success:
                print("\n[SUCCESS] Subclass selection working correctly")
            else:
                print("\n[FAIL] Subclass selection not working")
                
            # Keep window open for manual inspection
            print("\n[INFO] Leaving window open for manual inspection...")
            print("[INFO] Close the window to end the test")
            
            return success
            
        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    debugger = SubclassSelectionDebugger()
    debugger.run_test()
    
    # Keep app running
    if debugger.app:
        debugger.app.exec()