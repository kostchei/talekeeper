#!/usr/bin/env python3
"""
Test triangle advantage functionality
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
import time

def test_triangle_advantage():
    """Test if clicking triangle applies advantage to next attack."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    QTest.qWait(1000)
    
    # Load character
    from core.game_engine_sqlite import GameEngineSQLite
    engine = GameEngineSQLite()
    character = engine.load_character_sync(1)
    
    if not character:
        print("[FAIL] No character loaded")
        return
    
    window._load_character_into_ui(character, "Test load")
    QTest.qWait(1000)
    
    # Find weapon card (Rapier)
    rapier_card = None
    for card in window.action_panel.action_cards.values():
        if hasattr(card, 'name') and 'rapier' in card.name.lower():
            rapier_card = card
            break
            
    if not rapier_card:
        print("[FAIL] Rapier card not found")
        return
        
    print(f"[INFO] Found rapier card: {rapier_card.name}")
    print(f"[INFO] Card has halo: {hasattr(rapier_card, 'advantage_halo')}")
    
    # Check if halo is available (has resources)
    if hasattr(rapier_card, 'resource_manager'):
        print(f"[INFO] Resource manager available: {rapier_card.resource_manager is not None}")
        if rapier_card.resource_manager:
            counts = rapier_card.resource_manager.get_resource_counts()
            print(f"[INFO] Resources: Lucky {counts['lucky_current']}/{counts['lucky_max']}, Inspiration {counts['inspiration_current']}/{counts['inspiration_max']}")
    
    # Check offensive flags before clicking
    print(f"[INFO] Before click - Inspiration offensive: {window.action_panel.inspiration_offensive_active}")
    print(f"[INFO] Before click - Lucky offensive: {window.action_panel.lucky_offensive_active}")
    
    # Hover over rapier card to show halo  
    print(f"[DEBUG] Manually calling _update_advantage_halo()")
    rapier_card._update_advantage_halo()
    QTest.mouseMove(rapier_card)
    QTest.qWait(500)
    
    # Check if halo is visible
    if hasattr(rapier_card, 'advantage_halo'):
        halo = rapier_card.advantage_halo
        print(f"[INFO] Halo visible after hover: {halo.isVisible()}")
        print(f"[INFO] Halo size: {halo.size()}")
        print(f"[INFO] Halo resource type: {halo.resource_type if hasattr(halo, 'resource_type') else 'None'}")
        
        # Always try to click even if not visible (might be a visibility detection issue)
        print(f"[INFO] Attempting to click triangle regardless of visibility...")
        # Click the halo
        halo_center = halo.rect().center()
        print(f"[INFO] Clicking halo at: {halo_center}")
        QTest.mouseClick(halo, Qt.MouseButton.LeftButton, pos=halo_center)
        QTest.qWait(500)
            
        # Check flags after clicking
        print(f"[INFO] After click - Inspiration offensive: {window.action_panel.inspiration_offensive_active}")
        print(f"[INFO] After click - Lucky offensive: {window.action_panel.lucky_offensive_active}")
        
        # Now test the actual attack roll system
        print(f"[INFO] Testing attack roll with advantage...")
        
        # Mock context for attack roll
        context = {
            'name': 'Rapier',
            'strength': character.get('strength', 10),
            'dexterity': character.get('dexterity', 10),
            'level': character.get('level', 1),
            'weapon_properties': ['finesse'],
            'target_monster_id': 'test_monster'
        }
        
        # Test the roll attack function
        total, breakdown = window.action_panel._roll_attack(context)
        print(f"[INFO] Attack roll total: {total}")
        print(f"[INFO] Attack breakdown: {breakdown}")
        
        # Check if advantage was applied
        roll_details = breakdown.get('roll_details', {})
        if 'advantage' in str(roll_details).lower():
            print("[SUCCESS] Advantage applied to attack roll!")
        else:
            print("[FAIL] Advantage not applied to attack roll")
        # Now test what happens after clicking
    else:
        print("[FAIL] Rapier card has no advantage_halo")
    
    # Close after delay
    QTimer.singleShot(3000, app.quit)
    app.exec()

if __name__ == "__main__":
    test_triangle_advantage()