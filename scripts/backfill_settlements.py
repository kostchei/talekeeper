# core
#utility
# core
"""
Backfill settlement_type for existing hexes that don't have it.
This updates hexes that were created before settlement generation was implemented.
"""
import sqlite3
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def get_position_seed(q: int, r: int) -> int:
    prime1, prime2 = 73856093, 19349663
    return abs((q * prime1) ^ (r * prime2)) % (2**31)

def generate_settlement_type(seed: int) -> str:
    random.seed(seed)
    settlement_roll = random.randint(1, 100)

    if settlement_roll <= 6:
        return 'empty'
    elif settlement_roll <= 31:
        return 'hamlet'
    elif settlement_roll <= 99:
        return 'village'
    else:
        town_roll = random.randint(1, 6)
        if town_roll <= 3:
            return 'town_small'
        elif town_roll <= 5:
            return 'town_medium'
        else:
            return 'town_large'

def backfill_settlements(db_path: str = 'talekeeper.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT character_id, q, r, encounter_seed
        FROM character_hex_map
        WHERE settlement_type IS NULL OR settlement_type = ''
    """)

    hexes_to_update = cursor.fetchall()

    print(f"Found {len(hexes_to_update)} hexes to backfill")

    for character_id, q, r, encounter_seed in hexes_to_update:
        seed = encounter_seed if encounter_seed else get_position_seed(q, r)
        settlement_type = generate_settlement_type(seed)

        cursor.execute("""
            UPDATE character_hex_map
            SET settlement_type = ?
            WHERE character_id = ? AND q = ? AND r = ?
        """, (settlement_type, character_id, q, r))

        print(f"  Hex ({q}, {r}) for character {character_id[:8]}... -> {settlement_type}")

    conn.commit()
    conn.close()

    print(f"\nBackfilled {len(hexes_to_update)} hexes with settlement data")

if __name__ == '__main__':
    backfill_settlements()
