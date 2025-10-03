import re
from typing import Dict, Any, List, Optional


class CombatLogParser:

    def __init__(self):
        self.attack_pattern = re.compile(
            r'(?P<attacker>[\w\s]+?)\s+attacks?\s+(?P<target>[\w\s]+?)(?:\s+with\s+(?P<weapon>[\w\s]+?))?:'
            r'(?:.*?Roll:?\s*(?P<roll>\d+)(?:\s*\+\s*(?P<bonus>\d+))?\s*=\s*(?P<total>\d+))?'
            r'(?:\s+vs\s+AC\s+(?P<ac>\d+))?'
            r'(?:.*?(?P<result>HIT|MISS|CRITICAL))?',
            re.IGNORECASE
        )

        self.damage_pattern = re.compile(
            r'Damage:?\s*(?:(?P<dice>[\dd+\-]+)\s*=\s*)?(?P<total>\d+)',
            re.IGNORECASE
        )

        self.condition_pattern = re.compile(
            r'(?P<entity>[\w\s]+?)\s+(?:is|becomes|gains|suffers)\s+(?P<condition>Prone|Stunned|Paralyzed|Frightened|Poisoned|Blinded|Deafened|Grappled|Restrained|Invisible)\b',
            re.IGNORECASE
        )

        self.death_pattern = re.compile(
            r'(?P<entity>[\w\s]+?)\s+(?:dies|is defeated|falls|is killed)',
            re.IGNORECASE
        )

        self.healing_pattern = re.compile(
            r'(?P<entity>[\w\s]+?)\s+(?:heals|regains|recovers)\s+(?P<amount>\d+)',
            re.IGNORECASE
        )

    def parse_attack_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        match = self.attack_pattern.search(log_text)
        if not match:
            return None

        groups = match.groupdict()

        result = groups.get('result')
        result = result.upper() if result else ''
        hit = result == 'HIT' or result == 'CRITICAL'
        critical = result == 'CRITICAL'

        if not hit and result != 'MISS':
            total_str = groups.get('total')
            ac_str = groups.get('ac')
            if total_str and ac_str:
                total = int(total_str)
                ac = int(ac_str)
                hit = total >= ac

        damage = 0
        damage_dice = None
        damage_match = self.damage_pattern.search(log_text)
        if damage_match:
            damage = int(damage_match.group('total'))
            damage_dice = damage_match.group('dice')

        return {
            'type': 'attack',
            'attacker': groups.get('attacker', '').strip(),
            'target': groups.get('target', '').strip(),
            'weapon': groups.get('weapon', '').strip() if groups.get('weapon') else None,
            'attack_roll': int(groups['total']) if groups.get('total') else None,
            'target_ac': int(groups['ac']) if groups.get('ac') else None,
            'hit': hit,
            'damage': damage,
            'damage_dice': damage_dice,
            'critical': critical,
            'raw_text': log_text
        }

    def parse_damage_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        damage_match = self.damage_pattern.search(log_text)
        if not damage_match:
            return None

        return {
            'type': 'damage',
            'damage': int(damage_match.group('total')),
            'damage_dice': damage_match.group('dice'),
            'raw_text': log_text
        }

    def parse_condition_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        match = self.condition_pattern.search(log_text)
        if not match:
            return None

        return {
            'type': 'condition',
            'entity': match.group('entity').strip(),
            'condition': match.group('condition').strip(),
            'applied': True,
            'raw_text': log_text
        }

    def parse_death_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        match = self.death_pattern.search(log_text)
        if not match:
            return None

        return {
            'type': 'death',
            'entity': match.group('entity').strip(),
            'raw_text': log_text
        }

    def parse_healing_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        match = self.healing_pattern.search(log_text)
        if not match:
            return None

        return {
            'type': 'healing',
            'entity': match.group('entity').strip(),
            'amount': int(match.group('amount')),
            'raw_text': log_text
        }

    def parse_event(self, log_text: str) -> Optional[Dict[str, Any]]:

        if not log_text or not log_text.strip():
            return None

        parsers = [
            self.parse_attack_event,
            self.parse_death_event,
            self.parse_healing_event,
            self.parse_condition_event,
            self.parse_damage_event,
        ]

        for parser in parsers:
            event = parser(log_text)
            if event:
                return event

        return None

    def parse_combat_round(self, log_entries: List[str]) -> List[Dict[str, Any]]:

        events = []
        for entry in log_entries:
            event = self.parse_event(entry)
            if event:
                events.append(event)

        return events
