import json
import urllib.request
import time

MISSING_MONSTERS = [
    ('Preist Acolyte', 'Acolyte'),
    ('Spectre', 'Specter'),
    ('Manes Vapourswarm', None),
    ('Orgrillon Ogre', 'Orgrillon'),
    ('Yuan-ti Infiltrator', 'Yuan-ti'),
    ('Mage Apprentice', 'Apprentice'),
    ('Shadow Mastif', 'Shadow Mastiff'),
    ('Scout Captain', 'Captain'),
    ('Shadow Demon', 'Shadow Demon'),
    ('Champion', 'Champion'),
    ('Giant Axe Beak', 'Axe Beak'),
    ('Skum', 'Skum'),
    ('Pirate Capatain', 'Pirate Captain'),
    ('Giant Squid', 'Giant Squid'),
    ('Bandit Deceiver', 'Deceiver'),
    ('Aberrant Cultist', 'Cultist'),
    ('Berserker Commander', 'Commander'),
    ('Death Cultist', 'Cultist'),
    ('Fiend Cultist', 'Cultist'),
    ('Vampire Nightbringer', 'Vampire'),
    ('Cultist Heirophant', 'Hierophant'),
    ('Noble Prodigy', 'Noble'),
    ('Spy Master', 'Spy'),
    ('Warrior Commander', 'Commander')
]

SOURCEBOOKS = [
    'mm',
    'vgm',
    'mpmm',
    'mtf',
    'tce',
    'ftd',
    'gos',
    'bgdia',
    'skt',
    'hotdq',
    'rot',
    'pota',
    'oota',
    'cos',
    'scc',
    'aag',
]

BASE_URL = 'https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/master/data/bestiary/bestiary-{}.json'

def fetch_bestiary(sourcebook):
    url = BASE_URL.format(sourcebook)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get('monster', [])
    except Exception as e:
        return None

def search_monsters():
    results = {}

    for original_name, search_term in MISSING_MONSTERS:
        results[original_name] = []

    print('=' * 80)
    print('SEARCHING 5ETOOLS FOR MISSING MONSTERS')
    print('=' * 80)
    print()

    for sourcebook in SOURCEBOOKS:
        print(f'Fetching {sourcebook.upper()}...', end=' ')
        monsters = fetch_bestiary(sourcebook)

        if monsters is None:
            print('FAILED')
            continue

        print(f'OK ({len(monsters)} monsters)')

        for original_name, search_term in MISSING_MONSTERS:
            if search_term is None:
                continue

            for monster in monsters:
                name = monster.get('name', '')
                if search_term.lower() in name.lower():
                    results[original_name].append({
                        'name': name,
                        'cr': monster.get('cr', 'Unknown'),
                        'source': monster.get('source', sourcebook.upper()),
                        'page': monster.get('page', 'Unknown'),
                        'type': monster.get('type', 'Unknown'),
                        'size': monster.get('size', 'Unknown'),
                        'alignment': monster.get('alignment', 'Unknown'),
                        'full_data': monster
                    })

        time.sleep(0.5)

    return results

def print_results(results):
    print()
    print('=' * 80)
    print('SEARCH RESULTS')
    print('=' * 80)
    print()

    found_count = 0
    not_found_count = 0

    for original_name, matches in results.items():
        if matches:
            found_count += 1
            print(f'[FOUND] {original_name}')
            for match in matches:
                print(f'  -> {match["name"]} (CR {match["cr"]}, {match["source"]})')
        else:
            not_found_count += 1
            print(f'[NOT FOUND] {original_name}')

    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Total searched: {len(MISSING_MONSTERS)}')
    print(f'Found: {found_count}')
    print(f'Not found: {not_found_count}')

    return results

def save_results(results, filename='5etools_monster_matches.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f'\nResults saved to {filename}')

if __name__ == '__main__':
    results = search_monsters()
    print_results(results)
    save_results(results)
