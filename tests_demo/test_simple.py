#!/usr/bin/env python3
"""
Simple test to check if PyQt6 imports work
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

print("Creating simple test window...")
try:
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("TaleKeeper - Simple Test")
    window.setMinimumSize(400, 300)
    
    layout = QVBoxLayout()
    label = QLabel("PyQt6 is working!")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    window.setLayout(layout)
    
    window.show()
    print("[OK] Test window created successfully!")
    print("Close the window to continue...")
    
    sys.exit(app.exec())
except Exception as e:
    print(f"[FAIL] Window creation failed: {e}")
    sys.exit(1)