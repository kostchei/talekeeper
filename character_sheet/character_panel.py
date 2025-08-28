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
        """Setup the basic character panel (always visible) with D&D layout."""
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(40)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Character name as title (will be updated with actual character name)
        self.char_name_title = QLabel("Character Name")
        self.char_name_title.setObjectName("charTitle")
        header_layout.addWidget(self.char_name_title)
        
        header_layout.addStretch()
        
        self.expand_btn = QPushButton("▶ Expand")
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.clicked.connect(self._toggle_expansion)
        header_layout.addWidget(self.expand_btn)
        
        # === D&D CHARACTER SHEET LAYOUT ===
        # Main scrollable area for the character sheet
        sheet_scroll = QScrollArea()
        sheet_scroll.setWidgetResizable(True)
        sheet_scroll.setObjectName("sheetScroll")
        
        sheet_widget = QWidget()
        sheet_layout = QVBoxLayout(sheet_widget)
        sheet_layout.setContentsMargins(5, 5, 5, 5)
        sheet_layout.setSpacing(8)
        
        # Storage for widgets
        self.ability_widgets = {}
        self.skill_widgets = {}
        self.saving_throw_widgets = {}
        
        # === ABILITY SCORE ROWS ===
        # Each row: [ABILITY BOX] [SAVING THROW] [SKILLS...]
        
        # STRENGTH ROW
        str_row = self._create_ability_row('STR', 'Strength', [('Athletics', 'STR')])
        sheet_layout.addWidget(str_row)
        
        # DEXTERITY ROW  
        dex_row = self._create_ability_row('DEX', 'Dexterity', [
            ('Acrobatics', 'DEX'), ('Sleight of Hand', 'DEX'), ('Stealth', 'DEX')
        ])
        sheet_layout.addWidget(dex_row)
        
        # CONSTITUTION ROW (no skills, add secondary stats here)
        con_row = self._create_ability_row_with_stats('CON', 'Constitution')
        sheet_layout.addWidget(con_row)
        
        # INTELLIGENCE ROW
        int_row = self._create_ability_row('INT', 'Intelligence', [
            ('Arcana', 'INT'), ('History', 'INT'), ('Investigation', 'INT'), 
            ('Nature', 'INT'), ('Religion', 'INT')
        ])
        sheet_layout.addWidget(int_row)
        
        # WISDOM ROW
        wis_row = self._create_ability_row('WIS', 'Wisdom', [
            ('Animal Handling', 'WIS'), ('Insight', 'WIS'), ('Medicine', 'WIS'), 
            ('Perception', 'WIS'), ('Survival', 'WIS')
        ])
        sheet_layout.addWidget(wis_row)
        
        # CHARISMA ROW
        cha_row = self._create_ability_row('CHA', 'Charisma', [
            ('Deception', 'CHA'), ('Intimidation', 'CHA'), ('Performance', 'CHA'), 
            ('Persuasion', 'CHA')
        ])
        sheet_layout.addWidget(cha_row)
        
        sheet_scroll.setWidget(sheet_widget)
        
        # Add to basic panel layout
        self.basic_layout.addWidget(self.header_frame)
        self.basic_layout.addWidget(sheet_scroll, 1)  # Take all remaining space
    
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
    
    def _create_ability_widget(self, short_name: str, full_name: str) -> QWidget:
        """Create an ability score widget like in D&D character sheet."""
        widget = QFrame()
        widget.setObjectName("abilityWidget")
        widget.setFixedSize(80, 90)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        
        # Ability name label
        name_label = QLabel(short_name)
        name_label.setObjectName("abilityName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Modifier (bonus) - displayed prominently
        modifier_label = QLabel("+0")
        modifier_label.setObjectName("abilityModifier")
        modifier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(modifier_label)
        
        # Score - displayed below modifier
        score_label = QLabel("10")
        score_label.setObjectName("abilityScore")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(score_label)
        
        # Store references for updating
        widget.modifier_label = modifier_label
        widget.score_label = score_label
        widget.ability_name = short_name
        
        return widget
    
    def _create_stat_widget(self, name: str, value: str) -> QWidget:
        """Create a secondary stat widget (AC, Init, HP, Speed)."""
        widget = QFrame()
        widget.setObjectName("statWidget")
        widget.setFixedSize(80, 60)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        
        # Stat name
        name_label = QLabel(name)
        name_label.setObjectName("statName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Stat value
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # Store reference for updating
        widget.value_label = value_label
        widget.stat_name = name
        
        return widget
    
    def _create_skill_widget(self, skill_name: str, ability: str) -> QWidget:
        """Create a skill widget with proficiency indicator and bonus."""
        widget = QFrame()
        widget.setObjectName("skillWidget")
        widget.setFixedHeight(25)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Proficiency indicator (circle or diamond)
        prof_label = QLabel("○")
        prof_label.setObjectName("proficiencyIndicator")
        prof_label.setFixedWidth(15)
        layout.addWidget(prof_label)
        
        # Skill name
        name_label = QLabel(skill_name)
        name_label.setObjectName("skillName")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Skill bonus
        bonus_label = QLabel("+0")
        bonus_label.setObjectName("skillBonus")
        bonus_label.setFixedWidth(25)
        bonus_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(bonus_label)
        
        # Store references for updating
        widget.prof_label = prof_label
        widget.bonus_label = bonus_label
        widget.skill_name = skill_name
        widget.ability = ability
        widget.is_proficient = False
        
        return widget
    
    def _create_ability_row(self, short_name: str, full_name: str, skills: list) -> QWidget:
        """Create a complete ability row: [ABILITY BOX] [SAVING THROW] [SKILLS...]"""
        row_frame = QFrame()
        row_frame.setObjectName("abilityRow")
        
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)
        
        # === ABILITY SCORE BOX ===
        ability_widget = self._create_ability_widget(short_name, full_name)
        self.ability_widgets[short_name] = ability_widget
        row_layout.addWidget(ability_widget)
        
        # === SAVING THROW ===
        saving_throw_widget = self._create_saving_throw_widget(short_name)
        self.saving_throw_widgets[short_name] = saving_throw_widget
        row_layout.addWidget(saving_throw_widget)
        
        # === SKILLS SECTION ===
        skills_container = QWidget()
        skills_layout = QVBoxLayout(skills_container)
        skills_layout.setContentsMargins(0, 0, 0, 0)
        skills_layout.setSpacing(2)
        
        for skill_name, ability in skills:
            skill_widget = self._create_skill_widget(skill_name, ability)
            self.skill_widgets[skill_name] = skill_widget
            skills_layout.addWidget(skill_widget)
        
        row_layout.addWidget(skills_container)
        row_layout.addStretch()  # Push everything to the left
        
        return row_frame
    
    def _create_ability_row_with_stats(self, short_name: str, full_name: str) -> QWidget:
        """Create Constitution row with secondary stats instead of skills."""
        row_frame = QFrame()
        row_frame.setObjectName("abilityRow")
        
        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(5, 5, 5, 5)
        row_layout.setSpacing(10)
        
        # === ABILITY SCORE BOX ===
        ability_widget = self._create_ability_widget(short_name, full_name)
        self.ability_widgets[short_name] = ability_widget
        row_layout.addWidget(ability_widget)
        
        # === SAVING THROW ===
        saving_throw_widget = self._create_saving_throw_widget(short_name)
        self.saving_throw_widgets[short_name] = saving_throw_widget
        row_layout.addWidget(saving_throw_widget)
        
        # === SECONDARY STATS (AC, INIT, HP, SPEED) ===
        stats_container = QWidget()
        stats_layout = QGridLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(8)
        
        # Create secondary stats
        self.ac_widget = self._create_stat_widget("AC", "10")
        self.init_widget = self._create_stat_widget("INIT", "+0")
        self.hp_widget = self._create_stat_widget("HP", "8/8")
        self.speed_widget = self._create_stat_widget("SPEED", "30 ft")
        
        stats_layout.addWidget(self.ac_widget, 0, 0)
        stats_layout.addWidget(self.init_widget, 0, 1)
        stats_layout.addWidget(self.hp_widget, 1, 0)
        stats_layout.addWidget(self.speed_widget, 1, 1)
        
        row_layout.addWidget(stats_container)
        row_layout.addStretch()
        
        return row_frame
    
    def _create_saving_throw_widget(self, ability_name: str) -> QWidget:
        """Create a saving throw widget with diamond indicator."""
        widget = QFrame()
        widget.setObjectName("savingThrowWidget")
        widget.setFixedHeight(25)
        widget.setMinimumWidth(120)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Diamond proficiency indicator
        prof_label = QLabel("◆")
        prof_label.setObjectName("savingThrowIndicator")
        prof_label.setFixedWidth(15)
        layout.addWidget(prof_label)
        
        # Saving throw label
        save_label = QLabel("SAVING THROWS")
        save_label.setObjectName("savingThrowLabel")
        layout.addWidget(save_label)
        
        layout.addStretch()
        
        # Saving throw bonus
        bonus_label = QLabel("+0")
        bonus_label.setObjectName("savingThrowBonus")
        bonus_label.setFixedWidth(25)
        bonus_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(bonus_label)
        
        # Store references
        widget.prof_label = prof_label
        widget.bonus_label = bonus_label
        widget.ability_name = ability_name
        widget.is_proficient = False
        
        return widget
    
    def _apply_styles(self):
        """No hardcoded styling - let main theme handle all colors."""
        # Disabled - theme system handles all styling now
        return
        style_sheet = """
        CharacterPanel {
            background-color: #202020;
        }
        
        QFrame#headerFrame {
            background-color: #2a2a2a;
        }
        
        QFrame#abilitiesFrame, QFrame#secondaryFrame, QFrame#skillsFrame,
        QFrame#featuresFrame, QFrame#spellsFrame {
            background-color: #252525;
            border: 1px solid #404040;
            border-radius: 4px;
        }
        
        QFrame#abilityWidget {
            background-color: #2a2a2a;
            border: 2px solid #404040;
            border-radius: 6px;
        }
        
        QLabel#abilityName {
            color: #ffffff;
            font-size: 10px;
            font-weight: bold;
        }
        
        QLabel#abilityModifier {
            color: #4a90e2;
            font-size: 18px;
            font-weight: bold;
        }
        
        QLabel#abilityScore {
            color: #cccccc;
            font-size: 14px;
        }
        
        QFrame#statWidget {
            background-color: #2a2a2a;
            border: 2px solid #404040;
            border-radius: 6px;
        }
        
        QLabel#statName {
            color: #ffffff;
            font-size: 9px;
            font-weight: bold;
        }
        
        QLabel#statValue {
            color: #4a90e2;
            font-size: 14px;
            font-weight: bold;
        }
        
        QFrame#skillWidget {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-radius: 3px;
            margin: 1px;
        }
        
        QLabel#proficiencyIndicator {
            color: #888888;
            font-size: 12px;
            font-weight: bold;
        }
        
        QLabel#skillName {
            color: #cccccc;
            font-size: 11px;
        }
        
        QLabel#skillBonus {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
        }
        
        QFrame#abilityRow {
            background-color: transparent;
            border-bottom: 1px solid #333333;
            margin: 2px 0px;
        }
        
        QFrame#savingThrowWidget {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-radius: 3px;
            margin: 1px;
        }
        
        QLabel#savingThrowIndicator {
            color: #888888;
            font-size: 12px;
            font-weight: bold;
        }
        
        QLabel#savingThrowLabel {
            color: #cccccc;
            font-size: 10px;
            font-weight: bold;
        }
        
        QLabel#savingThrowBonus {
            color: #ffffff;
            font-size: 11px;
            font-weight: bold;
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
        
        # Update character name in title
        name = character_data.get('name', 'Unknown Character')
        level = character_data.get('level', 1)
        race = character_data.get('race_name', 'Unknown Race')
        char_class = character_data.get('class_name', 'Unknown Class')
        
        self.char_name_title.setText(f"{name} - Level {level} {race} {char_class}")
        
        # Update ability scores with D&D layout (modifier prominent, score below)
        abilities = {
            'STR': character_data.get('strength', 10),
            'DEX': character_data.get('dexterity', 10), 
            'CON': character_data.get('constitution', 10),
            'INT': character_data.get('intelligence', 10),
            'WIS': character_data.get('wisdom', 10),
            'CHA': character_data.get('charisma', 10)
        }
        
        for ability_name, score in abilities.items():
            if ability_name in self.ability_widgets:
                widget = self.ability_widgets[ability_name]
                modifier = (score - 10) // 2
                modifier_text = f"+{modifier}" if modifier >= 0 else str(modifier)
                
                widget.modifier_label.setText(modifier_text)
                widget.score_label.setText(str(score))
        
        # Update secondary stats
        ac = character_data.get('armor_class', 10)
        self.ac_widget.value_label.setText(str(ac))
        
        # Initiative = DEX modifier
        dex_mod = (abilities['DEX'] - 10) // 2
        init_text = f"+{dex_mod}" if dex_mod >= 0 else str(dex_mod)
        self.init_widget.value_label.setText(init_text)
        
        # Hit Points
        current_hp = character_data.get('current_hit_points', 0)
        max_hp = character_data.get('hit_points', 0)
        self.hp_widget.value_label.setText(f"{current_hp}/{max_hp}")
        
        # Speed
        speed = character_data.get('speed', 30)
        self.speed_widget.value_label.setText(f"{speed} ft")
        
        # Update skills
        proficiency_bonus = 2 + ((level - 1) // 4)  # D&D 5e proficiency scaling
        
        for skill_name, skill_widget in self.skill_widgets.items():
            ability = skill_widget.ability
            ability_score = abilities.get(ability, 10)
            ability_mod = (ability_score - 10) // 2
            
            # For now, assume no proficiencies (could be enhanced later)
            skill_bonus = ability_mod
            bonus_text = f"+{skill_bonus}" if skill_bonus >= 0 else str(skill_bonus)
            skill_widget.bonus_label.setText(bonus_text)
        
        # Update saving throws
        for ability_name, saving_throw_widget in self.saving_throw_widgets.items():
            ability_score = abilities.get(ability_name, 10)
            ability_mod = (ability_score - 10) // 2
            
            # For now, assume no saving throw proficiencies
            save_bonus = ability_mod
            bonus_text = f"+{save_bonus}" if save_bonus >= 0 else str(save_bonus)
            saving_throw_widget.bonus_label.setText(bonus_text)
        
        # Update detailed panel data
        self._update_detail_panel()
        
        # Character data loaded successfully
    
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
    
    def clear_character_data(self):
        """Clear the character display."""
        self.character_data = None
        self.char_name_title.setText("Character Name")
        
        # Reset ability scores to defaults
        for ability_widget in self.ability_widgets.values():
            ability_widget.modifier_label.setText("+0")
            ability_widget.score_label.setText("10")
        
        # Reset secondary stats
        self.ac_widget.value_label.setText("10")
        self.init_widget.value_label.setText("+0")
        self.hp_widget.value_label.setText("8/8")
        self.speed_widget.value_label.setText("30 ft")
        
        # Reset skills
        for skill_widget in self.skill_widgets.values():
            skill_widget.bonus_label.setText("+0")
        
        # Reset saving throws
        for saving_throw_widget in self.saving_throw_widgets.values():
            saving_throw_widget.bonus_label.setText("+0")
    
    def update_hp(self, current_hp: int, max_hp: int):
        """Update HP display."""
        self.hp_widget.value_label.setText(f"{current_hp}/{max_hp}")
        
        if self.character_data:
            self.character_data['current_hit_points'] = current_hp
            self.character_data['hit_points'] = max_hp
            self._update_details_text()
    
    def is_expanded(self) -> bool:
        """Return current expansion state."""
        return self.expanded