import json
import sqlite3
import re

def normalize_name(name):
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def extract_attack_info_from_db(actions_json):
    if not actions_json or actions_json == '[]':
        return []

    try:
        actions = json.loads(actions_json)
    except:
        return []

    attacks = []
    for action in actions:
        if not isinstance(action, dict):
            continue

        name = action.get('name', '')
        entries = action.get('entries', [])
        if not entries:
            continue

        desc = entries[0] if isinstance(entries, list) else str(entries)

        to_hit_match = re.search(r'\+(\d+) to hit', desc, re.IGNORECASE)
        damage_match = re.search(r'(\d+)\s*\(([^)]+)\)\s*(\w+)\s*damage', desc, re.IGNORECASE)
        dc_match = re.search(r'DC (\d+)', desc)

        attack_info = {'name': name}

        if to_hit_match:
            attack_info['attack_bonus'] = int(to_hit_match.group(1))

        if damage_match:
            attack_info['damage_avg'] = int(damage_match.group(1))
            attack_info['damage_dice'] = damage_match.group(2).strip()
            attack_info['damage_type'] = damage_match.group(3).strip()

        if dc_match:
            attack_info['dc'] = int(dc_match.group(1))

        if len(attack_info) > 1:
            attacks.append(attack_info)

    return attacks

def main():
    print("Loading SRD parsed data...")
    with open('srd_monsters_parsed.json', 'r') as f:
        srd_monsters = json.load(f)

    srd_map = {normalize_name(m['name']): m for m in srd_monsters}

    print(f"Loaded {len(srd_monsters)} SRD monsters")

    print("\nConnecting to database...")
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, actions, special_abilities FROM monsters")
    db_monsters = cursor.fetchall()

    print(f"Loaded {len(db_monsters)} database monsters")

    discrepancies = []

    print("\n=== COMPARING ATTACKS, SAVING THROWS, AND DAMAGE ===\n")

    for monster_id, name, actions_json, abilities_json in db_monsters:
        normalized = normalize_name(name)

        if normalized not in srd_map:
            continue

        srd_monster = srd_map[normalized]
        db_attacks = extract_attack_info_from_db(actions_json)
        db_abilities = extract_attack_info_from_db(abilities_json)

        all_db_attacks = db_attacks + db_abilities

        issues = []

        for srd_attack in srd_monster['attacks']:
            srd_name = normalize_name(srd_attack['name'])

            matching_db_attack = None
            for db_attack in all_db_attacks:
                if srd_name in normalize_name(db_attack['name']) or normalize_name(db_attack['name']) in srd_name:
                    matching_db_attack = db_attack
                    break

            if not matching_db_attack:
                issues.append(f"Missing attack: {srd_attack['name']}")
                continue

            if 'attack_bonus' in srd_attack and 'attack_bonus' in matching_db_attack:
                if srd_attack['attack_bonus'] != matching_db_attack['attack_bonus']:
                    issues.append(f"{srd_attack['name']}: Attack bonus {matching_db_attack['attack_bonus']} should be {srd_attack['attack_bonus']}")

            if 'damage_avg' in srd_attack and 'damage_avg' in matching_db_attack:
                if srd_attack['damage_avg'] != matching_db_attack['damage_avg']:
                    issues.append(f"{srd_attack['name']}: Damage {matching_db_attack['damage_avg']} should be {srd_attack['damage_avg']}")

            if 'damage_dice' in srd_attack and 'damage_dice' in matching_db_attack:
                if srd_attack['damage_dice'] != matching_db_attack['damage_dice']:
                    issues.append(f"{srd_attack['name']}: Dice {matching_db_attack['damage_dice']} should be {srd_attack['damage_dice']}")

            if 'damage_type' in srd_attack and 'damage_type' in matching_db_attack:
                srd_type = srd_attack['damage_type'].lower()
                db_type = matching_db_attack['damage_type'].lower()
                if srd_type != db_type:
                    issues.append(f"{srd_attack['name']}: Type {db_type} should be {srd_type}")

        for srd_save in srd_monster['saving_throws']:
            found_save = False
            for db_attack in all_db_attacks:
                if 'dc' in db_attack:
                    if db_attack['dc'] == srd_save['dc']:
                        found_save = True
                        break

            if not found_save and srd_save['ability'] != 'terity':
                issues.append(f"Missing or incorrect saving throw: {srd_save['ability']} DC {srd_save['dc']}")

        if issues:
            discrepancies.append({
                'name': name,
                'issues': issues,
                'srd_attacks': srd_monster['attacks'],
                'db_attacks': all_db_attacks
            })

    print(f"=== SUMMARY ===")
    print(f"Monsters compared: {len([m for m in db_monsters if normalize_name(m[1]) in srd_map])}")
    print(f"Monsters with discrepancies: {len(discrepancies)}")

    if discrepancies:
        print(f"\n=== TOP 20 DISCREPANCIES ===\n")
        for i, disc in enumerate(discrepancies[:20]):
            print(f"{i+1}. {disc['name']}")
            for issue in disc['issues']:
                print(f"   - {issue}")
            print()

    with open('monster_attack_discrepancies.json', 'w') as f:
        json.dump(discrepancies, f, indent=2)

    print(f"Full report saved to: monster_attack_discrepancies.json")

    cursor.execute("""
        SELECT name, actions FROM monsters
        WHERE name IN ('Aboleth', 'Assassin', 'Lich', 'Dragon Turtle')
        ORDER BY name
    """)

    print("\n=== SAMPLE: Critical Monster Actions ===")
    for name, actions in cursor.fetchall():
        print(f"\n{name}:")
        attacks = extract_attack_info_from_db(actions)
        for attack in attacks[:3]:
            parts = [attack['name']]
            if 'attack_bonus' in attack:
                parts.append(f"+{attack['attack_bonus']} to hit")
            if 'damage_avg' in attack:
                parts.append(f"{attack['damage_avg']} ({attack['damage_dice']}) {attack['damage_type']}")
            if 'dc' in attack:
                parts.append(f"DC {attack['dc']}")
            print(f"  {', '.join(parts)}")

    conn.close()

if __name__ == '__main__':
    main()
