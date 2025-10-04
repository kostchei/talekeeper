import json
from collections import Counter

with open('monsters_extracted.json', 'r') as f:
    data = json.load(f)

def cr_sort_key(cr):
    if cr == 'N/A':
        return (True, 0)
    try:
        if '/' in cr:
            parts = cr.split('/')
            return (False, float(parts[0]) / float(parts[1]))
        else:
            return (False, float(cr))
    except:
        return (True, 0)

print('=== D&D 2024 SRD MONSTER EXTRACTION SUMMARY ===\n')
print(f'Total Monsters Extracted: {len(data)}\n')

cr_distribution = Counter([m.get('cr', 'N/A') for m in data])
print('Challenge Rating Distribution:')
for cr in sorted(cr_distribution.keys(), key=cr_sort_key):
    print(f'  CR {cr}: {cr_distribution[cr]} monsters')

print()
type_distribution = Counter([m.get('type', 'Unknown') for m in data])
print('Creature Type Distribution:')
for ctype in sorted(type_distribution.keys(), key=lambda x: (-type_distribution[x], x)):
    print(f'  {ctype}: {type_distribution[ctype]} monsters')

print()
size_distribution = Counter([m.get('size', 'Unknown') for m in data])
print('Size Distribution:')
size_order = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan', 'Unknown']
for size in size_order:
    if size in size_distribution:
        print(f'  {size}: {size_distribution[size]} monsters')

print('\n=== COMPLETE MONSTER LIST (alphabetical) ===')
for i, m in enumerate(sorted(data, key=lambda x: x['name']), 1):
    print(f'{i}. {m["name"]} - {m["size"]} {m["type"]}, CR {m.get("cr", "N/A")}')
