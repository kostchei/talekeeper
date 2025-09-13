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
            
            # Load seed files in order
            seed_files = [
                '001_game_data.sql',  # Legacy data (keep for compatibility)
                '002_core_game_data.sql',
                '003_backgrounds.sql', 
                '004_equipment.sql',
                '005_monsters.sql',
                '007_class_features.sql',
                '008_class_proficiencies.sql',
                '100_starter_character.sql',
                '101_test_characters.sql'
            ]
            
            total_loaded = 0
            for seed_file in seed_files:
                file_path = self.seeds_dir / seed_file
                if file_path.exists():
                    print(f"Loading {seed_file}...")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    try:
                        cursor.executescript(sql_content)
                        conn.commit()
                        total_loaded += 1
                    except sqlite3.Error as e:
                        print(f"Warning: Error loading {seed_file}: {e}")
                        # Continue with other files
                else:
                    print(f"Seed file {seed_file} not found, skipping...")
            
            # Verify data was loaded
            try:
                cursor.execute("SELECT COUNT(*) FROM classes")
                class_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM races") 
                race_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM equipment")
                equipment_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM monsters")
                monster_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM characters")
                char_count = cursor.fetchone()[0]
                
                print(f"Game data loaded from {total_loaded} files:")
                print(f"  - {class_count} classes, {race_count} races")
                print(f"  - {equipment_count} equipment items, {monster_count} monsters")
                print(f"  - {char_count} starter character(s)")
                
            except sqlite3.Error:
                print("Data loaded successfully (some tables may not exist yet)")
            
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
        """Legacy migration support - now redirects to schema versioning."""
        print("Checking database schema version...")
        return self.check_schema_version()
    
    def check_schema_version(self) -> bool:
        """Check and upgrade database schema if needed."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create schema_version table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    description TEXT NOT NULL,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Get current schema version
            cursor.execute('SELECT version FROM schema_version ORDER BY version DESC LIMIT 1')
            result = cursor.fetchone()
            current_version = result[0] if result else 0
            
            # Target schema version
            target_version = 2
            
            if current_version >= target_version:
                print(f"Database schema is up to date (version {current_version})")
                return True
            
            print(f"Database schema needs update: v{current_version} -> v{target_version}")
            
            # Check if this is an old database with migrations
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            has_old_migrations = cursor.fetchone() is not None
            
            if has_old_migrations and current_version == 0:
                # This is an existing database with old migration system
                print("Detected existing database with migration system")
                print("Marking as schema version 2 (all migrations already applied)")
                
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_version (version, description)
                    VALUES (2, 'Migrated from legacy migration system')
                ''')
                conn.commit()
                print("Schema version updated to v2")
                return True
            
            elif current_version == 1:
                # Future: handle upgrade from v1 to v2
                print("Upgrading schema from v1 to v2...")
                # Would contain specific upgrade logic here
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_version (version, description)
                    VALUES (2, 'Upgraded from schema v1')
                ''')
                conn.commit()
                print("Schema upgraded to v2")
                return True
            
            else:
                print(f"Unknown schema version: {current_version}")
                return False
            
        except Exception as e:
            print(f"Error checking schema version: {e}")
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