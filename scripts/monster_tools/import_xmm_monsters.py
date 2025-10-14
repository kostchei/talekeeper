import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..', '..')
db_path = os.path.join(project_root, 'talekeeper.db')
input_file = os.path.join(project_root, 'data', 'monsters', '5etools', 'xmm_missing_monsters.json')

from convert_5etools_to_talekeeper import FiveEToolsConverter

converter = FiveEToolsConverter(db_path=db_path)
converter.import_from_file(input_file, dry_run=False)
