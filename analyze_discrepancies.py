import json
from collections import Counter

with open(r"d:\Code\TaleKeeper\monster_comparison_results.json", 'r', encoding='utf-8') as f:
    results = json.load(f)

print("=" * 80)
print("DISCREPANCY DISTRIBUTION ANALYSIS")
print("=" * 80)
print()

disc_counts = Counter()
for disc in results['discrepancies']:
    num_diffs = len(disc['differences'])
    disc_counts[num_diffs] += 1

print("Number of Differences | Number of Monsters")
print("-" * 80)
for num_diffs in sorted(disc_counts.keys(), reverse=True):
    count = disc_counts[num_diffs]
    bar = "#" * (count // 2)
    print(f"{num_diffs:>20} | {count:>3} monsters {bar}")

print()
print("FIELD-SPECIFIC DISCREPANCIES")
print("-" * 80)

field_counts = Counter()
for disc in results['discrepancies']:
    for field in disc['differences'].keys():
        field_counts[field] += 1

print("Field | Discrepancies | % of Compared Monsters")
print("-" * 80)
total_compared = results['in_both']
for field, count in field_counts.most_common():
    pct = (count / total_compared) * 100
    print(f"{field:>5} | {count:>13} | {pct:>6.1f}%")

print()
print("EXAMPLES OF EACH DISCREPANCY TYPE")
print("-" * 80)

examples_by_field = {}
for disc in results['discrepancies']:
    for field, detail in disc['differences'].items():
        if field not in examples_by_field:
            examples_by_field[field] = []
        if len(examples_by_field[field]) < 3:
            examples_by_field[field].append((disc['name'], detail))

for field in sorted(examples_by_field.keys()):
    print(f"\n{field.upper()}:")
    for name, detail in examples_by_field[field]:
        print(f"  {name}: {detail}")

print()
print("=" * 80)
