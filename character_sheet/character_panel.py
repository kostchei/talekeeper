"""
Character Sheet Widget - Expandable character information panel

PyQt6 widget that displays character information with animation capability:
- Character stats, abilities, and details
- Expandable from 648px to 1296px width
- Smooth animation using QPropertyAnimation
- Integration ready for GameEngine character data

Designed to match ui_plan.md specifications:
- Default size: 648x972
- Expanded size: 1296x972  
- Animation duration: 400ms with OutCubic easing
- Dark theme styling
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QTextEdit, QScrollArea,
                            QGridLayout, QProgressBar)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from typing import Optional, Dict, Any


class CharacterPanel(QWidget):
    """
    Expandable character sheet widget with animation.
    
    Signals:
        expansion_changed: Emitted when panel expands/collapses (bool expanded)
        character_action_requested: Emitted when character action is requested (str action)
    """
    
    expansion_changed = pyqtSignal(bool)  # expanded state
    character_action_requested = pyqtSignal(str)  # action name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.expanded = False
        self.animation = None
        self.character_data = None
        
        # Set initial size (fits between menu and action cards)
        self.setFixedSize(648, 512)  # 726 - 214 = 512px available space
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the character panel UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Character title and expand button
        self.char_title = QLabel("Character Sheet")
        self.char_title.setObjectName("charTitle")
        header_layout.addWidget(self.char_title)
        
        header_layout.addStretch()
        
        self.expand_btn = QPushButton("▶ Expand")
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.clicked.connect(self._toggle_expansion)
        header_layout.addWidget(self.expand_btn)
        
        # === CHARACTER INFO SECTION ===
        self.info_frame = QFrame()
        self.info_frame.setObjectName("infoFrame")
        
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        
        # Basic character info
        self.char_name_label = QLabel("No Character Loaded")
        self.char_name_label.setObjectName("charNameLabel")
        self.char_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.char_name_label)
        
        self.char_details_label = QLabel("Level 1 | Unknown Race | Unknown Class")
        self.char_details_label.setObjectName("charDetailsLabel")
        self.char_details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.char_details_label)
        
        # === STATS SECTION ===
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("statsFrame")
        
        stats_layout = QVBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(5, 5, 5, 5)
        
        # Health bar
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP:"))
        self.hp_bar = QProgressBar()
        self.hp_bar.setObjectName("hpBar")
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        hp_layout.addWidget(self.hp_bar)
        self.hp_label = QLabel("100/100")
        self.hp_label.setObjectName("hpLabel")
        hp_layout.addWidget(self.hp_label)
        stats_layout.addLayout(hp_layout)
        
        # Ability scores grid
        self.abilities_frame = QFrame()
        self.abilities_frame.setObjectName("abilitiesFrame")
        abilities_layout = QGridLayout(self.abilities_frame)
        
        # Create ability score displays
        self.ability_labels = {}
        abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        
        for i, ability in enumerate(abilities):
            row = i // 2
            col = (i % 2) * 2
            
            # Ability name
            name_label = QLabel(ability)
            name_label.setObjectName("abilityName")
            abilities_layout.addWidget(name_label, row, col)
            
            # Ability value
            value_label = QLabel("10 (+0)")
            value_label.setObjectName("abilityValue")
            self.ability_labels[ability] = value_label
            abilities_layout.addWidget(value_label, row, col + 1)
        
        stats_layout.addWidget(self.abilities_frame)
        
        # === SCROLLABLE CONTENT AREA ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        
        # Content widget for scrollable area
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        
        # Detailed character information (expandable content)
        self.details_text = QTextEdit()
        self.details_text.setObjectName("detailsText")
        self.details_text.setReadOnly(True)
        self.details_text.setPlainText("Character details will appear here...")
        content_layout.addWidget(self.details_text)
        
        # Action buttons section
        self.actions_frame = QFrame()
        self.actions_frame.setObjectName("actionsFrame")
        actions_layout = QVBoxLayout(self.actions_frame)
        
        # Quick action buttons
        self.rest_btn = QPushButton("Take Rest")
        self.rest_btn.clicked.connect(lambda: self.character_action_requested.emit("rest"))
        actions_layout.addWidget(self.rest_btn)
        
        self.level_up_btn = QPushButton("Level Up")
        self.level_up_btn.clicked.connect(lambda: self.character_action_requested.emit("level_up"))
        self.level_up_btn.setEnabled(False)  # Disabled until XP threshold met
        actions_layout.addWidget(self.level_up_btn)
        
        content_layout.addWidget(self.actions_frame)
        content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        
        # Add sections to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.info_frame)
        self.main_layout.addWidget(self.stats_frame)
        self.main_layout.addWidget(self.scroll_area, 1)  # Take remaining space
    
    def _apply_styles(self):
        """Apply dark theme styling to character panel components."""
        style_sheet = """
        CharacterPanel {
            background-color: #202020;
        }
        
        QFrame#headerFrame {
            background-color: #2a2a2a;
        }
        
        QFrame#infoFrame, QFrame#statsFrame, QFrame#actionsFrame {
            background-color: #252525;
        }
        
        QFrame#abilitiesFrame {
            background-color: transparent;
            border: none;
        }
        
        QLabel#charTitle {
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel#charNameLabel {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 5px;
        }
        
        QLabel#charDetailsLabel {
            color: #cccccc;
            font-size: 12px;
            padding: 2px;
        }
        
        QLabel#hpLabel {
            color: #ffffff;
            font-size: 12px;
            min-width: 60px;
        }
        
        QLabel#abilityName {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            padding: 2px;
        }
        
        QLabel#abilityValue {
            color: #cccccc;
            font-size: 11px;
            padding: 2px;
        }
        
        QPushButton#expandButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        
        QPushButton#expandButton:hover {
            background-color: #505050;
        }
        
        QPushButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #303030;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
        }
        
        QProgressBar#hpBar {
            border: 1px solid #666666;
            border-radius: 3px;
            text-align: center;
            background-color: #1a1a1a;
        }
        
        QProgressBar#hpBar::chunk {
            background-color: #4a9;
            border-radius: 2px;
        }
        
        QTextEdit#detailsText {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
        }
        
        QScrollArea#scrollArea {
            background-color: transparent;
            border: none;
        }
        
        QScrollArea QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollArea QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollArea QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        """
        self.setStyleSheet(style_sheet)
    
    def _toggle_expansion(self):
        """Toggle the panel expansion with animation."""
        # Determine target width
        start_width = self.width()
        end_width = 1296 if not self.expanded else 648
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Set animation values
        current_geometry = self.geometry()
        self.animation.setStartValue(current_geometry)
        self.animation.setEndValue(QRect(
            current_geometry.x(),
            current_geometry.y(), 
            end_width,
            current_geometry.height()
        ))
        
        # Start animation
        self.animation.start()
        
        # Update state
        self.expanded = not self.expanded
        
        # Update button text
        if self.expanded:
            self.expand_btn.setText("◀ Collapse")
        else:
            self.expand_btn.setText("▶ Expand")
        
        # Emit signal
        self.expansion_changed.emit(self.expanded)
    
    def load_character_data(self, character_data: Dict[str, Any]):
        """Load character data into the panel display."""
        self.character_data = character_data
        
        # Update basic info
        name = character_data.get('name', 'Unknown Character')
        level = character_data.get('level', 1)
        race = character_data.get('race_name', 'Unknown Race')
        char_class = character_data.get('class_name', 'Unknown Class')
        
        self.char_name_label.setText(name)
        self.char_details_label.setText(f"Level {level} {race} {char_class}")
        
        # Update HP
        current_hp = character_data.get('current_hit_points', 100)
        max_hp = character_data.get('hit_points', 100)
        self.hp_bar.setMaximum(max_hp)
        self.hp_bar.setValue(current_hp)
        self.hp_label.setText(f"{current_hp}/{max_hp}")
        
        # Update ability scores
        abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        ability_names = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        
        for ability, display_name in zip(abilities, ability_names):
            score = character_data.get(ability, 10)
            modifier = (score - 10) // 2
            modifier_text = f"+{modifier}" if modifier >= 0 else str(modifier)
            self.ability_labels[display_name].setText(f"{score} ({modifier_text})")
        
        # Update detailed text
        self._update_details_text()
        
        # Check level up eligibility
        experience = character_data.get('experience_points', 0)
        next_level_xp = self._calculate_next_level_xp(level)
        self.level_up_btn.setEnabled(experience >= next_level_xp)
    
    def _update_details_text(self):
        """Update the detailed character information text."""
        if not self.character_data:
            self.details_text.setPlainText("No character data available.")
            return
        
        details = []
        details.append(f"Character: {self.character_data.get('name', 'Unknown')}")
        details.append(f"Level: {self.character_data.get('level', 1)}")
        details.append(f"Race: {self.character_data.get('race_name', 'Unknown')}")
        details.append(f"Class: {self.character_data.get('class_name', 'Unknown')}")
        details.append("")
        
        # Combat stats
        details.append("=== Combat Stats ===")
        details.append(f"Armor Class: {self.character_data.get('armor_class', 10)}")
        details.append(f"Hit Points: {self.character_data.get('current_hit_points', 0)}/{self.character_data.get('hit_points', 0)}")
        details.append(f"Speed: {self.character_data.get('speed', 30)} ft")
        details.append("")
        
        # Experience
        details.append("=== Progression ===")
        details.append(f"Experience: {self.character_data.get('experience_points', 0)} XP")
        
        level = self.character_data.get('level', 1)
        next_level_xp = self._calculate_next_level_xp(level)
        details.append(f"Next Level: {next_level_xp} XP")
        details.append("")
        
        # Background and other details can be added here
        if self.character_data.get('background_name'):
            details.append(f"Background: {self.character_data.get('background_name')}")
        
        self.details_text.setPlainText("\n".join(details))
    
    def _calculate_next_level_xp(self, current_level: int) -> int:
        """Calculate XP needed for next level (D&D 5e progression)."""
        xp_table = {
            1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000,
            6: 23000, 7: 34000, 8: 48000, 9: 64000, 10: 85000,
            11: 100000, 12: 120000, 13: 140000, 14: 165000, 15: 195000,
            16: 225000, 17: 265000, 18: 305000, 19: 355000, 20: 355000
        }
        return xp_table.get(current_level, 355000)
    
    def clear_character_data(self):
        """Clear the character display."""
        self.character_data = None
        self.char_name_label.setText("No Character Loaded")
        self.char_details_label.setText("Level 1 | Unknown Race | Unknown Class")
        self.hp_bar.setValue(100)
        self.hp_label.setText("100/100")
        
        for ability in self.ability_labels.values():
            ability.setText("10 (+0)")
        
        self.details_text.setPlainText("Character details will appear here...")
        self.level_up_btn.setEnabled(False)
    
    def update_hp(self, current_hp: int, max_hp: int):
        """Update HP display."""
        self.hp_bar.setMaximum(max_hp)
        self.hp_bar.setValue(current_hp)
        self.hp_label.setText(f"{current_hp}/{max_hp}")
        
        if self.character_data:
            self.character_data['current_hit_points'] = current_hp
            self.character_data['hit_points'] = max_hp
            self._update_details_text()
    
    def is_expanded(self) -> bool:
        """Return current expansion state."""
        return self.expanded