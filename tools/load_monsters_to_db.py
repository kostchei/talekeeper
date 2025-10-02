import sqlite3
import xml.etree.ElementTree as ET
import json
import sys

def parse_ability_scores(ability_scores_elem):
    scores = {}
    for ability in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
        elem = ability_scores_elem.find(ability)
        if elem is not None:
            scores[ability] = {
                'value': int(elem.get('value', 10)),
                'mod': elem.get('mod', '+0'),
                'save': elem.get('save', '+0')
            }
        else:
            scores[ability] = {'value': 10, 'mod': '+0', 'save': '+0'}
    return scores

def parse_traits(traits_elem):
    if traits_elem is None:
        return []

    traits = []
    for trait in traits_elem.findall('trait'):
        trait_data = {
            'name': trait.find('name').text if trait.find('name') is not None else '',
            'description': trait.find('description').text if trait.find('description') is not None else ''
        }
        usage_elem = trait.find('usage')
        if usage_elem is not None:
            trait_data['usage'] = usage_elem.text
        traits.append(trait_data)
    return traits

def parse_actions(actions_elem):
    if actions_elem is None:
        return []

    actions = []
    for action in actions_elem.findall('action'):
        action_data = {
            'name': action.find('name').text if action.find('name') is not None else '',
            'description': action.find('description').text if action.find('description') is not None else '',
            'type': action.get('type', 'special')
        }

        attack_bonus = action.find('attack_bonus')
        if attack_bonus is not None:
            action_data['attack_bonus'] = attack_bonus.text

        reach = action.find('reach')
        if reach is not None:
            action_data['reach'] = reach.text

        save_dc = action.find('save_dc')
        if save_dc is not None:
            action_data['save_dc'] = save_dc.text

        save_type = action.find('save_type')
        if save_type is not None:
            action_data['save_type'] = save_type.text

        usage = action.find('usage')
        if usage is not None:
            action_data['usage'] = usage.text

        actions.append(action_data)
    return actions

def parse_legendary_actions(legendary_actions_elem):
    if legendary_actions_elem is None:
        return None

    result = {
        'uses': legendary_actions_elem.get('uses', '3'),
        'actions': []
    }

    uses_in_lair = legendary_actions_elem.get('uses_in_lair')
    if uses_in_lair:
        result['uses_in_lair'] = uses_in_lair

    for la in legendary_actions_elem.findall('legendary_action'):
        result['actions'].append({
            'name': la.find('name').text if la.find('name') is not None else '',
            'description': la.find('description').text if la.find('description') is not None else ''
        })

    return result

def parse_reactions(reactions_elem):
    if reactions_elem is None:
        return []

    reactions = []
    for reaction in reactions_elem.findall('reaction'):
        reactions.append({
            'name': reaction.find('name').text if reaction.find('name') is not None else '',
            'description': reaction.find('description').text if reaction.find('description') is not None else ''
        })
    return reactions

def load_monsters_from_xml(xml_file, db_path='talekeeper.db'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    monsters_loaded = 0
    monsters_updated = 0
    monsters_skipped = 0

    for monster_elem in root.findall('monster'):
        monster_id = monster_elem.get('id')
        name = monster_elem.find('name').text

        basic_info = monster_elem.find('basic_info')
        size = basic_info.find('size').text if basic_info.find('size') is not None else 'Medium'
        creature_type = basic_info.find('type').text if basic_info.find('type') is not None else 'Humanoid'
        alignment = basic_info.find('alignment').text if basic_info.find('alignment') is not None else 'Neutral'

        combat_stats = monster_elem.find('combat_stats')
        ac = int(combat_stats.find('ac').text) if combat_stats.find('ac') is not None else 10
        hp = int(combat_stats.find('hp').text) if combat_stats.find('hp') is not None else 1
        speed = combat_stats.find('speed').text if combat_stats.find('speed') is not None else '30 ft.'

        ability_scores = parse_ability_scores(monster_elem.find('ability_scores'))

        skills = monster_elem.find('skills').text or ''
        resistances = monster_elem.find('resistances').text or ''
        immunities_elem = monster_elem.find('immunities')
        immunities_text = immunities_elem.text if immunities_elem is not None else ''

        damage_immunities = ''
        condition_immunities = ''
        if immunities_text and ';' in immunities_text:
            parts = immunities_text.split(';')
            damage_immunities = parts[0].strip()
            condition_immunities = parts[1].strip() if len(parts) > 1 else ''
        else:
            damage_immunities = immunities_text

        senses = monster_elem.find('senses').text if monster_elem.find('senses') is not None else 'Passive Perception 10'
        languages = monster_elem.find('languages').text if monster_elem.find('languages') is not None else 'None'

        cr = monster_elem.find('cr').text if monster_elem.find('cr') is not None else '0'
        xp = int(monster_elem.find('xp').text) if monster_elem.find('xp') is not None else 0
        pb = monster_elem.find('pb').text if monster_elem.find('pb') is not None else '+2'
        pb_value = int(pb.replace('+', '')) if '+' in pb else int(pb)

        traits = parse_traits(monster_elem.find('traits'))
        actions = parse_actions(monster_elem.find('actions'))
        reactions = parse_reactions(monster_elem.find('reactions'))
        legendary_actions = parse_legendary_actions(monster_elem.find('legendary_actions'))

        saving_throws = {}
        for ability in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
            save_value = ability_scores[ability]['save']
            if save_value != ability_scores[ability]['mod']:
                saving_throws[ability.upper()] = save_value

        cursor.execute('SELECT id FROM monsters WHERE id = ?', (monster_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute('''
                UPDATE monsters SET
                    name = ?, type = ?, size = ?, alignment = ?,
                    armor_class = ?, hit_points = ?, speed = ?,
                    strength = ?, dexterity = ?, constitution = ?,
                    intelligence = ?, wisdom = ?, charisma = ?,
                    challenge_rating = ?, experience_points = ?, proficiency_bonus = ?,
                    saving_throws = ?, skills = ?,
                    damage_resistances = ?, damage_immunities = ?, condition_immunities = ?,
                    senses = ?, languages = ?,
                    special_abilities = ?, actions = ?, legendary_actions = ?, reactions = ?
                WHERE id = ?
            ''', (
                name, creature_type, size, alignment,
                ac, hp, speed,
                ability_scores['str']['value'], ability_scores['dex']['value'], ability_scores['con']['value'],
                ability_scores['int']['value'], ability_scores['wis']['value'], ability_scores['cha']['value'],
                cr, xp, pb_value,
                json.dumps(saving_throws), skills,
                resistances, damage_immunities, condition_immunities,
                senses, languages,
                json.dumps(traits), json.dumps(actions), json.dumps(legendary_actions) if legendary_actions else None, json.dumps(reactions),
                monster_id
            ))
            monsters_updated += 1
        else:
            cursor.execute('''
                INSERT INTO monsters (
                    id, name, type, size, alignment,
                    armor_class, hit_points, speed,
                    strength, dexterity, constitution, intelligence, wisdom, charisma,
                    challenge_rating, experience_points, proficiency_bonus,
                    saving_throws, skills,
                    damage_resistances, damage_immunities, condition_immunities,
                    senses, languages,
                    special_abilities, actions, legendary_actions, reactions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                monster_id, name, creature_type, size, alignment,
                ac, hp, speed,
                ability_scores['str']['value'], ability_scores['dex']['value'], ability_scores['con']['value'],
                ability_scores['int']['value'], ability_scores['wis']['value'], ability_scores['cha']['value'],
                cr, xp, pb_value,
                json.dumps(saving_throws), skills,
                resistances, damage_immunities, condition_immunities,
                senses, languages,
                json.dumps(traits), json.dumps(actions), json.dumps(legendary_actions) if legendary_actions else None, json.dumps(reactions)
            ))
            monsters_loaded += 1

    conn.commit()
    conn.close()

    print(f'Monster database updated:')
    print(f'  New monsters: {monsters_loaded}')
    print(f'  Updated monsters: {monsters_updated}')
    print(f'  Total processed: {monsters_loaded + monsters_updated}')

def list_monsters_in_db(db_path='talekeeper.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM monsters')
    total = cursor.fetchone()[0]
    print(f'Total monsters in database: {total}')

    cursor.execute('SELECT challenge_rating, COUNT(*) FROM monsters GROUP BY challenge_rating ORDER BY CAST(challenge_rating AS REAL)')
    print('\nMonsters by CR:')
    for cr, count in cursor.fetchall():
        print(f'  CR {cr}: {count}')

    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python load_monsters_to_db.py <action> [args]')
        print('Actions:')
        print('  load <xml_file> [db_path] - Load monsters from XML into database')
        print('  list [db_path] - List monsters in database')
        sys.exit(1)

    action = sys.argv[1]

    if action == 'load':
        if len(sys.argv) < 3:
            print('Usage: python load_monsters_to_db.py load <xml_file> [db_path]')
            sys.exit(1)
        xml_file = sys.argv[2]
        db_path = sys.argv[3] if len(sys.argv) > 3 else 'talekeeper.db'
        load_monsters_from_xml(xml_file, db_path)

    elif action == 'list':
        db_path = sys.argv[2] if len(sys.argv) > 2 else 'talekeeper.db'
        list_monsters_in_db(db_path)

    else:
        print(f'Unknown action: {action}')
        sys.exit(1)
