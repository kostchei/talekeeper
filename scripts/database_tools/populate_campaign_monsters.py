# core
#utility
# core
import sqlite3
import uuid
from typing import List, Tuple

DB_PATH = '../../talekeeper.db'

CONAN_MONSTERS_BY_CR = {
    '0': [('Commoner', 1, 1, 5)],
    '1/8': [
        ('Bandit', 1, 5),
        ('Guard', 1, 5),
        ('Cultist', 1, 5),
        ('Tribal Warrior', 1, 5),
        ('Warrior Infantry', 1, 5),
        ('Noble', 1, 5)
    ],
    '1/4': [
        ('Skeleton', 1, 5),
        ('Priest Acolyte', 1, 5),
        ('Grimlock', 1, 5),
        ('Axe Beak', 1, 5),
        ('Zombie', 1, 5)
    ],
    '1/2': [
        ('Scout', 2, 6),
        ('Tough', 2, 6),
        ('Ape', 2, 6),
        ('Shadow', 2, 6)
    ],
    '1': [
        ('Animated Armor', 2, 7),
        ('Giant Spider', 2, 7),
        ('Giant Vulture', 2, 7),
        ('Lion', 2, 7),
        ('Pirate', 2, 7),
        ('Spy', 2, 7),
        ('Specter', 2, 7),
        ('Manes Vaporspawn', 2, 7),
        ('Ogrillon Ogre', 2, 7),
        ('Yuan-ti Infiltrator', 2, 7)
    ],
    '2': [
        ('Bandit Captain', 3, 8),
        ('Berserker', 3, 8),
        ('Cult Fanatic', 3, 8),
        ('Apprentice Wizard', 3, 8),
        ('Giant Constrictor Snake', 3, 8),
        ('Gibbering Mouther', 3, 8),
        ('Priest', 3, 8),
        ('Shadow Mastiff', 3, 8),
        ('Ogre', 3, 8),
        ('Ettercap', 3, 8),
        ('Quaggoth', 3, 8)
    ],
    '3': [
        ('Knight', 4, 9),
        ('Warrior Veteran', 4, 9),
        ('Scout Captain', 4, 9),
        ('Wight', 4, 9),
        ('Phase Spider', 4, 9),
        ('Manticore', 4, 9),
        ('Quaggoth Thonot', 4, 9),
        ('Yeti', 4, 9),
        ('Mummy', 4, 9)
    ],
    '4': [
        ('Shadow Demon', 5, 10),
        ('Guard Captain', 5, 10),
        ('Tough Boss', 5, 10),
        ('Succubus', 5, 10),
        ('Helmed Horror', 5, 10),
        ('Black Pudding', 5, 10),
        ('Ghost', 5, 10)
    ],
    '5': [
        ('Gladiator', 6, 11),
        ('Champion', 6, 11),
        ('Gibbering Mouther', 6, 11),
        ('Giant Crocodile', 6, 11),
        ('Barlgura', 6, 11),
        ('Hill Giant', 6, 11),
        ('Giant Axe Beak', 6, 11),
        ('Wraith', 6, 11),
        ('Skum', 6, 11)
    ],
    '6': [
        ('Mage', 7, 12),
        ('Pirate Captain', 7, 12),
        ('Vrock', 7, 12),
        ('Wyvern', 7, 12),
        ('Giant Squid', 7, 12)
    ],
    '7': [
        ('Giant Ape', 8, 13),
        ('Bandit Deceiver', 8, 13),
        ('Stone Giant', 8, 13),
        ('Yuan-ti Abomination', 8, 13)
    ],
    '8': [
        ('Assassin', 9, 14),
        ('Aberrant Cultist', 9, 14),
        ('Frost Giant', 9, 14),
        ('Berserker Commander', 9, 14, 1),  # Boss flag
        ('Death Cultist', 9, 14),
        ('Fiend Cultist', 9, 14),
        ('Tyrannosaurus Rex', 9, 14),
        ('Hezrou', 9, 14),
        ('Vampire Nightbringer', 9, 14, 1)  # Boss flag
    ],
    '9': [
        ('Champion', 10, 15, 1),  # Boss flag
        ('Glabrezu', 10, 15),
        ('Gray Slaad', 10, 15),
        ('Fire Giant', 10, 15),
        ('Abominable Yeti', 10, 15)
    ],
    '10': [
        ('Cultist Hierophant', 11, 16, 1),  # Boss flag
        ('Noble Prodigy', 11, 16),
        ('Spy Master', 11, 16),
        ('Warrior Commander', 11, 16, 1),  # Boss flag
        ('Stone Golem', 11, 16),
        ('Aboleth', 11, 16, 1)  # Boss flag
    ]
}

def create_campaign_monsters_table(conn):
    cursor = conn.cursor()

    # Create table directly
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaign_monsters (
            id TEXT PRIMARY KEY,
            campaign_id TEXT NOT NULL,
            monster_id TEXT NOT NULL,
            encounter_weight INTEGER DEFAULT 1,
            min_party_level INTEGER DEFAULT 1,
            max_party_level INTEGER DEFAULT 20,
            environment_override TEXT,
            notes TEXT,
            variant_rules TEXT,
            is_boss INTEGER DEFAULT 0,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (monster_id) REFERENCES monsters(id) ON DELETE CASCADE,
            UNIQUE(campaign_id, monster_id)
        )
    ''')

    # Create indexes
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_campaign_monsters_campaign
        ON campaign_monsters(campaign_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_campaign_monsters_monster
        ON campaign_monsters(monster_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_campaign_monsters_level
        ON campaign_monsters(min_party_level, max_party_level)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_campaign_monsters_boss
        ON campaign_monsters(is_boss)
    ''')

    conn.commit()
    print('[OK] Campaign monsters table created/verified')

def populate_conan_campaign(conn, campaign_id='conan'):
    cursor = conn.cursor()

    added = 0
    skipped = 0
    missing = []

    print(f'\nPopulating Conan campaign monsters...')
    print('=' * 60)

    for cr, monsters in CONAN_MONSTERS_BY_CR.items():
        print(f'\nCR {cr}:')

        for monster_data in monsters:
            if len(monster_data) == 3:
                name, min_level, max_level = monster_data
                is_boss = 0
            else:
                name, min_level, max_level, is_boss = monster_data

            # Get monster ID
            cursor.execute('SELECT id FROM monsters WHERE name = ?', (name,))
            result = cursor.fetchone()

            if not result:
                print(f'  [MISSING] {name}')
                missing.append((name, cr))
                continue

            monster_id = result[0]

            # Check if already exists
            cursor.execute(
                'SELECT id FROM campaign_monsters WHERE campaign_id = ? AND monster_id = ?',
                (campaign_id, monster_id)
            )

            if cursor.fetchone():
                print(f'  [SKIP] {name}')
                skipped += 1
                continue

            # Insert
            campaign_monster_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO campaign_monsters
                (id, campaign_id, monster_id, min_party_level, max_party_level, is_boss, encounter_weight)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (campaign_monster_id, campaign_id, monster_id, min_level, max_level, is_boss, 1))

            boss_marker = ' [BOSS]' if is_boss else ''
            print(f'  [ADDED] {name} (L{min_level}-{max_level}){boss_marker}')
            added += 1

    conn.commit()

    print()
    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f'Added: {added}')
    print(f'Skipped: {skipped}')
    print(f'Missing: {len(missing)}')

    if missing:
        print('\nMissing monsters:')
        for name, cr in missing:
            print(f'  - {name} (CR {cr})')

    return added, skipped, missing

def main():
    print('Campaign Monsters Populator')
    print('=' * 60)

    conn = sqlite3.connect(DB_PATH)

    try:
        create_campaign_monsters_table(conn)

        added, skipped, missing = populate_conan_campaign(conn)

        if missing:
            print('\nWARNING: Some monsters were not found in database!')
            print('Run the monster import tools first.')
        else:
            print('\n[SUCCESS] All Conan campaign monsters populated!')

        # Show stats
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ?', ('conan',))
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ? AND is_boss = 1', ('conan',))
        bosses = cursor.fetchone()[0]

        print(f'\nConan Campaign Stats:')
        print(f'  Total monsters: {total}')
        print(f'  Boss monsters: {bosses}')
        print(f'  Regular monsters: {total - bosses}')

    finally:
        conn.close()

if __name__ == '__main__':
    main()
