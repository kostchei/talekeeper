# core
#utility
# core
import sqlite3
import sys
from pathlib import Path

def cleanup_hex_maps(db_path: str, character_id: str = None, confirm: bool = False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if character_id:
        cursor.execute(
            'SELECT id, name FROM characters WHERE id = ?',
            (character_id,)
        )
        characters = cursor.fetchall()
        if not characters:
            print(f"Character {character_id} not found")
            conn.close()
            return
    else:
        cursor.execute('SELECT id, name FROM characters')
        characters = cursor.fetchall()

    if not characters:
        print("No characters found")
        conn.close()
        return

    print("Characters with hex map data:")
    print("-" * 60)

    total_hexes = 0
    for char_id, char_name in characters:
        cursor.execute(
            'SELECT COUNT(*) FROM character_hex_map WHERE character_id = ?',
            (char_id,)
        )
        hex_count = cursor.fetchone()[0]

        if hex_count > 0:
            print(f"{char_name:30} ({char_id}): {hex_count} hexes")
            total_hexes += hex_count

    print("-" * 60)
    print(f"Total hexes to clean: {total_hexes}")

    if total_hexes == 0:
        print("No hex data to clean")
        conn.close()
        return

    if not confirm:
        print("\nThis will delete:")
        print("- character_hex_map entries")
        print("- character_hex_position entries")
        print("- hex_events entries")
        print("- hex_combat_log entries")
        print("- hex_loot_log entries")
        print("- hex_narrative_log entries")
        print("\nHex maps will regenerate when characters travel next time.")
        print("\nRun with --confirm to proceed")
        conn.close()
        return

    print("\nCleaning up hex map data...")

    tables_to_clean = [
        'character_hex_map',
        'character_hex_position',
        'hex_events',
        'hex_combat_log',
        'hex_loot_log',
        'hex_narrative_log'
    ]

    for table in tables_to_clean:
        if character_id:
            cursor.execute(f'DELETE FROM {table} WHERE character_id = ?', (character_id,))
            deleted = cursor.rowcount
        else:
            cursor.execute(f'DELETE FROM {table}')
            deleted = cursor.rowcount
        print(f"  {table}: {deleted} rows deleted")

    conn.commit()
    conn.close()

    print("\nCleanup complete! Hex maps will regenerate on next character load.")

if __name__ == '__main__':
    db_path = Path(__file__).parent.parent.parent / 'talekeeper.db'

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        sys.exit(1)

    character_id = None
    confirm = False

    for arg in sys.argv[1:]:
        if arg == '--confirm':
            confirm = True
        elif arg.startswith('--character='):
            character_id = arg.split('=')[1]
        elif not arg.startswith('--'):
            character_id = arg

    cleanup_hex_maps(str(db_path), character_id, confirm)
