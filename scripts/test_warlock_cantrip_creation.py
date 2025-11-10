"""Test warlock cantrip saving during character creation"""
import sys
import sqlite3
sys.path.insert(0, 'src')

from talekeeper.core.game_engine_sqlite import GameEngineSQLite

# Create a test warlock with cantrips
character_data = {
    'name': 'TestWarlockDebug',
    'class_id': 'warlock',
    'background_id': 'acolyte',
    'race_id': 'human',
    'level': 1,
    'experience_points': 0,
    'strength': 10,
    'dexterity': 14,
    'constitution': 13,
    'intelligence': 12,
    'wisdom': 10,
    'charisma': 16,
    'hit_points_max': 8,
    'hit_points_current': 8,
    'armor_class': 12,
    'selected_cantrips': ['eldritch_blast', 'chill_touch'],
    'selected_spells': ['hex', 'hellish_rebuke'],
    'selected_class_skills': ['arcana', 'deception'],
    'selected_species_skills': []
}

print("Creating test warlock with cantrips:")
print(f"  selected_cantrips: {character_data['selected_cantrips']}")
print(f"  selected_spells: {character_data['selected_spells']}")

# Create the character
engine = GameEngineSQLite('talekeeper.db')

# Find an empty save slot
import sqlite3
test_conn = sqlite3.connect('talekeeper.db')
test_cursor = test_conn.cursor()
test_cursor.execute("SELECT slot_number FROM save_slots WHERE is_occupied = 0 ORDER BY slot_number LIMIT 1")
empty_slot = test_cursor.fetchone()
save_slot = empty_slot[0] if empty_slot else 10  # Use slot 10 if none available
test_conn.close()

print(f"Using save slot: {save_slot}\n")
result = engine.create_new_character_sync(character_data, save_slot)

print(f"\nCharacter creation result: {result is not None}")

if result:
    char_id = result['id']
    print(f"Character ID: {char_id}")

    # Check what was actually saved
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT s.name, s.level, cs.is_prepared
        FROM character_spells cs
        JOIN spells s ON cs.spell_id = s.id
        WHERE cs.character_id = ?
        ORDER BY s.level, s.name
    ''', (char_id,))

    spells = cursor.fetchall()
    print(f"\nSpells in database: {len(spells)}")
    for spell_name, spell_level, is_prepared in spells:
        level_text = 'Cantrip' if spell_level == 0 else f'Level {spell_level}'
        print(f"  - {spell_name} ({level_text}, prepared={is_prepared})")

    # Clean up - delete test character
    cursor.execute('DELETE FROM characters WHERE id = ?', (char_id,))
    conn.commit()
    conn.close()

    print("\nTest character cleaned up")
else:
    print("Character creation failed!")
