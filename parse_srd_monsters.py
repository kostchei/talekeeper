import re
import json

def parse_srd_monsters(srd_file):
    with open(srd_file, 'r') as f:
        content = f.read()

    monsters = []

    pattern = r'^([A-Z][a-z]+(?: [A-Z][a-z]+)*)\n\1\n(Large|Medium|Small|Tiny|Huge|Gargantuan) (\w+).*?\nAC (\d+).*?\nHP (\d+) \(([^)]+)\).*?\nSpeed\s+(.+?)\n.*?CR (\d+(?:/\d+)?)'

    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        name = match.group(1)
        size = match.group(2)
        creature_type = match.group(3)
        ac = int(match.group(4))
        hp = int(match.group(5))
        hp_dice = match.group(6)
        speed = match.group(7).strip()
        cr = match.group(8)

        full_block_start = match.start()
        next_monster = re.search(r'\n([A-Z][a-z]+(?: [A-Z][a-z]+)*)\n\1\n', content[match.end():])
        if next_monster:
            full_block_end = match.end() + next_monster.start()
        else:
            full_block_end = len(content)

        full_block = content[full_block_start:full_block_end]

        attacks = []
        actions_section = re.search(r'\nActions\n(.*?)(?:\nLegendary Actions|\nBonus Actions|\n[A-Z][a-z]+(?: [A-Z][a-z]+)*\n\1|$)', full_block, re.DOTALL)
        if actions_section:
            actions_text = actions_section.group(1)
            attack_pattern = r'^([\w\s\'-]+)\.\s*(?:Melee|Ranged|Melee or Ranged) Attack Roll:\s*\+(\d+),\s*(?:reach|range)\s+([^.]+)\.\s*Hit:\s*(\d+)\s*\(([^)]+)\)\s*(\w+)\s*damage'
            for attack_match in re.finditer(attack_pattern, actions_text, re.MULTILINE):
                attacks.append({
                    'name': attack_match.group(1).strip(),
                    'attack_bonus': int(attack_match.group(2)),
                    'reach_range': attack_match.group(3).strip(),
                    'damage_avg': int(attack_match.group(4)),
                    'damage_dice': attack_match.group(5).strip(),
                    'damage_type': attack_match.group(6).strip()
                })

        saving_throws = []
        save_pattern = r'(\w+) Saving Throw:\s*DC (\d+)'
        for save_match in re.finditer(save_pattern, full_block):
            saving_throws.append({
                'ability': save_match.group(1),
                'dc': int(save_match.group(2))
            })

        ability_pattern = r'Str (\d+)\s+([+-]\d+)([+-]\d+)\s+Dex (\d+)\s+([+-]\d+)([+-]\d+)\s+Con (\d+)\s+([+-]\d+)([+-]\d+)\s+Int (\d+)\s+([+-]\d+)([+-]\d+)\s+WIS (\d+)\s+([+-]\d+)([+-]\d+)\s+Cha (\d+)\s+([+-]\d+)([+-]\d+)'
        ability_match = re.search(ability_pattern, full_block)

        abilities = {}
        if ability_match:
            abilities = {
                'str': int(ability_match.group(1)),
                'dex': int(ability_match.group(4)),
                'con': int(ability_match.group(7)),
                'int': int(ability_match.group(10)),
                'wis': int(ability_match.group(13)),
                'cha': int(ability_match.group(16))
            }

        monsters.append({
            'name': name,
            'size': size,
            'type': creature_type,
            'ac': ac,
            'hp': hp,
            'hp_dice': hp_dice,
            'speed': speed,
            'cr': cr,
            'abilities': abilities,
            'attacks': attacks,
            'saving_throws': saving_throws
        })

    return monsters

def main():
    print("Parsing SRD monsters...")
    monsters = parse_srd_monsters('docs/SRD_CC_v5.2.1.md')

    print(f"\nFound {len(monsters)} monsters in SRD")

    if monsters:
        print("\nFirst 5 monsters:")
        for m in monsters[:5]:
            print(f"\n{m['name']}:")
            print(f"  AC: {m['ac']}, HP: {m['hp']}, CR: {m['cr']}")
            print(f"  Abilities: STR {m['abilities'].get('str', '?')}, DEX {m['abilities'].get('dex', '?')}, CON {m['abilities'].get('con', '?')}")
            print(f"  Attacks: {len(m['attacks'])}")
            for attack in m['attacks']:
                print(f"    - {attack['name']}: +{attack['attack_bonus']} to hit, {attack['damage_avg']} ({attack['damage_dice']}) {attack['damage_type']}")
            print(f"  Saving Throws: {len(m['saving_throws'])}")
            for save in m['saving_throws']:
                print(f"    - {save['ability']} DC {save['dc']}")

    with open('srd_monsters_parsed.json', 'w') as f:
        json.dump(monsters, f, indent=2)

    print(f"\nSaved to srd_monsters_parsed.json")

if __name__ == '__main__':
    main()
