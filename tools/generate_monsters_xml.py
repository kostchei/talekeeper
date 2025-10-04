import json
import sqlite3
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_monster_element(monster_data):
    monster = ET.Element('monster', id=monster_data['name'].lower().replace(' ', '_'), validate_stats='true')

    name = ET.SubElement(monster, 'name')
    name.text = monster_data['name']

    image_path = ET.SubElement(monster, 'image_path')
    image_path.text = ''

    basic_info = ET.SubElement(monster, 'basic_info')
    size = ET.SubElement(basic_info, 'size')
    size.text = monster_data.get('size', '')
    type_elem = ET.SubElement(basic_info, 'type')
    type_elem.text = monster_data.get('type', '')
    alignment = ET.SubElement(basic_info, 'alignment')
    alignment.text = monster_data.get('alignment', '')

    combat_stats = ET.SubElement(monster, 'combat_stats')
    ac = ET.SubElement(combat_stats, 'ac')
    ac.text = str(monster_data.get('ac', 10))
    initiative = ET.SubElement(combat_stats, 'initiative')
    initiative.text = monster_data.get('initiative', '+0')
    initiative_score = ET.SubElement(combat_stats, 'initiative_score')
    initiative_score.text = str(monster_data.get('initiative_score', 10))
    hp = ET.SubElement(combat_stats, 'hp')
    hp.text = str(monster_data.get('hp', 1))
    hp_dice = ET.SubElement(combat_stats, 'hp_dice')
    hp_dice.text = monster_data.get('hp_dice', '1d8')
    speed = ET.SubElement(combat_stats, 'speed')
    speed.text = monster_data.get('speed', '30 ft.')

    ability_scores = ET.SubElement(monster, 'ability_scores')
    for ability in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
        ability_elem = ET.SubElement(ability_scores, ability)
        ability_elem.set('value', str(monster_data.get(ability, 10)))
        ability_elem.set('mod', monster_data.get(f'{ability}_mod', '+0'))
        ability_elem.set('save', monster_data.get(f'{ability}_save', '+0'))

    skills = ET.SubElement(monster, 'skills')
    skills.text = monster_data.get('skills', '')

    resistances = ET.SubElement(monster, 'resistances')
    resistances.text = monster_data.get('resistances', '')

    vulnerabilities = ET.SubElement(monster, 'vulnerabilities')
    vulnerabilities.text = monster_data.get('vulnerabilities', '')

    immunities = ET.SubElement(monster, 'immunities')
    immunities.text = monster_data.get('immunities', '')

    senses = ET.SubElement(monster, 'senses')
    senses.text = monster_data.get('senses', 'Passive Perception 10')

    languages = ET.SubElement(monster, 'languages')
    languages.text = monster_data.get('languages', 'None')

    cr = ET.SubElement(monster, 'cr')
    cr.text = str(monster_data.get('cr', '0'))

    xp = ET.SubElement(monster, 'xp')
    xp.text = str(monster_data.get('xp', '0'))

    if monster_data.get('xp_in_lair'):
        xp_in_lair = ET.SubElement(monster, 'xp_in_lair')
        xp_in_lair.text = str(monster_data['xp_in_lair'])

    pb = ET.SubElement(monster, 'pb')
    pb.text = monster_data.get('pb', '+2')

    if monster_data.get('traits'):
        traits = ET.SubElement(monster, 'traits')
        for trait_data in monster_data['traits']:
            trait = ET.SubElement(traits, 'trait')
            trait_name = ET.SubElement(trait, 'name')
            trait_name.text = trait_data.get('name', '')
            if 'usage' in trait_data.get('description', ''):
                usage = ET.SubElement(trait, 'usage')
                desc_parts = trait_data['description'].split('.', 1)
                if len(desc_parts) > 1 and '/' in desc_parts[0]:
                    usage.text = desc_parts[0].strip()
            description = ET.SubElement(trait, 'description')
            description.text = trait_data.get('description', '')

    if monster_data.get('actions'):
        actions = ET.SubElement(monster, 'actions')
        for action_data in monster_data['actions']:
            action_name = action_data.get('name', '').lower()
            action_type = 'multiattack' if 'multiattack' in action_name else \
                         'melee' if 'melee' in action_data.get('description', '').lower() else \
                         'ranged' if 'ranged' in action_data.get('description', '').lower() else \
                         'special'

            action = ET.SubElement(actions, 'action', type=action_type)
            name = ET.SubElement(action, 'name')
            name.text = action_data.get('name', '')

            desc = action_data.get('description', '')
            if 'attack roll:' in desc.lower():
                bonus_start = desc.lower().find('attack roll:') + 12
                bonus_end = desc.find(',', bonus_start)
                if bonus_end > bonus_start:
                    attack_bonus = ET.SubElement(action, 'attack_bonus')
                    attack_bonus.text = desc[bonus_start:bonus_end].strip()

            if 'reach' in desc.lower():
                reach_start = desc.lower().find('reach') + 5
                reach_end = desc.find('.', reach_start)
                if reach_end > reach_start:
                    reach = ET.SubElement(action, 'reach')
                    reach.text = desc[reach_start:reach_end].strip()

            if 'saving throw' in desc.lower():
                if 'dc' in desc.lower():
                    dc_start = desc.lower().find('dc') + 2
                    dc_end = desc.find(',', dc_start)
                    if dc_end > dc_start:
                        save_dc = ET.SubElement(action, 'save_dc')
                        save_dc.text = desc[dc_start:dc_end].strip()

                for save_type in ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charisma']:
                    if save_type.lower() in desc.lower():
                        save_type_elem = ET.SubElement(action, 'save_type')
                        save_type_elem.text = save_type
                        break

            if '/' in action_data.get('name', '') or 'recharge' in desc.lower():
                usage = ET.SubElement(action, 'usage')
                if '/' in action_data['name'] and '(' in action_data['name']:
                    usage.text = action_data['name'].split('(')[1].split(')')[0]
                elif 'recharge' in desc.lower():
                    recharge_start = desc.lower().find('recharge') + 8
                    recharge_end = desc.find(')', recharge_start)
                    if recharge_end > recharge_start:
                        usage.text = 'Recharge ' + desc[recharge_start:recharge_end].strip()

            description = ET.SubElement(action, 'description')
            description.text = desc

    if monster_data.get('bonus_actions'):
        bonus_actions = ET.SubElement(monster, 'bonus_actions')
        for ba_data in monster_data['bonus_actions']:
            bonus_action = ET.SubElement(bonus_actions, 'bonus_action')
            name = ET.SubElement(bonus_action, 'name')
            name.text = ba_data.get('name', '')
            description = ET.SubElement(bonus_action, 'description')
            description.text = ba_data.get('description', '')

    if monster_data.get('reactions'):
        reactions = ET.SubElement(monster, 'reactions')
        for reaction_data in monster_data['reactions']:
            reaction = ET.SubElement(reactions, 'reaction')
            name = ET.SubElement(reaction, 'name')
            name.text = reaction_data.get('name', '')
            description = ET.SubElement(reaction, 'description')
            description.text = reaction_data.get('description', '')

    if monster_data.get('legendary_actions'):
        legendary_actions = ET.SubElement(monster, 'legendary_actions')
        if 'uses' in str(monster_data.get('legendary_actions_header', '')):
            header = monster_data.get('legendary_actions_header', '')
            if 'uses:' in header.lower():
                uses_start = header.lower().find('uses:') + 5
                uses_end = header.find(' ', uses_start)
                if uses_end > uses_start:
                    legendary_actions.set('uses', header[uses_start:uses_end].strip())

        for la_data in monster_data['legendary_actions']:
            legendary_action = ET.SubElement(legendary_actions, 'legendary_action')
            name = ET.SubElement(legendary_action, 'name')
            name.text = la_data.get('name', '')
            description = ET.SubElement(legendary_action, 'description')
            description.text = la_data.get('description', '')

    return monster

def prettify_xml(elem):
    rough_string = ET.tostring(elem)
    reparsed = minidom.parseString(rough_string)
    xml_str = reparsed.toprettyxml(indent='  ')
    return ''.join(char for char in xml_str if ord(char) < 128)

def generate_monsters_xml(json_file, output_xml):
    with open(json_file, 'r') as f:
        monsters_data = json.load(f)

    root = ET.Element('monsters', version='5.2.1', source='SRD_CC_v5.2.1')

    comment = ET.Comment('''
    TaleKeeper Monster Database - D&D 2024 SRD

    Usage:
    - Add image paths in the image_path attribute
    - Use validate_stats="true" to check against database
    - Custom monsters can be added with source="custom"
  ''')
    root.append(comment)

    for monster_data in monsters_data:
        monster_element = create_monster_element(monster_data)
        root.append(monster_element)

    xml_string = prettify_xml(root)

    with open(output_xml, 'w') as f:
        f.write(xml_string)

    print(f'Generated {output_xml} with {len(monsters_data)} monsters')

def validate_monster_against_db(monster_name, db_path='talekeeper.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM monsters WHERE name = ?', (monster_name,))
    db_monster = cursor.fetchone()

    if not db_monster:
        print(f'Monster "{monster_name}" not found in database')
        return False

    cursor.execute('PRAGMA table_info(monsters)')
    columns = [col[1] for col in cursor.fetchall()]

    monster_dict = dict(zip(columns, db_monster))

    print(f'\nMonster: {monster_name}')
    print(f'Database stats:')
    for key, value in monster_dict.items():
        if value is not None:
            print(f'  {key}: {value}')

    conn.close()
    return True

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python generate_monsters_xml.py <action> [args]')
        print('Actions:')
        print('  generate <json_file> <output_xml> - Generate XML from JSON')
        print('  validate <monster_name> [db_path] - Validate monster against database')
        sys.exit(1)

    action = sys.argv[1]

    if action == 'generate':
        if len(sys.argv) < 4:
            print('Usage: python generate_monsters_xml.py generate <json_file> <output_xml>')
            sys.exit(1)
        generate_monsters_xml(sys.argv[2], sys.argv[3])

    elif action == 'validate':
        if len(sys.argv) < 3:
            print('Usage: python generate_monsters_xml.py validate <monster_name> [db_path]')
            sys.exit(1)
        db_path = sys.argv[3] if len(sys.argv) > 3 else 'talekeeper.db'
        validate_monster_against_db(sys.argv[2], db_path)

    else:
        print(f'Unknown action: {action}')
        sys.exit(1)
