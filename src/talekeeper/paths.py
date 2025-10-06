import os
import sys
from pathlib import Path

def get_root_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent

def get_data_path(relative_path=''):
    root = get_root_path()
    data_dir = root / 'data'
    if relative_path:
        return str(data_dir / relative_path)
    return str(data_dir)

def get_config_path(relative_path=''):
    root = get_root_path()
    config_dir = root / 'data' / 'config'
    if relative_path:
        return str(config_dir / relative_path)
    return str(config_dir)

def get_database_path(db_name='talekeeper.db'):
    root = get_root_path()
    return str(root / db_name)

def get_assets_path(relative_path=''):
    root = get_root_path()
    assets_dir = root / 'data' / 'assets'
    if relative_path:
        return str(assets_dir / relative_path)
    return str(assets_dir)

def get_logs_path(relative_path=''):
    root = get_root_path()
    logs_dir = root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    if relative_path:
        return str(logs_dir / relative_path)
    return str(logs_dir)
