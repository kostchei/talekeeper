# test
from unittest.mock import patch

from encounter_pane import alt_encounters


def test_generate_skill_challenge_structure():
    event = alt_encounters.generate_skill_challenge(8)

    assert event['type'] in alt_encounters.CHECK_TYPES
    assert event['skill'] in [entry['skill'] for entry in alt_encounters.SKILLS]
    assert event['stat'] in {entry['stat'] for entry in alt_encounters.SKILLS}
    assert event['xp_success'] in {tier['xp'] for tier in alt_encounters.SKILL_TIERS}
    assert event['xp_failure'] == event['xp_success'] // 2
    assert 'Check Type:' in event['text']
    assert 'XP Rewards:' in event['text']
    assert event['intro'].startswith('In ')


def test_generate_skill_challenge_resource_swap_text():
    def controlled_choice(options):
        if options == alt_encounters.CHECK_TYPES:
            return 'Resource Swap'
        return options[0]

    with patch('encounter_pane.alt_encounters.random.choice', side_effect=controlled_choice):
        event = alt_encounters.generate_skill_challenge(10)

    assert event['type'] == 'Resource Swap'
    assert 'Resource Swap' in event['text']
    assert 'costs' in event['text']
    assert 'Failure: You also suffer' in event['text']
