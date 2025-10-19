# core
#utility
# core
import re
import sys

old_pattern = r'''cursor\.execute\("""
\s+INSERT OR IGNORE INTO character_features \(character_id, feature_id, feature_source, feature_data\)
\s+VALUES \(\?, '[^']+', 'warlock_patron', \?\)
\s+""", \(character_id, json\.dumps\((\{[^}]+\})\)\)\)'''

def convert_insert(match):
    data_dict_str = match.group(1)
    feature_name = re.search(r"'name':\s*'([^']+)'", data_dict_str).group(1)
    description = re.search(r"'description':\s*'([^']+)'", data_dict_str)
    desc_text = description.group(1) if description else ''

    usage_type = 'permanent'
    feature_type = 'passive'
    if 'action' in desc_text.lower():
        feature_type = 'action'
    if 'reaction' in desc_text.lower():
        feature_type = 'reaction'
    if 'bonus action' in desc_text.lower():
        feature_type = 'bonus_action'

    data_with_source = data_dict_str.rstrip('}') + ", 'source': 'warlock_patron'}"

    return f'''cursor.execute("""
                    INSERT OR IGNORE INTO character_features
                    (character_id, feature_name, feature_type, usage_type, level_gained, description, mechanics)
                    VALUES (?, '{feature_name}', '{feature_type}', '{usage_type}', ?, ?, ?)
                """, (character_id, level, {data_dict_str}.get('description', ''),
                      json.dumps({data_with_source})))'''

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_warlock_schema.py <file>")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(old_pattern, convert_insert, content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed {filepath}")
