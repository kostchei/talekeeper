#!/usr/bin/env python3
"""
Test the GameMenu widget
Run this to see the menu widget in action
"""

import sys
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from menu.game_menu import GameMenu


class MenuTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaleKeeper - Menu Widget Test")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Create menu widget
        self.menu = GameMenu()
        layout.addWidget(self.menu)
        
        # Connect signals to test functions
        self.menu.create_character_requested.connect(lambda: print("Create Character clicked"))
        self.menu.load_game_requested.connect(lambda: print("Load Game clicked"))
        self.menu.save_and_exit_requested.connect(lambda: print("Save & Exit clicked"))
        self.menu.archive_character_requested.connect(lambda: print("Archive Character clicked"))
        self.menu.settings_requested.connect(lambda: print("Settings clicked"))
        self.menu.campaign_frame_requested.connect(lambda: print("Campaign Frame clicked"))
        
        # Test different states after 3 seconds
        QTimer.singleShot(3000, self.test_character_loaded)
    
    def test_character_loaded(self):
        """Test the character loaded state"""
        print("Testing character loaded state...")
        self.menu.update_game_info("Aragorn", 3)
        self.menu.set_character_loaded(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle('Fusion')
    
    window = MenuTestWindow()
    window.show()
    
    print("Menu Widget Test")
    print("================")
    print("- Click the menu toggle button to expand/collapse")
    print("- Try clicking the different menu options")
    print("- Watch console for signal outputs")
    print("- After 3 seconds, character will be 'loaded' and buttons will enable")
    
    sys.exit(app.exec())