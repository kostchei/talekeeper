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
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QParallelAnimationGroup
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
        self.setMinimumSize(648, 570)  # Use minimum size instead of fixed
        self.setMaximumSize(1296, 570)  # Allow expansion to double width
        self.resize(648, 570)  # Set initial size
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Initialize the character panel UI components."""
        # Main horizontal layout for basic + detailed sections
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Basic character panel (always visible)
        self.basic_panel = QWidget()
        self.basic_panel.setFixedWidth(648)
        self.basic_layout = QVBoxLayout(self.basic_panel)
        self.basic_layout.setContentsMargins(0, 0, 0, 0)
        self.basic_layout.setSpacing(0)
        
        # Detailed expansion panel (hidden by default)
        self.detail_panel = QWidget()
        self.detail_panel.setMinimumWidth(0)
        self.detail_panel.setMaximumWidth(0)  # Start hidden
        self.detail_layout = QVBoxLayout(self.detail_panel)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_layout.setSpacing(0)
        
        # Add panels to main layout
        self.main_layout.addWidget(self.basic_panel)
        self.main_layout.addWidget(self.detail_panel)
        
        # === BASIC PANEL SETUP ===
        self._setup_basic_panel()
        
        # === DETAILED PANEL SETUP ===
        self._setup_detail_panel()
    
    def _setup_basic_panel(self):
        """Setup the basic character panel (always visible)."""
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
        
        # Add sections to basic panel layout
        self.basic_layout.addWidget(self.header_frame)
        self.basic_layout.addWidget(self.info_frame)
        self.basic_layout.addWidget(self.stats_frame)
        self.basic_layout.addWidget(self.scroll_area, 1)  # Take remaining space
    
    def _setup_detail_panel(self):
        """Setup the detailed character panel (shown when expanded)."""
        # === DETAILED HEADER ===
        self.detail_header = QFrame()
        self.detail_header.setObjectName("detailHeader")
        self.detail_header.setFixedHeight(80)
        
        detail_header_layout = QHBoxLayout(self.detail_header)
        detail_header_layout.setContentsMargins(10, 5, 10, 5)
        
        self.detail_title = QLabel("Character Details")
        self.detail_title.setObjectName("charTitle")
        detail_header_layout.addWidget(self.detail_title)
        detail_header_layout.addStretch()
        
        # === SKILLS SECTION ===
        self.skills_frame = QFrame()
        self.skills_frame.setObjectName("skillsFrame")
        skills_layout = QVBoxLayout(self.skills_frame)
        skills_layout.setContentsMargins(5, 5, 5, 5)
        
        skills_label = QLabel("Skills & Proficiencies")
        skills_label.setObjectName("sectionTitle")
        skills_layout.addWidget(skills_label)
        
        # Skills scroll area
        self.skills_scroll = QScrollArea()
        self.skills_scroll.setWidgetResizable(True)
        self.skills_scroll.setObjectName("skillsScroll")
        
        self.skills_widget = QWidget()
        self.skills_layout = QVBoxLayout(self.skills_widget)
        
        # Create skill entries (will be populated with character data)
        self.skill_labels = {}
        skills = [
            'Acrobatics (Dex)', 'Animal Handling (Wis)', 'Arcana (Int)', 'Athletics (Str)',
            'Deception (Cha)', 'History (Int)', 'Insight (Wis)', 'Intimidation (Cha)',
            'Investigation (Int)', 'Medicine (Wis)', 'Nature (Int)', 'Perception (Wis)',
            'Performance (Cha)', 'Persuasion (Cha)', 'Religion (Int)', 'Sleight of Hand (Dex)',
            'Stealth (Dex)', 'Survival (Wis)'
        ]
        
        for skill in skills:
            skill_frame = QFrame()
            skill_frame.setObjectName("skillEntry")
            skill_layout = QHBoxLayout(skill_frame)
            skill_layout.setContentsMargins(5, 2, 5, 2)
            
            skill_name = QLabel(skill)
            skill_name.setObjectName("skillName")
            skill_layout.addWidget(skill_name)
            
            skill_layout.addStretch()
            
            skill_bonus = QLabel("+0")
            skill_bonus.setObjectName("skillBonus")
            self.skill_labels[skill] = skill_bonus
            skill_layout.addWidget(skill_bonus)
            
            self.skills_layout.addWidget(skill_frame)
        
        self.skills_scroll.setWidget(self.skills_widget)
        skills_layout.addWidget(self.skills_scroll, 1)
        
        # === FEATURES & TRAITS SECTION ===
        self.features_frame = QFrame()
        self.features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(self.features_frame)
        features_layout.setContentsMargins(5, 5, 5, 5)
        
        features_label = QLabel("Features & Traits")
        features_label.setObjectName("sectionTitle")
        features_layout.addWidget(features_label)
        
        self.features_text = QTextEdit()
        self.features_text.setObjectName("featuresText")
        self.features_text.setReadOnly(True)
        self.features_text.setPlainText("Racial traits, class features, and special abilities will appear here...")
        features_layout.addWidget(self.features_text, 1)
        
        # === SPELLS SECTION (if applicable) ===
        self.spells_frame = QFrame()
        self.spells_frame.setObjectName("spellsFrame")
        spells_layout = QVBoxLayout(self.spells_frame)
        spells_layout.setContentsMargins(5, 5, 5, 5)
        
        spells_label = QLabel("Spells & Abilities")
        spells_label.setObjectName("sectionTitle")
        spells_layout.addWidget(spells_label)
        
        self.spells_text = QTextEdit()
        self.spells_text.setObjectName("spellsText")
        self.spells_text.setReadOnly(True)
        self.spells_text.setPlainText("Known spells and special abilities will appear here...")
        spells_layout.addWidget(self.spells_text, 1)
        
        # Add all sections to detail panel
        self.detail_layout.addWidget(self.detail_header)
        self.detail_layout.addWidget(self.skills_frame, 1)
        self.detail_layout.addWidget(self.features_frame, 1)
        self.detail_layout.addWidget(self.spells_frame, 1)
    
    def _apply_styles(self):
        """Apply dark theme styling to character panel components."""
        style_sheet = """
        CharacterPanel {
            background-color: #202020;
        }
        
        QFrame#headerFrame {
            background-color: #2a2a2a;
        }
        
        QFrame#infoFrame, QFrame#statsFrame, QFrame#actionsFrame,
        QFrame#skillsFrame, QFrame#featuresFrame, QFrame#spellsFrame {
            background-color: #252525;
        }
        
        QFrame#detailHeader {
            background-color: #2a2a2a;
        }
        
        QLabel#sectionTitle {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            padding: 5px;
        }
        
        QFrame#skillEntry {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-radius: 3px;
            margin: 1px;
        }
        
        QLabel#skillName {
            color: #cccccc;
            font-size: 11px;
            padding: 2px;
        }
        
        QLabel#skillBonus {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
            padding: 2px;
            min-width: 30px;
        }
        
        QTextEdit#featuresText, QTextEdit#spellsText {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            font-size: 11px;
        }
        
        QScrollArea#skillsScroll {
            background-color: transparent;
            border: none;
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
        """Toggle the panel expansion - simple and reliable approach."""
        # Toggle expansion state
        self.expanded = not self.expanded
        
        if self.expanded:
            # EXPAND: Show detail panel and resize main widget
            self.detail_panel.setMinimumWidth(648)
            self.detail_panel.setMaximumWidth(648)
            self.setMinimumSize(1296, 570)
            self.setMaximumSize(1296, 570)
            self.expand_btn.setText("◀ Collapse")
            self.raise_()  # Bring to front to cover encounter pane
        else:
            # COLLAPSE: Hide detail panel and resize main widget
            self.detail_panel.setMinimumWidth(0)
            self.detail_panel.setMaximumWidth(0)
            self.setMinimumSize(648, 570)
            self.setMaximumSize(1296, 570)  # Allow future expansion
            self.expand_btn.setText("▶ Expand")
        
        # Force immediate layout update
        self.updateGeometry()
        self.adjustSize()
        
        # Emit signal for parent to handle layout changes
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
        
        # Update detailed panel with character data
        self._update_detail_panel()
        
        # Check level up eligibility
        experience = character_data.get('experience_points', 0)
        next_level_xp = self._calculate_next_level_xp(level)
        self.level_up_btn.setEnabled(experience >= next_level_xp)
    
    def _update_detail_panel(self):
        """Update the detailed panel with character-specific information."""
        if not self.character_data:
            return
        
        # Update skill bonuses
        base_abilities = {
            'Acrobatics (Dex)': self.character_data.get('dexterity', 10),
            'Animal Handling (Wis)': self.character_data.get('wisdom', 10),
            'Arcana (Int)': self.character_data.get('intelligence', 10),
            'Athletics (Str)': self.character_data.get('strength', 10),
            'Deception (Cha)': self.character_data.get('charisma', 10),
            'History (Int)': self.character_data.get('intelligence', 10),
            'Insight (Wis)': self.character_data.get('wisdom', 10),
            'Intimidation (Cha)': self.character_data.get('charisma', 10),
            'Investigation (Int)': self.character_data.get('intelligence', 10),
            'Medicine (Wis)': self.character_data.get('wisdom', 10),
            'Nature (Int)': self.character_data.get('intelligence', 10),
            'Perception (Wis)': self.character_data.get('wisdom', 10),
            'Performance (Cha)': self.character_data.get('charisma', 10),
            'Persuasion (Cha)': self.character_data.get('charisma', 10),
            'Religion (Int)': self.character_data.get('intelligence', 10),
            'Sleight of Hand (Dex)': self.character_data.get('dexterity', 10),
            'Stealth (Dex)': self.character_data.get('dexterity', 10),
            'Survival (Wis)': self.character_data.get('wisdom', 10)
        }
        
        # Calculate and display skill bonuses
        proficiency_bonus = 2 + ((self.character_data.get('level', 1) - 1) // 4)  # D&D 5e proficiency scaling
        
        for skill, ability_score in base_abilities.items():
            ability_mod = (ability_score - 10) // 2
            # For now, assume no skill proficiencies (could be enhanced later)
            skill_bonus = ability_mod
            
            bonus_text = f"+{skill_bonus}" if skill_bonus >= 0 else str(skill_bonus)
            if skill in self.skill_labels:
                self.skill_labels[skill].setText(bonus_text)
        
        # Update features and traits
        race_name = self.character_data.get('race_name', 'Unknown')
        class_name = self.character_data.get('class_name', 'Unknown') 
        level = self.character_data.get('level', 1)
        
        features_text = f"=== Racial Traits ({race_name}) ===\n"
        features_text += "• Racial abilities and traits based on character race\n"
        features_text += "• Special resistances or bonuses\n\n"
        
        features_text += f"=== Class Features ({class_name}) ===\n"
        features_text += f"• Level {level} class abilities and features\n"
        features_text += "• Subclass specialization\n"
        features_text += "• Fighting style or specialization\n\n"
        
        features_text += "=== Background Features ===\n"
        if self.character_data.get('background_name'):
            features_text += f"• {self.character_data.get('background_name')} background benefits\n"
        features_text += "• Skill proficiencies\n"
        features_text += "• Equipment and tools\n"
        
        self.features_text.setPlainText(features_text)
        
        # Update spells section (basic implementation)
        spells_text = "=== Cantrips ===\n"
        spells_text += "• Known cantrips will appear here\n\n"
        
        spells_text += "=== Spells Known ===\n"
        spells_text += f"• Level 1-{(level + 1) // 2} spells available\n"
        spells_text += "• Spell slots and casting ability\n\n"
        
        spells_text += "=== Special Abilities ===\n"
        spells_text += "• Class-specific magical abilities\n"
        spells_text += "• Racial magical traits\n"
        
        self.spells_text.setPlainText(spells_text)
    
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