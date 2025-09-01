import sqlite3
from datetime import datetime
from core.game_engine_sqlite import GameEngineSQLite
from core.dtos import CharacterDTO


def test_multiple_feat_effects_applied():
    engine = GameEngineSQLite(':memory:')
    char = CharacterDTO(
        id='1',
        name='Tester',
        level=1,
        experience_points=0,
        race_id='human',
        race_name='Human',
        class_id='fighter',
        class_name='Fighter',
        subclass_id=None,
        subclass_name=None,
        background_id='farmer',
        background_name='Farmer',
        strength=10,
        dexterity=10,
        constitution=10,
        intelligence=10,
        wisdom=10,
        charisma=10,
        strength_modifier=0,
        dexterity_modifier=0,
        constitution_modifier=0,
        intelligence_modifier=0,
        wisdom_modifier=0,
        charisma_modifier=0,
        armor_class=10,
        hit_points_max=10,
        hit_points_current=10,
        hit_points_temporary=0,
        hit_dice_max=1,
        hit_dice_current=1,
        death_saves_successes=0,
        death_saves_failures=0,
        conditions=[],
        proficiencies=[],
        features={},
        feats=[],
        weapon_masteries=[],
        spell_slots_current={},
        spell_slots_max={},
        class_resources={},
        class_resources_max={},
        ability_uses={},
        ability_uses_max={},
        created_at=datetime.now(),
        notes=""
    )
    modified = engine._apply_feat_effects_to_character(char, ['Tough', 'Linguist'])
    assert modified.hit_points_max == 12
    assert modified.intelligence == 11
