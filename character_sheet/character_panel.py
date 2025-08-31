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
                            QGridLayout, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QParallelAnimationGroup
from typing import Optional, Dict, Any
from datetime import datetime


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
        self.header_frame.setFixedHeight(35)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 3, 8, 3)
        
        # Character name as title (will be updated with actual character name)
        self.char_name_title = QLabel("Character Name")
        self.char_name_title.setObjectName("charTitle")
        header_layout.addWidget(self.char_name_title)
        
        header_layout.addStretch()
        
        self.expand_btn = QPushButton("▼ Expand")
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.clicked.connect(self._toggle_expansion)
        # Apply styling directly to override global theme
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
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
        
        # === EXPERIENCE & PROGRESSION SECTION === Compact design
        self.xp_frame = QFrame()
        self.xp_frame.setObjectName("xpFrame")
        xp_layout = QVBoxLayout(self.xp_frame)
        xp_layout.setContentsMargins(8, 4, 8, 4)
        xp_layout.setSpacing(3)
        
        # Title
        xp_label = QLabel("Experience & Progression")
        xp_label.setObjectName("sectionTitle")
        xp_layout.addWidget(xp_label)
        
        # Current XP - single line
        current_xp_layout = QHBoxLayout()
        current_xp_layout.setContentsMargins(0, 0, 0, 0)
        current_xp_layout.setSpacing(5)
        
        current_xp_title = QLabel("Current XP:")
        current_xp_title.setObjectName("xpLabel")
        current_xp_layout.addWidget(current_xp_title)
        
        self.current_xp_value = QLabel("0")
        self.current_xp_value.setObjectName("xpValue")
        current_xp_layout.addWidget(self.current_xp_value)
        
        current_xp_layout.addStretch()
        
        xp_layout.addLayout(current_xp_layout)
        
        # Progress bar
        self.xp_progress_bar = QProgressBar()
        self.xp_progress_bar.setObjectName("xpProgressBar")
        self.xp_progress_bar.setTextVisible(False)
        self.xp_progress_bar.setFixedHeight(16)
        xp_layout.addWidget(self.xp_progress_bar)
        
        # XP needed - single line
        self.xp_needed_label = QLabel("XP needed for level 2: 300")
        self.xp_needed_label.setObjectName("xpNeededLabel")
        xp_layout.addWidget(self.xp_needed_label)
        
        # Level history (recent XP gains)
        self.xp_history_frame = QFrame()
        self.xp_history_frame.setObjectName("xpHistoryFrame")
        history_layout = QVBoxLayout(self.xp_history_frame)
        history_layout.setContentsMargins(8, 5, 8, 5)
        
        history_title = QLabel("Recent XP Gains")
        history_title.setObjectName("xpHistoryTitle")
        history_layout.addWidget(history_title)
        
        self.xp_history_list = QWidget()
        self.xp_history_layout = QVBoxLayout(self.xp_history_list)
        self.xp_history_layout.setContentsMargins(0, 0, 0, 0)
        self.xp_history_layout.setSpacing(2)
        
        # Add some placeholder entries
        self._add_xp_history_entry("Session start", 0)
        
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setObjectName("xpHistoryScroll")
        history_scroll.setWidget(self.xp_history_list)
        history_scroll.setMaximumHeight(120)
        
        history_layout.addWidget(history_scroll)
        # xp_layout.addWidget(self.xp_history_frame, 1)  # Removed bulky history section
        
        # === FEATURES & TRAITS SECTION ===
        self.features_frame = QFrame()
        self.features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(self.features_frame)
        features_layout.setContentsMargins(5, 5, 5, 5)
        
        features_label = QLabel("Features & Traits")
        features_label.setObjectName("sectionTitle")
        features_layout.addWidget(features_label)
        
        # Add weapon mastery selection section (Fighter only)
        self.weapon_mastery_frame = QFrame()
        mastery_layout = QVBoxLayout(self.weapon_mastery_frame)
        mastery_layout.setContentsMargins(5, 5, 5, 5)
        
        self.mastery_label = QLabel("Weapon Masteries")
        self.mastery_label.setObjectName("featSubtitle")
        mastery_layout.addWidget(self.mastery_label)
        
        # Create grid layout for mastery selections
        mastery_grid = QGridLayout()
        mastery_grid.setSpacing(10)
        
        # Weapon mastery options based on D&D 2024 rules
        self.weapon_masteries = [
            ("Cleave", "If you hit a creature, you can make a bonus action attack against another creature within reach."),
            ("Graze", "If you miss with an attack, you can deal damage equal to your ability modifier."),
            ("Nick", "When you make the Attack action with a light weapon, you can make a bonus action attack with another light weapon."),
            ("Push", "If you hit a creature, you can push it 10 feet away from you if it's no more than one size larger."),
            ("Sap", "If you hit a creature, it has disadvantage on its next attack roll before the start of your next turn."),
            ("Slow", "If you hit a creature, its speed is reduced by 10 feet until the start of your next turn."),
            ("Topple", "If you hit a creature, it must make a Constitution save or be knocked prone."),
            ("Vex", "If you hit a creature, you have advantage on your next attack roll against it before the end of your next turn.")
        ]
        
        self.mastery_checkboxes = []
        for i, (mastery, description) in enumerate(self.weapon_masteries):
            checkbox = QCheckBox(mastery)
            checkbox.setToolTip(description)
            checkbox.stateChanged.connect(lambda state, m=mastery: self._on_mastery_changed(m, state))
            mastery_grid.addWidget(checkbox, i // 2, i % 2)
            self.mastery_checkboxes.append(checkbox)
        
        mastery_layout.addLayout(mastery_grid)
        
        # Selected masteries display
        self.selected_masteries_label = QLabel("Selected: None")
        self.selected_masteries_label.setObjectName("featDescription")
        mastery_layout.addWidget(self.selected_masteries_label)
        
        features_layout.addWidget(self.weapon_mastery_frame)
        
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
        self.detail_layout.addWidget(self.xp_frame, 1)  # Replaced skills with XP section
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
    
    def _add_xp_history_entry(self, description: str, xp_gain: int):
        """Add an entry to the XP history list."""
        entry_frame = QFrame()
        entry_frame.setObjectName("xpHistoryEntry")
        entry_layout = QHBoxLayout(entry_frame)
        entry_layout.setContentsMargins(5, 3, 5, 3)
        
        desc_label = QLabel(description)
        desc_label.setObjectName("xpHistoryDesc")
        entry_layout.addWidget(desc_label)
        
        entry_layout.addStretch()
        
        if xp_gain > 0:
            xp_label = QLabel(f"+{xp_gain} XP")
            xp_label.setObjectName("xpHistoryGain")
        else:
            xp_label = QLabel("—")
            xp_label.setObjectName("xpHistoryNone")
        
        entry_layout.addWidget(xp_label)
        
        # Insert at the top of the history
        self.xp_history_layout.insertWidget(0, entry_frame)
        
        # Keep only the last 10 entries
        if self.xp_history_layout.count() > 10:
            old_item = self.xp_history_layout.takeAt(10)
            if old_item and old_item.widget():
                old_item.widget().deleteLater()
    
    def add_xp_gain(self, description: str, xp_gain: int):
        """Public method to add XP gain and update displays."""
        if xp_gain > 0:
            # Add to history
            self._add_xp_history_entry(description, xp_gain)
            
            # Update character data if available
            if self.character_data:
                old_xp = self.character_data.get('experience_points', 0)
                new_xp = old_xp + xp_gain
                self.character_data['experience_points'] = new_xp
                
                # Update XP displays
                self._update_xp_displays()
    
    def _update_xp_displays(self):
        """Update all XP-related displays."""
        if not self.character_data:
            return
        
        current_xp = self.character_data.get('experience_points', 0)
        current_level = self.character_data.get('level', 1)
        
        # D&D 5e XP thresholds
        xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
            100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]
        
        # Update current XP display
        self.current_xp_value.setText(f"{current_xp:,}")
        
        # Calculate progress to next level
        if current_level >= 20:
            # Max level
            self.xp_needed_label.setText("Maximum level reached!")
            self.xp_progress_bar.setValue(100)
        else:
            current_level_xp = xp_thresholds[current_level - 1] if current_level <= len(xp_thresholds) else 0
            next_level_xp = xp_thresholds[current_level] if current_level < len(xp_thresholds) else xp_thresholds[-1]
            
            xp_needed = next_level_xp - current_xp
            xp_progress = current_xp - current_level_xp
            xp_level_range = next_level_xp - current_level_xp
            
            if xp_needed <= 0:
                # Level up available!
                self.xp_needed_label.setText("LEVEL UP AVAILABLE!")
                self.xp_progress_bar.setValue(100)
            else:
                progress_percent = int((xp_progress / xp_level_range) * 100) if xp_level_range > 0 else 0
                self.xp_needed_label.setText(f"XP needed for level {current_level + 1}: {xp_needed:,}")
                self.xp_progress_bar.setValue(progress_percent)
    
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
        
        QFrame#abilitiesFrame, QFrame#secondaryFrame, QFrame#xpFrame,
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
            font-size: 12px;
            font-weight: normal !important;
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
            border-radius: 3px;
            padding: 4px 8px;
            font-size: 10px !important;
            font-weight: bold !important;
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
        
        /* XP Section Styles */
        QFrame#xpStatFrame, QFrame#xpProgressFrame, QFrame#xpHistoryFrame {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-radius: 4px;
            margin: 3px;
        }
        
        QLabel#xpLabel, QLabel#xpProgressTitle, QLabel#xpHistoryTitle {
            color: #cccccc;
            font-size: 12px;
            font-weight: bold;
        }
        
        QLabel#xpValue {
            color: #ffcc00;
            font-size: 16px;
            font-weight: bold;
        }
        
        QLabel#xpNeededLabel {
            color: #cccccc;
            font-size: 11px;
        }
        
        QProgressBar#xpProgressBar {
            border: 1px solid #404040;
            border-radius: 8px;
            background-color: #1a1a1a;
            text-align: center;
        }
        
        QProgressBar#xpProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 7px;
        }
        
        QFrame#xpHistoryEntry {
            background-color: #333333;
            border: 1px solid #404040;
            border-radius: 3px;
            margin: 1px;
        }
        
        QLabel#xpHistoryDesc {
            color: #cccccc;
            font-size: 10px;
        }
        
        QLabel#xpHistoryGain {
            color: #4CAF50;
            font-size: 10px;
            font-weight: bold;
        }
        
        QLabel#xpHistoryNone {
            color: #666666;
            font-size: 10px;
        }
        
        QScrollArea#xpHistoryScroll {
            background-color: transparent;
            border: none;
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
            self.expand_btn.setText("▲ Collapse")
            self.raise_()  # Bring to front to cover encounter pane
        else:
            # COLLAPSE: Hide detail panel and resize main widget
            self.detail_panel.setMinimumWidth(0)
            self.detail_panel.setMaximumWidth(0)
            self.setMinimumSize(648, 570)
            self.setMaximumSize(1296, 570)  # Allow future expansion
            self.expand_btn.setText("▼ Expand")
        
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
        self.detail_title.setText(f"Character Details - {name}")
        
        # Update XP displays
        self._update_xp_displays()
        
        # Load weapon masteries for Fighter characters
        self._load_weapon_masteries()
        
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
        current_hp = character_data.get('current_hit_points', character_data.get('hit_points_current', 0))
        max_hp = character_data.get('max_hit_points', character_data.get('hit_points_max', character_data.get('hit_points', 0)))
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
        
        # Skill calculations removed - skills are displayed in main view only
        
        # Update features and traits
        race_name = self.character_data.get('race_name', 'Unknown')
        class_name = self.character_data.get('class_name', 'Unknown') 
        level = self.character_data.get('level', 1)
        character_features = self.character_data.get('features', {})
        
        features_text = f"=== Class Features ({class_name}) ===\n"
        
        # Display actual class features
        if character_features:
            for feature_name, feature_data in character_features.items():
                features_text += f"• {feature_name} (Level {feature_data.get('level_gained', 1)})\n"
                if feature_data.get('type') in ['bonus_action', 'action', 'reaction']:
                    features_text += f"  {feature_data['type'].replace('_', ' ').title()}"
                    if feature_data.get('usage') != 'permanent':
                        features_text += f" • {feature_data.get('usage', 'unknown').replace('_', ' ').title()} Recharge"
                    features_text += "\n"
                features_text += f"  {feature_data.get('description', 'No description available.')}\n\n"
        else:
            features_text += f"• Level {level} class abilities and features\n"
            features_text += "• Features will appear here as character gains levels\n\n"
        
        features_text += f"=== Racial Traits ({race_name}) ===\n"
        features_text += "• Racial abilities and traits based on character race\n"
        features_text += "• Special resistances or bonuses\n\n"
        
        # Add weapon masteries if Fighter
        if class_name == 'Fighter' and self.character_data.get('weapon_masteries'):
            masteries = self.character_data.get('weapon_masteries', [])
            features_text += f"=== Weapon Masteries ===\n"
            for mastery in masteries:
                # Get description from our stored data
                mastery_desc = next((desc for name, desc in self.weapon_masteries if name == mastery), "Special weapon technique")
                features_text += f"• {mastery}: {mastery_desc}\n"
            features_text += "\n"
        
        features_text += "=== Background Features ===\n"
        if self.character_data.get('background_name'):
            features_text += f"• {self.character_data.get('background_name')} background benefits\n"
        features_text += "• Skill proficiencies\n"
        features_text += "• Equipment and tools\n"
        
        self.features_text.setPlainText(features_text)
        
        # Load weapon masteries for Fighter characters (ensure UI is visible)
        self._load_weapon_masteries()
        
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
        """Update HP display - database should already be updated by game engine."""
        # Update the UI display
        self.hp_widget.value_label.setText(f"{current_hp}/{max_hp}")
        
        if self.character_data:
            # Update local character data to reflect database state
            self.character_data['current_hit_points'] = current_hp
            self.character_data['hit_points_current'] = current_hp
            self.character_data['max_hit_points'] = max_hp
            self.character_data['hit_points_max'] = max_hp
            self.character_data['hit_points'] = max_hp  # Legacy field
            
            # Log the HP change
            self._log_hp_change(current_hp, max_hp)
    
    def _log_hp_change(self, current_hp: int, max_hp: int):
        """Log HP change to game log."""
        try:
            # Find the log panel in parent hierarchy
            parent = self.parent()
            while parent:
                if hasattr(parent, 'log_panel'):
                    character_name = self.character_data.get('name', 'Character')
                    parent.log_panel.log_combat(f"{character_name} HP: {current_hp}/{max_hp}")
                    break
                parent = parent.parent()
        except Exception as e:
            # Not critical if logging fails
            pass
    
    def is_expanded(self) -> bool:
        """Return current expansion state."""
        return self.expanded
    
    def _on_mastery_changed(self, mastery_name: str, state: int):
        """Handle weapon mastery checkbox changes - max 3 selections."""
        selected_masteries = self._get_selected_masteries()
        
        if state == 2:  # Checked
            if len(selected_masteries) >= 3:
                # Find the checkbox and uncheck it
                for checkbox in self.mastery_checkboxes:
                    if checkbox.text() == mastery_name:
                        checkbox.blockSignals(True)
                        checkbox.setChecked(False)
                        checkbox.blockSignals(False)
                        break
                return
            selected_masteries.append(mastery_name)
        else:  # Unchecked
            if mastery_name in selected_masteries:
                selected_masteries.remove(mastery_name)
        
        # Update display and character data
        self._update_masteries_display(selected_masteries)
        self._save_masteries_to_character(selected_masteries)
    
    def _get_selected_masteries(self) -> list:
        """Get list of currently selected weapon masteries."""
        selected = []
        for checkbox in self.mastery_checkboxes:
            if checkbox.isChecked():
                selected.append(checkbox.text())
        return selected
    
    def _update_masteries_display(self, selected_masteries: list):
        """Update the selected masteries display label."""
        if selected_masteries:
            self.selected_masteries_label.setText(f"Selected: {', '.join(selected_masteries)}")
        else:
            self.selected_masteries_label.setText("Selected: None")
    
    def _save_masteries_to_character(self, selected_masteries: list):
        """Save weapon masteries to character data and database."""
        if not self.character_data:
            return
        
        # Update local character data
        if 'weapon_masteries' not in self.character_data:
            self.character_data['weapon_masteries'] = []
        
        self.character_data['weapon_masteries'] = selected_masteries
        
        # Save to database through game engine
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'game_engine') and parent.game_engine.current_character:
                    # Update the current character object
                    parent.game_engine.current_character.weapon_masteries = selected_masteries
                    parent.game_engine.current_character.updated_at = datetime.now().isoformat()
                    
                    # Save to database
                    import asyncio
                    from core.database_indexeddb import indexeddb
                    asyncio.run(indexeddb.put('characters', parent.game_engine.current_character.to_dict(), parent.game_engine.current_character.id))
                    
                    # Log the change
                    parent.log_panel.log_info(f"Updated weapon masteries: {', '.join(selected_masteries) if selected_masteries else 'None'}")
                    break
                parent = parent.parent()
        except Exception as e:
            # Not critical if save fails, but log it
            print(f"Warning: Could not save weapon masteries to database: {e}")
    
    def _load_weapon_masteries(self):
        """Load and display weapon masteries from character data."""
        if not self.character_data:
            return
        
        # Only show weapon mastery section for Fighter class
        class_name = self.character_data.get('class_name', '')
        class_id = self.character_data.get('class_id', '')
        
        
        if class_name != 'Fighter' and class_id != 'Fighter':
            self.weapon_mastery_frame.hide()
            return
        
        self.weapon_mastery_frame.show()
        
        # Load saved masteries
        saved_masteries = self.character_data.get('weapon_masteries', [])
        
        # Update checkboxes
        for checkbox in self.mastery_checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(checkbox.text() in saved_masteries)
            checkbox.blockSignals(False)
        
        # Update display
        self._update_masteries_display(saved_masteries)