import json
import sqlite3

def normalize_name(name):
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def load_json_monsters():
    with open('monsters_extracted.json', 'r') as f:
        return json.load(f)

def main():
    print("Loading 2024 monsters from JSON...")
    json_monsters = load_json_monsters()
    json_names = {normalize_name(m['name']) for m in json_monsters}
    print(f"Found {len(json_names)} unique 2024 monster names")

    print("\nConnecting to database...")
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM monsters")
    all_db_monsters = cursor.fetchall()

    db_only_monsters = []
    for monster_id, monster_name in all_db_monsters:
        normalized = normalize_name(monster_name)
        if normalized not in json_names:
            db_only_monsters.append((monster_id, monster_name, normalized))

    print(f"\nFound {len(db_only_monsters)} monsters in DB that are NOT in 2024 JSON")

    if not db_only_monsters:
        print("No legacy monsters to check!")
        conn.close()
        return

    print("\n=== Checking for duplicates vs 2024 variants ===")

    duplicates = []
    unique_5e = []

    for monster_id, monster_name, normalized in db_only_monsters:
        is_duplicate = False

        for json_name in json_names:
            if normalized in json_name or json_name in normalized:
                if normalized != json_name:
                    is_duplicate = True
                    duplicates.append((monster_id, monster_name, f"Duplicate of 2024 variant: {json_name}"))
                    break

        core_name = normalized.replace('elite ', '').replace('young ', '').replace('ancient ', '').replace('adult ', '')
        for json_name in json_names:
            json_core = json_name.replace('elite ', '').replace('young ', '').replace('ancient ', '').replace('adult ', '')
            if core_name == json_core and normalized != json_name:
                is_duplicate = True
                duplicates.append((monster_id, monster_name, f"Variant exists in 2024: {json_name}"))
                break

        if not is_duplicate:
            unique_5e.append((monster_id, monster_name))

    print(f"\n=== RESULTS ===")
    print(f"Total legacy monsters: {len(db_only_monsters)}")
    print(f"Duplicates (have 2024 equivalent): {len(duplicates)}")
    print(f"Unique 5e-only (keep): {len(unique_5e)}")

    if duplicates:
        print(f"\n=== DUPLICATES TO REMOVE ({len(duplicates)}) ===")
        for monster_id, monster_name, reason in duplicates[:20]:
            print(f"  - {monster_name} ({monster_id}): {reason}")
        if len(duplicates) > 20:
            print(f"  ... and {len(duplicates) - 20} more")

    if unique_5e:
        print(f"\n=== UNIQUE 5e MONSTERS TO KEEP ({len(unique_5e)}) ===")
        for monster_id, monster_name in unique_5e[:30]:
            print(f"  - {monster_name} ({monster_id})")
        if len(unique_5e) > 30:
            print(f"  ... and {len(unique_5e) - 30} more")

    print("\n=== REMOVING DUPLICATES ===")
    if duplicates:
        for monster_id, monster_name, reason in duplicates:
            cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
            print(f"Deleted: {monster_name}")
        conn.commit()
        print(f"\nRemoved {len(duplicates)} duplicate monsters")

    cursor.execute("SELECT COUNT(*) FROM monsters")
    final_count = cursor.fetchone()[0]
    print(f"\nFinal monster count: {final_count}")

    cursor.execute("SELECT name FROM monsters WHERE id IN ({})".format(','.join(['?'] * len(unique_5e))),
                   [m[0] for m in unique_5e])
    kept_names = [row[0] for row in cursor.fetchall()]
    print(f"Kept {len(kept_names)} unique 5e monsters")

    with open('unique_5e_monsters_kept.txt', 'w') as f:
        f.write("UNIQUE D&D 5e MONSTERS KEPT\n")
        f.write("=" * 50 + "\n\n")
        for name in sorted(kept_names):
            f.write(f"- {name}\n")

    print("\nSaved list to: unique_5e_monsters_kept.txt")

    conn.close()

if __name__ == '__main__':
    main()
