import sqlite3
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import json
import hashlib
from datetime import datetime

class DatabaseInitializer:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        self.database_dir = Path(__file__).parent
        self.schema_dir = self.database_dir / 'schema'
        self.seeds_dir = self.database_dir / 'seeds'
        self.migrations_dir = self.database_dir / 'migrations'
        
    def initialize(self, force: bool = False, dev_mode: bool = False) -> bool:
        if os.path.exists(self.db_path) and not force:
            print(f"Database already exists at {self.db_path}")
            return self.check_and_apply_migrations()
        
        if force and os.path.exists(self.db_path):
            print(f"Force mode: Backing up existing database...")
            backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(self.db_path, backup_path)
            print(f"Existing database backed up to {backup_path}")
        
        print("Initializing new database...")
        
        if not self.create_schema():
            return False
            
        if not self.load_game_data():
            return False
            
        if dev_mode and not self.load_dev_data():
            print("Warning: Failed to load dev data, continuing...")
        
        if not self.create_migrations_table():
            return False
            
        print("Database initialization complete!")
        return True
    
    def create_schema(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            schema_file = self.schema_dir / '001_initial_schema.sql'
            if not schema_file.exists():
                print(f"Error: Schema file not found at {schema_file}")
                return False
            
            print(f"Loading schema from {schema_file}...")
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor.executescript(schema_sql)
            conn.commit()
            
            print("Schema created successfully")
            return True
            
        except Exception as e:
            print(f"Error creating schema: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def load_game_data(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            game_data_file = self.seeds_dir / '001_game_data.sql'
            if not game_data_file.exists():
                print(f"Error: Game data file not found at {game_data_file}")
                return False
            
            print(f"Loading game data from {game_data_file}...")
            with open(game_data_file, 'r', encoding='utf-8') as f:
                game_data_sql = f.read()
            
            cursor.executescript(game_data_sql)
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM classes")
            class_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM races")
            race_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM equipment")
            equipment_count = cursor.fetchone()[0]
            
            print(f"Game data loaded: {class_count} classes, {race_count} races, {equipment_count} equipment items")
            return True
            
        except Exception as e:
            print(f"Error loading game data: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def load_dev_data(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            dev_data_file = self.seeds_dir / '002_dev_data.sql'
            if not dev_data_file.exists():
                print("No dev data file found, skipping...")
                return True
            
            print(f"Loading dev data from {dev_data_file}...")
            with open(dev_data_file, 'r', encoding='utf-8') as f:
                dev_data_sql = f.read()
            
            cursor.executescript(dev_data_sql)
            conn.commit()
            
            print("Dev data loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading dev data: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def create_migrations_table(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO schema_migrations (version, checksum, description)
                VALUES ('001_initial_schema', 'initial', 'Initial database schema')
            ''')
            
            conn.commit()
            print("Migrations table created")
            return True
            
        except Exception as e:
            print(f"Error creating migrations table: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def check_and_apply_migrations(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            ''')
            
            cursor.execute('SELECT version FROM schema_migrations')
            applied_migrations = {row[0] for row in cursor.fetchall()}
            
            migration_files = sorted([f for f in os.listdir(self.migrations_dir) 
                                    if f.endswith('.sql')] if self.migrations_dir.exists() else [])
            
            new_migrations = []
            for migration_file in migration_files:
                version = migration_file.replace('.sql', '')
                if version not in applied_migrations:
                    new_migrations.append(migration_file)
            
            if not new_migrations:
                print("Database is up to date")
                return True
            
            print(f"Found {len(new_migrations)} new migration(s) to apply")
            
            for migration_file in new_migrations:
                migration_path = self.migrations_dir / migration_file
                version = migration_file.replace('.sql', '')
                
                print(f"Applying migration: {version}")
                
                with open(migration_path, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                    checksum = hashlib.md5(migration_sql.encode()).hexdigest()
                
                try:
                    cursor.executescript(migration_sql)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"  Column already exists (skipping): {e}")
                    else:
                        raise
                
                description = migration_sql.split('\n')[0].replace('--', '').strip() if migration_sql.startswith('--') else version
                
                cursor.execute('''
                    INSERT INTO schema_migrations (version, checksum, description)
                    VALUES (?, ?, ?)
                ''', (version, checksum, description))
                
                print(f"Applied migration: {version}")
            
            conn.commit()
            print("All migrations applied successfully")
            return True
            
        except Exception as e:
            print(f"Error applying migrations: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    def verify_database(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            required_tables = [
                'characters', 'classes', 'races', 'equipment', 
                'feats', 'backgrounds', 'level_progression'
            ]
            
            missing_tables = []
            for table in required_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"Error: Missing required tables: {', '.join(missing_tables)}")
                return False
            
            print("Database verification passed")
            return True
            
        except Exception as e:
            print(f"Error verifying database: {e}")
            return False
        finally:
            if conn:
                conn.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='TaleKeeper Database Initialization')
    parser.add_argument('--force', action='store_true', help='Force recreate database (backs up existing)')
    parser.add_argument('--dev', action='store_true', help='Load development test data')
    parser.add_argument('--verify', action='store_true', help='Verify database integrity')
    parser.add_argument('--db-path', default='talekeeper.db', help='Database file path')
    
    args = parser.parse_args()
    
    initializer = DatabaseInitializer(args.db_path)
    
    if args.verify:
        success = initializer.verify_database()
        sys.exit(0 if success else 1)
    
    success = initializer.initialize(force=args.force, dev_mode=args.dev)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()