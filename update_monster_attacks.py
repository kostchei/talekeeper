import json
import sqlite3
import re

def parse_action_entry(entry_text):
    attack_info = {}

    attack_match = re.search(r'(?:Melee|Ranged)\s+Attack\s+Roll:\s*\+(\d+)', entry_text, re.IGNORECASE)
    if attack_match:
        attack_info['attack_bonus'] = int(attack_match.group(1))

    reach_match = re.search(r'reach\s+(\d+\s*ft)', entry_text, re.IGNORECASE)
    range_match = re.search(r'range\s+([\d/]+\s*ft)', entry_text, re.IGNORECASE)
    if reach_match:
        attack_info['reach'] = reach_match.group(1)
    elif range_match:
        attack_info['reach'] = range_match.group(1)

    damage_match = re.search(r'(\d+)\s*\(([^)]+)\)\s*(\w+)\s*damage', entry_text, re.IGNORECASE)
    if damage_match:
        attack_info['damage_dice'] = damage_match.group(2).strip()
        attack_info['damage_type'] = damage_match.group(3).strip()

    return attack_info

def update_monster_from_srd(conn, monster_name, srd_attacks):
    cursor = conn.cursor()

    cursor.execute("SELECT id, actions FROM monsters WHERE name = ?", (monster_name,))
    result = cursor.fetchone()

    if not result:
        print(f"  Monster not found: {monster_name}")
        return False

    monster_id, actions_json = result

    try:
        actions = json.loads(actions_json) if actions_json else []
    except:
        actions = []

    updates_made = False

    for srd_attack in srd_attacks:
        attack_name = srd_attack['name'].strip()

        found = False
        for i, action in enumerate(actions):
            if not isinstance(action, dict):
                continue

            db_name = action.get('name', '').strip()
            if attack_name.lower() in db_name.lower() or db_name.lower() in attack_name.lower():
                found = True

                entries = action.get('entries', [])
                if entries and isinstance(entries, list):
                    entry_text = entries[0] if entries else ''

                    new_entry = f"Melee Attack Roll: +{srd_attack['attack_bonus']}, reach {srd_attack['reach_range']}. Hit: {srd_attack['damage_avg']} ({srd_attack['damage_dice']}) {srd_attack['damage_type']} damage."

                    if entry_text != new_entry:
                        actions[i]['entries'] = [new_entry]
                        updates_made = True
                        print(f"  Updated: {attack_name}")
                break

        if not found:
            new_action = {
                'name': attack_name,
                'entries': [
                    f"Melee Attack Roll: +{srd_attack['attack_bonus']}, reach {srd_attack['reach_range']}. Hit: {srd_attack['damage_avg']} ({srd_attack['damage_dice']}) {srd_attack['damage_type']} damage."
                ]
            }
            actions.append(new_action)
            updates_made = True
            print(f"  Added: {attack_name}")

    if updates_made:
        cursor.execute(
            "UPDATE monsters SET actions = ? WHERE id = ?",
            (json.dumps(actions), monster_id)
        )

        primary_attack = srd_attacks[0] if srd_attacks else None
        if primary_attack:
            cursor.execute("""
                UPDATE monsters
                SET primary_attack_name = ?,
                    primary_attack_bonus = ?,
                    primary_attack_reach = ?,
                    primary_damage_dice = ?,
                    primary_damage_type = ?
                WHERE id = ?
            """, (
                primary_attack['name'],
                primary_attack['attack_bonus'],
                primary_attack['reach_range'],
                primary_attack['damage_dice'],
                primary_attack['damage_type'],
                monster_id
            ))

    return updates_made

def main():
    print("Loading monster attack discrepancies...")
    with open('monster_attack_discrepancies.json', 'r') as f:
        discrepancies = json.load(f)

    print(f"Loaded {len(discrepancies)} monsters with issues\n")

    conn = sqlite3.connect('talekeeper.db')

    print("Running migration...")
    with open('database/migrations/022_restructure_monster_attacks.sql', 'r') as f:
        migration_sql = f.read()

    try:
        for statement in migration_sql.split(';'):
            if statement.strip():
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as e:
                    if 'duplicate column' not in str(e).lower():
                        raise
    except Exception as e:
        print(f"Migration error (may be already applied): {e}")

    conn.commit()
    print("Migration complete\n")

    print("Updating monster attacks from SRD data...\n")

    updated_count = 0
    for monster_data in discrepancies:
        monster_name = monster_data['name']
        srd_attacks = monster_data['srd_attacks']

        if not srd_attacks:
            continue

        print(f"Processing: {monster_name}")
        if update_monster_from_srd(conn, monster_name, srd_attacks):
            updated_count += 1
        print()

    conn.commit()

    print(f"\n=== SUMMARY ===")
    print(f"Monsters processed: {len(discrepancies)}")
    print(f"Monsters updated: {updated_count}")

    print("\n=== VERIFICATION ===")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, primary_attack_name, primary_attack_bonus, primary_damage_dice, primary_damage_type
        FROM monsters
        WHERE name IN ('Air Elemental', 'Barbed Devil', 'Goblin')
        ORDER BY name
    """)

    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} (+{row[2]}) {row[3]} {row[4]}")

    conn.close()
    print("\nUpdate complete!")

if __name__ == '__main__':
    main()
