"""
Test script for Monster Knowledge System

This demonstrates the monster knowledge check mechanics:
- DC = 10 + CR
- Information revealed based on margin of success
- Skill to monster type mapping
"""

import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from talekeeper.ui.monster_knowledge_label import MonsterKnowledgeLabel
from talekeeper.services.monster_knowledge import monster_knowledge_service


def get_sample_monsters():
    """Get some sample monsters from the database."""
    db_path = Path(__file__).parent / "talekeeper.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get a variety of monsters
    cursor.execute("""
        SELECT * FROM monsters
        WHERE challenge_rating IN ('1', '2', '3', '5', '1/4', '1/2')
        LIMIT 10
    """)

    monsters = []
    for row in cursor.fetchall():
        monster = dict(row)
        monsters.append(monster)

    conn.close()
    return monsters


class MonsterKnowledgeDemo(QMainWindow):
    """Demo window for monster knowledge system."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monster Knowledge System Demo")
        self.setMinimumSize(800, 600)

        # Sample character data
        self.character_data = {
            'id': 'test_char',
            'name': 'Test Wizard',
            'class_id': 'wizard',
            'level': 5,
            'intelligence': 16,  # +3 modifier
            'wisdom': 12,  # +1 modifier
            'charisma': 10,  # +0 modifier
        }

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Monster Knowledge System Demo")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Click on any monster name to make a knowledge check.\n"
            "The system will calculate DC based on CR and reveal information based on your roll.\n\n"
            "Your character: Level 5 Wizard (Int 16, Wis 12)"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #2b2b2b;")
        layout.addWidget(instructions)

        # Get monsters from database
        monsters = get_sample_monsters()

        if not monsters:
            error_label = QLabel("No monsters found in database. Please ensure talekeeper.db exists.")
            error_label.setStyleSheet("color: #f44336; padding: 20px;")
            layout.addWidget(error_label)
            return

        # Create monster labels
        monsters_widget = QWidget()
        monsters_layout = QVBoxLayout(monsters_widget)

        for monster in monsters:
            monster_row = QHBoxLayout()

            # Monster knowledge label
            label = MonsterKnowledgeLabel(monster, self.character_data, self)
            label.knowledge_checked.connect(
                lambda k, m=monster: self.on_knowledge_checked(m, k)
            )

            monster_row.addWidget(label)

            # CR and Type info
            cr = monster.get('challenge_rating', '0')
            monster_type = monster.get('type', 'Unknown')
            dc = monster_knowledge_service.calculate_dc(cr)
            skills = monster_knowledge_service.get_applicable_skills(monster_type)
            skills_text = ', '.join([s.title() for s in skills]) if skills else 'None'

            info_label = QLabel(f"CR {cr} (DC {dc}) - {monster_type.title()} - Skills: {skills_text}")
            info_label.setStyleSheet("color: #888; padding: 2px;")
            monster_row.addWidget(info_label)

            monster_row.addStretch()

            monsters_layout.addLayout(monster_row)

        layout.addWidget(monsters_widget)
        layout.addStretch()

        # Add example section
        self.add_example_section(layout)

    def add_example_section(self, layout):
        """Add an example showing different success levels."""
        example_widget = QWidget()
        example_layout = QVBoxLayout(example_widget)

        example_title = QLabel("Knowledge Check Examples:")
        example_title.setStyleSheet("font-weight: bold; margin-top: 20px;")
        example_layout.addWidget(example_title)

        examples = [
            ("DC Exactly", "Name + Type + CR"),
            ("DC +2", "Also adds Vulnerabilities/Resistances/Immunities"),
            ("DC +4", "Also adds AC and HP"),
            ("DC +6", "Also adds Special Abilities and Attacks"),
            ("DC +8", "Also adds all ability scores, senses, languages, etc."),
        ]

        for threshold, info in examples:
            example_label = QLabel(f"  • {threshold}: {info}")
            example_label.setStyleSheet("color: #aaa; margin-left: 20px;")
            example_layout.addWidget(example_label)

        layout.addWidget(example_widget)

    def on_knowledge_checked(self, monster, knowledge):
        """Handle knowledge check completion."""
        print(f"\n=== Knowledge Check Complete ===")
        print(f"Monster: {monster.get('name')}")
        print(f"DC: {knowledge.dc}")
        print(f"Success: {knowledge.success}")
        print(f"Margin: {knowledge.margin}")
        print(f"Revealed Info:")
        for category, value in knowledge.revealed_info:
            print(f"  {category}: {value}")


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)

    # Set dark theme
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #ddd;
        }
        QPushButton {
            background-color: #333;
            border: 1px solid #555;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #444;
        }
        QLabel {
            color: #ddd;
        }
    """)

    window = MonsterKnowledgeDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
