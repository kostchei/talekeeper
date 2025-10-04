import json
import re

data = json.load(open('monsters_extracted.json'))

name_fixes = {
    'Hide action.Goblin Boss': 'Goblin Boss',
    'ter 1 minute, it succeeds automatically.Adult Gold Dragon': 'Adult Gold Dragon',
    'Piercing damage.Jackal': 'Jackal',
    '(2d8) Piercing damage and has the Prone condition.Tyrannosaurus Rex': 'Tyrannosaurus Rex',
    'damage.Wolf': 'Wolf',
    'If the target is a': 'Stone Giant'
}

for monster in data:
    if monster['name'] in name_fixes:
        print(f"Fixing: {monster['name']} -> {name_fixes[monster['name']]}")
        monster['name'] = name_fixes[monster['name']]

with open('monsters_extracted.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nFixed {len(name_fixes)} monster names")
print(f"Total monsters: {len(data)}")
