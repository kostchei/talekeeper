import json

with open('d:\\Code\\TaleKeeper\\monsters_extracted.json', 'r', encoding='utf-8') as f:
    monsters = json.load(f)

aquatic_keywords = ['fish', 'shark', 'crab', 'octopus', 'squid', 'eel', 'whale', 'dolphin',
                    'sea', 'water', 'reef', 'coral', 'merfolk', 'sahuagin', 'kraken',
                    'turtle', 'crocodile', 'frog', 'toad']

aquatic_monsters = []
harmless_monsters = []

def extract_cr_value(cr_str):
    if cr_str == "0":
        return 0.0
    elif cr_str == "1/8":
        return 0.125
    elif cr_str == "1/4":
        return 0.25
    elif cr_str == "1/2":
        return 0.5
    else:
        try:
            return float(cr_str)
        except:
            return 999

for monster in monsters:
    name = monster.get('name', '')
    cr = monster.get('cr', '')
    type_info = monster.get('type', '')
    speed = monster.get('speed', '')

    cr_value = extract_cr_value(cr)

    is_aquatic = False
    amphibious = False
    aquatic_reason = []

    if 'swim' in speed.lower():
        is_aquatic = True
        aquatic_reason.append('Has swim speed')

    name_lower = name.lower()
    for keyword in aquatic_keywords:
        if keyword in name_lower:
            is_aquatic = True
            aquatic_reason.append(f'Name contains "{keyword}"')
            break

    if 'amphibious' in str(monster).lower():
        is_aquatic = True
        amphibious = True
        aquatic_reason.append('Amphibious trait')

    if is_aquatic:
        aquatic_monsters.append({
            'name': name,
            'cr': cr,
            'cr_value': cr_value,
            'type': type_info,
            'speed': speed,
            'amphibious': amphibious,
            'reason': ', '.join(aquatic_reason)
        })

    if cr_value <= 0.25:
        harmless_monsters.append({
            'name': name,
            'cr': cr,
            'cr_value': cr_value,
            'type': type_info,
            'speed': speed
        })

aquatic_monsters.sort(key=lambda x: x['cr_value'])
harmless_monsters.sort(key=lambda x: x['cr_value'])

print("=" * 80)
print("AQUATIC/WATER-DWELLING MONSTERS")
print("=" * 80)
print(f"\nTotal Count: {len(aquatic_monsters)}\n")

for m in aquatic_monsters:
    swim_info = ""
    amphibious_marker = ""

    if 'swim' in m['speed'].lower():
        parts = m['speed'].split(',')
        for part in parts:
            if 'swim' in part.lower():
                swim_info = f" | {part.strip()}"
                break

    if m.get('amphibious', False):
        amphibious_marker = " [AMPHIBIOUS]"

    print(f"CR {m['cr']:>4} | {m['name']:35} | {m['type']:20}{swim_info}{amphibious_marker}")

harmless_animals = ['Baboon', 'Badger', 'Bat', 'Cat', 'Crab', 'Deer', 'Eagle', 'Frog',
                    'Goat', 'Hawk', 'Hyena', 'Jackal', 'Lizard', 'Octopus', 'Owl',
                    'Piranha', 'Rat', 'Raven', 'Scorpion', 'Seahorse', 'Spider', 'Vulture',
                    'Weasel', 'Camel', 'Giant Rat', 'Mastiff', 'Mule', 'Pony',
                    'Boar', 'Draft Horse', 'Elk', 'Riding Horse']

print("\n" + "=" * 80)
print("HARMLESS/NON-THREATENING MONSTERS (CR 1/4 or lower)")
print("=" * 80)
print(f"\nTotal Count: {len(harmless_monsters)}\n")

print("TRULY HARMLESS (Common animals, non-aggressive):")
print("-" * 80)
for m in harmless_monsters:
    if m['name'] in harmless_animals:
        category = "Beast" if "Beast" in m['type'] else m['type']
        print(f"CR {m['cr']:>4} | {m['name']:35} | {category:20}")

print("\nWEAK CREATURES (Low CR but potentially hostile):")
print("-" * 80)
for m in harmless_monsters:
    if m['name'] not in harmless_animals:
        category = m['type']
        print(f"CR {m['cr']:>4} | {m['name']:35} | {category:20}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Monsters Analyzed: {len(monsters)}")
print(f"Aquatic/Water Monsters: {len(aquatic_monsters)}")
print(f"Harmless Monsters (CR <= 1/4): {len(harmless_monsters)}")
print("=" * 80)