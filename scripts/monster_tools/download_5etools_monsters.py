import json
import urllib.request
import os
from typing import List, Dict, Optional

SOURCEBOOKS = {
    'mm': 'Monster Manual',
    'xmm': 'Expanded Monster Manual',
    'vgm': 'Volos Guide to Monsters',
    'mpmm': 'Mordenkainen Presents Monsters of the Multiverse',
    'mtf': 'Mordenkainens Tome of Foes',
    'tce': 'Tashas Cauldron of Everything',
    'ftd': 'Fizbans Treasury of Dragons',
    'gos': 'Ghosts of Saltmarsh',
    'bgdia': 'Baldurs Gate Descent into Avernus',
    'skt': 'Storm Kings Thunder',
    'hotdq': 'Hoard of the Dragon Queen',
    'rot': 'Rise of Tiamat',
    'pota': 'Princes of the Apocalypse',
    'oota': 'Out of the Abyss',
    'cos': 'Curse of Strahd',
    'scc': 'Strixhaven A Curriculum of Chaos',
}

BASE_URL = 'https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/master/data/bestiary/bestiary-{}.json'
OUTPUT_DIR = 'data/monsters/5etools'

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_bestiary(sourcebook: str) -> Optional[List[Dict]]:
    url = BASE_URL.format(sourcebook)
    try:
        print(f'Downloading {sourcebook.upper()}...', end=' ')
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            monsters = data.get('monster', [])
            print(f'OK ({len(monsters)} monsters)')
            return monsters
    except Exception as e:
        print(f'FAILED: {e}')
        return None

def find_monster_by_name(monsters: List[Dict], name: str) -> List[Dict]:
    matches = []
    name_lower = name.lower()

    for monster in monsters:
        monster_name = monster.get('name', '').lower()
        if name_lower == monster_name or name_lower in monster_name:
            matches.append(monster)

    return matches

def download_specific_monsters(monster_names: List[str], output_file: str = '5etools_monsters_raw.json'):
    ensure_output_dir()

    all_matches = {}

    print('=' * 80)
    print('DOWNLOADING MONSTERS FROM 5ETOOLS')
    print('=' * 80)
    print()

    for sourcebook in SOURCEBOOKS.keys():
        monsters = fetch_bestiary(sourcebook)
        if monsters is None:
            continue

        for target_name in monster_names:
            matches = find_monster_by_name(monsters, target_name)
            if matches:
                if target_name not in all_matches:
                    all_matches[target_name] = []

                for match in matches:
                    all_matches[target_name].append({
                        'monster_data': match,
                        'sourcebook': sourcebook.upper(),
                        'sourcebook_full': SOURCEBOOKS[sourcebook]
                    })

    output_path = os.path.join(OUTPUT_DIR, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, indent=2)

    print()
    print('=' * 80)
    print('DOWNLOAD SUMMARY')
    print('=' * 80)
    print(f'Monsters requested: {len(monster_names)}')
    print(f'Monsters found: {len(all_matches)}')
    print(f'Output file: {output_path}')
    print()

    for name, matches in all_matches.items():
        print(f'{name}: {len(matches)} variant(s)')
        for match in matches:
            monster = match['monster_data']
            print(f'  - {monster["name"]} (CR {monster.get("cr", "?")}, {match["sourcebook"]})')

    return all_matches

def download_all_monsters(sourcebook: str):
    ensure_output_dir()

    monsters = fetch_bestiary(sourcebook)
    if monsters is None:
        print(f'Failed to download {sourcebook}')
        return

    output_path = os.path.join(OUTPUT_DIR, f'{sourcebook}_monsters_raw.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({'monsters': monsters, 'sourcebook': sourcebook.upper()}, f, indent=2)

    print(f'Saved {len(monsters)} monsters to {output_path}')

if __name__ == '__main__':
    priority_monsters = [
        'Specter',
        'Shadow Demon',
        'Shadow Mastiff',
        'Champion',
        'Skum',
        'Pirate Captain',
        'Apprentice Wizard',
        'Yuan-ti Mind Whisperer',
        'Yuan-ti Pit Master',
    ]

    print('Downloading priority monsters...')
    download_specific_monsters(priority_monsters)

    print()
    print('=' * 80)
    print('COMPLETE')
    print('=' * 80)
