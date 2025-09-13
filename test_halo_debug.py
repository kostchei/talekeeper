#!/usr/bin/env python3
"""
Self-contained test framework for Lucky/Inspiration halo system
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("=== Testing Imports ===")
    
    try:
        from ui.advantage_halo import AdvantageHalo, AdvantageResourceManager
        print("[OK] AdvantageHalo imported successfully")
    except Exception as e:
        print(f"[FAIL] AdvantageHalo import failed: {e}")
        return False
    
    try:
        from action_cards.action_panel import ActionCard, ActionPanel
        print("[OK] ActionCard imported successfully")
    except Exception as e:
        print(f"[FAIL] ActionCard import failed: {e}")
        return False
        
    return True

def test_resource_manager():
    """Test the AdvantageResourceManager with test data."""
    print("\n=== Testing AdvantageResourceManager ===")
    
    from ui.advantage_halo import AdvantageResourceManager
    
    # Test character with both resources
    test_char = {
        'name': 'TestChar',
        'lucky_uses_current': 3,
        'lucky_uses_max': 3,
        'inspiration_uses_current': 1,
        'inspiration_uses_max': 1
    }
    
    manager = AdvantageResourceManager(test_char)
    
    # Test has_resources
    if manager.has_resources():
        print("[OK] has_resources() returns True")
    else:
        print("[FAIL] has_resources() returns False")
        return False
        
    # Test primary resource (should be inspiration)
    primary = manager.get_primary_resource()
    if primary == "inspiration":
        print("[OK] Primary resource is inspiration (correct priority)")
    else:
        print(f"[FAIL] Primary resource is {primary}, expected inspiration")
        return False
        
    # Test resource consumption
    if manager.consume_resource("inspiration"):
        print("[OK] Inspiration consumed successfully")
        
        # Now primary should be lucky
        new_primary = manager.get_primary_resource()
        if new_primary == "lucky":
            print("[OK] Primary resource switched to lucky after inspiration consumed")
        else:
            print(f"[FAIL] Primary resource is {new_primary}, expected lucky")
            return False
    else:
        print("[FAIL] Failed to consume inspiration")
        return False
        
    return True

def test_halo_widget():
    """Test the AdvantageHalo widget."""
    print("\n=== Testing AdvantageHalo Widget ===")
    
    from PyQt6.QtWidgets import QApplication, QWidget
    from ui.advantage_halo import AdvantageHalo
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create parent widget
    parent = QWidget()
    parent.show()
    
    # Create halo
    halo = AdvantageHalo(parent)
    
    # Test update_resources with inspiration
    halo.update_resources(lucky_current=3, lucky_max=3, 
                         inspiration_current=1, inspiration_max=1)
    
    if halo.isVisible():
        print("[OK] Halo becomes visible with resources")
        
        if halo.resource_type == "inspiration":
            print("[OK] Halo shows inspiration (correct priority)")
        else:
            print(f"[FAIL] Halo shows {halo.resource_type}, expected inspiration")
            return False
            
        if "🔥" in halo.icon_label.text():
            print("[OK] Halo shows flame icon for inspiration")
        else:
            print(f"[FAIL] Halo shows '{halo.icon_label.text()}', expected flame")
            return False
    else:
        print("[FAIL] Halo not visible with resources")
        return False
        
    # Test with no resources
    halo.update_resources(lucky_current=0, lucky_max=3,
                         inspiration_current=0, inspiration_max=1)
    
    if not halo.isVisible():
        print("[OK] Halo hides when no resources")
    else:
        print("[FAIL] Halo still visible with no resources")
        return False
        
    parent.close()
    return True

def test_action_card_integration():
    """Test ActionCard halo integration."""
    print("\n=== Testing ActionCard Integration ===")
    
    from PyQt6.QtWidgets import QApplication
    from action_cards.action_panel import ActionCard, ActionType
    from ui.advantage_halo import AdvantageResourceManager
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create action card
    card = ActionCard(
        action_type=ActionType.ATTACK_MAIN_HAND,
        icon="⚔️",
        name="Attack",
        description="Make a weapon attack"
    )
    card.show()
    
    # Test that halo exists
    if hasattr(card, 'advantage_halo'):
        print("[OK] ActionCard has advantage_halo attribute")
    else:
        print("[FAIL] ActionCard missing advantage_halo attribute")
        return False
        
    if hasattr(card, 'resource_manager'):
        print("[OK] ActionCard has resource_manager attribute")
    else:
        print("[FAIL] ActionCard missing resource_manager attribute")
        return False
        
    # Test setting resource manager
    test_char = {
        'name': 'TestChar',
        'lucky_uses_current': 3,
        'lucky_uses_max': 3,
        'inspiration_uses_current': 1,
        'inspiration_uses_max': 1
    }
    
    manager = AdvantageResourceManager(test_char)
    card.set_resource_manager(manager)
    
    if card.resource_manager is not None:
        print("[OK] Resource manager set on ActionCard")
    else:
        print("[FAIL] Resource manager not set on ActionCard")
        return False
        
    # Test halo update method
    try:
        card._update_advantage_halo()
        print("[OK] _update_advantage_halo() called successfully")
    except Exception as e:
        print(f"[FAIL] _update_advantage_halo() failed: {e}")
        return False
        
    # Check if halo is visible after update
    if card.advantage_halo.isVisible():
        print("[OK] Halo visible after manual update")
    else:
        print("[FAIL] Halo not visible after manual update")
        return False
        
    card.close()
    return True

def test_mouse_events():
    """Test mouse event handling on ActionCard."""
    print("\n=== Testing Mouse Events ===")
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtTest import QTest
    from PyQt6.QtCore import Qt
    from action_cards.action_panel import ActionCard, ActionType
    from ui.advantage_halo import AdvantageResourceManager
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Create action card with resources
    card = ActionCard(
        action_type=ActionType.ATTACK_MAIN_HAND,
        icon="⚔️",
        name="Test Attack",
        description="Test attack action"
    )
    
    test_char = {
        'name': 'TestChar',
        'lucky_uses_current': 3,
        'lucky_uses_max': 3,
        'inspiration_uses_current': 1,
        'inspiration_uses_max': 1
    }
    
    manager = AdvantageResourceManager(test_char)
    card.set_resource_manager(manager)
    card.show()
    
    # Test mouse enter event
    print("Testing mouse enter event...")
    initial_visible = card.advantage_halo.isVisible()
    
    # Simulate mouse enter
    QTest.mouseMove(card, card.rect().center())
    QTest.qWait(100)  # Wait for event processing
    
    after_move_visible = card.advantage_halo.isVisible()
    
    if not initial_visible and after_move_visible:
        print("[OK] Halo appeared on mouse enter")
    elif after_move_visible:
        print("? Halo was already visible (may be expected)")
    else:
        print("[FAIL] Halo did not appear on mouse enter")
        return False
        
    # Test halo click
    if card.advantage_halo.isVisible():
        print("Testing halo click...")
        initial_count = manager.inspiration_current
        
        # Click on halo
        halo_center = card.advantage_halo.rect().center()
        QTest.mouseClick(card.advantage_halo, Qt.MouseButton.LeftButton, pos=halo_center)
        QTest.qWait(100)
        
        final_count = manager.inspiration_current
        if final_count == initial_count - 1:
            print("[OK] Resource consumed on halo click")
        else:
            print(f"[FAIL] Resource not consumed: {initial_count} -> {final_count}")
            return False
    
    card.close()
    return True

def run_all_tests():
    """Run all tests in sequence."""
    print("Lucky/Inspiration Halo Debug Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Resource Manager Test", test_resource_manager),
        ("Halo Widget Test", test_halo_widget),
        ("ActionCard Integration Test", test_action_card_integration),
        ("Mouse Events Test", test_mouse_events)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\nRunning {test_name}...")
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:<4} | {test_name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("[SUCCESS] All tests passed! Halo system should be working.")
    else:
        print("[ERROR] Some tests failed. Check the output above for issues.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    
    # Keep Qt app running briefly to see any visual components
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app:
        print("\nClosing in 2 seconds...")
        import time
        time.sleep(2)
    
    sys.exit(0 if success else 1)