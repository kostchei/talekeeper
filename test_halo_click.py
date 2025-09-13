#!/usr/bin/env python3
"""
Test halo click activation
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

def test_halo_click():
    """Test if the halo can be clicked."""
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    # Load a character
    from core.game_engine_sqlite import GameEngineSQLite
    engine = GameEngineSQLite()
    character = engine.load_character_sync(1)
    
    if not character:
        print("[FAIL] No character loaded")
        return
    
    window._load_character_into_ui(character, "Test character load")
    QApplication.processEvents()
    
    # Find a weapon card
    weapon_cards = []
    for card in window.action_panel.action_cards.values():
        if hasattr(card, 'advantage_halo') and card.advantage_halo.isVisible():
            weapon_cards.append(card)
            
    if not weapon_cards:
        print("[FAIL] No weapon cards with visible halos found")
        return
        
    test_card = weapon_cards[0]
    halo = test_card.advantage_halo
    
    print(f"[INFO] Testing card: {test_card.name}")
    print(f"[INFO] Halo visible: {halo.isVisible()}")
    print(f"[INFO] Halo size: {halo.size()}")
    print(f"[INFO] Halo pos: {halo.pos()}")
    print(f"[INFO] Halo resource: {halo.resource_type}")
    print(f"[INFO] Halo cursor: {halo.cursor().shape()}")
    
    # Try clicking the halo
    halo_center = halo.rect().center()
    print(f"[INFO] Clicking halo at: {halo_center}")
    
    QTest.mouseClick(halo, Qt.MouseButton.LeftButton, pos=halo_center)
    QApplication.processEvents()
    
    print("[INFO] Click sent")
    
    # Close after delay
    QTimer.singleShot(2000, app.quit)
    app.exec()

if __name__ == "__main__":
    test_halo_click()