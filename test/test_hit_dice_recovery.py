import os
import sys
import types


# Run Qt in offscreen mode to avoid GUI requirements
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# Stub encounter_generator to avoid database access during import
stub = types.ModuleType("encounter_pane.encounter_generator")
stub.EncounterGenerator = object
stub.CampaignFrame = object
stub.roll_monster_hp = lambda *args, **kwargs: 0
sys.modules.setdefault("encounter_pane.encounter_generator", stub)


from encounter_pane.encounter_panel import (
    sync_hit_dice_with_level,
    restore_hit_dice_on_long_rest,
)


def test_hit_dice_persist_after_short_rest():
    character = {"level": 2, "hit_dice_max": 2, "hit_dice_current": 1}
    sync_hit_dice_with_level(character)
    assert character["hit_dice_current"] == 1
    assert character["hit_dice_max"] == 2


def test_long_rest_replenishes_and_levels_hit_dice():
    character = {"level": 2, "hit_dice_max": 2, "hit_dice_current": 1}
    character["level"] = 3  # Level up before long rest
    new_total, restored = restore_hit_dice_on_long_rest(character)
    assert character["hit_dice_max"] == 3
    assert new_total == 3
    assert restored == 1  # Only one die restored; one gained from leveling


def test_long_rest_restores_half_when_not_full():
    character = {"level": 3, "hit_dice_max": 3, "hit_dice_current": 1}
    new_total, restored = restore_hit_dice_on_long_rest(character)
    assert character["hit_dice_current"] == 2
    assert new_total == 2 and restored == 1

