# core
#utility
# core
import sqlite3
import uuid

DB_PATH = '../../talekeeper.db'

def create_campaigns_table(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campaigns'")
    if cursor.fetchone():
        print('[OK] Campaigns table already exists')
    else:
        print('[ERROR] Campaigns table does not exist - run database init first')
        raise Exception('Campaigns table missing')

def create_conan_campaigns(conn):
    cursor = conn.cursor()

    campaigns = [
        ('conan-core', 'Conan Core', 'sword-and-sorcery'),
        ('conan-like', 'Conan-Like', 'sword-and-sorcery')
    ]

    for campaign_id, name, style in campaigns:
        cursor.execute('SELECT id FROM campaigns WHERE id = ?', (campaign_id,))
        if cursor.fetchone():
            print(f'[SKIP] Campaign already exists: {name}')
        else:
            cursor.execute(
                'INSERT INTO campaigns (id, name, style) VALUES (?, ?, ?)',
                (campaign_id, name, style)
            )
            print(f'[ADDED] Campaign: {name}')

    conn.commit()

def populate_conan_core(conn):
    cursor = conn.cursor()

    # Copy all monsters from 'conan' campaign to 'conan-core'
    cursor.execute('''
        SELECT monster_id, encounter_weight, min_party_level, max_party_level,
               environment_override, notes, variant_rules, is_boss
        FROM campaign_monsters
        WHERE campaign_id = 'conan'
    ''')

    conan_monsters = cursor.fetchall()

    print(f'\nPopulating Conan-Core with {len(conan_monsters)} monsters...')

    added = 0
    for monster_data in conan_monsters:
        monster_id = monster_data[0]

        # Check if already exists
        cursor.execute(
            'SELECT id FROM campaign_monsters WHERE campaign_id = ? AND monster_id = ?',
            ('conan-core', monster_id)
        )

        if cursor.fetchone():
            continue

        # Insert with new campaign_id
        new_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO campaign_monsters
            (id, campaign_id, monster_id, encounter_weight, min_party_level, max_party_level,
             environment_override, notes, variant_rules, is_boss)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (new_id, 'conan-core', *monster_data))

        added += 1

    conn.commit()
    print(f'[OK] Added {added} monsters to Conan-Core')

def populate_conan_like(conn):
    cursor = conn.cursor()

    # Get all monsters that match Conan-Like criteria
    query = '''
        SELECT id, name, type, challenge_rating
        FROM monsters
        WHERE
            -- Aberrations
            (LOWER(type) = 'aberration')

            -- Fiends
            OR (LOWER(type) = 'fiend')

            -- Oozes
            OR (LOWER(type) = 'ooze')

            -- Monstrosities
            OR (LOWER(type) = 'monstrosity')

            -- Humanoids
            OR (LOWER(type) = 'humanoid')

            -- Giants
            OR (LOWER(type) = 'giant')

            -- Constructs (excluding Modrons)
            OR (LOWER(type) = 'construct' AND LOWER(name) NOT LIKE '%modron%')

            -- Beasts CR 1 and over
            OR (LOWER(type) = 'beast' AND CAST(
                CASE
                    WHEN challenge_rating = '1/8' THEN 0.125
                    WHEN challenge_rating = '1/4' THEN 0.25
                    WHEN challenge_rating = '1/2' THEN 0.5
                    ELSE CAST(challenge_rating AS REAL)
                END AS REAL) >= 1.0)

            -- Undead
            OR (LOWER(type) = 'undead')

        ORDER BY challenge_rating, name
    '''

    cursor.execute(query)
    monsters = cursor.fetchall()

    print(f'\nPopulating Conan-Like with {len(monsters)} monsters...')
    print('=' * 60)

    # Determine level ranges based on CR
    def get_level_range(cr):
        cr_map = {
            '0': (1, 2), '1/8': (1, 3), '1/4': (1, 4), '1/2': (1, 5),
            '1': (1, 6), '2': (2, 7), '3': (3, 8), '4': (4, 9),
            '5': (5, 10), '6': (6, 11), '7': (7, 12), '8': (8, 13),
            '9': (9, 14), '10': (10, 15), '11': (11, 16), '12': (12, 17),
            '13': (13, 18), '14': (14, 19), '15': (15, 20), '16': (16, 20),
            '17': (17, 20), '18': (18, 20), '19': (19, 20), '20': (20, 20),
        }
        return cr_map.get(cr, (1, 20))

    added = 0
    skipped = 0
    by_type = {}

    for monster_id, name, mtype, cr in monsters:
        # Check if already exists
        cursor.execute(
            'SELECT id FROM campaign_monsters WHERE campaign_id = ? AND monster_id = ?',
            ('conan-like', monster_id)
        )

        if cursor.fetchone():
            skipped += 1
            continue

        min_level, max_level = get_level_range(cr)

        new_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO campaign_monsters
            (id, campaign_id, monster_id, encounter_weight, min_party_level, max_party_level, is_boss)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (new_id, 'conan-like', monster_id, 1, min_level, max_level, 0))

        added += 1

        # Track by type
        if mtype not in by_type:
            by_type[mtype] = 0
        by_type[mtype] += 1

    conn.commit()

    print(f'\n[OK] Added {added} monsters to Conan-Like')
    print(f'[SKIP] Skipped {skipped} (already existed)')

    print('\nMonsters by type:')
    for mtype, count in sorted(by_type.items()):
        print(f'  {mtype}: {count}')

def main():
    print('Conan Campaign Creator')
    print('=' * 60)

    conn = sqlite3.connect(DB_PATH)

    try:
        # Create campaigns table
        create_campaigns_table(conn)

        # Create campaign entries
        create_conan_campaigns(conn)

        # Populate Conan-Core (89 monsters)
        populate_conan_core(conn)

        # Populate Conan-Like (expanded)
        populate_conan_like(conn)

        # Show stats
        cursor = conn.cursor()

        print('\n' + '=' * 60)
        print('CAMPAIGN STATISTICS')
        print('=' * 60)

        for campaign_id in ['conan-core', 'conan-like']:
            cursor.execute(
                'SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ?',
                (campaign_id,)
            )
            total = cursor.fetchone()[0]

            cursor.execute(
                'SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ? AND is_boss = 1',
                (campaign_id,)
            )
            bosses = cursor.fetchone()[0]

            print(f'\n{campaign_id.upper()}:')
            print(f'  Total monsters: {total}')
            print(f'  Boss monsters: {bosses}')
            print(f'  Regular monsters: {total - bosses}')

        print('\n[SUCCESS] Conan campaigns created!')

    finally:
        conn.close()

if __name__ == '__main__':
    main()
