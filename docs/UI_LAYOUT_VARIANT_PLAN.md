# UI Layout Variant Implementation Plan

## Objectives
- Reduce the apparent frame/margin around the fixed-layout desktop UI while keeping the 1920×1080 minimum window size intact.【F:ui/main_window.py†L41-L103】
- Rebalance horizontal space: shrink the character sheet and log panels, and invest the recovered width in the encounter panel.【F:ui/main_window.py†L80-L103】【F:character_sheet/character_panel.py†L54-L92】【F:log/log_panel.py†L50-L135】
- Flatten the action panel so it consumes less vertical space while continuing to span the gameplay columns.【F:ui/main_window.py†L100-L104】【F:action_cards/action_panel.py†L135-L190】
- Increase text/background contrast by darkening foreground text and brightening the light-theme surfaces (and mirroring the idea for the dark theme) without breaking existing theme plumbing.【F:ui/themes.py†L10-L200】
- Produce two side-by-side variants of the UI ("10%" and "20%" adjustments) that can be launched as independent builds for comparison, without destabilizing the existing baseline.

## Baseline Snapshot (for reference)
| Component | Current Metric | Source |
| --- | --- | --- |
| Window minimum size | 1920×1080 | `MainWindow.__init__`【F:ui/main_window.py†L41-L60】 |
| Layout margins | 96 px left/right, 54 px top/bottom (≈5%) | `MainWindow._setup_ui`【F:ui/main_window.py†L66-L93】 |
| Character panel width | 648 px minimum (expandable to 1296 px) | `CharacterPanel.__init__`【F:character_sheet/character_panel.py†L54-L92】 |
| Encounter panel width | 648 px | `MainWindow._setup_ui` positioning【F:ui/main_window.py†L85-L93】 |
| Log panel size | 432×486 px | `LogPanel.__init__`【F:log/log_panel.py†L50-L135】 |
| Equipment panel size | 432×486 px | `EquipmentPanel.__init__`【F:equipment_layout/equipment_panel.py†L43-L124】 |
| Action panel size/placement | 1280×300 px, anchored at bottom margin | `ActionPanel.__init__` & `MainWindow._setup_ui`【F:action_cards/action_panel.py†L135-L190】【F:ui/main_window.py†L100-L104】 |
| Theme palette | Light & dark dictionaries with shared stylesheet builder | `ui/themes.py`【F:ui/themes.py†L10-L200】 |

## Variant Layout Targets
The variant percentages express how much the left (character) and right (log) panels shrink relative to baseline widths; the encounter panel receives the freed horizontal pixels. Margins scale by the same percentage to visually tighten the frame, and the action bar height follows suit.

### Calculated Metrics
| Element | Baseline | Variant 10% | Variant 20% |
| --- | --- | --- | --- |
| Horizontal margin | 96 px | 86 px (≈−10%) | 77 px (≈−20%) |
| Vertical margin | 54 px | 49 px (≈−10%) | 43 px (≈−20%) |
| Character panel width | 648 px | 583 px | 520 px |
| Encounter panel width | 648 px | 756 px | 862 px |
| Log panel width | 432 px | 389 px | 346 px |
| Equipment panel width | 432 px (unchanged) | 389 px (to match log) | 346 px (to match log) |
| Action panel height | 300 px | 270 px | 240 px |
| Action panel width | 1728 px usable span | 1728 px usable span (keep full width) | 1728 px usable span |

_Notes_
- Character and log widths are rounded to the nearest whole pixel after scaling; encounter width is recomputed so all columns continue to consume exactly the 1728 px usable width (1920 minus horizontal margins).
- Equipment panel should mirror the log panel width so the right column remains vertically aligned.
- Action panel width should be stretched to the full usable width (rather than the hard-coded 1280 px) to remove the current inset and stay consistent across variants.

### Placement Offsets
For deterministic positioning inside `MainWindow._setup_ui`, update the `move(...)` coordinates to use cumulative sums driven by each variant's constants.

| Element | Variant 10% (x, y) | Variant 20% (x, y) |
| --- | --- | --- |
| Menu origin | (86, 49) | (77, 43) |
| Character panel origin | (86, 139) — preserves 90 px gap below menu | (77, 133) |
| Encounter panel origin | (669, 49) | (597, 43) |
| Log panel origin | (1425, 49) | (1459, 43) |
| Equipment panel origin | (1425, 49 + log height) | (1459, 43 + log height) |
| Action panel origin | (86, 761) | (77, 797) |
| Theme toggle button | align 10 px inset from right column edge (x = log_x + log_width − 100) | same pattern |

## Implementation Steps
1. **Introduce layout profiles**
   - Create `ui/layout_profiles.py` (or similar) containing dataclasses for `baseline`, `variant_10`, and `variant_20` with all measurements above.
   - Refactor `MainWindow` to accept a profile object so positioning math reads from a single source of truth.

2. **Duplicate launchers for side-by-side builds**
   - Add lightweight entry scripts (e.g., `main_variant10.py`, `main_variant20.py`) that instantiate `MainWindow(profile=VARIANT_10)` and `MainWindow(profile=VARIANT_20)` respectively while keeping the existing `main.py` wired to the baseline profile.
   - Adjust packaging or deployment scripts to emit separate executables/folders per profile as needed.

3. **Panel-specific adjustments**
   - Update constructor widths/heights in `CharacterPanel`, `LogPanel`, `EquipmentPanel`, and `ActionPanel` to consume the profile data instead of hard-coded numbers so each variant scales automatically.【F:character_sheet/character_panel.py†L54-L149】【F:log/log_panel.py†L50-L158】【F:equipment_layout/equipment_panel.py†L63-L124】【F:action_cards/action_panel.py†L135-L190】
   - Ensure expandable widths (e.g., character/equipment panel animations) respect new maximums by scaling them relative to the base width (e.g., double the profile width).
   - Revisit scroll areas and layouts for any assumptions about exact pixel counts (e.g., hard-coded spacers) to prevent clipping after resizing.

4. **Action panel flattening**
   - Replace the fixed 1280 px width with the usable width from the profile and drop the hard-coded `move(...)` value to center the panel.【F:action_cards/action_panel.py†L178-L190】
   - Review child layouts to ensure the reduced height still fits header controls and card rows; adjust padding if necessary.

5. **Contrast enhancements**
   - Update `LIGHT_THEME` and `DARK_THEME` dictionaries with higher-contrast values (e.g., lighten `background`/`surface` by 3–5% luminance and darken `text` by ~10%) and tweak `border` colors to maintain separation.【F:ui/themes.py†L10-L200】
   - Audit widgets with bespoke stylesheets (notably the character/equipment expand buttons and the log panel styling) so they derive colors from the updated palette rather than hard-coded dark grays that would clash with brighter surfaces.【F:character_sheet/character_panel.py†L124-L149】【F:log/log_panel.py†L137-L158】【F:equipment_layout/equipment_panel.py†L101-L113】
   - Validate theme toggle logic still flips button labels/icons appropriately after palette changes.【F:ui/main_window.py†L106-L113】

6. **Testing & QA**
   - Manual smoke-test all three profiles (baseline + two variants) to verify widget alignment, clickable regions, and lack of overlap at 1920×1080.
   - Run the existing automated test suite to ensure no regressions in business logic.
   - Visually inspect light and dark themes under each profile to confirm the desired contrast gain.

## Deployment & Comparison Workflow
- Package or zip each profile-specific entry script into its own distribution folder (e.g., `TaleKeeper-UI10/`, `TaleKeeper-UI20/`) so stakeholders can open them side-by-side.
- Document in release notes that the builds differ only by layout profile to aid QA comparisons.

## Open Questions / Risks
- Hard-coded pixel math scattered across nested widgets may require additional refactoring if animation or positioning relies on the old dimensions.
- Theme overrides embedded in individual widgets could dilute the intended contrast boost unless normalized during implementation.
- Any persistence of window geometry or splitter settings should be checked to ensure they do not override the new defaults when profiles switch.
