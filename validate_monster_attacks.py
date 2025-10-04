import json
import sqlite3
import re

def normalize_dice(dice_str):
    return re.sub(r'\s+', '', str(dice_str).strip())

def normalize_name(name):
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def extract_attack_info(actions_json):
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

        if to_hit_match or damage_match:
            attack_info = {
                'name': name,
                'description': desc[:200]
            }

            if to_hit_match:
                attack_info['attack_bonus'] = int(to_hit_match.group(1))

            if damage_match:
                attack_info['damage_avg'] = int(damage_match.group(1))
                attack_info['damage_dice'] = normalize_dice(damage_match.group(2))
                attack_info['damage_type'] = damage_match.group(3).strip().lower()

            if dc_match:
                attack_info['dc'] = int(dc_match.group(1))

            attacks.append(attack_info)

    return attacks

def main():
    print("Loading SRD and database for detailed validation...")

    with open('srd_monsters_parsed.json', 'r') as f:
        srd_monsters = json.load(f)

    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()

    real_issues = []

    for srd_monster in srd_monsters:
        cursor.execute("SELECT actions, special_abilities FROM monsters WHERE LOWER(name) = ?",
                      (srd_monster['name'].lower(),))
        result = cursor.fetchone()

        if not result:
            continue

        actions_json, abilities_json = result
        db_attacks = extract_attack_info(actions_json) + extract_attack_info(abilities_json)

        for srd_attack in srd_monster['attacks']:
            if 'Actions' in srd_attack['name']:
                continue

            srd_name_norm = normalize_name(srd_attack['name'])

            matching = None
            for db_attack in db_attacks:
                db_name_norm = normalize_name(db_attack['name'])
                if srd_name_norm == db_name_norm or srd_name_norm in db_name_norm or db_name_norm in srd_name_norm:
                    matching = db_attack
                    break

            if not matching:
                real_issues.append({
                    'monster': srd_monster['name'],
                    'issue_type': 'missing_attack',
                    'attack_name': srd_attack['name'],
                    'srd_data': srd_attack
                })
                continue

            if 'attack_bonus' in srd_attack and 'attack_bonus' in matching:
                if srd_attack['attack_bonus'] != matching['attack_bonus']:
                    real_issues.append({
                        'monster': srd_monster['name'],
                        'issue_type': 'attack_bonus_mismatch',
                        'attack_name': srd_attack['name'],
                        'db_value': matching['attack_bonus'],
                        'srd_value': srd_attack['attack_bonus']
                    })

            if 'damage_avg' in srd_attack and 'damage_avg' in matching:
                if srd_attack['damage_avg'] != matching['damage_avg']:
                    real_issues.append({
                        'monster': srd_monster['name'],
                        'issue_type': 'damage_avg_mismatch',
                        'attack_name': srd_attack['name'],
                        'db_value': matching['damage_avg'],
                        'srd_value': srd_attack['damage_avg']
                    })

            if 'damage_dice' in srd_attack and 'damage_dice' in matching:
                srd_dice_norm = normalize_dice(srd_attack['damage_dice'])
                db_dice_norm = normalize_dice(matching['damage_dice'])
                if srd_dice_norm != db_dice_norm:
                    real_issues.append({
                        'monster': srd_monster['name'],
                        'issue_type': 'damage_dice_mismatch',
                        'attack_name': srd_attack['name'],
                        'db_value': matching['damage_dice'],
                        'srd_value': srd_attack['damage_dice']
                    })

            if 'damage_type' in srd_attack and 'damage_type' in matching:
                if srd_attack['damage_type'].lower() != matching['damage_type']:
                    real_issues.append({
                        'monster': srd_monster['name'],
                        'issue_type': 'damage_type_mismatch',
                        'attack_name': srd_attack['name'],
                        'db_value': matching['damage_type'],
                        'srd_value': srd_attack['damage_type'].lower()
                    })

    print(f"\n=== VALIDATION RESULTS ===")
    print(f"Total real issues found: {len(real_issues)}")

    issue_types = {}
    for issue in real_issues:
        issue_type = issue['issue_type']
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    print(f"\nIssue breakdown:")
    for issue_type, count in sorted(issue_types.items()):
        print(f"  {issue_type}: {count}")

    print(f"\n=== TOP 30 CRITICAL ISSUES ===\n")
    critical = [i for i in real_issues if i['issue_type'] in ['damage_avg_mismatch', 'attack_bonus_mismatch', 'damage_type_mismatch']]

    for i, issue in enumerate(critical[:30]):
        print(f"{i+1}. {issue['monster']} - {issue['attack_name']}")
        print(f"   {issue['issue_type']}: DB={issue.get('db_value')} vs SRD={issue.get('srd_value')}")

    with open('monster_validation_issues.json', 'w') as f:
        json.dump(real_issues, f, indent=2)

    print(f"\n\nFull report saved to: monster_validation_issues.json")

    print(f"\n=== SUMMARY ===")
    print(f"Monsters in SRD: {len(srd_monsters)}")
    print(f"Monsters with issues: {len(set(i['monster'] for i in real_issues))}")
    print(f"Critical issues (damage/attack mismatches): {len(critical)}")
    print(f"Missing attacks: {len([i for i in real_issues if i['issue_type'] == 'missing_attack'])}")

    conn.close()

if __name__ == '__main__':
    main()
