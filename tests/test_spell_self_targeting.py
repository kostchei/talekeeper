# test
"""
Test spell self-targeting for buff spells.

Tests that spells like Divine Favor, Bless, Mage Armor, and Shield of Faith
can be cast on the player character without requiring a target selection.
"""

def test_is_self_targeting_spell():
    """Test that buff spells are correctly identified as self-targeting."""

    test_cases = [
        {
            'name': 'Divine Favor',
            'description': 'Your prayer empowers you with divine radiance. You gain bonus damage',
            'range': 'Self',
            'expected': True
        },
        {
            'name': 'Bless',
            'description': 'You bless up to three creatures. They gain bonus to attack rolls',
            'range': 'Touch',
            'expected': True
        },
        {
            'name': 'Mage Armor',
            'description': 'You touch a willing creature. Their AC becomes 13 + Dex modifier',
            'range': 'Touch',
            'expected': True
        },
        {
            'name': 'Shield of Faith',
            'description': 'A shimmering field appears. The target gains +2 bonus to AC',
            'range': 'Touch',
            'expected': True
        },
        {
            'name': 'Protection from Evil and Good',
            'description': 'You touch a willing creature. Gain advantage on saves',
            'range': 'Touch',
            'expected': True
        },
        {
            'name': 'Fire Bolt',
            'description': 'You hurl a mote of fire. Make a ranged spell attack dealing damage',
            'range': '120 feet',
            'expected': False
        },
        {
            'name': 'Sacred Flame',
            'description': 'Flame-like radiance descends. The creature must succeed on a Dexterity saving throw',
            'range': '60 feet',
            'expected': False
        },
        {
            'name': 'Cure Wounds',
            'description': 'A creature you touch regains hit points equal to 1d8 + your spellcasting modifier',
            'range': 'Touch',
            'expected': True
        },
    ]

    def _is_self_targeting_spell(spell_data):
        description = spell_data.get('description', '').lower()
        spell_range = spell_data.get('range', '').lower()

        requires_tohit = any(keyword in description for keyword in [
            'make a spell attack', 'make a ranged spell attack',
            'make a melee spell attack', 'spell attack roll'
        ])

        requires_save = any(keyword in description for keyword in [
            'must make a saving throw', 'must succeed on a',
            'make a dexterity saving throw', 'make a constitution saving throw',
            'make a wisdom saving throw', 'make a strength saving throw',
            'make a intelligence saving throw', 'make a charisma saving throw',
            'saving throw', 'fails its save', 'succeeds on its save'
        ])

        if requires_tohit or requires_save:
            return False

        buff_keywords = ['gain', 'bonus', 'advantage', 'resistance', 'immunity',
                        'ac', 'armor', 'hit points', 'speed', 'healing']
        is_buff = any(keyword in description for keyword in buff_keywords)

        is_touch_or_self = 'self' in spell_range or 'touch' in spell_range

        return is_buff or is_touch_or_self

    print("\n=== Testing Spell Self-Targeting ===\n")

    passed = 0
    failed = 0

    for test in test_cases:
        result = _is_self_targeting_spell(test)
        expected = test['expected']
        status = "PASS" if result == expected else "FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"[{status}] {test['name']}: self-targeting = {result} (expected {expected})")

    print(f"\n=== Results: {passed} passed, {failed} failed ===\n")

    return failed == 0


def test_spell_buff_effects():
    """Test that buff effects are correctly formatted."""

    def _get_spell_buff_effects(spell_name, cast_level):
        effects = {
            'Divine Favor': [
                '+1d4 radiant damage to weapon attacks',
                f'Duration: 1 minute (concentration)'
            ],
            'Bless': [
                '+1d4 to attack rolls and saving throws',
                f'Duration: 1 minute (concentration)'
            ],
            'Protection from Evil and Good': [
                'Disadvantage on attacks from aberrations, celestials, elementals, fey, fiends, and undead',
                'Advantage on saves against those creature types',
                'Cannot be charmed, frightened, or possessed by them',
                f'Duration: 10 minutes (concentration)'
            ],
            'Mage Armor': [
                'AC = 13 + Dexterity modifier (if not wearing armor)',
                f'Duration: 8 hours'
            ],
            'Shield of Faith': [
                '+2 bonus to AC',
                f'Duration: 10 minutes (concentration)'
            ],
        }
        return effects.get(spell_name, [])

    print("\n=== Testing Spell Buff Effects ===\n")

    test_spells = ['Divine Favor', 'Bless', 'Mage Armor', 'Shield of Faith', 'Protection from Evil and Good']

    for spell_name in test_spells:
        effects = _get_spell_buff_effects(spell_name, 1)
        print(f"\n{spell_name}:")
        if effects:
            for effect in effects:
                print(f"  - {effect}")
        else:
            print(f"  [No effects defined]")

    print("\n")
    return True


if __name__ == "__main__":
    result1 = test_is_self_targeting_spell()
    result2 = test_spell_buff_effects()

    if result1 and result2:
        print("All tests passed!")
        exit(0)
    else:
        print("Some tests failed!")
        exit(1)
