#!/usr/bin/env python3
"""
Qt6 GUI Test for Encounter Scene Description

Tests the encounter generation and scene description display functionality.
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_encounter_scene():
    """Test encounter generation and scene description display using Qt6 test framework."""
    
    print("=== Qt6 ENCOUNTER SCENE TEST ===")
    
    # Import after path setup
    from ui.main_window import MainWindow
    
    # Create application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Create main window
        print("[TEST] Creating main window...")
        window = MainWindow()
        window.show()
        
        # Wait for window to initialize
        QTest.qWait(1000)
        print("[TEST] Window initialized")
        
        # Find encounter panel
        encounter_panel = None
        if hasattr(window, 'encounter_pane'):
            encounter_panel = window.encounter_pane
            print(f"[TEST] Found encounter pane: {type(encounter_panel)}")
        else:
            print("[TEST] ERROR: No encounter pane found")
            return False
        
        # Check if scene_text exists
        if hasattr(encounter_panel, 'scene_text'):
            scene_text = encounter_panel.scene_text
            print(f"[TEST] Found scene_text widget: {type(scene_text)}")
            print(f"[TEST] Initial scene text: '{scene_text.toPlainText()[:100]}...'")
            
            # Check widget geometry and visibility
            geometry = scene_text.geometry()
            print(f"[TEST] Widget geometry: x={geometry.x()}, y={geometry.y()}, w={geometry.width()}, h={geometry.height()}")
            print(f"[TEST] Widget visible: {scene_text.isVisible()}")
            print(f"[TEST] Widget enabled: {scene_text.isEnabled()}")
            print(f"[TEST] Widget has focus: {scene_text.hasFocus()}")
            print(f"[TEST] Parent widget: {type(scene_text.parent())}")
            
            # Check size policies
            size_policy = scene_text.sizePolicy()
            print(f"[TEST] Horizontal policy: {size_policy.horizontalPolicy()}")
            print(f"[TEST] Vertical policy: {size_policy.verticalPolicy()}")
            
        else:
            print("[TEST] ERROR: No scene_text widget found")
            return False
        
        # Test manual scene description update
        print("\n[TEST] Testing manual scene description update...")
        test_description = "== TEST ENCOUNTER ==\nThis is a test description with multiple lines.\nIt should be visible!"
        encounter_panel.update_scene_description(test_description)
        
        # Wait for update
        QTest.qWait(500)
        
        # Check if text was set
        current_text = scene_text.toPlainText()
        print(f"[TEST] Text after manual update: '{current_text[:100]}...'")
        print(f"[TEST] Text length: {len(current_text)}")
        
        # Check styling
        style = scene_text.styleSheet()
        print(f"[TEST] Current stylesheet: '{style[:100]}...'")
        
        # Test encounter generation button
        print("\n[TEST] Testing encounter generation...")
        if hasattr(encounter_panel, 'generate_encounter_btn'):
            btn = encounter_panel.generate_encounter_btn
            print(f"[TEST] Found generate button: {btn.text()}")
            print(f"[TEST] Button enabled: {btn.isEnabled()}")
            
            # Click the button
            print("[TEST] Clicking generate encounter button...")
            QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
            
            # Wait for generation
            QTest.qWait(2000)
            
            # Check scene text after generation
            new_text = scene_text.toPlainText()
            print(f"[TEST] Text after encounter generation: '{new_text[:200]}...'")
            print(f"[TEST] Text changed: {new_text != current_text}")
            
            return new_text != current_text and len(new_text) > 0
            
        else:
            print("[TEST] ERROR: No generate encounter button found")
            return False
            
    except Exception as e:
        print(f"[TEST] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        if 'window' in locals():
            window.close()
        QTest.qWait(100)

def main():
    """Main test runner."""
    success = test_encounter_scene()
    
    if success:
        print("\n[PASS] Encounter scene test PASSED")
        return 0
    else:
        print("\n[FAIL] Encounter scene test FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)