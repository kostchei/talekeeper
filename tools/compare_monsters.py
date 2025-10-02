import sqlite3
import json
import xml.etree.ElementTree as ET

def compare_xml_to_db(xml_file='database/seeds/monsters_complete.xml', db_path='talekeeper.db'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print('Monster Comparison: XML vs Database\n')
    print(f'{"Monster Name":<30} {"XML CR":<8} {"DB CR":<8} {"XML HP":<8} {"DB HP":<8} {"Status":<15}')
    print('=' * 95)

    xml_monsters = {}
    for monster_elem in root.findall('monster'):
        name = monster_elem.find('name').text
        combat_stats = monster_elem.find('combat_stats')
        xml_monsters[name] = {
            'cr': monster_elem.find('cr').text,
            'hp': int(combat_stats.find('hp').text),
            'ac': int(combat_stats.find('ac').text)
        }

    for name, xml_data in sorted(xml_monsters.items()):
        cursor.execute('SELECT challenge_rating, hit_points, armor_class FROM monsters WHERE name = ?', (name,))
        db_row = cursor.fetchone()

        if not db_row:
            print(f'{name:<30} {xml_data["cr"]:<8} {"N/A":<8} {xml_data["hp"]:<8} {"N/A":<8} {"Not in DB":<15}')
            continue

        db_cr, db_hp, db_ac = db_row

        cr_match = str(xml_data['cr']) == str(db_cr)
        hp_match = xml_data['hp'] == db_hp
        ac_match = xml_data['ac'] == db_ac

        if cr_match and hp_match and ac_match:
            status = 'Match'
        else:
            status = 'Mismatch'
            if not cr_match:
                status += ' CR'
            if not hp_match:
                status += ' HP'
            if not ac_match:
                status += ' AC'

        print(f'{name:<30} {xml_data["cr"]:<8} {str(db_cr):<8} {xml_data["hp"]:<8} {str(db_hp):<8} {status:<15}')

    cursor.execute('SELECT name FROM monsters')
    db_monsters = {row[0] for row in cursor.fetchall()}
    xml_names = set(xml_monsters.keys())

    db_only = db_monsters - xml_names
    xml_only = xml_names - db_monsters

    print('\n' + '=' * 95)
    print(f'\nSummary:')
    print(f'  XML monsters: {len(xml_monsters)}')
    print(f'  DB monsters: {len(db_monsters)}')
    print(f'  In both: {len(xml_names & db_monsters)}')
    print(f'  Only in XML: {len(xml_only)}')
    print(f'  Only in DB: {len(db_only)}')

    if xml_only:
        print(f'\nMonsters only in XML (first 10):')
        for name in sorted(list(xml_only))[:10]:
            print(f'  - {name}')

    if db_only:
        print(f'\nMonsters only in DB (first 10):')
        for name in sorted(list(db_only))[:10]:
            print(f'  - {name}')

    conn.close()

def show_monster_details(monster_name, db_path='talekeeper.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM monsters WHERE name = ?', (monster_name,))
    row = cursor.fetchone()

    if not row:
        print(f'Monster "{monster_name}" not found in database')
        conn.close()
        return

    cursor.execute('PRAGMA table_info(monsters)')
    columns = [col[1] for col in cursor.fetchall()]

    monster_dict = dict(zip(columns, row))

    print(f'\n{"="*80}')
    print(f'Monster: {monster_name}')
    print(f'{"="*80}\n')

    print(f'Basic Info:')
    print(f'  ID: {monster_dict.get("id")}')
    print(f'  Name: {monster_dict.get("name")}')
    print(f'  Type: {monster_dict.get("type")} ({monster_dict.get("size")})')
    print(f'  Alignment: {monster_dict.get("alignment")}')

    print(f'\nCombat Stats:')
    print(f'  AC: {monster_dict.get("armor_class")}')
    print(f'  HP: {monster_dict.get("hit_points")}')
    print(f'  Speed: {monster_dict.get("speed")}')

    print(f'\nAbility Scores:')
    print(f'  STR: {monster_dict.get("strength")}')
    print(f'  DEX: {monster_dict.get("dexterity")}')
    print(f'  CON: {monster_dict.get("constitution")}')
    print(f'  INT: {monster_dict.get("intelligence")}')
    print(f'  WIS: {monster_dict.get("wisdom")}')
    print(f'  CHA: {monster_dict.get("charisma")}')

    print(f'\nChallenge:')
    print(f'  CR: {monster_dict.get("challenge_rating")}')
    print(f'  XP: {monster_dict.get("experience_points")}')
    print(f'  Proficiency Bonus: +{monster_dict.get("proficiency_bonus")}')

    if monster_dict.get("skills"):
        print(f'\nSkills: {monster_dict.get("skills")}')

    if monster_dict.get("saving_throws"):
        print(f'\nSaving Throws:')
        try:
            saves = json.loads(monster_dict.get("saving_throws"))
            for save, bonus in saves.items():
                print(f'  {save}: {bonus}')
        except:
            print(f'  {monster_dict.get("saving_throws")}')

    if monster_dict.get("damage_resistances"):
        print(f'\nResistances: {monster_dict.get("damage_resistances")}')

    if monster_dict.get("damage_immunities"):
        print(f'Damage Immunities: {monster_dict.get("damage_immunities")}')

    if monster_dict.get("condition_immunities"):
        print(f'Condition Immunities: {monster_dict.get("condition_immunities")}')

    print(f'\nSenses: {monster_dict.get("senses")}')
    print(f'Languages: {monster_dict.get("languages")}')

    if monster_dict.get("special_abilities"):
        print(f'\nSpecial Abilities:')
        try:
            abilities = json.loads(monster_dict.get("special_abilities"))
            for ability in abilities:
                print(f'  - {ability.get("name")}: {ability.get("description")[:100]}...')
        except:
            print(f'  {monster_dict.get("special_abilities")[:200]}...')

    if monster_dict.get("actions"):
        print(f'\nActions:')
        try:
            actions = json.loads(monster_dict.get("actions"))
            for action in actions:
                print(f'  - {action.get("name")}: {action.get("description")[:100]}...')
        except:
            print(f'  {monster_dict.get("actions")[:200]}...')

    conn.close()

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python compare_monsters.py <action> [args]')
        print('Actions:')
        print('  compare [xml_file] [db_path] - Compare XML monsters to database')
        print('  show <monster_name> [db_path] - Show detailed monster stats from database')
        sys.exit(1)

    action = sys.argv[1]

    if action == 'compare':
        xml_file = sys.argv[2] if len(sys.argv) > 2 else 'database/seeds/monsters_complete.xml'
        db_path = sys.argv[3] if len(sys.argv) > 3 else 'talekeeper.db'
        compare_xml_to_db(xml_file, db_path)

    elif action == 'show':
        if len(sys.argv) < 3:
            print('Usage: python compare_monsters.py show <monster_name> [db_path]')
            sys.exit(1)
        monster_name = sys.argv[2]
        db_path = sys.argv[3] if len(sys.argv) > 3 else 'talekeeper.db'
        show_monster_details(monster_name, db_path)

    else:
        print(f'Unknown action: {action}')
        sys.exit(1)
