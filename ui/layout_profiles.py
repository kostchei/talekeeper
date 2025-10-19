# core
# core
"""Layout profiles for TaleKeeper UI variants."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutProfile:
    """Pixel measurements that describe the fixed layout geometry."""

    name: str
    horizontal_margin: int
    vertical_margin: int
    character_panel_width: int
    encounter_panel_width: int
    log_panel_width: int
    action_panel_height: int
    min_window_width: int = 1920
    min_window_height: int = 1080
    character_panel_height: int = 570
    log_panel_height: int = 486
    equipment_panel_height: int = 486
    menu_character_gap: int = 90
    theme_toggle_inset: int = 100
    theme_toggle_height: int = 30
    theme_toggle_width: int = 90

    @property
    def usable_width(self) -> int:
        """Horizontal span inside the left/right margins."""

        return self.min_window_width - (self.horizontal_margin * 2)

    @property
    def character_panel_max_width(self) -> int:
        """Expanded width for animated character sheet."""

        return int(self.character_panel_width * 2.6)

    @property
    def encounter_panel_height(self) -> int:
        """Height for the encounter column above the action panel."""

        return (
            self.min_window_height
            - (self.vertical_margin * 2)
            - self.action_panel_height
        )

    @property
    def equipment_panel_width(self) -> int:
        """Right column equipment width matches the log width."""

        return self.log_panel_width


BASELINE_PROFILE = LayoutProfile(
    name="baseline",
    horizontal_margin=96,
    vertical_margin=54,
    character_panel_width=520,  # Reduced by ~20% from 648
    encounter_panel_width=810,  # Increased by 25% from 648
    log_panel_width=410,  # Reduced by ~5% from 432
    action_panel_height=270,  # Reduced by 10% from 300
)

VARIANT_10_PROFILE = LayoutProfile(
    name="variant_10",
    horizontal_margin=86,
    vertical_margin=49,
    character_panel_width=583,
    encounter_panel_width=756,
    log_panel_width=389,
    action_panel_height=270,
)

VARIANT_20_PROFILE = LayoutProfile(
    name="variant_20",
    horizontal_margin=77,
    vertical_margin=43,
    character_panel_width=520,
    encounter_panel_width=862,
    log_panel_width=346,
    action_panel_height=240,
)
