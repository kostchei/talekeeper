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
from PyQt6.QtGui import QPixmap
from typing import Optional, Dict, Any
from datetime import datetime
import sqlite3
import os

# Import condition display widget
try:
    from ui.condition_display import ConditionDisplayWidget
except ImportError:
    ConditionDisplayWidget = None
    print("[CharacterPanel] Condition display not available")


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
        
        # Character portrait
        self.portrait_label = QLabel()
        self.portrait_label.setObjectName("characterPortrait")
        self.portrait_label.setFixedSize(30, 30)
        self.portrait_label.setStyleSheet("""
            QLabel#characterPortrait {
                border: 1px solid #666;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
        """)
        self.portrait_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.portrait_label.setText("📸")  # Default emoji
        header_layout.addWidget(self.portrait_label)
        
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
        
        
        self.features_text = QTextEdit()
        self.features_text.setObjectName("featuresText")
        self.features_text.setReadOnly(True)
        self.features_text.setPlainText("Racial traits, class features, and special abilities will appear here...")
        features_layout.addWidget(self.features_text, 1)
        
        # === PROFICIENCIES SECTION ===
        self.proficiencies_frame = QFrame()
        self.proficiencies_frame.setObjectName("proficienciesFrame")
        prof_layout = QVBoxLayout(self.proficiencies_frame)
        prof_layout.setContentsMargins(5, 5, 5, 5)
        
        prof_header = QLabel("Proficiencies")
        prof_header.setObjectName("sectionHeader")
        prof_layout.addWidget(prof_header)
        
        self.proficiencies_text = QTextEdit()
        self.proficiencies_text.setObjectName("proficienciesText")
        self.proficiencies_text.setReadOnly(True)
        self.proficiencies_text.setPlainText("Loading proficiencies...")
        self.proficiencies_text.setMaximumHeight(80)
        prof_layout.addWidget(self.proficiencies_text)
        
        # === SPELLS SECTION (if applicable) ===
        self.spells_frame = QFrame()
        self.spells_frame.setObjectName("spellsFrame")
        spells_layout = QVBoxLayout(self.spells_frame)
        spells_layout.setContentsMargins(5, 5, 5, 5)
        
        spells_label = QLabel("Spells & Abilities")
        spells_label.setObjectName("sectionTitle")
        spells_layout.addWidget(spells_label)
        
        # Spell slots display
        self.spell_slots_widget = QWidget()
        spell_slots_layout = QVBoxLayout(self.spell_slots_widget)
        spell_slots_layout.setContentsMargins(0, 0, 0, 0)
        spell_slots_layout.setSpacing(5)
        
        # Create spell slot level displays (1st through 9th level)
        self.spell_slot_displays = {}
        for level in range(1, 10):
            level_widget = self._create_spell_slot_level_widget(level)
            self.spell_slot_displays[level] = level_widget
            spell_slots_layout.addWidget(level_widget)
        
        # Warlock pact magic slots (separate)
        self.pact_magic_widget = self._create_pact_magic_widget()
        spell_slots_layout.addWidget(self.pact_magic_widget)
        
        spells_layout.addWidget(self.spell_slots_widget)
        
        # Spell description area
        self.spells_text = QTextEdit()
        self.spells_text.setObjectName("spellsText")
        self.spells_text.setReadOnly(True)
        self.spells_text.setPlainText("Known spells and cantrips will appear here...")
        self.spells_text.setMaximumHeight(100)
        spells_layout.addWidget(self.spells_text)
        
        # Add all sections to detail panel
        self.detail_layout.addWidget(self.detail_header)
        self.detail_layout.addWidget(self.xp_frame, 1)  # Replaced skills with XP section
        self.detail_layout.addWidget(self.proficiencies_frame, 1)
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
        
        # Proficiency indicator (default to circle for no proficiency)
        prof_label = QLabel('o')
        prof_label.setObjectName("proficiencyIndicator")
        prof_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        # Add condition display widget
        if ConditionDisplayWidget:
            self.conditions_widget = ConditionDisplayWidget(parent=self)
            stats_layout.addWidget(self.conditions_widget, 2, 0, 1, 2)  # Span both columns
        else:
            self.conditions_widget = None
        
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
    
    def _create_spell_slot_level_widget(self, level: int) -> QWidget:
        """Create a spell slot level display widget."""
        widget = QWidget()
        widget.setVisible(False)  # Hidden by default, shown only if character has slots
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Level label
        level_suffix = {1: "st", 2: "nd", 3: "rd"}.get(level, "th")
        level_label = QLabel(f"{level}{level_suffix} Level")
        level_label.setFixedWidth(80)
        level_label.setObjectName("spellSlotLevel")
        layout.addWidget(level_label)
        
        # Slot circles container
        slots_container = QWidget()
        slots_layout = QHBoxLayout(slots_container)
        slots_layout.setContentsMargins(0, 0, 0, 0)
        slots_layout.setSpacing(3)
        
        # Store references to slot circles for updating
        widget.slot_circles = []
        widget.slots_layout = slots_layout
        
        layout.addWidget(slots_container, 1)
        
        return widget
    
    def _create_pact_magic_widget(self) -> QWidget:
        """Create Warlock pact magic slots display."""
        widget = QWidget()
        widget.setVisible(False)  # Hidden by default, shown only for Warlocks
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Pact magic label
        pact_label = QLabel("Pact Magic")
        pact_label.setObjectName("pactMagicLabel")
        pact_label.setStyleSheet("color: #9932cc; font-weight: bold;")
        layout.addWidget(pact_label)
        
        # Slot level indicator
        self.pact_slot_level_label = QLabel("1st Level")
        self.pact_slot_level_label.setObjectName("pactSlotLevel")
        layout.addWidget(self.pact_slot_level_label)
        
        # Slot circles container
        pact_slots_container = QWidget()
        pact_slots_layout = QHBoxLayout(pact_slots_container)
        pact_slots_layout.setContentsMargins(0, 0, 0, 0)
        pact_slots_layout.setSpacing(3)
        
        widget.slot_circles = []
        widget.slots_layout = pact_slots_layout
        
        layout.addWidget(pact_slots_container, 1)
        
        return widget
    
    def _create_spell_slot_circle(self, used: bool = False) -> QWidget:
        """Create a single spell slot circle indicator."""
        circle = QLabel("●")
        circle.setFixedSize(16, 16)
        circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if used:
            circle.setStyleSheet("color: #444444; font-size: 14px;")  # Dark gray for used
            circle.setToolTip("Used spell slot")
        else:
            circle.setStyleSheet("color: #4a9eff; font-size: 14px;")  # Blue for available
            circle.setToolTip("Available spell slot")
        
        return circle
    
    def _update_spell_slots_display(self, character_data: Dict[str, Any]):
        """Update spell slot display based on character class and level."""
        if not character_data:
            return
            
        class_name = character_data.get('class_name', '')
        level = character_data.get('level', 1)
        
        # Hide all spell slot displays first
        for level_widget in self.spell_slot_displays.values():
            level_widget.setVisible(False)
        self.pact_magic_widget.setVisible(False)
        
        # D&D 2024 spell slot progressions
        spell_slots = self._get_spell_slots_for_class_level(class_name, level)
        
        if class_name == 'Warlock':
            # Warlock Pact Magic
            self._update_warlock_pact_slots(level, character_data)
        else:
            # Regular spellcasters
            self._update_regular_spell_slots(spell_slots, character_data)
    
    def _get_spell_slots_for_class_level(self, class_name: str, level: int) -> Dict[int, int]:
        """Get spell slots by level for a class/level combination."""
        # D&D 2024 spell slot tables
        
        # Full casters (Cleric, Wizard) - spell slots by level
        full_caster_table = {
            1: {1: 2},
            2: {1: 3},
            3: {1: 4, 2: 2},
            4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2},
            6: {1: 4, 2: 3, 3: 3},
            7: {1: 4, 2: 3, 3: 3, 4: 1},
            8: {1: 4, 2: 3, 3: 3, 4: 2},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
        }
        
        # Half casters (Paladin) - start at level 2, max 5th level spells
        half_caster_table = {
            2: {1: 2},
            3: {1: 3},
            4: {1: 3},
            5: {1: 4, 2: 2},
            6: {1: 4, 2: 2},
            7: {1: 4, 2: 3},
            8: {1: 4, 2: 3},
            9: {1: 4, 2: 3, 3: 2},
            10: {1: 4, 2: 3, 3: 2},
            11: {1: 4, 2: 3, 3: 3},
            12: {1: 4, 2: 3, 3: 3},
            13: {1: 4, 2: 3, 3: 3, 4: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 2},
            16: {1: 4, 2: 3, 3: 3, 4: 2},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        }
        
        if class_name in ['Cleric', 'Wizard']:
            return full_caster_table.get(level, {})
        elif class_name == 'Paladin':
            return half_caster_table.get(level, {})
        else:
            return {}
    
    def _update_regular_spell_slots(self, spell_slots: Dict[int, int], character_data: Dict[str, Any]):
        """Update regular spell slot displays."""
        spell_slots_current = character_data.get('spell_slots_current', {})
        
        for spell_level, max_slots in spell_slots.items():
            if spell_level in self.spell_slot_displays:
                level_widget = self.spell_slot_displays[spell_level]
                level_widget.setVisible(True)
                
                # Clear existing circles
                for circle in level_widget.slot_circles:
                    circle.setParent(None)
                level_widget.slot_circles.clear()
                
                # Add slot circles
                current_slots = spell_slots_current.get(str(spell_level), max_slots)
                for i in range(max_slots):
                    used = i >= current_slots
                    circle = self._create_spell_slot_circle(used)
                    level_widget.slot_circles.append(circle)
                    level_widget.slots_layout.addWidget(circle)
    
    def _update_warlock_pact_slots(self, level: int, character_data: Dict[str, Any]):
        """Update Warlock pact magic slot display."""
        # Warlock pact magic progression
        pact_slots_by_level = {
            1: (1, 1),   # (slot_count, slot_level)
            2: (2, 1),
            3: (2, 2),
            4: (2, 2),
            5: (2, 3),
            6: (2, 3),
            7: (2, 4),
            8: (2, 4),
            9: (2, 5),
            10: (2, 5),
            11: (3, 5),
            12: (3, 5),
            13: (3, 5),
            14: (3, 5),
            15: (3, 5),
            16: (3, 5),
            17: (4, 5),
            18: (4, 5),
            19: (4, 5),
            20: (4, 5),
        }
        
        if level in pact_slots_by_level:
            slot_count, slot_level = pact_slots_by_level[level]
            self.pact_magic_widget.setVisible(True)
            
            # Update slot level label
            level_suffix = {1: "st", 2: "nd", 3: "rd"}.get(slot_level, "th")
            self.pact_slot_level_label.setText(f"{slot_level}{level_suffix} Level")
            
            # Clear existing circles
            for circle in self.pact_magic_widget.slot_circles:
                circle.setParent(None)
            self.pact_magic_widget.slot_circles.clear()
            
            # Add pact slot circles - assume all available for now
            for i in range(slot_count):
                circle = self._create_spell_slot_circle(False)
                circle.setStyleSheet("color: #9932cc; font-size: 14px;")  # Purple for pact magic
                circle.setToolTip(f"Pact Magic slot ({slot_level}{level_suffix} level)")
                self.pact_magic_widget.slot_circles.append(circle)
                self.pact_magic_widget.slots_layout.addWidget(circle)
    
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

        # Always load feats and class features from database to ensure
        # only persisted data is displayed
        char_id = character_data.get('id')
        if char_id:
            feats, features = self._load_feats_and_features_from_db(char_id)
            self.character_data['feats'] = feats
            self.character_data['features'] = features
        else:
            self.character_data['feats'] = []
            self.character_data['features'] = {}

        # Update character name in title
        name = character_data.get('name', 'Unknown Character')
        level = character_data.get('level', 1)
        race = character_data.get('race_name', 'Unknown Race')
        char_class = character_data.get('class_name', 'Unknown Class')
        
        # Load character portrait
        self._load_character_portrait(name)
        
        # Check for subclass
        subclass_display = char_class
        subclass_id = None

        try:
            manager = SubclassManager()
            subclass_id = manager.get_character_subclass(character_data.get('id'), char_class.lower())
        except Exception as subclass_error:
            print(f"[CharacterPanel] Subclass lookup error: {subclass_error}")

        if not subclass_id:
            subclass_id = character_data.get('subclass_id')

        if subclass_id:
            try:
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM subclasses WHERE id = ?", (subclass_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    subclass_display = f"{char_class} ({row[0]})"
                conn.close()
            except Exception as subclass_error:
                print(f"[CharacterPanel] Could not load subclass name: {subclass_error}")

        self.char_name_title.setText(f"{name} - Level {level} {race} {subclass_display}")
        self.detail_title.setText(f"Character Details - {name}")
        
        # Update XP displays
        self._update_xp_displays()
        
        # Load weapon masteries for Fighter characters
        
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
        from services.proficiency_bonus import get_proficiency_bonus
        from services.proficiency_system import ProficiencySystem
        proficiency_bonus = get_proficiency_bonus(level)
        proficiency_system = ProficiencySystem()
        
        # Get character proficiencies
        character_id = character_data.get('id')
        char_proficiencies = proficiency_system.get_character_proficiencies(character_id) if character_id else {
            'skill': [], 'saving_throw': [], 'weapon': [], 'armor': [], 'tool': [], 'language': [], 'skill_expertise': []
        }
        skill_proficiencies = {name.lower() for name in char_proficiencies.get('skill', [])}
        expertise_skills = {name.lower() for name in char_proficiencies.get('skill_expertise', [])}

        for skill_name, skill_widget in self.skill_widgets.items():
            ability = skill_widget.ability
            ability_score = abilities.get(ability, 10)
            ability_mod = (ability_score - 10) // 2

            key = skill_name.lower()
            is_expertise = key in expertise_skills
            is_proficient = key in skill_proficiencies or is_expertise

            if is_expertise:
                skill_bonus = ability_mod + (proficiency_bonus * 2)
            elif is_proficient:
                skill_bonus = ability_mod + proficiency_bonus
            else:
                skill_bonus = ability_mod

            bonus_text = f"+{skill_bonus}" if skill_bonus >= 0 else str(skill_bonus)
            skill_widget.bonus_label.setText(bonus_text)
            skill_widget.is_proficient = is_proficient
            skill_widget.is_expertise = is_expertise

            if hasattr(skill_widget, 'prof_label'):
                if is_expertise:
                    indicator = '★'
                    color = '#2a1c10'
                elif is_proficient:
                    indicator = '●'
                    color = '#2a1c10'
                else:
                    indicator = '○'
                    color = '#695d52'

                skill_widget.prof_label.setText(indicator)
                skill_widget.prof_label.setStyleSheet(f"color: {color}; font-size: 11px;")

        # Update saving throws
        save_proficiencies = char_proficiencies.get('saving_throw', [])
        
        # Map short ability names to full names for proficiency lookup
        ability_name_map = {
            'STR': 'strength',
            'DEX': 'dexterity', 
            'CON': 'constitution',
            'INT': 'intelligence',
            'WIS': 'wisdom',
            'CHA': 'charisma'
        }
        
        for ability_name, saving_throw_widget in self.saving_throw_widgets.items():
            ability_score = abilities.get(ability_name, 10)
            ability_mod = (ability_score - 10) // 2
            
            # Check for saving throw proficiency using new proficiency system
            full_ability_name = ability_name_map.get(ability_name, ability_name.lower())
            is_proficient = full_ability_name in [save.lower() for save in save_proficiencies]
            
            save_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)
            bonus_text = f"+{save_bonus}" if save_bonus >= 0 else str(save_bonus)
            saving_throw_widget.bonus_label.setText(bonus_text)
            
            # Update diamond indicator for proficiency
            if hasattr(saving_throw_widget, 'diamond'):
                saving_throw_widget.diamond.setVisible(is_proficient)
        
        # Update spell slots display
        self._update_spell_slots_display(character_data)
        
        # Update detailed panel data
        self._update_detail_panel()

        # Update condition display
        self._update_conditions(character_data)

        # Character data loaded successfully

    def _load_character_portrait(self, character_name: str):
        """Load character portrait from data/images/characters directory."""
        try:
            # Get path to character images directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            characters_dir = os.path.join(project_root, "data", "images", "characters")
            
            # Create safe filename from character name
            import re
            safe_name = character_name.lower().replace(' ', '_').replace('-', '_')
            safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)
            
            # Try common image extensions
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                image_path = os.path.join(characters_dir, f"{safe_name}{ext}")
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Scale to fit the portrait label
                        scaled_pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, 
                                                    Qt.TransformationMode.SmoothTransformation)
                        self.portrait_label.setPixmap(scaled_pixmap)
                        return
            
            # No image found - use default emoji
            self.portrait_label.clear()
            self.portrait_label.setText("📸")
            
        except Exception as e:
            print(f"Error loading character portrait: {e}")
            self.portrait_label.clear()
            self.portrait_label.setText("📸")

    def _load_feats_and_features_from_db(self, character_id: str):
        """Fetch feats and class features for a character from SQLite."""
        try:
            conn = sqlite3.connect("talekeeper.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT feat_name FROM character_feats WHERE character_id = ? ORDER BY level_acquired, feat_name",
                (character_id,)
            )
            feats = [row["feat_name"] for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT feature_name, feature_type, usage_type, level_gained, description
                FROM character_features
                WHERE character_id = ?
                """,
                (character_id,)
            )
            features = {}
            for row in cursor.fetchall():
                features[row["feature_name"]] = {
                    "type": row["feature_type"],
                    "usage": row["usage_type"],
                    "level_gained": row["level_gained"],
                    "description": row["description"],
                }

            conn.close()
            return feats, features
        except Exception:
            return [], {}
    
    def _get_feature_description(self, feature_name: str, class_name: str = "fighter") -> str:
        """Get feature description from feature definitions."""
        try:
            # Get all features for the class and search for matching name
            from core.feature_definitions import ClassFeatures
            all_features = []
            
            # Get features up to level 20 to search through all possible features
            for level in range(1, 21):
                level_features = ClassFeatures.get_feature_at_level(class_name, level)
                if level_features:
                    all_features.extend(level_features)
            
            # Find matching feature by name
            for feature in all_features:
                if feature.name == feature_name:
                    return feature.description
                    
        except Exception as e:
            print(f"Error getting feature description for {feature_name}: {e}")
        
        # Final fallback
        return "Class feature"

    def _update_detail_panel(self):
        """Update the detailed panel with character-specific information."""
        if not self.character_data:
            return
        
        # Get character details
        class_name = self.character_data.get('class_name', 'Unknown') 
        level = self.character_data.get('level', 1)
        race_name = self.character_data.get('race_name', 'Unknown')
        background_name = self.character_data.get('background_name', 'Unknown')
        char_id = self.character_data.get('id')
        
        
        # Build features text from actual database data
        features_text = ""
        
        # === CLASS FEATURES ===
        features_text += "=== CLASS FEATURES ===\n"
        
        # Get class features from database
        if char_id:
            try:
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()
                
                # Get all class features for this character from both tables
                cursor.execute("""
                    SELECT feature_name, description, usage_type 
                    FROM character_features 
                    WHERE character_id = ? 
                    ORDER BY level_gained, feature_name
                """, (char_id,))
                
                class_features = cursor.fetchall()
                
                # Also check the newer feature_states table
                if not class_features:
                    cursor.execute("""
                        SELECT feature_name, feature_type, '' as description
                        FROM feature_states 
                        WHERE character_id = ? 
                        ORDER BY feature_name
                    """, (char_id,))
                    
                    feature_states = cursor.fetchall()
                    if feature_states:
                        class_features = [(name, self._get_feature_description(name, class_name.lower()), ftype) 
                                        for name, ftype, _ in feature_states]
                
                if class_features:
                    for feature_name, description, usage_type in class_features:
                        features_text += f"• {feature_name}"
                        if usage_type and usage_type != 'permanent':
                            features_text += f" ({usage_type})"
                        features_text += "\n"
                        if description:
                            features_text += f"  {description[:100]}...\n" if len(description) > 100 else f"  {description}\n"
                
                conn.close()
            except Exception as e:
                print(f"Error loading class features: {e}")
        
        features_text += "\n"
        
        # === WEAPON MASTERY ===
        if char_id and class_name.lower() == 'fighter':
            try:
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT weapon_name, mastery_type 
                    FROM character_weapon_masteries 
                    WHERE character_id = ?
                """, (char_id,))
                
                masteries = cursor.fetchall()
                if masteries:
                    features_text += "=== WEAPON MASTERY ===\n"
                    for weapon_name, mastery_type in masteries:
                        features_text += f"• {weapon_name}: {mastery_type}\n"
                    features_text += "\n"
                
                conn.close()
            except Exception as e:
                print(f"Error loading weapon masteries: {e}")
        
        # === FEATS ===
        character_feats = self.character_data.get('feats', [])
        
        # Always try to get feat details from database if we have char_id
        if char_id:
            try:
                conn = sqlite3.connect("talekeeper.db")
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT cf.feat_name, cf.feat_source, f.category
                    FROM character_feats cf
                    LEFT JOIN feats f ON cf.feat_name = f.name
                    WHERE cf.character_id = ? 
                    ORDER BY cf.feat_source, cf.feat_name
                """, (char_id,))
                
                feat_data = cursor.fetchall()
                
                if feat_data:
                    features_text += "=== FEATS ===\n"
                    
                    # Group feats by source
                    background_feats = []
                    species_feats = []
                    class_feats = []
                    fighting_styles = []
                    other_feats = []
                    
                    for feat_name, feat_source, feat_category in feat_data:
                        # Check if it's a fighting style by category
                        if feat_category == 'fighting_style':
                            fighting_styles.append(feat_name)
                        elif feat_source == 'background':
                            background_feats.append(feat_name)
                        elif feat_source == 'species':
                            species_feats.append(feat_name)
                        elif feat_source in ['class', 'fighting_style']:
                            class_feats.append(feat_name)
                        else:
                            other_feats.append(feat_name)
                    
                    if background_feats:
                        features_text += f"• Background Origin Feat: {', '.join(background_feats)}\n"
                    if fighting_styles:
                        for style in fighting_styles:
                            features_text += f"• Fighting Style: {style}\n"
                    if class_feats:
                        for feat in class_feats:
                            features_text += f"• {feat}\n"
                    if species_feats:
                        features_text += f"• Species Feat: {', '.join(species_feats)}\n"
                    if other_feats:
                        for feat in other_feats:
                            features_text += f"• {feat}\n"
                    
                    features_text += "\n"
                
                conn.close()
            except Exception as e:
                print(f"Error loading feat details: {e}")
                if character_feats:
                    features_text += "=== FEATS ===\n"
                    for feat_name in character_feats:
                        features_text += f"• {feat_name}\n"
                    features_text += "\n"
        elif character_feats:
            # Fallback if no char_id but we have feats in memory
            features_text += "=== FEATS ===\n"
            for feat_name in character_feats:
                features_text += f"• {feat_name}\n"
            features_text += "\n"
        
        # === PROFICIENCIES ===
        if char_id:
            try:
                from services.proficiency_system import ProficiencySystem
                proficiency_system = ProficiencySystem()
                char_proficiencies = proficiency_system.get_character_proficiencies(char_id)
                
                prof_text = ""
                
                # Armor proficiencies
                if char_proficiencies.get('armor'):
                    armor_list = []
                    for armor in char_proficiencies['armor']:
                        if armor == 'shields':
                            armor_list.append('Shields')
                        else:
                            armor_list.append(f"{armor.title()} armor")
                    prof_text += f"Armor: {', '.join(armor_list)}\n"
                
                # Weapon proficiencies
                if char_proficiencies.get('weapon'):
                    weapon_list = []
                    for weapon in char_proficiencies['weapon']:
                        if weapon in ['simple', 'martial']:
                            weapon_list.append(f"{weapon.title()} weapons")
                        else:
                            weapon_list.append(weapon.title())
                    prof_text += f"Weapons: {', '.join(weapon_list)}\n"
                
                # Skill proficiencies (already shown in main panel)
                if char_proficiencies.get('skill'):
                    prof_text += f"Skills: {', '.join(char_proficiencies['skill'])}\n"
                
                # Tool proficiencies
                if char_proficiencies.get('tool'):
                    prof_text += f"Tools: {', '.join(char_proficiencies['tool'])}\n"
                
                # Language proficiencies
                if char_proficiencies.get('language'):
                    prof_text += f"Languages: {', '.join(char_proficiencies['language'])}\n"
                
                # Update proficiencies text widget
                if prof_text:
                    self.proficiencies_text.setPlainText(prof_text)
                else:
                    self.proficiencies_text.setPlainText("No proficiencies found")
                    
            except Exception as e:
                print(f"Error loading proficiencies: {e}")
                self.proficiencies_text.setPlainText("Error loading proficiencies")
        
        
        # Set the complete features text  
        self.features_text.setPlainText(features_text)
        
        # Load weapon masteries for Fighter characters (ensure UI is visible)
        
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

    def _update_conditions(self, character_data: Dict[str, Any]):
        """Update the condition display widget."""
        if not self.conditions_widget:
            return

        character_id = character_data.get('id')
        if character_id:
            # Set character ID and refresh conditions
            self.conditions_widget.set_character_id(character_id)
        else:
            # Clear conditions if no character ID
            self.conditions_widget.set_character_id(None)

    def refresh_conditions(self):
        """Force refresh of condition display (for external updates)."""
        if self.conditions_widget:
            self.conditions_widget.refresh_conditions()

    def clear_character_data(self):
        """Clear the character display."""
        self.character_data = None
        self.char_name_title.setText("Character Name")

        # Clear condition display
        if self.conditions_widget:
            self.conditions_widget.set_character_id(None)
        
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
    
    
    def update_ac(self, new_ac):
        """Update the AC display when equipment changes."""
        if hasattr(self, 'ac_widget') and self.ac_widget:
            self.ac_widget.value_label.setText(str(new_ac))
