"""
Condition Display Widget - Compact status badges for character conditions

PyQt6 widget for displaying active character conditions as small badges:
- Compact 3-letter abbreviations (PAR, POI, FRI, etc.)
- Color-coded by severity (critical/moderate/minor)
- Hover tooltips with full condition details
- Auto-updates when conditions change
- Integrates with log panel for detailed descriptions
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from talekeeper.services.condition_manager import ConditionManager, ConditionType, ActiveCondition, ConditionEffects
except ImportError:
    # Graceful fallback if condition system not available
    ConditionManager = None
    ConditionType = None
    ActiveCondition = None
    ConditionEffects = None


class ConditionBadge(QLabel):
    """Individual condition badge with tooltip and styling."""

    # Color schemes for different condition severities
    SEVERITY_COLORS = {
        "critical": "#ff4444",    # Red - incapacitating conditions
        "moderate": "#ff8800",    # Orange - debilitating but not incapacitating
        "minor": "#ffaa00",       # Yellow - minor debuffs
        "special": "#8844ff"      # Purple - special conditions like exhaustion
    }

    def __init__(self, condition: ActiveCondition, parent=None):
        super().__init__(parent)
        self.condition = condition
        self._setup_badge()

    def _setup_badge(self):
        """Initialize the badge appearance and content."""
        # Set badge text (3-letter abbreviation)
        badge_text = self._get_badge_text()
        self.setText(badge_text)

        # Set styling
        self.setObjectName("conditionBadge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(28, 20)
        self.setMaximumSize(28, 20)

        # Set font
        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)
        self.setFont(font)

        # Apply severity-based styling
        severity = self._get_condition_severity()
        color = self.SEVERITY_COLORS.get(severity, "#666666")

        self.setStyleSheet(f"""
            QLabel#conditionBadge {{
                background-color: {color};
                color: white;
                border-radius: 3px;
                border: 1px solid {color};
                padding: 1px;
                margin: 1px;
            }}
            QLabel#conditionBadge:hover {{
                border: 1px solid white;
                background-color: {color}dd;
            }}
        """)

        # Set detailed tooltip
        tooltip = self._build_tooltip()
        self.setToolTip(tooltip)

    def _get_badge_text(self) -> str:
        """Get 3-letter abbreviation for condition."""
        condition_abbrevs = {
            ConditionType.BLINDED: "BLI",
            ConditionType.CHARMED: "CHA",
            ConditionType.DEAFENED: "DEA",
            ConditionType.EXHAUSTION: f"EX{self.condition.exhaustion_level}",  # EX1, EX2, etc.
            ConditionType.FRIGHTENED: "FRI",
            ConditionType.GRAPPLED: "GRA",
            ConditionType.INCAPACITATED: "INC",
            ConditionType.INVISIBLE: "INV",
            ConditionType.PARALYZED: "PAR",
            ConditionType.PETRIFIED: "PET",
            ConditionType.POISONED: "POI",
            ConditionType.PRONE: "PRO",
            ConditionType.RESTRAINED: "RES",
            ConditionType.STUNNED: "STU",
            ConditionType.UNCONSCIOUS: "UNC"
        }

        return condition_abbrevs.get(self.condition.condition_type, "???")

    def _get_condition_severity(self) -> str:
        """Determine severity level for color coding."""
        if not ConditionEffects:
            return "minor"

        # Critical: Incapacitating conditions
        if ConditionEffects.is_incapacitating(self.condition.condition_type):
            return "critical"

        # Special: Exhaustion (gets worse with levels)
        if self.condition.condition_type == ConditionType.EXHAUSTION:
            if self.condition.exhaustion_level >= 4:
                return "critical"
            elif self.condition.exhaustion_level >= 2:
                return "moderate"
            else:
                return "special"

        # Moderate: Significant debuffs
        moderate_conditions = [
            ConditionType.POISONED, ConditionType.FRIGHTENED,
            ConditionType.RESTRAINED, ConditionType.GRAPPLED
        ]
        if self.condition.condition_type in moderate_conditions:
            return "moderate"

        # Minor: Everything else
        return "minor"

    def _build_tooltip(self) -> str:
        """Build detailed HTML tooltip."""
        tooltip = f"<b>{self.condition.condition_type.value.title()}</b><br>"
        tooltip += f"<i>Source: {self.condition.source}</i><br><br>"

        # Duration info
        if self.condition.duration_remaining > 0:
            tooltip += f"⏱️ <b>{self.condition.duration_remaining} rounds remaining</b><br>"
        elif self.condition.duration_type == "save_ends" and self.condition.save_dc:
            tooltip += f"🎲 <b>Save DC {self.condition.save_dc} ({self.condition.save_ability.title()})</b><br>"
        elif self.condition.duration_type == "permanent":
            tooltip += "♾️ <b>Permanent</b><br>"
        else:
            tooltip += f"📝 <b>{self.condition.duration_type.replace('_', ' ').title()}</b><br>"

        # Add mechanical effects summary
        tooltip += "<br><u>Effects:</u><br>"
        tooltip += self._get_effects_summary()

        return tooltip

    def _get_effects_summary(self) -> str:
        """Get brief summary of condition's mechanical effects."""
        if not ConditionEffects:
            return "• See log for details"

        effects = ConditionEffects.get_effects(self.condition.condition_type)
        summary = []

        # Common effect translations
        if effects.get("attack_rolls") == "disadvantage":
            summary.append("• Disadvantage on attack rolls")
        if effects.get("movement_speed") == 0:
            summary.append("• Speed reduced to 0")
        if effects.get("no_actions"):
            summary.append("• Cannot take actions")
        if effects.get("auto_fail_sight_checks"):
            summary.append("• Auto-fail sight-based checks")
        if effects.get("auto_fail_hearing_checks"):
            summary.append("• Auto-fail hearing-based checks")
        if effects.get("cannot_attack_charmer"):
            summary.append("• Cannot attack charmer")
        if effects.get("d20_test_penalty"):
            level = self.condition.exhaustion_level or 1
            penalty = level * 2
            summary.append(f"• -{penalty} to all D20 tests")
        if effects.get("speed_reduction"):
            level = self.condition.exhaustion_level or 1
            reduction = level * 5
            summary.append(f"• Speed reduced by {reduction} ft")

        return "<br>".join(summary) if summary else "• See D&D rules for details"


class ConditionDisplayWidget(QWidget):
    """Widget displaying all active conditions as compact badges."""

    # Signal emitted when conditions change (for log integration)
    conditions_changed = pyqtSignal(list)  # List of ActiveCondition objects

    def __init__(self, character_id: str = None, db_path: str = "talekeeper.db", parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.db_path = db_path
        self.condition_manager = None
        self.badges = []

        # Initialize condition manager if available
        if ConditionManager:
            try:
                self.condition_manager = ConditionManager(db_path)
            except Exception as e:
                print(f"[ConditionDisplay] Could not initialize condition manager: {e}")

        self._setup_ui()

    def _setup_ui(self):
        """Initialize the widget layout."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)

        # Add status label for when no conditions
        self.no_conditions_label = QLabel("No active conditions")
        self.no_conditions_label.setObjectName("noConditionsLabel")
        self.no_conditions_label.setStyleSheet("""
            QLabel#noConditionsLabel {
                color: #888888;
                font-size: 10px;
                font-style: italic;
            }
        """)
        self.layout.addWidget(self.no_conditions_label)
        self.no_conditions_label.show()  # Explicitly show initially

        # Set widget properties
        self.setMaximumHeight(24)
        self.setMinimumHeight(24)

    def set_character_id(self, character_id: str):
        """Update the character ID and refresh display."""
        self.character_id = character_id
        self.refresh_conditions()

    def refresh_conditions(self):
        """Update the condition display from talekeeper.database."""
        if not self.character_id or not self.condition_manager:
            self._clear_display()
            return

        try:
            # Get current conditions
            conditions = self.condition_manager.get_active_conditions(self.character_id)
            self._update_display(conditions)

            # Emit signal for log integration
            self.conditions_changed.emit(conditions)

        except Exception as e:
            print(f"[ConditionDisplay] Error refreshing conditions: {e}")
            self._clear_display()

    def _update_display(self, conditions: List[ActiveCondition]):
        """Update the badge display with current conditions."""
        # Clear existing badges
        self._clear_badges()

        if not conditions:
            self.no_conditions_label.show()
            return

        self.no_conditions_label.hide()

        # Show up to 5 badges, then overflow indicator
        visible_conditions = conditions[:5]
        overflow_count = len(conditions) - len(visible_conditions)

        # Create badges for visible conditions
        for condition in visible_conditions:
            badge = ConditionBadge(condition, self)
            self.badges.append(badge)
            self.layout.addWidget(badge)

        # Add overflow indicator if needed
        if overflow_count > 0:
            overflow_label = QLabel(f"+{overflow_count}")
            overflow_label.setObjectName("overflowLabel")
            overflow_label.setStyleSheet("""
                QLabel#overflowLabel {
                    color: #888888;
                    font-size: 10px;
                    font-weight: bold;
                    margin-left: 2px;
                }
            """)
            overflow_label.setToolTip(f"{overflow_count} additional conditions - see log for details")
            self.layout.addWidget(overflow_label)
            self.badges.append(overflow_label)  # Track for cleanup

        # Add stretch to push badges to left
        self.layout.addStretch()

    def _clear_display(self):
        """Clear all condition badges."""
        self._clear_badges()
        self.no_conditions_label.show()

    def _clear_badges(self):
        """Remove all existing badge widgets."""
        for badge in self.badges:
            badge.setParent(None)
            badge.deleteLater()
        self.badges.clear()

    def add_test_conditions(self):
        """Add test conditions for UI development (debug only)."""
        if not self.condition_manager or not self.character_id:
            return

        # Add some test conditions
        test_conditions = [
            ActiveCondition(
                condition_type=ConditionType.POISONED,
                source="Test Poison",
                duration_type="rounds",
                duration_remaining=3
            ),
            ActiveCondition(
                condition_type=ConditionType.FRIGHTENED,
                source="Dragon Fear",
                duration_type="save_ends",
                save_dc=15,
                save_ability="wisdom"
            ),
            ActiveCondition(
                condition_type=ConditionType.EXHAUSTION,
                source="Forced March",
                duration_type="permanent",
                exhaustion_level=2
            )
        ]

        for condition in test_conditions:
            self.condition_manager.add_condition(self.character_id, condition)

        self.refresh_conditions()

    def get_condition_summary_for_log(self) -> str:
        """Get a detailed text summary for log panel."""
        if not self.character_id or not self.condition_manager:
            return ""

        try:
            conditions = self.condition_manager.get_active_conditions(self.character_id)
            if not conditions:
                return "No active conditions."

            summary_lines = ["Active conditions:"]
            for condition in conditions:
                line = f"• {condition.condition_type.value.title()}"

                if condition.condition_type == ConditionType.EXHAUSTION:
                    line += f" (Level {condition.exhaustion_level})"

                if condition.duration_remaining > 0:
                    line += f" - {condition.duration_remaining} rounds"
                elif condition.duration_type == "save_ends":
                    line += f" - Save DC {condition.save_dc} ({condition.save_ability})"

                line += f" (from {condition.source})"
                summary_lines.append(line)

            return "\n".join(summary_lines)

        except Exception as e:
            return f"Error reading conditions: {e}"