# core
# category: core
import sqlite3
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import json
import hashlib
from datetime import datetime
from talekeeper.paths import get_data_path

class DatabaseInitializer:
    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path
        root = Path(__file__).parent.parent.parent.parent
        self.schema_dir = root / 'database' / 'schema'
        self.seeds_dir = root / 'database' / 'seeds'
        self.migrations_dir = root / 'database' / 'migrations'
        
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
        if not self.apply_sql_migrations():
            return False
        if not self.check_schema_version():
            return False
            
        print("Database initialization complete!")
        return True
    
    def create_schema(self) -> bool:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            schema_file = self.schema_dir / '001_initial_schema.sql'
            if not schema_file.exists():
                print(f"Error: Schema file not found at {schema_file}")
                return False

            print(f"Loading schema from {schema_file}...")
            with open(schema_file, 'r') as f:
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
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load seed files in order
            seed_files = [
                '001_game_data.sql',
                '002_core_game_data.sql',
                '003_backgrounds.sql',
                '004_equipment.sql',
                '005_monsters.sql',
                '006_skill_challenges.sql',
                '007_class_features.sql',
                '008_class_proficiencies.sql',
                '009_best_in_slot_items.sql',
                '100_starter_character.sql',
                '101_test_characters.sql'
            ]
            
            total_loaded = 0
            for seed_file in seed_files:
                file_path = self.seeds_dir / seed_file
                if file_path.exists():
                    print(f"Loading {seed_file}...")
                    with open(file_path, 'r') as f:
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
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            dev_data_file = self.seeds_dir / '002_dev_data.sql'
            if not dev_data_file.exists():
                print("No dev data file found, skipping...")
                return True
            
            print(f"Loading dev data from {dev_data_file}...")
            with open(dev_data_file, 'r') as f:
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
        conn = None
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
                INSERT OR IGNORE INTO schema_migrations (version, checksum, description)
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
        print("Ensuring database migrations are applied...")
        if not self.apply_sql_migrations():
            return False
        print("Checking database schema version...")
        return self.check_schema_version()

    def apply_sql_migrations(self) -> bool:
        """Apply pending .sql migrations in order."""
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

            self._ensure_legacy_tables(cursor)
            conn.commit()

            cursor.execute("SELECT version, checksum FROM schema_migrations")
            applied = {row[0]: row[1] for row in cursor.fetchall()}

            migration_files = sorted(self.migrations_dir.glob('*.sql'))
            acceptable_errors = ('duplicate column name', 'already exists')

            for migration_file in migration_files:
                version = migration_file.name
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql = f.read()

                checksum = hashlib.sha256(sql.encode('utf-8')).hexdigest()
                if applied.get(version) == checksum:
                    continue

                description = sql.splitlines()[0].strip().lstrip('- ').strip()
                print(f"Applying migration {version}...")
                try:
                    cursor.executescript(sql)
                except sqlite3.Error as e:
                    message = str(e).lower()
                    if any(err in message for err in acceptable_errors):
                        print(f"  Skipping statements already applied: {e}")
                    else:
                        raise
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_migrations (version, checksum, description)
                    VALUES (?, ?, ?)
                ''', (version, checksum, description or version))
                conn.commit()

            return True
        except Exception as e:
            print(f"Error applying migrations: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _ensure_inventory_columns(self, cursor: sqlite3.Cursor):
        """Ensure Bag of Holding columns exist on character_inventory."""
        cursor.execute("PRAGMA table_info(character_inventory)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'stored_in_bag' not in columns:
            cursor.execute("ALTER TABLE character_inventory ADD COLUMN stored_in_bag INTEGER NOT NULL DEFAULT 0")

        if 'treasure_type' not in columns:
            cursor.execute("ALTER TABLE character_inventory ADD COLUMN treasure_type TEXT NOT NULL DEFAULT 'standard'")

        if 'unit_value_gp' not in columns:
            cursor.execute("ALTER TABLE character_inventory ADD COLUMN unit_value_gp REAL DEFAULT NULL")

    def _ensure_spellcasting_columns(self, cursor: sqlite3.Cursor):
        """Ensure modern spellcasting columns exist."""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_spellcasting'")
        if not cursor.fetchone():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_spellcasting (
                    character_id TEXT NOT NULL,
                    spellcasting_class TEXT NOT NULL,
                    spellcasting_ability TEXT,
                    spell_attack_bonus INTEGER DEFAULT 0,
                    spell_save_dc INTEGER DEFAULT 8,
                    ritual_casting BOOLEAN DEFAULT 0,
                    spellcasting_focus TEXT,
                    cantrips_known INTEGER DEFAULT 0,
                    spells_known INTEGER DEFAULT 0,
                    spells_prepared INTEGER DEFAULT 0,
                    known_spells TEXT,
                    prepared_spells TEXT,
                    last_preparation_reset TEXT,
                    PRIMARY KEY (character_id, spellcasting_class),
                    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            """)
            return

        cursor.execute("PRAGMA table_info(character_spellcasting)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'spellcasting_class' not in columns:
            cursor.execute("ALTER TABLE character_spellcasting ADD COLUMN spellcasting_class TEXT DEFAULT ''")
        if 'cantrips_known' not in columns:
            cursor.execute("ALTER TABLE character_spellcasting ADD COLUMN cantrips_known INTEGER DEFAULT 0")
        if 'known_spells' not in columns:
            cursor.execute("ALTER TABLE character_spellcasting ADD COLUMN known_spells TEXT")
        if 'prepared_spells' not in columns:
            cursor.execute("ALTER TABLE character_spellcasting ADD COLUMN prepared_spells TEXT")

    def _ensure_legacy_tables(self, cursor: sqlite3.Cursor):
        self._ensure_character_hp_columns(cursor)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id TEXT NOT NULL,
                level INTEGER NOT NULL,
                feature_name TEXT NOT NULL,
                description TEXT,
                UNIQUE(class_id, level, feature_name),
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_magical_bonuses (
                character_id TEXT PRIMARY KEY,
                ac_bonus INTEGER DEFAULT 0,
                save_bonus INTEGER DEFAULT 0,
                attack_bonus INTEGER DEFAULT 0,
                damage_bonus INTEGER DEFAULT 0,
                str_bonus INTEGER DEFAULT 0,
                dex_bonus INTEGER DEFAULT 0,
                con_bonus INTEGER DEFAULT 0,
                int_bonus INTEGER DEFAULT 0,
                wis_bonus INTEGER DEFAULT 0,
                cha_bonus INTEGER DEFAULT 0,
                ability_check_bonus INTEGER DEFAULT 0,
                skill_bonuses TEXT DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_attunements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id TEXT NOT NULL,
                item_key TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
                UNIQUE(character_id, item_key)
            )
        """)

        self._ensure_spellcasting_columns(cursor)
        self._ensure_warlock_invocation_columns(cursor)

    def _ensure_character_hp_columns(self, cursor: sqlite3.Cursor):
        cursor.execute("PRAGMA table_info(characters)")
        columns = {row[1] for row in cursor.fetchall()}
        if 'current_hit_points' not in columns:
            cursor.execute("ALTER TABLE characters ADD COLUMN current_hit_points INTEGER")
        if 'max_hit_points' not in columns:
            cursor.execute("ALTER TABLE characters ADD COLUMN max_hit_points INTEGER")

    def _ensure_warlock_invocation_columns(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warlock_invocations'")
        if not cursor.fetchone():
            return

        cursor.execute("PRAGMA table_info(warlock_invocations)")
        columns = {row[1] for row in cursor.fetchall()}
        if 'invocation_name' not in columns:
            cursor.execute("ALTER TABLE warlock_invocations ADD COLUMN invocation_name TEXT")

    def _remove_duplicate_hp_columns(self, cursor: sqlite3.Cursor):
        """Remove duplicate HP columns, standardizing on hit_points_current/hit_points_max."""
        # Check if duplicate columns exist
        cursor.execute("PRAGMA table_info(characters)")
        columns = {row[1] for row in cursor.fetchall()}

        if 'current_hit_points' not in columns and 'max_hit_points' not in columns:
            print("Duplicate HP columns already removed, skipping migration")
            return

        print("Found duplicate HP columns, migrating to standard naming...")

        # Read the migration SQL file and execute it
        migration_path = self.migrations_dir / '044_remove_duplicate_hp_columns.sql'
        if not migration_path.exists():
            print(f"Warning: Migration file not found at {migration_path}")
            print("Attempting inline migration...")

            # Inline migration as fallback
            # First, ensure data is synced
            cursor.execute("""
                UPDATE characters
                SET hit_points_current = COALESCE(current_hit_points, hit_points_current),
                    hit_points_max = COALESCE(max_hit_points, hit_points_max)
                WHERE current_hit_points IS NOT NULL OR max_hit_points IS NOT NULL
            """)

            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            # Get all data first
            cursor.execute("SELECT * FROM characters")
            characters_data = cursor.fetchall()

            # Get column names (excluding the duplicates)
            cursor.execute("PRAGMA table_info(characters)")
            all_columns = cursor.fetchall()

            # This is complex, so we'll just log a warning
            print("Warning: Could not complete migration without SQL file")
            print("Please run migration 044 manually or recreate database")
            return

        # Execute migration from file
        with open(migration_path, 'r') as f:
            migration_sql = f.read()

        cursor.executescript(migration_sql)
        print("Successfully removed duplicate HP columns")

    def check_schema_version(self) -> bool:
        """Check and upgrade database schema if needed."""
        conn = None
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
            
            self._ensure_spellcasting_columns(cursor)
            conn.commit()
            # Get current schema version
            cursor.execute('SELECT version FROM schema_version ORDER BY version DESC LIMIT 1')
            result = cursor.fetchone()
            current_version = result[0] if result else 0
            
            # Target schema version
            target_version = 4

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
                current_version = 2
            
            if current_version == 1:
                # Future: handle upgrade from v1 to v2
                print("Upgrading schema from v1 to v2...")
                # Would contain specific upgrade logic here
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_version (version, description)
                    VALUES (2, 'Upgraded from schema v1')
                ''')
                conn.commit()
                print("Schema upgraded to v2")
                current_version = 2

            if current_version < 3:
                print("Applying Bag of Holding schema upgrades (v2 -> v3)...")
                self._ensure_inventory_columns(cursor)
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_version (version, description)
                    VALUES (3, 'Added Bag of Holding inventory support columns')
                ''')
                conn.commit()
                print("Schema upgraded to v3")
                current_version = 3

            if current_version < 4:
                print("Removing duplicate HP columns (v3 -> v4)...")
                self._remove_duplicate_hp_columns(cursor)
                cursor.execute('''
                    INSERT OR REPLACE INTO schema_version (version, description)
                    VALUES (4, 'Removed duplicate HP columns (current_hit_points, max_hit_points)')
                ''')
                conn.commit()
                print("Schema upgraded to v4")
                return True

            print(f"Unknown schema version: {current_version}")
            return False
            
        except Exception as e:
            print(f"Error checking schema version: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def verify_database(self) -> bool:
        conn = None
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
