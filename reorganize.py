import os
import shutil
from pathlib import Path

root = Path(__file__).parent

moves = {
    'core': 'src/talekeeper/core',
    'services': 'src/talekeeper/services',
    'audio': 'src/talekeeper/audio',
    'models': 'src/talekeeper/models',
    'ui': 'src/talekeeper/ui',
    'action_cards': 'src/talekeeper/ui/action_cards',
    'character_sheet': 'src/talekeeper/ui/character_sheet',
    'encounter_pane': 'src/talekeeper/ui/encounter_pane',
    'equipment_layout': 'src/talekeeper/ui/equipment_layout',
    'menu': 'src/talekeeper/ui/menu',
    'database/schema': 'data/database/schema',
    'database/seeds': 'data/database/seeds',
    'database/migrations': 'data/database/migrations',
}

data_files = {
    'monsters_extracted.json': 'data/monsters/',
    'srd_monsters_parsed.json': 'data/monsters/',
    'monsters_sample_with_metadata.json': 'data/monsters/',
    'monster_validation_issues.json': 'data/monsters/validation/',
    'monster_attack_discrepancies.json': 'data/monsters/validation/',
    'monster_comparison_results.json': 'data/monsters/validation/',
    'talekeeper_config.json': 'data/config/',
}

script_files = {
    'extract_monsters.py': 'scripts/monster_tools/',
    'compare_monsters.py': 'scripts/monster_tools/',
    'compare_monster_attacks.py': 'scripts/monster_tools/',
    'validate_monster_attacks.py': 'scripts/monster_tools/',
    'cleanup_monster_data.py': 'scripts/monster_tools/',
    'fix_monster_attacks.py': 'scripts/monster_tools/',
    'fix_monster_names.py': 'scripts/monster_tools/',
    'fix_monster_stats.py': 'scripts/monster_tools/',
    'update_monster_attacks.py': 'scripts/monster_tools/',
    'update_monsters_to_2024.py': 'scripts/monster_tools/',
    'parse_srd_monsters.py': 'scripts/monster_tools/',
    'check_legacy_monsters.py': 'scripts/monster_tools/',
    'analyze_discrepancies.py': 'scripts/utilities/',
    'generate_summary.py': 'scripts/utilities/',
    'priority_review_list.py': 'scripts/utilities/',
    'create_level5_rogue.py': 'scripts/character_tools/',
    'fix_spell_slots.py': 'scripts/database_tools/',
    'spell_diagnostic.py': 'scripts/database_tools/',
    'validate_unified_system.py': 'scripts/utilities/',
    'manage_subclass_filter.py': 'scripts/utilities/',
}

doc_files = {
    'MONSTER_ATTACK_VALIDATION_REPORT.md': 'docs/reports/',
    'MONSTER_UPDATE_SUMMARY.md': 'docs/reports/',
    'monster_comparison_summary.md': 'docs/reports/',
    'MONSTERS_README.md': 'docs/reports/',
    'MONSTERS_SUMMARY.txt': 'docs/reports/',
    'CLASS_FEATURE_SYSTEM_DESIGN.md': 'docs/development/',
    'INSTALLATION_COMPLETE.md': 'docs/development/',
    'README_TESTING_FRAMEWORK.md': 'docs/development/',
    'RELEASE_NOTES_v3.0.md': 'docs/development/',
}

asset_files = {
    'art': 'data/assets/art',
    'assets': 'data/assets/images',
}

def copy_directory(src, dst):
    src_path = root / src
    dst_path = root / dst
    if src_path.exists():
        print(f"Moving {src} -> {dst}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if dst_path.exists():
            shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)

        for py_file in dst_path.rglob('*.py'):
            update_imports(py_file)
    else:
        print(f"SKIP: {src} does not exist")

def copy_file(src, dst_dir):
    src_path = root / src
    dst_path = root / dst_dir / src_path.name
    if src_path.exists():
        print(f"Moving {src} -> {dst_dir}")
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
    else:
        print(f"SKIP: {src} does not exist")

def update_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        replacements = {
            'from core.': 'from talekeeper.core.',
            'from services.': 'from talekeeper.services.',
            'from audio.': 'from talekeeper.audio.',
            'from ui.': 'from talekeeper.ui.',
            'from action_cards.': 'from talekeeper.ui.action_cards.',
            'from character_sheet.': 'from talekeeper.ui.character_sheet.',
            'from encounter_pane.': 'from talekeeper.ui.encounter_pane.',
            'from equipment_layout.': 'from talekeeper.ui.equipment_layout.',
            'from menu.': 'from talekeeper.ui.menu.',
            'from database.': 'from talekeeper.database.',
            'from models.': 'from talekeeper.models.',
            'import core.': 'import talekeeper.core.',
            'import services.': 'import talekeeper.services.',
            'import audio.': 'import talekeeper.audio.',
            'import ui.': 'import talekeeper.ui.',
        }

        for old, new in replacements.items():
            content = content.replace(old, new)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Updated imports in {file_path.name}")
    except Exception as e:
        print(f"  Error updating {file_path}: {e}")

print("=== Phase 2: Moving Application Code ===")
for src, dst in moves.items():
    copy_directory(src, dst)

print("\n=== Creating __init__.py files ===")
for subdir in ['ui', 'core', 'services', 'audio', 'database', 'models']:
    init_file = root / 'src' / 'talekeeper' / subdir / '__init__.py'
    if not init_file.exists():
        init_file.write_text('')
        print(f"Created {init_file}")

for subdir in ['action_cards', 'character_sheet', 'encounter_pane', 'equipment_layout', 'menu']:
    init_file = root / 'src' / 'talekeeper' / 'ui' / subdir / '__init__.py'
    if not init_file.exists():
        init_file.write_text('')
        print(f"Created {init_file}")

print("\n=== Phase 3: Moving Data Files ===")
for src, dst in data_files.items():
    copy_file(src, dst)

print("\n=== Moving Assets ===")
for src, dst in asset_files.items():
    copy_directory(src, dst)

print("\n=== Phase 4: Moving Script Files ===")
for src, dst in script_files.items():
    copy_file(src, dst)

print("\n=== Moving Documentation ===")
for src, dst in doc_files.items():
    copy_file(src, dst)

print("\n=== Moving database initialization ===")
db_init = root / 'database' / 'database_init.py'
if db_init.exists():
    dst = root / 'src' / 'talekeeper' / 'database' / 'database_init.py'
    shutil.copy2(db_init, dst)
    update_imports(dst)
    print(f"Moved database_init.py")

db_populate = root / 'database' / 'populate_test_characters.py'
if db_populate.exists():
    dst = root / 'scripts' / 'database_tools' / 'populate_test_characters.py'
    shutil.copy2(db_populate, dst)
    print(f"Moved populate_test_characters.py")

print("\n=== Consolidating Tests ===")
test_dirs = ['test', 'tests', 'testing']
for test_dir in test_dirs:
    src_path = root / test_dir
    if src_path.exists() and src_path.is_dir():
        for file in src_path.rglob('*.py'):
            rel_path = file.relative_to(src_path)
            dst_file = root / 'tests' / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dst_file)
            print(f"Moved test: {file} -> {dst_file}")

print("\nDone! Review changes before committing.")
