import json
import sqlite3
from typing import Dict, List, Tuple, Any
from collections import defaultdict

def load_json_monsters(json_path: str) -> Dict[str, Dict]:
    with open(json_path, 'r', encoding='utf-8') as f:
        monsters_list = json.load(f)

    monsters = {}
    for monster in monsters_list:
        name = monster.get('name', '').strip()
        if name:
            monsters[name] = monster
    return monsters

def load_db_monsters(db_path: str) -> Dict[str, Dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM monsters")
    rows = cursor.fetchall()

    monsters = {}
    for row in rows:
        name = row['name'].strip()
        monsters[name] = dict(row)

    conn.close()
    return monsters

def compare_stat(json_val, db_val, field_name: str) -> Tuple[bool, str]:
    if json_val is None and db_val is None:
        return True, "Both None"

    if json_val is None or db_val is None:
        return False, f"JSON: {json_val}, DB: {db_val}"

    if field_name == 'challenge_rating' or field_name == 'cr':
        json_cr = str(json_val).strip()
        db_cr = str(db_val).strip()
        return json_cr == db_cr, f"JSON: {json_cr}, DB: {db_cr}"

    try:
        if isinstance(json_val, (int, float)) and isinstance(db_val, (int, float)):
            return json_val == db_val, f"JSON: {json_val}, DB: {db_val}"
        return str(json_val) == str(db_val), f"JSON: {json_val}, DB: {db_val}"
    except:
        return False, f"JSON: {json_val}, DB: {db_val}"

def compare_monsters(json_path: str, db_path: str) -> Dict:
    json_monsters = load_json_monsters(json_path)
    db_monsters = load_db_monsters(db_path)

    json_names = set(json_monsters.keys())
    db_names = set(db_monsters.keys())

    in_both = json_names & db_names
    only_json = json_names - db_names
    only_db = db_names - json_names

    results = {
        'total_json': len(json_names),
        'total_db': len(db_names),
        'in_both': len(in_both),
        'only_in_json': sorted(only_json),
        'only_in_db': sorted(only_db),
        'discrepancies': [],
        'stats_summary': {
            'json_complete': 0,
            'json_incomplete': 0,
            'db_complete': 0,
            'db_incomplete': 0
        }
    }

    fields_to_compare = [
        ('ac', 'armor_class'),
        ('hp', 'hit_points'),
        ('cr', 'challenge_rating'),
        ('str', 'strength'),
        ('dex', 'dexterity'),
        ('con', 'constitution'),
        ('int', 'intelligence'),
        ('wis', 'wisdom'),
        ('cha', 'charisma')
    ]

    for name in sorted(in_both):
        json_monster = json_monsters[name]
        db_monster = db_monsters[name]

        json_complete = all([
            json_monster.get('ac') is not None,
            json_monster.get('hp') is not None,
            json_monster.get('cr') is not None
        ])

        db_complete = all([
            db_monster.get('armor_class') is not None,
            db_monster.get('hit_points') is not None,
            db_monster.get('challenge_rating') is not None
        ])

        if json_complete:
            results['stats_summary']['json_complete'] += 1
        else:
            results['stats_summary']['json_incomplete'] += 1

        if db_complete:
            results['stats_summary']['db_complete'] += 1
        else:
            results['stats_summary']['db_incomplete'] += 1

        differences = {}
        for json_field, db_field in fields_to_compare:
            json_val = json_monster.get(json_field)
            db_val = db_monster.get(db_field)

            match, detail = compare_stat(json_val, db_val, json_field)
            if not match:
                differences[json_field] = detail

        if differences:
            results['discrepancies'].append({
                'name': name,
                'differences': differences
            })

    results['discrepancies'].sort(key=lambda x: len(x['differences']), reverse=True)

    return results

def generate_report(results: Dict) -> str:
    report = []
    report.append("=" * 80)
    report.append("MONSTER DATA COMPARISON REPORT")
    report.append("=" * 80)
    report.append("")

    report.append("SUMMARY STATISTICS")
    report.append("-" * 80)
    report.append(f"Total monsters in JSON:      {results['total_json']}")
    report.append(f"Total monsters in Database:  {results['total_db']}")
    report.append(f"Monsters in both sources:    {results['in_both']}")
    report.append(f"Only in JSON:                {len(results['only_in_json'])}")
    report.append(f"Only in Database:            {len(results['only_in_db'])}")
    report.append("")

    report.append("DATA COMPLETENESS")
    report.append("-" * 80)
    json_complete = results['stats_summary']['json_complete']
    json_total = results['in_both']
    json_pct = (json_complete / json_total * 100) if json_total > 0 else 0

    db_complete = results['stats_summary']['db_complete']
    db_pct = (db_complete / json_total * 100) if json_total > 0 else 0

    report.append(f"JSON monsters with AC/HP/CR: {json_complete}/{json_total} ({json_pct:.1f}%)")
    report.append(f"DB monsters with AC/HP/CR:   {db_complete}/{json_total} ({db_pct:.1f}%)")
    report.append("")

    report.append("TOP 10 MONSTERS WITH DISCREPANCIES")
    report.append("-" * 80)
    for i, disc in enumerate(results['discrepancies'][:10], 1):
        report.append(f"\n{i}. {disc['name']} ({len(disc['differences'])} differences)")
        for field, detail in disc['differences'].items():
            report.append(f"   - {field}: {detail}")

    if len(results['discrepancies']) > 10:
        report.append(f"\n... and {len(results['discrepancies']) - 10} more monsters with discrepancies")

    report.append("")
    report.append("MONSTERS ONLY IN JSON (First 20)")
    report.append("-" * 80)
    for name in results['only_in_json'][:20]:
        report.append(f"  - {name}")
    if len(results['only_in_json']) > 20:
        report.append(f"  ... and {len(results['only_in_json']) - 20} more")

    report.append("")
    report.append("MONSTERS ONLY IN DATABASE (First 20)")
    report.append("-" * 80)
    for name in results['only_in_db'][:20]:
        report.append(f"  - {name}")
    if len(results['only_in_db']) > 20:
        report.append(f"  ... and {len(results['only_in_db']) - 20} more")

    report.append("")
    report.append("RECOMMENDATION")
    report.append("-" * 80)

    if json_pct > 95 and len(results['discrepancies']) > 50:
        report.append("RECOMMENDATION: Update Database from JSON")
        report.append("REASON: JSON has complete stats with significant differences from DB")
    elif db_pct > 95 and json_pct < 80:
        report.append("RECOMMENDATION: Update JSON from Database")
        report.append("REASON: Database has more complete stats than JSON")
    elif len(results['discrepancies']) < 10:
        report.append("RECOMMENDATION: Manual review of discrepancies")
        report.append("REASON: Few differences exist, manual verification recommended")
    else:
        report.append("RECOMMENDATION: Hybrid approach")
        report.append("REASON: Both sources have valuable data, merge carefully")
        report.append("  - Use DB as baseline for AC/HP/CR")
        report.append("  - Use JSON for detailed action descriptions")
        report.append("  - Manually verify discrepancies")

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)

def save_detailed_json(results: Dict, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Detailed results saved to: {output_path}")

if __name__ == "__main__":
    json_path = r"d:\Code\TaleKeeper\monsters_extracted.json"
    db_path = r"d:\Code\TaleKeeper\talekeeper.db"

    print("Loading and comparing monster data...")
    results = compare_monsters(json_path, db_path)

    report = generate_report(results)
    print(report)

    output_path = r"d:\Code\TaleKeeper\monster_comparison_results.json"
    save_detailed_json(results, output_path)

    report_path = r"d:\Code\TaleKeeper\monster_comparison_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")
