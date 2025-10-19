# core
# category: core
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
    ConditionManager = None
    ConditionType = None
    ActiveCondition = None
    ConditionEffects = None

try:
    from talekeeper.services.spell_effects_service import SpellEffectsService
except ImportError:
    SpellEffectsService = None


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


class SpellEffectBadge(QLabel):

    EFFECT_COLORS = {
        "ac_bonus": "#4488ff",
        "attack_bonus": "#ff8844",
        "attack_and_save_bonus": "#ff8844",
        "damage_bonus": "#ff4488",
        "damage_bonus_per_hit": "#ff4488",
        "temp_hp_per_turn": "#44ff88",
        "hp_maximum_increase": "#44ff88",
        "condition_immunity": "#8844ff",
        "default": "#888888"
    }

    def __init__(self, spell_name: str, effect_type: str, effect_data: Dict, rounds_remaining: int = None, concentration: bool = False, parent=None):
        super().__init__(parent)
        self.spell_name = spell_name
        self.effect_type = effect_type
        self.effect_data = effect_data
        self.rounds_remaining = rounds_remaining
        self.concentration = concentration
        self._setup_badge()

    def _setup_badge(self):
        badge_text = self._get_badge_text()
        self.setText(badge_text)

        self.setObjectName("spellEffectBadge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(28, 20)
        self.setMaximumSize(28, 20)

        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)
        self.setFont(font)

        color = self.EFFECT_COLORS.get(self.effect_type, self.EFFECT_COLORS["default"])

        self.setStyleSheet(f"""
            QLabel#spellEffectBadge {{
                background-color: {color};
                color: white;
                border-radius: 3px;
                border: 1px solid {color};
                padding: 1px;
                margin: 1px;
            }}
            QLabel#spellEffectBadge:hover {{
                border: 1px solid white;
                background-color: {color}dd;
            }}
        """)

        tooltip = self._build_tooltip()
        self.setToolTip(tooltip)

    def _get_badge_text(self) -> str:
        spell_abbrevs = {
            "Shield of Faith": "SoF",
            "Divine Favor": "DvF",
            "Bless": "BLS",
            "Heroism": "HER",
            "Aid": "AID",
            "Magic Weapon": "MgW",
            "Death Ward": "DtW",
            "Protection from Evil and Good": "PEG",
            "Warding Bond": "WBd",
            "Aura of Life": "AoL",
            "Shining Smite": "ShS",
            "Zone of Truth": "ZoT"
        }

        abbrev = spell_abbrevs.get(self.spell_name, self.spell_name[:3].upper())

        if self.concentration:
            abbrev = f"{abbrev}*"

        return abbrev

    def _build_tooltip(self) -> str:
        tooltip = f"<b>{self.spell_name}</b><br>"

        if self.concentration:
            tooltip += "⚡ <b>Concentration</b><br>"

        if self.rounds_remaining:
            if self.rounds_remaining >= 100:
                minutes = self.rounds_remaining // 10
                tooltip += f"⏱ <b>{minutes} min remaining</b><br>"
            else:
                tooltip += f"⏱ <b>{self.rounds_remaining} rounds remaining</b><br>"

        tooltip += "<br><u>Effect:</u><br>"
        tooltip += self._get_effect_description()

        return tooltip

    def _get_effect_description(self) -> str:
        if self.effect_type == "ac_bonus":
            value = self.effect_data.get('value', 0)
            return f"+{value} AC"
        elif self.effect_type in ("attack_bonus", "attack_and_save_bonus"):
            dice = self.effect_data.get('bonus_dice', '+1d4')
            return f"{dice} to attacks/saves"
        elif self.effect_type in ("damage_bonus", "damage_bonus_per_hit"):
            dice = self.effect_data.get('damage_dice', '1d4')
            dtype = self.effect_data.get('damage_type', 'radiant')
            return f"+{dice} {dtype} damage per hit"
        elif self.effect_type == "temp_hp_per_turn":
            amount = self.effect_data.get('temp_hp_per_turn', 0)
            return f"{amount} temp HP at start of each turn"
        elif self.effect_type == "hp_maximum_increase":
            value = self.effect_data.get('value', 0)
            return f"+{value} HP maximum"
        elif self.effect_type == "condition_immunity":
            condition = self.effect_data.get('condition', 'unknown')
            return f"Immune to {condition.title()}"
        elif self.effect_type == "weapon_enchantment":
            attack_bonus = self.effect_data.get('attack_bonus', 1)
            damage_bonus = self.effect_data.get('damage_bonus', 1)
            return f"+{attack_bonus} to hit, +{damage_bonus} damage (magical)"
        elif self.effect_type == "warding_bond":
            return f"+1 AC, +1 saves, resistance to all damage"
        elif self.effect_type == "death_ward":
            return f"Prevents death once (restore to 1 HP)"
        elif self.effect_type == "aura_of_life":
            return f"30ft aura: necrotic resistance, heal unconscious 1 HP/turn"
        elif self.effect_type == "protection_from_evil_and_good":
            return f"Protection from 6 creature types"
        elif self.effect_type == "next_hit_bonus_damage":
            dice = self.effect_data.get('damage_dice', 2)
            die_type = self.effect_data.get('damage_die_type', 'd6')
            dtype = self.effect_data.get('damage_type', 'radiant')
            return f"Next hit: +{dice}{die_type} {dtype} damage"
        elif self.effect_type == "zone_of_truth":
            return f"15ft radius: creatures cannot lie (Cha save)"
        else:
            return "See spell description"


class ConditionDisplayWidget(QWidget):
    """Widget displaying all active conditions as compact badges."""

    # Signal emitted when conditions change (for log integration)
    conditions_changed = pyqtSignal(list)  # List of ActiveCondition objects

    def __init__(self, character_id: str = None, db_path: str = "talekeeper.db", parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.db_path = db_path
        self.condition_manager = None
        self.spell_effects_service = None
        self.badges = []

        if ConditionManager:
            try:
                self.condition_manager = ConditionManager(db_path)
            except Exception as e:
                print(f"[ConditionDisplay] Could not initialize condition manager: {e}")

        if SpellEffectsService:
            try:
                self.spell_effects_service = SpellEffectsService(db_path)
            except Exception as e:
                print(f"[ConditionDisplay] Could not initialize spell effects service: {e}")

        self._setup_ui()

    def _setup_ui(self):
        """Initialize the widget layout."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)

        self.no_conditions_label = QLabel("No active conditions or effects")
        self.no_conditions_label.setObjectName("noConditionsLabel")
        self.no_conditions_label.setStyleSheet("""
            QLabel#noConditionsLabel {
                color: #888888;
                font-size: 10px;
                font-style: italic;
            }
        """)
        self.layout.addWidget(self.no_conditions_label)
        self.no_conditions_label.show()

        self.setMaximumHeight(24)
        self.setMinimumHeight(24)

    def set_character_id(self, character_id: str):
        """Update the character ID and refresh display."""
        self.character_id = character_id
        self.refresh_conditions()

    def refresh_conditions(self):
        if not self.character_id:
            self._clear_display()
            return

        try:
            conditions = []
            spell_effects = []

            if self.condition_manager:
                conditions = self.condition_manager.get_active_conditions(self.character_id)

            if self.spell_effects_service:
                spell_effects = self.spell_effects_service.get_active_buffs(self.character_id)

            self._update_display(conditions, spell_effects)

            if conditions:
                self.conditions_changed.emit(conditions)

        except Exception as e:
            print(f"[ConditionDisplay] Error refreshing conditions: {e}")
            self._clear_display()

    def _update_display(self, conditions: List, spell_effects: List[Dict]):
        self._clear_badges()

        conditions = conditions or []
        spell_effects = spell_effects or []

        total_items = len(conditions) + len(spell_effects)

        if total_items == 0:
            self.no_conditions_label.show()
            return

        self.no_conditions_label.hide()

        max_badges = 8
        visible_count = 0

        for condition in conditions:
            if visible_count >= max_badges:
                break
            badge = ConditionBadge(condition, self)
            self.badges.append(badge)
            self.layout.addWidget(badge)
            visible_count += 1

        for effect in spell_effects:
            if visible_count >= max_badges:
                break
            badge = SpellEffectBadge(
                spell_name=effect.get('spell_name', 'Unknown'),
                effect_type=effect.get('effect_type', 'default'),
                effect_data=effect.get('effect_data', {}),
                rounds_remaining=effect.get('rounds_remaining'),
                concentration=effect.get('concentration', False),
                parent=self
            )
            self.badges.append(badge)
            self.layout.addWidget(badge)
            visible_count += 1

        overflow_count = total_items - visible_count
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
            overflow_label.setToolTip(f"{overflow_count} more - see character sheet for details")
            self.layout.addWidget(overflow_label)
            self.badges.append(overflow_label)

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