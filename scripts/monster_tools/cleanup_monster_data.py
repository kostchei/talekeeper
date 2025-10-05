import json
import sqlite3
import re

def clean_dice_notation(dice_str):
    if not dice_str:
        return dice_str
    cleaned = re.sub(r'\s*\n\s*', ' ', dice_str)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def clean_attack_name(name):
    if not name:
        return name
    cleaned = name.replace('Actions\n', '').replace('\n', ' ')
    return cleaned.strip()

def is_valid_attack_for_monster(attack_name, monster_cr):
    invalid_patterns = [
        'Bone Bow', 'Bone Cudgel', 'Force Bolt', 'Radiant Sword',
        'Withering Sword', 'Stone Club', 'Boulder'
    ]
    for pattern in invalid_patterns:
        if pattern.lower() in attack_name.lower():
            return False
    return True

def add_saving_throw(special_abilities, ability, dc):
    if not special_abilities:
        special_abilities = []

    try:
        abilities = json.loads(special_abilities) if isinstance(special_abilities, str) else special_abilities
    except:
        abilities = []

    save_name = f"{ability} Save"
    save_exists = False

    for ability_entry in abilities:
        if isinstance(ability_entry, dict):
            if save_name in ability_entry.get('name', '') or f'DC {dc}' in str(ability_entry.get('entries', [])):
                save_exists = True
                break

    if not save_exists:
        abilities.append({
            'name': save_name,
            'entries': [f"DC {dc} {ability} saving throw"]
        })

    return json.dumps(abilities)

def main():
    print("Loading SRD data for saving throws...")
    with open('srd_monsters_parsed.json', 'r', encoding='utf-8') as f:
        srd_monsters = json.load(f)

    srd_map = {m['name']: m for m in srd_monsters}

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    print("\n=== STEP 1: Clean dice notation whitespace ===\n")

    cursor.execute("SELECT id, name, actions, primary_damage_dice FROM monsters")
    monsters = cursor.fetchall()

    cleaned_count = 0

    for monster_id, name, actions_json, primary_dice in monsters:
        updates_made = False

        if actions_json:
            try:
                actions = json.loads(actions_json)
                for action in actions:
                    if isinstance(action, dict):
                        if action.get('name'):
                            old_name = action['name']
                            new_name = clean_attack_name(old_name)
                            if old_name != new_name:
                                action['name'] = new_name
                                updates_made = True

                        entries = action.get('entries', [])
                        for i, entry in enumerate(entries):
                            if isinstance(entry, str):
                                dice_match = re.search(r'\(([^)]+)\)', entry)
                                if dice_match:
                                    old_dice = dice_match.group(1)
                                    new_dice = clean_dice_notation(old_dice)
                                    if old_dice != new_dice:
                                        entries[i] = entry.replace(old_dice, new_dice)
                                        updates_made = True

                if updates_made:
                    cursor.execute("UPDATE monsters SET actions = ? WHERE id = ?",
                                 (json.dumps(actions), monster_id))
            except:
                pass

        if primary_dice:
            cleaned_dice = clean_dice_notation(primary_dice)
            if primary_dice != cleaned_dice:
                cursor.execute("UPDATE monsters SET primary_damage_dice = ? WHERE id = ?",
                             (cleaned_dice, monster_id))
                updates_made = True

        if updates_made:
            cleaned_count += 1
            print(f"Cleaned: {name}")

    conn.commit()
    print(f"\nCleaned {cleaned_count} monsters")

    print("\n=== STEP 2: Remove invalid duplicate attacks ===\n")

    cursor.execute("SELECT id, name, actions, challenge_rating FROM monsters")
    monsters = cursor.fetchall()

    removed_count = 0

    for monster_id, name, actions_json, cr in monsters:
        if not actions_json:
            continue

        try:
            actions = json.loads(actions_json)
            original_count = len(actions)

            valid_actions = []
            seen_attacks = {}

            for action in actions:
                if not isinstance(action, dict):
                    continue

                action_name = action.get('name', '')

                if action_name == 'Multiattack':
                    valid_actions.append(action)
                    continue

                if not is_valid_attack_for_monster(action_name, cr):
                    continue

                if action_name in seen_attacks:
                    continue

                seen_attacks[action_name] = True
                valid_actions.append(action)

            if len(valid_actions) < original_count:
                cursor.execute("UPDATE monsters SET actions = ? WHERE id = ?",
                             (json.dumps(valid_actions), monster_id))
                removed = original_count - len(valid_actions)
                print(f"Removed {removed} invalid attacks from: {name}")
                removed_count += 1
        except:
            pass

    conn.commit()
    print(f"\nCleaned {removed_count} monsters with duplicate/invalid attacks")

    print("\n=== STEP 3: Add missing saving throws ===\n")

    added_count = 0

    for srd_monster in srd_monsters:
        monster_name = srd_monster['name']
        saving_throws = srd_monster.get('saving_throws', [])

        if not saving_throws:
            continue

        cursor.execute("SELECT id, special_abilities FROM monsters WHERE name = ?", (monster_name,))
        result = cursor.fetchone()

        if not result:
            continue

        monster_id, special_abilities = result

        updated_abilities = special_abilities
        save_added = False

        for save in saving_throws:
            ability = save.get('ability', '')
            dc = save.get('dc', 0)

            if ability and dc and ability != 'terity':
                updated_abilities = add_saving_throw(updated_abilities, ability, dc)
                save_added = True

        if save_added:
            cursor.execute("UPDATE monsters SET special_abilities = ? WHERE id = ?",
                         (updated_abilities, monster_id))
            print(f"Added saving throws to: {monster_name}")
            added_count += 1

    conn.commit()
    print(f"\nAdded saving throws to {added_count} monsters")

    print("\n=== VERIFICATION ===\n")

    cursor.execute("""
        SELECT name, primary_attack_name, primary_attack_bonus, primary_damage_dice, primary_damage_type
        FROM monsters
        WHERE name IN ('Air Elemental', 'Barbed Devil', 'Behir')
        ORDER BY name
    """)

    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} (+{row[2]}) {row[3]} {row[4]}")

    cursor.execute("SELECT actions FROM monsters WHERE name = 'Air Elemental'")
    actions = json.loads(cursor.fetchone()[0])
    print(f"\nAir Elemental attacks: {len(actions)} total")
    for action in actions:
        print(f"  - {action['name']}")

    cursor.execute("SELECT special_abilities FROM monsters WHERE name = 'Behir' LIMIT 1")
    result = cursor.fetchone()
    if result and result[0]:
        abilities = json.loads(result[0])
        print(f"\nBehir special abilities: {len(abilities)} total")
        for ability in abilities[:3]:
            print(f"  - {ability.get('name', 'Unknown')}")

    conn.close()
    print("\nCleanup complete!")

if __name__ == '__main__':
    main()
