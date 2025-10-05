import json
import sqlite3
import sys
from pathlib import Path

def normalize_name(name):
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def load_json_monsters():
    with open('monsters_extracted.json', 'r') as f:
        return json.load(f)

def get_db_monsters(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM monsters")
    return {normalize_name(row[1]): row[0] for row in cursor.fetchall()}

def extract_stat(monster, stat_name):
    if 'stats' in monster and monster['stats']:
        for stat in monster['stats']:
            if stat.get('name', '').lower() == stat_name.lower():
                return stat.get('value')
    return None

def extract_abilities(monster):
    abilities = {}
    ability_names = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']

    if 'abilities' in monster:
        for ability in monster['abilities']:
            name = ability.get('name', '').upper()
            if name in ability_names:
                score = ability.get('score')
                if score and score.isdigit():
                    abilities[name.lower()] = int(score)

    return abilities

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

def update_monster(conn, monster_id, monster_data):
    abilities = extract_abilities(monster_data)

    ac = extract_stat(monster_data, 'AC')
    hp = extract_stat(monster_data, 'HP')
    cr = extract_stat(monster_data, 'CR')

    if ac and isinstance(ac, str) and ac.isdigit():
        ac = int(ac)
    if hp and isinstance(hp, str) and hp.isdigit():
        hp = int(hp)

    update_parts = []
    params = []

    if ac is not None:
        update_parts.append("armor_class = ?")
        params.append(ac)

    if hp is not None:
        update_parts.append("hit_points = ?")
        params.append(hp)

    if cr is not None:
        update_parts.append("challenge_rating = ?")
        params.append(str(cr))

    if 'size' in monster_data and monster_data['size']:
        update_parts.append("size = ?")
        params.append(monster_data['size'])

    if 'type' in monster_data and monster_data['type']:
        update_parts.append("type = ?")
        params.append(monster_data['type'].lower())

    if 'alignment' in monster_data and monster_data['alignment']:
        update_parts.append("alignment = ?")
        params.append(monster_data['alignment'])

    for ability_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
        short_name = ability_name[:3].lower()
        if short_name in abilities:
            update_parts.append(f"{ability_name} = ?")
            params.append(abilities[short_name])

    if 'actions' in monster_data and monster_data['actions']:
        update_parts.append("actions = ?")
        params.append(format_actions(monster_data['actions']))

    if 'traits' in monster_data and monster_data['traits']:
        update_parts.append("special_abilities = ?")
        params.append(format_traits(monster_data['traits']))

    if 'legendary_actions' in monster_data and monster_data['legendary_actions']:
        update_parts.append("legendary_actions = ?")
        params.append(format_actions(monster_data['legendary_actions']))

    if update_parts:
        params.append(monster_id)
        query = f"UPDATE monsters SET {', '.join(update_parts)} WHERE id = ?"
        conn.execute(query, params)
        return True
    return False

def insert_new_monster(conn, monster_data):
    abilities = extract_abilities(monster_data)

    ac = extract_stat(monster_data, 'AC')
    hp = extract_stat(monster_data, 'HP')
    cr = extract_stat(monster_data, 'CR')

    if ac and isinstance(ac, str) and ac.isdigit():
        ac = int(ac)
    if hp and isinstance(hp, str) and hp.isdigit():
        hp = int(hp)

    name = monster_data.get('name', 'Unknown')
    monster_id = normalize_name(name).replace(' ', '_')

    conn.execute('''
        INSERT INTO monsters (
            id, name, type, size, alignment, armor_class, hit_points,
            challenge_rating, strength, dexterity, constitution,
            intelligence, wisdom, charisma, actions, special_abilities, legendary_actions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        monster_id,
        name,
        monster_data.get('type', '').lower() if monster_data.get('type') else None,
        monster_data.get('size'),
        monster_data.get('alignment'),
        ac,
        hp,
        str(cr) if cr else None,
        abilities.get('str', 10),
        abilities.get('dex', 10),
        abilities.get('con', 10),
        abilities.get('int', 10),
        abilities.get('wis', 10),
        abilities.get('cha', 10),
        format_actions(monster_data.get('actions', [])),
        format_traits(monster_data.get('traits', [])),
        format_actions(monster_data.get('legendary_actions', []))
    ))
    return monster_id

def main():
    print("Loading monsters from JSON...")
    json_monsters = load_json_monsters()
    print(f"Loaded {len(json_monsters)} monsters from JSON")

    print("\nConnecting to database...")
    conn = sqlite3.connect('talekeeper.db')

    print("Getting existing monsters from database...")
    db_monsters = get_db_monsters(conn)
    print(f"Found {len(db_monsters)} monsters in database")

    json_monster_map = {normalize_name(m['name']): m for m in json_monsters}

    updated_count = 0
    new_count = 0
    skipped_count = 0

    print("\n=== STEP 1: Updating existing monsters with 2024 stats ===")
    for json_name, monster_data in json_monster_map.items():
        if json_name in db_monsters:
            if update_monster(conn, db_monsters[json_name], monster_data):
                updated_count += 1
                print(f"Updated: {monster_data['name']}")
            else:
                skipped_count += 1

    print(f"\nStep 1 complete: {updated_count} monsters updated, {skipped_count} skipped (no changes)")

    print("\n=== STEP 2: Adding new 2024 monsters ===")
    for json_name, monster_data in json_monster_map.items():
        if json_name not in db_monsters:
            monster_id = insert_new_monster(conn, monster_data)
            new_count += 1
            print(f"Added: {monster_data['name']} (id: {monster_id})")

    print(f"\nStep 2 complete: {new_count} new monsters added")

    conn.commit()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM monsters")
    total = cursor.fetchone()[0]

    print(f"\n=== SUMMARY ===")
    print(f"Monsters updated: {updated_count}")
    print(f"New monsters added: {new_count}")
    print(f"Total monsters in database: {total}")
    print(f"\nChanges committed to database.")

    conn.close()

if __name__ == '__main__':
    main()
