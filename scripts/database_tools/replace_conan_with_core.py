# core
#utility
# core
import sqlite3

DB_PATH = '../../talekeeper.db'

def replace_conan_campaign():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print('Replacing "conan" campaign with "conan-core" distribution...')

        cursor.execute('DELETE FROM campaign_monsters WHERE campaign_id = ?', ('conan',))
        deleted_count = cursor.rowcount
        print(f'  Deleted {deleted_count} old monsters from "conan"')

        cursor.execute('''
            INSERT INTO campaign_monsters (campaign_id, monster_id, min_party_level, max_party_level, is_boss)
            SELECT 'conan', monster_id, min_party_level, max_party_level, is_boss
            FROM campaign_monsters
            WHERE campaign_id = 'conan-core'
        ''')
        inserted_count = cursor.rowcount
        print(f'  Inserted {inserted_count} monsters from "conan-core" into "conan"')

        cursor.execute('UPDATE campaigns SET name = ? WHERE id = ?', ('Conan (Core)', 'conan'))

        conn.commit()
        print('\nSuccess! The "conan" campaign now matches "conan-core".')

        cursor.execute('SELECT COUNT(*) FROM campaign_monsters WHERE campaign_id = ?', ('conan',))
        final_count = cursor.fetchone()[0]
        print(f'Final count: {final_count} monsters in "conan" campaign')

    except Exception as e:
        conn.rollback()
        print(f'Error: {e}')
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    replace_conan_campaign()
