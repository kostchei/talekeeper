import sqlite3

db_path = 'talekeeper.db'
char_id = '3c17a911-88d7-422d-8999-949074b7f2ca'

print("=== SPELL HAND SYSTEM TEST ===\n")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.level, s.casting_time, s.concentration, cs.is_prepared
        FROM character_spells cs
        JOIN spells s ON cs.spell_id = s.id
        WHERE cs.character_id = ? AND (cs.is_prepared = 1 OR cs.always_prepared = 1)
        ORDER BY s.level, s.casting_time, s.name
    """, (char_id,))

    by_level_and_type = {}
    for row in cursor.fetchall():
        name, level, casting_time, concentration, is_prepared = row
        casting_type = 'action' if 'action' in casting_time.lower() and 'bonus' not in casting_time.lower() else \
                      'bonus' if 'bonus action' in casting_time.lower() else \
                      'reaction' if 'reaction' in casting_time.lower() else 'other'

        key = (level, casting_type)
        if key not in by_level_and_type:
            by_level_and_type[key] = []
        by_level_and_type[key].append({
            'name': name,
            'concentration': concentration
        })

    cursor.execute("""
        SELECT spell_level, max_slots, used_slots
        FROM character_spell_slots
        WHERE character_id = ?
    """, (char_id,))
    slots = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

print("Expected UI Display:\n")
print("=" * 60)

for (level, casting_type), spells in sorted(by_level_and_type.items()):
    max_slots, used_slots = slots.get(level, (0, 0))
    available = max_slots - used_slots

    tab = "Action" if casting_type == 'action' else \
          "Bonus" if casting_type == 'bonus' else \
          "Reaction" if casting_type == 'reaction' else "Other"

    print(f"\n[{tab}] Tab:")
    print(f"  Card Title: Lv {level} {available}/{max_slots}")
    print(f"  Spells in this hand:")
    for spell in spells:
        conc = " (Concentration)" if spell['concentration'] else ""
        print(f"    - {spell['name']}{conc}")

print("\n" + "=" * 60)
print("\nExpected Behavior:")
print("1. Divine Favor and Shield of Faith appear in [Bonus] tab")
print("2. Heroism appears in [Action] tab")
print("3. Card shows 'Lv 1 3/3' (no unicode stars)")
print("4. Description shows spell effects, not 'Time' or 'Range'")
print("5. Divine Favor shows NO concentration (2024 rule)")
