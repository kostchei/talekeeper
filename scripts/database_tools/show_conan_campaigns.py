# core
#utility
# core
import sqlite3

DB_PATH = '../../talekeeper.db'

def show_campaign_stats(conn):
    cursor = conn.cursor()

    print('=' * 80)
    print('CONAN CAMPAIGN COMPARISON')
    print('=' * 80)

    campaigns = ['conan-core', 'conan-like']

    for campaign_id in campaigns:
        cursor.execute('SELECT name FROM campaigns WHERE id = ?', (campaign_id,))
        campaign_name = cursor.fetchone()[0]

        print(f'\n### {campaign_name.upper()} ({campaign_id})')
        print('-' * 60)

        # Total monsters
        cursor.execute(
            'SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ?',
            (campaign_id,)
        )
        total = cursor.fetchone()[0]
        print(f'Total Monsters: {total}')

        # By type
        cursor.execute('''
            SELECT m.type, COUNT(*) as count
            FROM campaign_monsters cm
            JOIN monsters m ON cm.monster_id = m.id
            WHERE cm.campaign_id = ?
            GROUP BY m.type
            ORDER BY count DESC
        ''', (campaign_id,))

        print('\nMonsters by Type:')
        for mtype, count in cursor.fetchall():
            print(f'  {mtype}: {count}')

        # By CR range
        cursor.execute('''
            SELECT
                CASE
                    WHEN m.challenge_rating IN ('0', '1/8', '1/4', '1/2') THEN 'CR 0-1/2'
                    WHEN m.challenge_rating IN ('1', '2', '3', '4') THEN 'CR 1-4'
                    WHEN m.challenge_rating IN ('5', '6', '7', '8') THEN 'CR 5-8'
                    WHEN m.challenge_rating IN ('9', '10', '11', '12') THEN 'CR 9-12'
                    ELSE 'CR 13+'
                END as cr_range,
                COUNT(*) as count
            FROM campaign_monsters cm
            JOIN monsters m ON cm.monster_id = m.id
            WHERE cm.campaign_id = ?
            GROUP BY cr_range
            ORDER BY
                CASE cr_range
                    WHEN 'CR 0-1/2' THEN 1
                    WHEN 'CR 1-4' THEN 2
                    WHEN 'CR 5-8' THEN 3
                    WHEN 'CR 9-12' THEN 4
                    ELSE 5
                END
        ''', (campaign_id,))

        print('\nMonsters by CR Range:')
        for cr_range, count in cursor.fetchall():
            print(f'  {cr_range}: {count}')

        # Boss monsters
        cursor.execute(
            'SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ? AND is_boss = 1',
            (campaign_id,)
        )
        bosses = cursor.fetchone()[0]
        print(f'\nBoss Monsters: {bosses}')

def show_sample_monsters(conn):
    cursor = conn.cursor()

    print('\n' + '=' * 80)
    print('SAMPLE MONSTERS FROM EACH CAMPAIGN')
    print('=' * 80)

    campaigns = ['conan-core', 'conan-like']

    for campaign_id in campaigns:
        cursor.execute('SELECT name FROM campaigns WHERE id = ?', (campaign_id,))
        campaign_name = cursor.fetchone()[0]

        print(f'\n### {campaign_name.upper()} - Sample (10 random monsters)')
        print('-' * 60)

        cursor.execute('''
            SELECT m.name, m.type, m.challenge_rating
            FROM campaign_monsters cm
            JOIN monsters m ON cm.monster_id = m.id
            WHERE cm.campaign_id = ?
            ORDER BY RANDOM()
            LIMIT 10
        ''', (campaign_id,))

        for name, mtype, cr in cursor.fetchall():
            print(f'  {name} ({mtype}, CR {cr})')

def show_unique_to_conan_like(conn):
    cursor = conn.cursor()

    print('\n' + '=' * 80)
    print('MONSTERS UNIQUE TO CONAN-LIKE (not in Conan-Core)')
    print('=' * 80)

    cursor.execute('''
        SELECT m.name, m.type, m.challenge_rating, COUNT(*) as count
        FROM campaign_monsters cm
        JOIN monsters m ON cm.monster_id = m.id
        WHERE cm.campaign_id = 'conan-like'
          AND cm.monster_id NOT IN (
              SELECT monster_id FROM campaign_monsters WHERE campaign_id = 'conan-core'
          )
        GROUP BY m.type
        ORDER BY m.type, m.challenge_rating
    ''')

    current_type = None
    type_counts = {}

    cursor.execute('''
        SELECT m.type, COUNT(*) as count
        FROM campaign_monsters cm
        JOIN monsters m ON cm.monster_id = m.id
        WHERE cm.campaign_id = 'conan-like'
          AND cm.monster_id NOT IN (
              SELECT monster_id FROM campaign_monsters WHERE campaign_id = 'conan-core'
          )
        GROUP BY m.type
        ORDER BY count DESC
    ''')

    print('\nAdditional monsters by type:')
    total_unique = 0
    for mtype, count in cursor.fetchall():
        print(f'  {mtype}: +{count} monsters')
        total_unique += count

    print(f'\nTotal unique to Conan-Like: {total_unique}')

def show_query_examples(conn):
    cursor = conn.cursor()

    print('\n' + '=' * 80)
    print('EXAMPLE QUERIES')
    print('=' * 80)

    # Example 1: Get level-appropriate monsters
    print('\n### Query 1: Level 5 appropriate monsters for Conan-Core')
    print('-' * 60)
    cursor.execute('''
        SELECT m.name, m.type, m.challenge_rating
        FROM campaign_monsters cm
        JOIN monsters m ON cm.monster_id = m.id
        WHERE cm.campaign_id = 'conan-core'
          AND cm.min_party_level <= 5
          AND cm.max_party_level >= 5
        ORDER BY m.challenge_rating
        LIMIT 10
    ''')

    for name, mtype, cr in cursor.fetchall():
        print(f'  {name} ({mtype}, CR {cr})')

    # Example 2: Get fiends from Conan-Like
    print('\n### Query 2: All Fiends in Conan-Like')
    print('-' * 60)
    cursor.execute('''
        SELECT m.name, m.challenge_rating
        FROM campaign_monsters cm
        JOIN monsters m ON cm.monster_id = m.id
        WHERE cm.campaign_id = 'conan-like'
          AND LOWER(m.type) = 'fiend'
        ORDER BY m.challenge_rating
        LIMIT 15
    ''')

    for name, cr in cursor.fetchall():
        print(f'  {name} (CR {cr})')

    # Example 3: Boss monsters
    print('\n### Query 3: Boss Monsters in Conan-Core')
    print('-' * 60)
    cursor.execute('''
        SELECT m.name, m.type, m.challenge_rating, cm.min_party_level, cm.max_party_level
        FROM campaign_monsters cm
        JOIN monsters m ON cm.monster_id = m.id
        WHERE cm.campaign_id = 'conan-core'
          AND cm.is_boss = 1
        ORDER BY m.challenge_rating
    ''')

    for name, mtype, cr, min_lvl, max_lvl in cursor.fetchall():
        print(f'  {name} ({mtype}, CR {cr}) - Levels {min_lvl}-{max_lvl}')

def main():
    conn = sqlite3.connect(DB_PATH)

    try:
        show_campaign_stats(conn)
        show_sample_monsters(conn)
        show_unique_to_conan_like(conn)
        show_query_examples(conn)

    finally:
        conn.close()

if __name__ == '__main__':
    main()
