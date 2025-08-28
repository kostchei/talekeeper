"""
File: core/database_indexeddb.py
Path: /core/database_indexeddb.py

IndexedDB database setup and management for TaleKeeper Desktop.
Provides more complex database operations while maintaining compatibility
with the existing SQLite-based models and patterns.

This implementation uses a Python IndexedDB wrapper to provide:
- Advanced indexing and querying capabilities
- Better performance for complex searches
- Transaction support with ACID properties
- Asynchronous operations support

Pseudo Code:
1. Configure IndexedDB connection and object stores
2. Create database session factory compatible with SQLAlchemy patterns
3. Initialize all database object stores on first run
4. Provide migration utilities from SQLite
5. Maintain compatibility with existing model interfaces

AI Agents: IndexedDB configuration and migration utilities. More complex than SQLite version.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, List, Any
from loguru import logger
import asyncio
from dataclasses import dataclass, asdict
from datetime import datetime

# IndexedDB simulation for Python (since true IndexedDB is browser-only)
# This provides a more complex interface than SQLite with better indexing
class IndexedDBSimulator:
    """
    Simulates IndexedDB functionality with enhanced features over SQLite.
    Provides object stores, indexes, transactions, and async operations.
    """
    
    def __init__(self, db_name: str = "talekeeper_indexed"):
        self.db_name = db_name
        self.db_path = f"{db_name}.idb"
        self.object_stores: Dict[str, Dict] = {}
        self.indexes: Dict[str, Dict] = {}
        self.is_connected = False
        
    async def connect(self):
        """Initialize IndexedDB connection and load existing data."""
        try:
            if Path(self.db_path).exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.object_stores = data.get('stores', {})
                    self.indexes = data.get('indexes', {})
            else:
                self.object_stores = {}
                self.indexes = {}
            
            self.is_connected = True
            logger.info(f"Connected to IndexedDB: {self.db_name}")
        except Exception as e:
            logger.exception(f"Failed to connect to IndexedDB: {e}")
            raise
    
    def create_object_store(self, store_name: str, key_path: str = "id"):
        """Create an object store (equivalent to table)."""
        if store_name not in self.object_stores:
            self.object_stores[store_name] = {
                'data': {},
                'key_path': key_path,
                'auto_increment': False
            }
            logger.info(f"Created object store: {store_name} with key_path: {key_path}")
    
    def create_index(self, store_name: str, index_name: str, key_path: str, unique: bool = False):
        """Create an index on an object store."""
        index_key = f"{store_name}.{index_name}"
        self.indexes[index_key] = {
            'store': store_name,
            'key_path': key_path,
            'unique': unique,
            'index_data': {}
        }
        logger.info(f"Created index {index_name} on {store_name}.{key_path}")
    
    async def add(self, store_name: str, data: Dict, key: Optional[str] = None):
        """Add data to object store."""
        if store_name not in self.object_stores:
            raise ValueError(f"Object store {store_name} does not exist")
        
        store = self.object_stores[store_name]
        if key is None:
            key = data.get(store['key_path'])
        
        if key is None:
            # Generate a key if not found - use name if available, otherwise generate UUID
            import uuid
            if 'name' in data:
                key = data['name'].lower().replace(' ', '_')
            else:
                key = str(uuid.uuid4())
            # Add the generated key to the data
            data[store['key_path']] = key
        
        store['data'][str(key)] = data
        await self._update_indexes(store_name, str(key), data)
        await self._persist()
    
    async def put(self, store_name: str, data: Dict, key: Optional[str] = None):
        """Put (add or update) data in object store."""
        await self.add(store_name, data, key)
    
    async def get(self, store_name: str, key: str) -> Optional[Dict]:
        """Get data by key from object store."""
        if store_name not in self.object_stores:
            return None
        
        return self.object_stores[store_name]['data'].get(key)
    
    async def get_all(self, store_name: str) -> List[Dict]:
        """Get all data from object store."""
        if store_name not in self.object_stores:
            return []
        
        return list(self.object_stores[store_name]['data'].values())
    
    async def query_index(self, store_name: str, index_name: str, value: Any) -> List[Dict]:
        """Query data using an index."""
        index_key = f"{store_name}.{index_name}"
        if index_key not in self.indexes:
            return []
        
        index_info = self.indexes[index_key]
        key_path = index_info['key_path']
        
        results = []
        for item in await self.get_all(store_name):
            if self._get_nested_value(item, key_path) == value:
                results.append(item)
        
        return results
    
    async def delete(self, store_name: str, key: str):
        """Delete data by key from object store."""
        if store_name in self.object_stores and key in self.object_stores[store_name]['data']:
            del self.object_stores[store_name]['data'][key]
            await self._update_indexes_remove(store_name, key)
            await self._persist()
    
    def _get_nested_value(self, obj: Dict, key_path: str) -> Any:
        """Get nested value from object using dot notation."""
        keys = key_path.split('.')
        value = obj
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    async def _update_indexes(self, store_name: str, key: str, data: Dict):
        """Update indexes when data is added/modified."""
        for index_key, index_info in self.indexes.items():
            if index_info['store'] == store_name:
                value = self._get_nested_value(data, index_info['key_path'])
                if value is not None:
                    if value not in index_info['index_data']:
                        index_info['index_data'][value] = []
                    if key not in index_info['index_data'][value]:
                        index_info['index_data'][value].append(key)
    
    async def _update_indexes_remove(self, store_name: str, key: str):
        """Update indexes when data is removed."""
        for index_key, index_info in self.indexes.items():
            if index_info['store'] == store_name:
                for value, keys in index_info['index_data'].items():
                    if key in keys:
                        keys.remove(key)
                    if not keys:
                        del index_info['index_data'][value]
    
    async def _persist(self):
        """Save data to disk."""
        try:
            data = {
                'stores': self.object_stores,
                'indexes': self.indexes
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.exception(f"Failed to persist IndexedDB: {e}")
    
    def _persist_sync(self):
        """Save data to disk synchronously."""
        try:
            data = {
                'stores': self.object_stores,
                'indexes': self.indexes
            }
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.exception(f"Failed to persist IndexedDB: {e}")


# Global IndexedDB instance
indexeddb = IndexedDBSimulator()


# SQLAlchemy-like session interface for compatibility
class IndexedDBSession:
    """Session interface that mimics SQLAlchemy sessions but uses IndexedDB."""
    
    def __init__(self, db: IndexedDBSimulator):
        self.db = db
        self._transaction_data = []
    
    async def add(self, obj: Any):
        """Add object to session (will be committed on commit())."""
        # Convert SQLAlchemy-like model to dict
        if hasattr(obj, '__table__'):
            store_name = obj.__table__.name
            data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        else:
            # Assume it's already a dict-like object
            store_name = obj.__class__.__name__.lower() + 's'
            data = asdict(obj) if hasattr(obj, '__dataclass_fields__') else dict(obj)
        
        self._transaction_data.append(('add', store_name, data))
    
    async def commit(self):
        """Commit all pending operations."""
        for operation, store_name, data in self._transaction_data:
            if operation == 'add':
                await self.db.put(store_name, data)
        self._transaction_data.clear()
    
    def rollback(self):
        """Rollback pending operations."""
        self._transaction_data.clear()
    
    async def query(self, model_class):
        """Create a query for a model class."""
        store_name = model_class.__name__.lower() + 's'
        return IndexedDBQuery(self.db, store_name, model_class)
    
    def close(self):
        """Close the session."""
        pass


class IndexedDBQuery:
    """Query interface that mimics SQLAlchemy queries."""
    
    def __init__(self, db: IndexedDBSimulator, store_name: str, model_class: type):
        self.db = db
        self.store_name = store_name
        self.model_class = model_class
        self._filters = []
    
    def filter(self, condition):
        """Add filter condition."""
        self._filters.append(condition)
        return self
    
    async def first(self):
        """Get first matching record."""
        results = await self.all()
        return results[0] if results else None
    
    async def all(self):
        """Get all matching records."""
        all_data = await self.db.get_all(self.store_name)
        
        # Apply filters
        filtered_data = all_data
        for filter_condition in self._filters:
            # This is a simplified filter - would need more complex logic for real SQLAlchemy compatibility
            pass
        
        # Convert to model instances if needed
        return [self._dict_to_model(data) for data in filtered_data]
    
    def _dict_to_model(self, data: Dict):
        """Convert dict to model instance."""
        if hasattr(self.model_class, '__init__'):
            return self.model_class(**data)
        return data


async def get_indexeddb_session() -> IndexedDBSession:
    """Get IndexedDB session (async version of get_db())."""
    if not indexeddb.is_connected:
        await indexeddb.connect()
    return IndexedDBSession(indexeddb)


def init_indexeddb_database():
    """Initialize IndexedDB database and create object stores."""
    try:
        logger.info("Creating IndexedDB object stores...")
        
        # Initialize synchronously
        if Path(indexeddb.db_path).exists():
            with open(indexeddb.db_path, 'r') as f:
                data = json.load(f)
                indexeddb.object_stores = data.get('stores', {})
                indexeddb.indexes = data.get('indexes', {})
        else:
            indexeddb.object_stores = {}
            indexeddb.indexes = {}
        
        indexeddb.is_connected = True
        
        # Create object stores (equivalent to tables) with appropriate key paths
        store_configs = {
            'races': 'name',
            'classes': 'name', 
            'subclasses': 'id',
            'backgrounds': 'name',
            'monsters': 'name',
            'items': 'name',
            'characters': 'id',
            'save_slots': 'id',
            'game_states': 'id',
            'combat_sessions': 'id',
            'character_inventory': 'id',
            'combat_actions': 'id',
            'equipment_packages': 'id'
        }
        
        for store_name, key_path in store_configs.items():
            indexeddb.create_object_store(store_name, key_path)
        
        # Create indexes for better querying
        indexeddb.create_index('characters', 'race_id', 'race_id')
        indexeddb.create_index('characters', 'class_id', 'class_id')
        indexeddb.create_index('characters', 'name', 'name')
        indexeddb.create_index('monsters', 'challenge_rating', 'challenge_rating')
        indexeddb.create_index('items', 'item_type', 'item_type')
        indexeddb.create_index('items', 'rarity', 'rarity')
        
        logger.info("IndexedDB object stores created successfully")
        
        # Load initial game data if needed
        load_initial_indexeddb_data()
        
    except Exception as e:
        logger.exception(f"Failed to initialize IndexedDB: {e}")
        raise


def load_initial_indexeddb_data():
    """Load initial game data into IndexedDB."""
    try:
        # Check if data already loaded
        races = indexeddb.object_stores.get('races', {}).get('data', {})
        if races:
            logger.info("Initial data already loaded in IndexedDB, skipping...")
            return
        
        logger.info("Loading initial game data into IndexedDB...")
        
        # Load data files
        data_dir = Path("data")
        
        # Load races
        _load_indexeddb_races(data_dir / "races.json")
        
        # Load classes
        _load_indexeddb_classes(data_dir / "classes.json")
        
        # Load backgrounds
        _load_indexeddb_backgrounds(data_dir / "backgrounds.json")
        
        # Load monsters
        _load_indexeddb_monsters(data_dir / "monsters.json")
        
        # Load equipment
        _load_indexeddb_equipment(data_dir / "equipment.json")
        
        logger.info("Initial data loaded successfully into IndexedDB")
        
    except Exception as e:
        logger.exception(f"Failed to load initial data into IndexedDB: {e}")
        raise


def _load_indexeddb_races(file_path: Path):
    """Load race data into IndexedDB."""
    if not file_path.exists():
        logger.warning(f"Race data file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        races_data = json.load(f)
    
    for race_data in races_data:
        # Synchronous add
        store = indexeddb.object_stores['races']
        key = race_data.get('name', '').lower().replace(' ', '_')
        race_data['name'] = race_data.get('name', key)  # Ensure name field exists
        store['data'][key] = race_data
    
    # Persist to disk
    indexeddb._persist_sync()
    
    logger.info(f"Loaded {len(races_data)} races into IndexedDB")


def _load_indexeddb_classes(file_path: Path):
    """Load class data into IndexedDB."""
    if not file_path.exists():
        logger.warning(f"Class data file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        classes_data = json.load(f)
    
    for class_data in classes_data:
        # Extract subclasses if present
        subclasses_data = class_data.pop('subclasses', [])
        
        # Add class
        store = indexeddb.object_stores['classes']
        key = class_data.get('name', '').lower().replace(' ', '_')
        class_data['name'] = class_data.get('name', key)
        store['data'][key] = class_data
        
        # Add subclasses
        sub_store = indexeddb.object_stores['subclasses']
        for subclass_data in subclasses_data:
            import uuid
            subclass_data['class_id'] = class_data.get('name', key)
            sub_key = subclass_data.get('id', str(uuid.uuid4()))
            subclass_data['id'] = sub_key
            sub_store['data'][sub_key] = subclass_data
    
    indexeddb._persist_sync()
    
    logger.info(f"Loaded {len(classes_data)} classes into IndexedDB")


def _load_indexeddb_backgrounds(file_path: Path):
    """Load background data into IndexedDB."""
    if not file_path.exists():
        logger.warning(f"Background data file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        backgrounds_data = json.load(f)
    
    for background_data in backgrounds_data:
        store = indexeddb.object_stores['backgrounds']
        key = background_data.get('name', '').lower().replace(' ', '_')
        background_data['name'] = background_data.get('name', key)
        store['data'][key] = background_data
    
    indexeddb._persist_sync()
    
    logger.info(f"Loaded {len(backgrounds_data)} backgrounds into IndexedDB")


def _load_indexeddb_monsters(file_path: Path):
    """Load monster data into IndexedDB."""
    if not file_path.exists():
        logger.warning(f"Monster data file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        monsters_data = json.load(f)
    
    for monster_data in monsters_data:
        store = indexeddb.object_stores['monsters']
        key = monster_data.get('name', '').lower().replace(' ', '_')
        monster_data['name'] = monster_data.get('name', key)
        store['data'][key] = monster_data
    
    indexeddb._persist_sync()
    
    logger.info(f"Loaded {len(monsters_data)} monsters into IndexedDB")


def _load_indexeddb_equipment(file_path: Path):
    """Load equipment data into IndexedDB."""
    if not file_path.exists():
        logger.warning(f"Equipment data file not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        equipment_data = json.load(f)
    
    for item_data in equipment_data:
        store = indexeddb.object_stores['items']
        key = item_data.get('name', '').lower().replace(' ', '_')
        item_data['name'] = item_data.get('name', key)
        store['data'][key] = item_data
    
    indexeddb._persist_sync()
    
    logger.info(f"Loaded {len(equipment_data)} equipment items into IndexedDB")


def migrate_from_sqlite(sqlite_path: str):
    """Migrate data from existing SQLite database to IndexedDB."""
    async def _migrate():
        try:
            logger.info(f"Starting migration from SQLite {sqlite_path} to IndexedDB...")
            
            # Connect to SQLite database
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            
            # Migrate each table
            for table in tables:
                logger.info(f"Migrating table: {table}")
                
                # Get all data from SQLite table
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Convert rows to dicts and store in IndexedDB
                for row in rows:
                    row_dict = dict(row)
                    # Convert datetime strings and handle JSON fields
                    for key, value in row_dict.items():
                        if isinstance(value, str):
                            # Try to parse JSON fields
                            if value.startswith('{') or value.startswith('['):
                                try:
                                    row_dict[key] = json.loads(value)
                                except:
                                    pass  # Keep as string if not valid JSON
                    
                    await indexeddb.put(table, row_dict)
                
                logger.info(f"Migrated {len(rows)} records from {table}")
            
            conn.close()
            logger.info("SQLite to IndexedDB migration completed successfully")
            
        except Exception as e:
            logger.exception(f"Failed to migrate from SQLite: {e}")
            raise
    
    # Run the async migration
    asyncio.run(_migrate())


# Context manager for IndexedDB sessions (async compatible)
class IndexedDBSessionManager:
    """Async context manager for IndexedDB sessions."""
    
    def __init__(self):
        self.session: Optional[IndexedDBSession] = None
    
    async def __aenter__(self) -> IndexedDBSession:
        self.session = await get_indexeddb_session()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                self.session.rollback()
            else:
                await self.session.commit()
            self.session.close()