import re
import json

def parse_monsters(filepath, start_line=24667):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    monsters = []
    current_monster = None
    current_section = None
    i = start_line - 1

    creature_types = ['Aberration', 'Beast', 'Celestial', 'Construct', 'Dragon', 'Elemental',
                      'Fey', 'Fiend', 'Giant', 'Humanoid', 'Monstrosity', 'Ooze', 'Plant', 'Undead']

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        type_match = re.match(r'^(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+(.*?),\s+(.+)$', line)
        if type_match:
            if current_monster:
                monsters.append(current_monster)

            size = type_match.group(1)
            type_info = type_match.group(2)
            alignment = type_match.group(3)

            if i > 0:
                name = lines[i-1].strip()
                name = re.sub(r'.*?Half damage\.', '', name).strip()
                name = re.sub(r'.*?Success:\s+', '', name).strip()
                name = re.sub(r'.*?\(\d+d\d+[^)]*\)\s+\w+\s+damage\.\s*', '', name).strip()
                name = re.sub(r'^System Reference Document\s+[\d.]+', '', name).strip()
                name = re.sub(r'^[\d.]+\s+', '', name).strip()
                name = re.sub(r'^condition\.', '', name).strip()
                if not name or len(name) < 3:
                    if i > 1:
                        name = lines[i-2].strip()
                        name = re.sub(r'.*?Half damage\.', '', name).strip()
                        name = re.sub(r'^System Reference Document\s+[\d.]+', '', name).strip()
            else:
                name = "Unknown"

            current_monster = {
                'name': name,
                'size': size,
                'type': type_info,
                'alignment': alignment,
                'traits': [],
                'actions': [],
                'bonus_actions': [],
                'reactions': [],
                'legendary_actions': []
            }
            current_section = None
            i += 1
            continue

        if current_monster:
            if line.startswith('AC '):
                ac_match = re.search(r'AC\s+(\d+)', line)
                init_match = re.search(r'Initiative\s+([+\-]?\d+)', line)
                if ac_match:
                    current_monster['ac'] = int(ac_match.group(1))
                if init_match:
                    current_monster['initiative'] = init_match.group(1)

            elif line.startswith('HP '):
                hp_match = re.search(r'HP\s+(\d+)\s*\(([^)]+)\)', line)
                if hp_match:
                    current_monster['hp'] = int(hp_match.group(1))
                    current_monster['hp_dice'] = hp_match.group(2)

            elif line.startswith('Speed'):
                speed_text = line.replace('Speed', '').strip()
                current_monster['speed'] = speed_text

            elif line.startswith('Str '):
                str_match = re.search(r'Str\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                dex_match = re.search(r'Dex\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                con_match = re.search(r'Con\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                if str_match:
                    current_monster['str'] = int(str_match.group(1))
                    current_monster['str_mod'] = str_match.group(2).replace('−', '-')
                    current_monster['str_save'] = str_match.group(3).replace('−', '-')
                if dex_match:
                    current_monster['dex'] = int(dex_match.group(1))
                    current_monster['dex_mod'] = dex_match.group(2).replace('−', '-')
                    current_monster['dex_save'] = dex_match.group(3).replace('−', '-')
                if con_match:
                    current_monster['con'] = int(con_match.group(1))
                    current_monster['con_mod'] = con_match.group(2).replace('−', '-')
                    current_monster['con_save'] = con_match.group(3).replace('−', '-')

            elif line.startswith('Int '):
                int_match = re.search(r'Int\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                wis_match = re.search(r'WIS\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                cha_match = re.search(r'Cha\s+(\d+)\s*([+\-−]\d+)\s*([+\-−]\d+)', line)
                if int_match:
                    current_monster['int'] = int(int_match.group(1))
                    current_monster['int_mod'] = int_match.group(2).replace('−', '-')
                    current_monster['int_save'] = int_match.group(3).replace('−', '-')
                if wis_match:
                    current_monster['wis'] = int(wis_match.group(1))
                    current_monster['wis_mod'] = wis_match.group(2).replace('−', '-')
                    current_monster['wis_save'] = wis_match.group(3).replace('−', '-')
                if cha_match:
                    current_monster['cha'] = int(cha_match.group(1))
                    current_monster['cha_mod'] = cha_match.group(2).replace('−', '-')
                    current_monster['cha_save'] = cha_match.group(3).replace('−', '-')

            elif line.startswith('Skills'):
                current_monster['skills'] = line.replace('Skills', '').strip()

            elif line.startswith('Vulnerabilities'):
                current_monster['vulnerabilities'] = line.replace('Vulnerabilities', '').strip()

            elif line.startswith('Resistances'):
                current_monster['resistances'] = line.replace('Resistances', '').strip()

            elif line.startswith('Immunities'):
                current_monster['immunities'] = line.replace('Immunities', '').strip()

            elif line.startswith('Senses'):
                current_monster['senses'] = line.replace('Senses', '').strip()

            elif line.startswith('Languages'):
                current_monster['languages'] = line.replace('Languages', '').strip()

            elif line.startswith('CR '):
                cr_match = re.search(r'CR\s+([\d/]+)\s*\(XP\s+([\d,]+)(?:.*?PB\s+([+\-]?\d+))?', line)
                if cr_match:
                    current_monster['cr'] = cr_match.group(1)
                    current_monster['xp'] = cr_match.group(2).replace(',', '')
                    if cr_match.group(3):
                        current_monster['pb'] = cr_match.group(3)

            elif line.startswith('Gear'):
                current_monster['gear'] = line.replace('Gear', '').strip()

            elif line == 'Traits':
                current_section = 'traits'
            elif line == 'Actions':
                current_section = 'actions'
            elif line == 'Bonus Actions':
                current_section = 'bonus_actions'
            elif line == 'Reactions':
                current_section = 'reactions'
            elif line == 'Legendary Actions':
                current_section = 'legendary_actions'

            elif current_section and line and not line.startswith('MOD SAVE'):
                ability_match = re.match(r'^([A-Z][^.]+)\.\s*(.+)$', line)
                if ability_match:
                    ability_name = ability_match.group(1).strip()
                    ability_desc = ability_match.group(2).strip()

                    full_desc = ability_desc
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            break
                        if re.match(r'^[A-Z][^.]+\.\s*', next_line):
                            break
                        if next_line in ['Traits', 'Actions', 'Bonus Actions', 'Reactions', 'Legendary Actions']:
                            break
                        if re.match(r'^(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+', next_line):
                            break
                        full_desc += ' ' + next_line
                        i = j
                        j += 1

                    if current_section == 'traits':
                        current_monster['traits'].append({'name': ability_name, 'description': full_desc})
                    elif current_section == 'actions':
                        current_monster['actions'].append({'name': ability_name, 'description': full_desc})
                    elif current_section == 'bonus_actions':
                        current_monster['bonus_actions'].append({'name': ability_name, 'description': full_desc})
                    elif current_section == 'reactions':
                        current_monster['reactions'].append({'name': ability_name, 'description': full_desc})
                    elif current_section == 'legendary_actions':
                        current_monster['legendary_actions'].append({'name': ability_name, 'description': full_desc})

        i += 1

    if current_monster:
        monsters.append(current_monster)

    return monsters

if __name__ == '__main__':
    filepath = r'd:\Code\TaleKeeper\docs\SRD_CC_v5.2.1.md'
    monsters = parse_monsters(filepath)

    output_file = r'd:\Code\TaleKeeper\monsters_extracted.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(monsters)} monsters")
    print(f"Saved to {output_file}")

    print("\nFirst 10 monsters:")
    for m in monsters[:10]:
        print(f"  - {m['name']} (CR {m.get('cr', 'N/A')})")
