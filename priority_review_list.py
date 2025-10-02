import json
import sqlite3

with open(r"d:\Code\TaleKeeper\monster_comparison_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)

with open(r"d:\Code\TaleKeeper\monsters_extracted.json", 'r', encoding='utf-8') as f:
    json_monsters = {m['name']: m for m in json.load(f)}

conn = sqlite3.connect(r"d:\Code\TaleKeeper\talekeeper.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 100)
print("PRIORITY REVIEW LIST - Monster Discrepancies")
print("=" * 100)
print()

print("CRITICAL: Monsters with Missing Data in JSON (Fix Immediately)")
print("-" * 100)
print(f"{'Monster':<25} {'JSON AC':<10} {'JSON HP':<10} {'JSON CR':<10} {'DB AC':<10} {'DB HP':<10} {'DB CR':<10}")
print("-" * 100)

critical_monsters = []
for disc in results['discrepancies']:
    if 'ac' in disc['differences'] and 'None' in disc['differences']['ac']:
        critical_monsters.append(disc['name'])

for name in critical_monsters[:10]:
    cursor.execute("SELECT armor_class, hit_points, challenge_rating FROM monsters WHERE name = ?", (name,))
    db_row = cursor.fetchone()
    json_m = json_monsters.get(name, {})

    print(f"{name:<25} {str(json_m.get('ac')):<10} {str(json_m.get('hp')):<10} {str(json_m.get('cr')):<10} "
          f"{str(db_row['armor_class']):<10} {str(db_row['hit_points']):<10} {str(db_row['challenge_rating']):<10}")

print()
print("HIGH PRIORITY: Monsters with Large Stat Differences (>20 HP or >2 AC)")
print("-" * 100)
print(f"{'Monster':<25} {'Stat':<8} {'JSON':<15} {'DB':<15} {'Difference':<20}")
print("-" * 100)

high_priority = []
for disc in results['discrepancies']:
    name = disc['name']
    if name in critical_monsters:
        continue

    json_m = json_monsters.get(name, {})
    cursor.execute("SELECT armor_class, hit_points FROM monsters WHERE name = ?", (name,))
    db_row = cursor.fetchone()

    if db_row and json_m.get('hp') and json_m.get('ac'):
        hp_diff = abs(json_m.get('hp', 0) - db_row['hit_points'])
        ac_diff = abs(json_m.get('ac', 0) - db_row['armor_class'])

        if hp_diff > 20:
            high_priority.append((name, 'HP', json_m.get('hp'), db_row['hit_points'], hp_diff))
        if ac_diff > 2:
            high_priority.append((name, 'AC', json_m.get('ac'), db_row['armor_class'], ac_diff))

for name, stat, json_val, db_val, diff in sorted(high_priority, key=lambda x: x[4], reverse=True)[:15]:
    print(f"{name:<25} {stat:<8} {str(json_val):<15} {str(db_val):<15} {diff:>+5}")

print()
print("MEDIUM PRIORITY: Popular Monsters with Any Discrepancy")
print("-" * 100)

popular_monsters = [
    'Dragon', 'Goblin', 'Orc', 'Troll', 'Giant', 'Beholder', 'Mind Flayer',
    'Vampire', 'Werewolf', 'Zombie', 'Skeleton', 'Kobold', 'Gnoll'
]

print(f"{'Monster':<30} {'# Differences':<15} {'Fields':<50}")
print("-" * 100)

for disc in results['discrepancies']:
    name = disc['name']
    if any(pop in name for pop in popular_monsters):
        fields = ', '.join(disc['differences'].keys())
        print(f"{name:<30} {len(disc['differences']):<15} {fields:<50}")

print()
print("SUMMARY STATISTICS")
print("-" * 100)
print(f"Critical Issues (Missing JSON Data):    {len(critical_monsters)}")
print(f"High Priority (Large Differences):      {len(high_priority)}")
print(f"Total Monsters Needing Review:          {len(results['discrepancies'])}")
print(f"Estimated Time (5 min/monster):         {len(results['discrepancies']) * 5 / 60:.1f} hours")
print()

print("RECOMMENDED ACTION PLAN")
print("-" * 100)
print("1. Fix Critical Issues (5 monsters):     Extract missing stats manually from source")
print("2. Review High Priority (15 monsters):   Validate which version is correct")
print("3. Spot Check Medium Priority (20):      Sample popular monsters")
print("4. Batch Update Remainder (138):         Use JSON stats, log for reference")
print("5. Add Missing Monsters:                 121 from DB, 40 from JSON")
print()
print("=" * 100)

conn.close()
