"""Test warlock action card creation"""
import sys
import sqlite3
sys.path.insert(0, 'src')

from talekeeper.services.spellcasting_service import SpellcastingService

def test_warlock_spell_cards():
    char_id = '38140dc8-38e9-4fda-84b6-d43fc5b3e807'
    db_path = 'talekeeper.db'

    # Get character info
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, class_id, level FROM characters WHERE id = ?", (char_id,))
    char_info = cursor.fetchone()
    print(f"Character: {char_info}")

    # Get spells
    cursor.execute("""
        SELECT cs.spell_id, s.level as spell_level, cs.is_prepared, cs.always_prepared,
               s.name, s.school, s.casting_time, s.range_value, s.components,
               s.duration, s.concentration, s.description
        FROM character_spells cs
        JOIN spells s ON cs.spell_id = s.id
        WHERE cs.character_id = ?
        AND (cs.is_prepared = 1 OR s.level = 0 OR cs.always_prepared = 1)
        ORDER BY s.level, s.name
    """, (char_id,))

    spells = []
    spellcasting_service = SpellcastingService(db_path)

    for row in cursor.fetchall():
        spell_data = {
            'spell_id': row[0],
            'spell_level': row[1],
            'is_prepared': row[2],
            'always_prepared': row[3],
            'name': row[4],
            'school': row[5],
            'casting_time': row[6],
            'range_value': row[7],
            'components': row[8],
            'duration': row[9],
            'concentration': row[10],
            'description': row[11]
        }

        # Check if character has spell slots for this spell (except cantrips)
        if spell_data['spell_level'] > 0:
            can_cast, reason = spellcasting_service.can_cast_spell(char_id, spell_data['spell_id'])
            if not can_cast:
                print(f"  Skipping {spell_data['name']}: {reason}")
                continue

        spells.append(spell_data)

    print(f"\nFound {len(spells)} castable spells:")
    for spell in spells:
        print(f"  - {spell['name']} (level {spell['spell_level']}, casting_time: {spell['casting_time']})")

    # Get spell slots
    spell_slots = spellcasting_service.get_character_spell_slots(char_id)
    print(f"\nSpell slots:")
    for slot in spell_slots:
        print(f"  - Level {slot.level} ({slot.slot_type.value}): {slot.available_slots}/{slot.max_slots}")

    # Simulate card creation logic
    is_warlock = True
    pact_slot_level = None

    if is_warlock:
        pact_slots = [slot for slot in spell_slots if slot.slot_type.value == 'pact']
        if pact_slots:
            pact_slot_level = pact_slots[0].level
            print(f"\nWarlock detected - Pact Magic slot level: {pact_slot_level}")

    spells_by_level_and_type = {}
    for spell in spells:
        spell_level = spell['spell_level']
        casting_time = spell.get('casting_time', '').lower()

        if 'bonus action' in casting_time:
            cast_type = 'bonus'
        elif 'reaction' in casting_time:
            cast_type = 'reaction'
        else:
            cast_type = 'action'

        if is_warlock and spell_level > 0 and pact_slot_level:
            effective_level = pact_slot_level
        else:
            effective_level = spell_level

        key = (effective_level, cast_type)
        if key not in spells_by_level_and_type:
            spells_by_level_and_type[key] = []
        spells_by_level_and_type[key].append(spell)

    print(f"\nSpell groups:")
    for (spell_level, cast_type), available_spells in spells_by_level_and_type.items():
        print(f"  - Level {spell_level}, {cast_type}: {[s['name'] for s in available_spells]}")

        slot_info = next((slot for slot in spell_slots if slot.level == spell_level), None)

        if spell_level == 0:
            available_slots = float('inf')
            max_slots = float('inf')
        elif slot_info:
            available_slots = slot_info.available_slots
            max_slots = slot_info.max_slots
        else:
            available_slots = 0
            max_slots = 0

        print(f"    Slot info: available={available_slots}, max={max_slots}")

        if spell_level > 0 and available_slots == 0:
            print(f"    SKIPPING - no available slots!")
        else:
            print(f"    WOULD CREATE CARD")

    conn.close()

if __name__ == '__main__':
    test_warlock_spell_cards()
