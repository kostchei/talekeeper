import json
import sqlite3
import uuid
from typing import Dict, Any, Optional, List

CR_TO_XP = {
    '0': 10, '1/8': 25, '1/4': 50, '1/2': 100,
    '1': 200, '2': 450, '3': 700, '4': 1100, '5': 1800,
    '6': 2300, '7': 2900, '8': 3900, '9': 5000, '10': 5900,
    '11': 7200, '12': 8400, '13': 10000, '14': 11500, '15': 13000,
    '16': 15000, '17': 18000, '18': 20000, '19': 22000, '20': 25000,
    '21': 33000, '22': 41000, '23': 50000, '24': 62000, '25': 75000,
    '26': 90000, '27': 105000, '28': 120000, '29': 135000, '30': 155000
}

CR_TO_PROFICIENCY = {
    '0': 2, '1/8': 2, '1/4': 2, '1/2': 2,
    '1': 2, '2': 2, '3': 2, '4': 2,
    '5': 3, '6': 3, '7': 3, '8': 3,
    '9': 4, '10': 4, '11': 4, '12': 4,
    '13': 5, '14': 5, '15': 5, '16': 5,
    '17': 6, '18': 6, '19': 6, '20': 6,
    '21': 7, '22': 7, '23': 7, '24': 7,
    '25': 8, '26': 8, '27': 8, '28': 8,
    '29': 9, '30': 9
}

class FiveEToolsConverter:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def close(self):
        if self.conn:
            self.conn.close()

    def parse_ac(self, ac_data) -> int:
        if isinstance(ac_data, list):
            if len(ac_data) > 0:
                if isinstance(ac_data[0], dict):
                    return ac_data[0].get('ac', 10)
                return ac_data[0]
        return 10

    def parse_hp(self, hp_data) -> int:
        if isinstance(hp_data, dict):
            return hp_data.get('average', 0)
        return hp_data if isinstance(hp_data, int) else 0

    def parse_speed(self, speed_data) -> str:
        if isinstance(speed_data, dict):
            parts = []
            for mode, value in speed_data.items():
                if mode == 'walk':
                    parts.insert(0, f'{value} ft.')
                else:
                    parts.append(f'{mode} {value} ft.')
            return ', '.join(parts)
        return '30 ft.'

    def parse_size(self, size_data) -> str:
        if isinstance(size_data, list):
            size_data = size_data[0]

        size_map = {
            'T': 'Tiny', 'S': 'Small', 'M': 'Medium',
            'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'
        }
        return size_map.get(size_data, 'Medium')

    def parse_type(self, type_data) -> tuple:
        if isinstance(type_data, dict):
            main_type = type_data.get('type', 'unknown')
            tags = type_data.get('tags', [])
            subtype = ', '.join(tags) if tags else None
            return main_type, subtype
        return type_data, None

    def parse_alignment(self, alignment_data) -> str:
        if not alignment_data:
            return 'Unaligned'

        if isinstance(alignment_data, list):
            parts = []
            for item in alignment_data:
                if isinstance(item, dict):
                    if 'alignment' in item:
                        parts.extend(item['alignment'])
                    elif 'special' in item:
                        return item['special']
                else:
                    parts.append(item)

            if not parts:
                return 'Unaligned'

            alignment_map = {
                'L': 'Lawful', 'N': 'Neutral', 'C': 'Chaotic',
                'G': 'Good', 'E': 'Evil', 'U': 'Unaligned',
                'A': 'Any alignment'
            }

            result = ' '.join([alignment_map.get(p, p) for p in parts])
            return result

        return 'Unaligned'

    def parse_saves(self, saves_data) -> str:
        if not saves_data:
            return None

        parts = []
        for ability, bonus in saves_data.items():
            parts.append(f'{ability.upper()} +{bonus}')
        return ', '.join(parts)

    def parse_skills(self, skills_data) -> str:
        if not skills_data:
            return None

        parts = []
        for skill, bonus in skills_data.items():
            skill_name = skill.replace('_', ' ').title()
            parts.append(f'{skill_name} +{bonus}')
        return ', '.join(parts)

    def parse_resistances(self, resist_data) -> str:
        if not resist_data:
            return None

        if isinstance(resist_data, list):
            parts = []
            for item in resist_data:
                if isinstance(item, dict):
                    resist_type = item.get('resist', [])
                    if isinstance(resist_type, list):
                        parts.extend(resist_type)
                    else:
                        parts.append(resist_type)
                else:
                    parts.append(item)
            return ', '.join(parts)
        return str(resist_data)

    def parse_immunities(self, immune_data) -> str:
        return self.parse_resistances(immune_data)

    def parse_condition_immunities(self, immune_data) -> str:
        if not immune_data:
            return None
        if isinstance(immune_data, list):
            return ', '.join([str(x) for x in immune_data])
        return str(immune_data)

    def parse_senses(self, senses_data) -> str:
        if not senses_data:
            return 'passive Perception 10'

        if isinstance(senses_data, list):
            return ', '.join([str(x) for x in senses_data])
        return str(senses_data)

    def parse_languages(self, lang_data) -> str:
        if not lang_data:
            return None

        if isinstance(lang_data, list):
            parts = []
            for item in lang_data:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    if 'common' in item:
                        parts.append('Common')
            return ', '.join(parts)
        return str(lang_data)

    def parse_traits(self, trait_data) -> str:
        if not trait_data:
            return None

        traits = []
        for trait in trait_data:
            name = trait.get('name', 'Unknown')
            entries = trait.get('entries', [])
            description = self.parse_entries(entries)
            traits.append(f'**{name}**: {description}')

        return '\n\n'.join(traits)

    def parse_actions(self, action_data) -> str:
        if not action_data:
            return None

        actions = []
        for action in action_data:
            name = action.get('name', 'Unknown')
            entries = action.get('entries', [])
            description = self.parse_entries(entries)
            actions.append(f'**{name}**: {description}')

        return '\n\n'.join(actions)

    def parse_entries(self, entries) -> str:
        if not entries:
            return ''

        result = []
        for entry in entries:
            if isinstance(entry, str):
                result.append(entry)
            elif isinstance(entry, dict):
                if 'entries' in entry:
                    result.append(self.parse_entries(entry['entries']))
                elif 'items' in entry:
                    items = entry['items']
                    for item in items:
                        if isinstance(item, str):
                            result.append(f'- {item}')
                        elif isinstance(item, dict):
                            name = item.get('name', '')
                            entry_text = self.parse_entries(item.get('entries', []))
                            result.append(f'- {name}: {entry_text}')

        return ' '.join(result)

    def extract_primary_attack(self, action_data) -> tuple:
        if not action_data:
            return None, None, None, None, None

        for action in action_data:
            name = action.get('name', '')
            entries = action.get('entries', [])

            if not entries:
                continue

            for entry in entries:
                if isinstance(entry, str):
                    if 'Melee Weapon Attack' in entry or 'Ranged Weapon Attack' in entry:
                        import re

                        bonus_match = re.search(r'\+(\d+) to hit', entry)
                        reach_match = re.search(r'reach (\d+) ft', entry)
                        damage_match = re.search(r'(\d+d\d+(?:\s*\+\s*\d+)?)\s+(\w+)\s+damage', entry)

                        attack_bonus = int(bonus_match.group(1)) if bonus_match else None
                        reach = f'{reach_match.group(1)} ft.' if reach_match else '5 ft.'
                        damage_dice = damage_match.group(1) if damage_match else None
                        damage_type = damage_match.group(2) if damage_match else None

                        return name, attack_bonus, reach, damage_dice, damage_type

        return None, None, None, None, None

    def extract_multiattack(self, action_data) -> str:
        if not action_data:
            return None

        for action in action_data:
            name = action.get('name', '').lower()
            if 'multiattack' in name:
                entries = action.get('entries', [])
                return self.parse_entries(entries)

        return None

    def parse_environment(self, env_data) -> str:
        if not env_data:
            return None
        if isinstance(env_data, list):
            return ', '.join([str(x) for x in env_data])
        return str(env_data)

    def convert_monster(self, monster_data: Dict[str, Any]) -> Dict[str, Any]:
        cr = str(monster_data.get('cr', '0'))

        monster_type, subtype = self.parse_type(monster_data.get('type'))

        primary_attack_name, primary_attack_bonus, primary_attack_reach, primary_damage_dice, primary_damage_type = \
            self.extract_primary_attack(monster_data.get('action'))

        environment = self.parse_environment(monster_data.get('environment'))

        return {
            'id': str(uuid.uuid4()),
            'name': monster_data.get('name', 'Unknown'),
            'type': monster_type,
            'subtype': subtype,
            'size': self.parse_size(monster_data.get('size')),
            'alignment': self.parse_alignment(monster_data.get('alignment')),
            'armor_class': self.parse_ac(monster_data.get('ac')),
            'hit_points': self.parse_hp(monster_data.get('hp')),
            'speed': self.parse_speed(monster_data.get('speed')),
            'strength': monster_data.get('str', 10),
            'dexterity': monster_data.get('dex', 10),
            'constitution': monster_data.get('con', 10),
            'intelligence': monster_data.get('int', 10),
            'wisdom': monster_data.get('wis', 10),
            'charisma': monster_data.get('cha', 10),
            'challenge_rating': cr,
            'experience_points': CR_TO_XP.get(cr, 0),
            'proficiency_bonus': CR_TO_PROFICIENCY.get(cr, 2),
            'saving_throws': self.parse_saves(monster_data.get('save')),
            'skills': self.parse_skills(monster_data.get('skill')),
            'damage_resistances': self.parse_resistances(monster_data.get('resist')),
            'damage_immunities': self.parse_immunities(monster_data.get('immune')),
            'condition_immunities': self.parse_condition_immunities(monster_data.get('conditionImmune')),
            'senses': self.parse_senses(monster_data.get('senses')),
            'languages': self.parse_languages(monster_data.get('languages')),
            'special_abilities': self.parse_traits(monster_data.get('trait')),
            'actions': self.parse_actions(monster_data.get('action')),
            'legendary_actions': self.parse_actions(monster_data.get('legendary')),
            'reactions': self.parse_actions(monster_data.get('reaction')),
            'environment': environment,
            'aquatic_only': 1 if environment and 'underwater' in environment.lower() else 0,
            'multiattack_description': self.extract_multiattack(monster_data.get('action')),
            'primary_attack_name': primary_attack_name,
            'primary_attack_bonus': primary_attack_bonus,
            'primary_attack_reach': primary_attack_reach,
            'primary_damage_dice': primary_damage_dice,
            'primary_damage_type': primary_damage_type
        }

    def insert_monster(self, monster: Dict[str, Any], dry_run: bool = False):
        if dry_run:
            print(f'[DRY RUN] Would insert: {monster["name"]} (CR {monster["challenge_rating"]})')
            return

        cursor = self.conn.cursor()

        cursor.execute('SELECT id FROM monsters WHERE name = ?', (monster['name'],))
        existing = cursor.fetchone()

        if existing:
            print(f'[SKIP] Monster already exists: {monster["name"]}')
            return

        columns = ', '.join(monster.keys())
        placeholders = ', '.join(['?' for _ in monster])
        query = f'INSERT INTO monsters ({columns}) VALUES ({placeholders})'

        cursor.execute(query, list(monster.values()))
        self.conn.commit()

        print(f'[INSERTED] {monster["name"]} (CR {monster["challenge_rating"]})')

    def import_from_file(self, json_file: str, dry_run: bool = False):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.connect()

        print('=' * 80)
        print(f'IMPORTING MONSTERS FROM {json_file}')
        print(f'Mode: {"DRY RUN" if dry_run else "LIVE"}')
        print('=' * 80)
        print()

        imported = 0
        skipped = 0

        for monster_name, variants in data.items():
            print(f'\n--- {monster_name} ---')

            for variant in variants:
                monster_data = variant['monster_data']
                sourcebook = variant['sourcebook']

                converted = self.convert_monster(monster_data)
                print(f'Source: {sourcebook}')

                try:
                    self.insert_monster(converted, dry_run)
                    imported += 1
                except Exception as e:
                    print(f'[ERROR] Failed to import {converted["name"]}: {e}')
                    skipped += 1

        self.close()

        print()
        print('=' * 80)
        print('IMPORT SUMMARY')
        print('=' * 80)
        print(f'Imported: {imported}')
        print(f'Skipped/Errors: {skipped}')

if __name__ == '__main__':
    import sys
    import os

    dry_run = '--dry-run' in sys.argv

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')
    db_path = os.path.join(project_root, 'talekeeper.db')
    input_file = os.path.join(project_root, 'data', 'monsters', '5etools', '5etools_monsters_raw.json')

    converter = FiveEToolsConverter(db_path=db_path)
    converter.import_from_file(input_file, dry_run=dry_run)
