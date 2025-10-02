import json
import sqlite3

def normalize_name(name):
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def load_json_monsters():
    with open('monsters_extracted.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def format_actions(actions):
    if not actions:
        return '[]'
    formatted = []
    for action in actions:
        formatted.append({
            'name': action.get('name', ''),
            'entries': [action.get('description', '')]
        })
    return json.dumps(formatted)

def format_traits(traits):
    if not traits:
        return '[]'
    formatted = []
    for trait in traits:
        formatted.append({
            'name': trait.get('name', ''),
            'entries': [trait.get('description', '')]
        })
    return json.dumps(formatted)

def main():
    print("Loading monsters from JSON...")
    json_monsters = load_json_monsters()
    json_monster_map = {normalize_name(m['name']): m for m in json_monsters}

    print("Connecting to database...")
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM monsters")
    all_monsters = cursor.fetchall()

    updated = 0
    errors = 0

    print("\nUpdating monster stats from JSON...\n")

    for monster_id, monster_name in all_monsters:
        normalized = normalize_name(monster_name)

        if normalized in json_monster_map:
            m = json_monster_map[normalized]

            update_parts = []
            params = []

            if 'ac' in m and m['ac']:
                update_parts.append("armor_class = ?")
                params.append(int(m['ac']) if isinstance(m['ac'], (int, str)) and str(m['ac']).isdigit() else m['ac'])

            if 'hp' in m and m['hp']:
                update_parts.append("hit_points = ?")
                params.append(int(m['hp']) if isinstance(m['hp'], (int, str)) and str(m['hp']).isdigit() else m['hp'])

            if 'cr' in m and m['cr']:
                update_parts.append("challenge_rating = ?")
                params.append(str(m['cr']))

            if 'size' in m and m['size']:
                update_parts.append("size = ?")
                params.append(m['size'])

            if 'type' in m and m['type']:
                update_parts.append("type = ?")
                params.append(m['type'].lower())

            if 'alignment' in m and m['alignment']:
                update_parts.append("alignment = ?")
                params.append(m['alignment'])

            if 'str' in m and m['str']:
                update_parts.append("strength = ?")
                params.append(int(m['str']))

            if 'dex' in m and m['dex']:
                update_parts.append("dexterity = ?")
                params.append(int(m['dex']))

            if 'con' in m and m['con']:
                update_parts.append("constitution = ?")
                params.append(int(m['con']))

            if 'int' in m and m['int']:
                update_parts.append("intelligence = ?")
                params.append(int(m['int']))

            if 'wis' in m and m['wis']:
                update_parts.append("wisdom = ?")
                params.append(int(m['wis']))

            if 'cha' in m and m['cha']:
                update_parts.append("charisma = ?")
                params.append(int(m['cha']))

            if 'actions' in m and m['actions']:
                update_parts.append("actions = ?")
                params.append(format_actions(m['actions']))

            if 'traits' in m and m['traits']:
                update_parts.append("special_abilities = ?")
                params.append(format_traits(m['traits']))

            if 'legendary_actions' in m and m['legendary_actions']:
                update_parts.append("legendary_actions = ?")
                params.append(format_actions(m['legendary_actions']))

            if update_parts:
                try:
                    params.append(monster_id)
                    query = f"UPDATE monsters SET {', '.join(update_parts)} WHERE id = ?"
                    cursor.execute(query, params)
                    updated += 1
                    print(f"Updated: {monster_name}")
                except Exception as e:
                    errors += 1
                    print(f"ERROR updating {monster_name}: {e}")

    conn.commit()

    print(f"\n=== RESULTS ===")
    print(f"Updated: {updated}")
    print(f"Errors: {errors}")

    cursor.execute("SELECT name, armor_class, hit_points, challenge_rating FROM monsters WHERE name IN ('Lich', 'Rakshasa', 'Aboleth', 'Assassin') ORDER BY name")
    print("\n=== VERIFICATION (Critical Monsters) ===")
    for row in cursor.fetchall():
        print(f"{row[0]}: AC={row[1]}, HP={row[2]}, CR={row[3]}")

    conn.close()

if __name__ == '__main__':
    main()
