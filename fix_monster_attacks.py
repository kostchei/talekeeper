import json
import sqlite3

def main():
    print("Loading SRD parsed data...")
    with open('srd_monsters_parsed.json', 'r', encoding='utf-8') as f:
        srd_monsters = json.load(f)

    print(f"Loaded {len(srd_monsters)} SRD monsters\n")

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    print("Running migration...")
    try:
        with open('database/migrations/022_restructure_monster_attacks.sql', 'r') as f:
            migration_sql = f.read()

        for statement in migration_sql.split(';'):
            if statement.strip():
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as e:
                    if 'duplicate column' not in str(e).lower():
                        raise
    except Exception as e:
        print(f"Migration note: {e}")

    conn.commit()
    print("Migration complete\n")

    print("Updating monsters from SRD data...\n")

    updated_count = 0

    for srd_monster in srd_monsters:
        monster_name = srd_monster['name']
        srd_attacks = srd_monster.get('attacks', [])

        if not srd_attacks:
            continue

        cursor.execute("SELECT id, actions FROM monsters WHERE name = ?", (monster_name,))
        result = cursor.fetchone()

        if not result:
            continue

        monster_id, actions_json = result

        try:
            actions = json.loads(actions_json) if actions_json else []
        except:
            actions = []

        new_actions = []
        for action in actions:
            if isinstance(action, dict) and action.get('name') in ['Multiattack']:
                new_actions.append(action)

        for attack in srd_attacks:
            new_action = {
                'name': attack['name'],
                'entries': [
                    f"Melee Attack Roll: +{attack['attack_bonus']}, reach {attack['reach_range']}. Hit: {attack['damage_avg']} ({attack['damage_dice']}) {attack['damage_type']} damage."
                ]
            }
            new_actions.append(new_action)

        if new_actions:
            cursor.execute(
                "UPDATE monsters SET actions = ? WHERE id = ?",
                (json.dumps(new_actions), monster_id)
            )

            primary_attack = srd_attacks[0]
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

            updated_count += 1
            print(f"Updated: {monster_name} ({len(srd_attacks)} attacks)")

    conn.commit()

    print(f"\n=== SUMMARY ===")
    print(f"Monsters updated: {updated_count}")

    print("\n=== VERIFICATION ===")
    cursor.execute("""
        SELECT name, primary_attack_name, primary_attack_bonus, primary_damage_dice, primary_damage_type
        FROM monsters
        WHERE name IN ('Air Elemental', 'Barbed Devil', 'Goblin', 'Basilisk')
        ORDER BY name
    """)

    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} (+{row[2]}) {row[3]} {row[4]}")

    cursor.execute("""
        SELECT name, actions FROM monsters
        WHERE name = 'Air Elemental'
    """)
    name, actions = cursor.fetchone()
    print(f"\n{name} actions:")
    for action in json.loads(actions):
        print(f"  {action['name']}: {action['entries'][0][:80]}")

    conn.close()
    print("\nUpdate complete!")

if __name__ == '__main__':
    main()
