#!/usr/bin/env python3
"""
Test imports without GUI to check for syntax errors
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing PyQt6 import...")
try:
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
    from PyQt6.QtCore import Qt
    print("[OK] PyQt6 imports successful")
except ImportError as e:
    print(f"[FAIL] PyQt6 import failed: {e}")
    sys.exit(1)

print("Testing menu widget import...")
try:
    from menu.game_menu import GameMenu
    print("[OK] Menu widget import successful")
except Exception as e:
    print(f"[FAIL] Menu widget import failed: {e}")
    sys.exit(1)

print("Testing character sheet import...")
try:
    from character_sheet.character_panel import CharacterPanel
    print("[OK] Character sheet import successful")
except Exception as e:
    print(f"[FAIL] Character sheet import failed: {e}")
    sys.exit(1)

print("Testing encounter pane import...")
try:
    from encounter_pane.encounter_panel import EncounterPanel
    print("[OK] Encounter pane import successful")
except Exception as e:
    print(f"[FAIL] Encounter pane import failed: {e}")
    sys.exit(1)

print("Testing log panel import...")
try:
    from log.log_panel import LogPanel
    print("[OK] Log panel import successful")
except Exception as e:
    print(f"[FAIL] Log panel import failed: {e}")
    sys.exit(1)

print("Testing equipment panel import...")
try:
    from equipment_layout.equipment_panel import EquipmentPanel
    print("[OK] Equipment panel import successful")
except Exception as e:
    print(f"[FAIL] Equipment panel import failed: {e}")
    sys.exit(1)

print("Testing action panel import...")
try:
    from action_cards.action_panel import ActionPanel
    print("[OK] Action panel import successful")
except Exception as e:
    print(f"[FAIL] Action panel import failed: {e}")
    sys.exit(1)

print("\n[SUCCESS] All widget imports working!")
print("You can now run the UI tests:")
print("  python test_menu.py")
print("  python test_character_sheet.py")
print("  python test_full_ui.py")