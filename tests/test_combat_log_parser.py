#test
import pytest
from services.combat_log_parser import CombatLogParser


class TestCombatLogParser:

    def setup_method(self):
        self.parser = CombatLogParser()

    def test_parse_attack_hit_basic(self):
        log = "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. HIT! Damage: 1d8+3 = 11"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['type'] == 'attack'
        assert event['attacker'] == 'Fighter'
        assert event['target'] == 'Goblin'
        assert event['attack_roll'] == 23
        assert event['target_ac'] == 15
        assert event['hit'] is True
        assert event['damage'] == 11
        assert event['critical'] is False

    def test_parse_attack_miss(self):
        log = "Fighter attacks Goblin: Roll 7+5=12 vs AC 15. MISS!"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['hit'] is False
        assert event['damage'] == 0
        assert event['critical'] is False

    def test_parse_attack_critical(self):
        log = "Fighter attacks Goblin: Roll 20+5=25 vs AC 15. CRITICAL! Damage: 2d8+3 = 18"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['hit'] is True
        assert event['critical'] is True
        assert event['damage'] == 18

    def test_parse_attack_with_weapon(self):
        log = "Fighter attacks Goblin with Longsword: Roll 18+5=23 vs AC 15. HIT! Damage: 11"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['weapon'] == 'Longsword'

    def test_parse_attack_no_explicit_result(self):
        log = "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. Damage: 11"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['hit'] is True

    def test_parse_attack_no_damage(self):
        log = "Fighter attacks Goblin: Roll 7+5=12 vs AC 15. MISS!"
        event = self.parser.parse_attack_event(log)

        assert event is not None
        assert event['damage'] == 0

    def test_parse_damage_event(self):
        log = "Damage: 2d6+4 = 12"
        event = self.parser.parse_damage_event(log)

        assert event is not None
        assert event['type'] == 'damage'
        assert event['damage'] == 12
        assert event['damage_dice'] == '2d6+4'

    def test_parse_condition_event(self):
        log = "Goblin is Prone"
        event = self.parser.parse_condition_event(log)

        assert event is not None
        assert event['type'] == 'condition'
        assert event['entity'] == 'Goblin'
        assert event['condition'] == 'Prone'
        assert event['applied'] is True

    def test_parse_death_event(self):
        log = "Goblin dies"
        event = self.parser.parse_death_event(log)

        assert event is not None
        assert event['type'] == 'death'
        assert event['entity'] == 'Goblin'

    def test_parse_healing_event(self):
        log = "Fighter heals 10"
        event = self.parser.parse_healing_event(log)

        assert event is not None
        assert event['type'] == 'healing'
        assert event['entity'] == 'Fighter'
        assert event['amount'] == 10

    def test_parse_event_auto_detect_attack(self):
        log = "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. HIT! Damage: 11"
        event = self.parser.parse_event(log)

        assert event is not None
        assert event['type'] == 'attack'

    def test_parse_event_auto_detect_death(self):
        log = "Goblin is defeated"
        event = self.parser.parse_event(log)

        assert event is not None
        assert event['type'] == 'death'

    def test_parse_event_auto_detect_healing(self):
        log = "Fighter regains 8 HP"
        event = self.parser.parse_event(log)

        assert event is not None
        assert event['type'] == 'healing'

    def test_parse_combat_round(self):
        logs = [
            "Fighter attacks Goblin: Roll 18+5=23 vs AC 15. HIT! Damage: 11",
            "Goblin attacks Fighter: Roll 7+4=11 vs AC 18. MISS!",
            "Fighter attacks Goblin: Roll 15+5=20 vs AC 15. HIT! Damage: 9",
            "Goblin dies"
        ]
        events = self.parser.parse_combat_round(logs)

        assert len(events) == 4
        assert events[0]['type'] == 'attack'
        assert events[0]['hit'] is True
        assert events[1]['type'] == 'attack'
        assert events[1]['hit'] is False
        assert events[2]['type'] == 'attack'
        assert events[3]['type'] == 'death'

    def test_parse_empty_log(self):
        event = self.parser.parse_event("")
        assert event is None

    def test_parse_none_log(self):
        event = self.parser.parse_event(None)
        assert event is None

    def test_parse_unparseable_log(self):
        log = "This is just random text with no combat info"
        event = self.parser.parse_event(log)
        assert event is None
