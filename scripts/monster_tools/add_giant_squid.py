import sqlite3
import uuid

db_path = '../../talekeeper.db'

giant_squid = {
    'id': str(uuid.uuid4()),
    'name': 'Giant Squid',
    'type': 'beast',
    'subtype': None,
    'size': 'Huge',
    'alignment': 'Unaligned',
    'armor_class': 12,
    'hit_points': 120,
    'speed': '5 ft., swim 80 ft.',
    'strength': 23,
    'dexterity': 14,
    'constitution': 12,
    'intelligence': 5,
    'wisdom': 11,
    'charisma': 4,
    'challenge_rating': '6',
    'experience_points': 2300,
    'proficiency_bonus': 3,
    'saving_throws': 'STR +9, DEX +5',
    'skills': 'Perception +6',
    'damage_resistances': None,
    'damage_immunities': None,
    'condition_immunities': None,
    'senses': 'Darkvision 120 ft., Passive Perception 16',
    'languages': None,
    'special_abilities': '''**Keen Sight**: The giant squid has advantage on Wisdom (Perception) checks that rely on sight.

**Water Breathing**: The giant squid can breathe only underwater.''',
    'actions': '''**Multiattack**: The giant squid makes two attacks: one with its tentacles and one with its beak.

**Tentacles**: Melee Weapon Attack: +9 to hit, reach 15 ft., one target. Hit: 20 (3d8 + 7) bludgeoning damage. If the target is a Large or smaller creature, it is grappled (escape DC 16). Until this grapple ends, the target is restrained, and the giant squid can't use its tentacles on another target.

**Beak**: Melee Weapon Attack: +9 to hit, reach 5 ft., one target. Hit: 18 (3d6 + 7) piercing damage.

**Ink Cloud (Recharges after a Short or Long Rest)**: While underwater, the giant squid expels a 60-foot-radius cloud of ink. The cloud spreads around corners, and that area is heavily obscured to creatures other than the giant squid. Each creature other than the giant squid that ends its turn there must succeed on a DC 16 Constitution saving throw or take 10 (3d6) poison damage. A strong current disperses the cloud, which otherwise disappears at the end of the giant squid's next turn.''',
    'legendary_actions': None,
    'reactions': None,
    'environment': 'underwater',
    'aquatic_only': 1,
    'multiattack_description': 'The giant squid makes two attacks: one with its tentacles and one with its beak.',
    'primary_attack_name': 'Tentacles',
    'primary_attack_bonus': 9,
    'primary_attack_reach': '15 ft.',
    'primary_damage_dice': '3d8+7',
    'primary_damage_type': 'bludgeoning'
}

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id FROM monsters WHERE name = ?', (giant_squid['name'],))
existing = cursor.fetchone()

if existing:
    print(f'[SKIP] Monster already exists: {giant_squid["name"]}')
else:
    columns = ', '.join(giant_squid.keys())
    placeholders = ', '.join(['?' for _ in giant_squid])
    query = f'INSERT INTO monsters ({columns}) VALUES ({placeholders})'

    cursor.execute(query, list(giant_squid.values()))
    conn.commit()

    print(f'[SUCCESS] Added Giant Squid (CR 6) to database')
    print(f'  AC: 12')
    print(f'  HP: 120')
    print(f'  Tentacles: +9 to hit, 3d8+7 bludgeoning')
    print(f'  Environment: underwater')

conn.close()
