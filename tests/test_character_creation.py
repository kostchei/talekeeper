#test
#!/usr/bin/env python3
"""
Qt6 Test for Character Creation Workflow

Tests the character creation process to identify where it's failing.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt, QTimer
import traceback
import sqlite3


class CharacterCreationTester(QMainWindow):
    """Test window for character creation workflow"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Creation Tester")
        self.setGeometry(100, 100, 800, 600)
        
        # Test results
        self.test_results = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup test interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Character Creation Workflow Tester")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test buttons
        test1_btn = QPushButton("1. Test Basic Imports")
        test1_btn.clicked.connect(self.test_imports)
        layout.addWidget(test1_btn)
        
        test2_btn = QPushButton("2. Test Encounter Panel Creation")
        test2_btn.clicked.connect(self.test_encounter_panel)
        layout.addWidget(test2_btn)
        
        test3_btn = QPushButton("3. Test Character Creation Mode")
        test3_btn.clicked.connect(self.test_character_creation_mode)
        layout.addWidget(test3_btn)
        
        test4_btn = QPushButton("4. Test Full Character Creation Flow")
        test4_btn.clicked.connect(self.test_full_creation_flow)
        layout.addWidget(test4_btn)
        
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("font-family: monospace; background: #f5f5f5;")
        layout.addWidget(self.results_display)
    
    def log_test(self, test_name: str, success: bool, message: str = "", error: Exception = None):
        """Log test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        result = f"[{status}] {test_name}"
        
        if message:
            result += f": {message}"
        
        if error:
            result += f"\nError: {str(error)}"
            result += f"\nTraceback:\n{traceback.format_exc()}"
        
        result += "\n" + "-" * 60 + "\n"
        
        self.test_results.append(result)
        self.results_display.append(result)
        print(result)
    
    def clear_results(self):
        """Clear test results"""
        self.test_results.clear()
        self.results_display.clear()
    
    def test_imports(self):
        """Test 1: Basic imports"""
        try:
            # Test core imports
            from ui.main_window import MainWindow
            self.log_test("Import MainWindow", True, "Successfully imported")
            
            from encounter_pane.encounter_panel import EncounterPanel
            self.log_test("Import EncounterPanel", True, "Successfully imported")
            
            from encounter_pane.town_encounter import TownEncounterPanel
            self.log_test("Import TownEncounterPanel", True, "Successfully imported")
            
            from services.subclass_manager import SubclassManager
            self.log_test("Import SubclassManager", True, "Successfully imported")
            
        except Exception as e:
            self.log_test("Basic Imports", False, error=e)
    
    def test_encounter_panel(self):
        """Test 2: Create encounter panel with dummy data"""
        try:
            from encounter_pane.encounter_panel import EncounterPanel
            
            # Create dummy character data
            dummy_character = {
                'id': 'test-char-001',
                'name': 'TestChar',
                'level': 1,
                'class_id': 'fighter',
                'race_name': 'Human',
                'experience_points': 0
            }
            
            # Try to create encounter panel
            panel = EncounterPanel(dummy_character)
            self.log_test("Create EncounterPanel", True, f"Created with character: {dummy_character['name']}")
            
            # Test setting character creation mode
            panel.set_character_creation_mode()
            self.log_test("Set Character Creation Mode", True, "Mode set successfully")
            
        except Exception as e:
            self.log_test("Encounter Panel Creation", False, error=e)
    
    def test_character_creation_mode(self):
        """Test 3: Specifically test character creation mode activation"""
        try:
            from encounter_pane.encounter_panel import EncounterPanel
            from encounter_pane.town_encounter import TownEncounterPanel
            
            # Test with minimal character data (like during creation)
            minimal_character = {
                'id': '',
                'name': '',
                'level': 0,
                'class_id': '',
                'race_name': ''
            }
            
            # Try creating town encounter panel with minimal data
            town_panel = TownEncounterPanel(minimal_character)
            self.log_test("Create TownEncounterPanel with minimal data", True, "Panel created")
            
            # Try encounter panel
            encounter_panel = EncounterPanel(minimal_character)
            self.log_test("Create EncounterPanel with minimal data", True, "Panel created")
            
            # Try setting character creation mode
            encounter_panel.set_character_creation_mode()
            self.log_test("Character Creation Mode Activation", True, "Mode activated successfully")
            
        except Exception as e:
            self.log_test("Character Creation Mode Test", False, error=e)
    
    def test_full_creation_flow(self):
        """Test 4: Full character creation flow"""
        try:
            from ui.main_window import MainWindow
            
            # Create main window
            main_window = MainWindow()
            self.log_test("Create MainWindow", True, "Main window created")
            
            # Test character creation trigger
            main_window._start_character_creation()
            self.log_test("Start Character Creation", True, "Character creation started")
            
        except Exception as e:
            self.log_test("Full Character Creation Flow", False, error=e)


class CharacterCreationTestApp:
    """Test application for character creation"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = CharacterCreationTester()
    
    def run(self):
        """Run the test application"""
        self.window.show()
        return self.app.exec()


if __name__ == "__main__":
    # Change to project directory for proper imports and database access
    os.chdir(Path(__file__).parent.parent)
    
    # Run tests
    test_app = CharacterCreationTestApp()
    sys.exit(test_app.run())