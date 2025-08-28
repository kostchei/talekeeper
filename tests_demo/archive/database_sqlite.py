"""
File: core/database.py
Path: /core/database.py

Database setup and management for TaleKeeper Desktop.
Uses SQLite for local storage with SQLAlchemy ORM.

Pseudo Code:
1. Configure SQLAlchemy engine for SQLite database
2. Create database session factory
3. Initialize all database tables on first run
4. Load initial game data from JSON files into database
5. Provide database session management utilities

AI Agents: Database configuration and table initialization. Add new tables here.
"""

import os
import json
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from loguru import logger
from typing import Optional

# Database file path
DB_FILE = "talekeeper.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False}  # Allow SQLite in multithreaded environment
)

# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


def init_database():
    """Initialize database tables and load initial data."""
    try:
        logger.info("Creating database tables...")
        
        # Import all models to register them with Base
        from models.character import Character, Race, Class, Subclass, Background
        from models.monsters import Monster
        from models.combat import CombatSession
        from models.items import Item, Equipment
        from models.game import SaveSlot, GameState
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Load initial game data
        load_initial_data()
        
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise


def load_initial_data():
    """Load races, classes, monsters, and equipment from JSON files."""
    try:
        db = get_db()
        
        # Check if data already loaded
        from models.character import Race
        if db.query(Race).first():
            logger.info("Initial data already loaded, skipping...")
            db.close()
            return
        
        logger.info("Loading initial game data...")
        
        # Load data files
        data_dir = Path("data")
        
        # Load races
        _load_races(db, data_dir / "races.json")
        
        # Load classes  
        _load_classes(db, data_dir / "classes.json")
        
        # Load backgrounds
        _load_backgrounds(db, data_dir / "backgrounds.json")
        
        # Load monsters
        _load_monsters(db, data_dir / "monsters.json")
        
        # Load equipment
        _load_equipment(db, data_dir / "equipment.json")
        
        db.commit()
        logger.info("Initial data loaded successfully")
        
    except Exception as e:
        logger.exception(f"Failed to load initial data: {e}")
        if 'db' in locals():
            db.rollback()
        raise
    finally:
        if 'db' in locals():
            db.close()


def _load_races(db: Session, file_path: Path):
    """Load race data from JSON."""
    if not file_path.exists():
        logger.warning(f"Race data file not found: {file_path}")
        return
    
    from models.character import Race
    
    with open(file_path, 'r') as f:
        races_data = json.load(f)
    
    for race_data in races_data:
        race = Race(**race_data)
        db.add(race)
    
    logger.info(f"Loaded {len(races_data)} races")


def _load_classes(db: Session, file_path: Path):
    """Load class data from JSON."""
    if not file_path.exists():
        logger.warning(f"Class data file not found: {file_path}")
        return
    
    from models.character import Class, Subclass
    
    with open(file_path, 'r') as f:
        classes_data = json.load(f)
    
    for class_data in classes_data:
        # Extract subclasses if present
        subclasses_data = class_data.pop('subclasses', [])
        
        # Create class
        char_class = Class(**class_data)
        db.add(char_class)
        db.flush()  # Get the class ID
        
        # Create subclasses
        for subclass_data in subclasses_data:
            subclass_data['class_id'] = char_class.id
            subclass = Subclass(**subclass_data)
            db.add(subclass)
    
    logger.info(f"Loaded {len(classes_data)} classes with subclasses")


def _load_backgrounds(db: Session, file_path: Path):
    """Load background data from JSON.""" 
    if not file_path.exists():
        logger.warning(f"Background data file not found: {file_path}")
        return
    
    from models.character import Background
    
    with open(file_path, 'r') as f:
        backgrounds_data = json.load(f)
    
    for background_data in backgrounds_data:
        background = Background(**background_data)
        db.add(background)
    
    logger.info(f"Loaded {len(backgrounds_data)} backgrounds")


def _load_monsters(db: Session, file_path: Path):
    """Load monster data from JSON."""
    if not file_path.exists():
        logger.warning(f"Monster data file not found: {file_path}")
        return
    
    from models.monsters import Monster
    
    with open(file_path, 'r') as f:
        monsters_data = json.load(f)
    
    for monster_data in monsters_data:
        monster = Monster(**monster_data)
        db.add(monster)
    
    logger.info(f"Loaded {len(monsters_data)} monsters")


def _load_equipment(db: Session, file_path: Path):
    """Load equipment data from JSON."""
    if not file_path.exists():
        logger.warning(f"Equipment data file not found: {file_path}")
        return
    
    from models.items import Item
    
    with open(file_path, 'r') as f:
        equipment_data = json.load(f)
    
    for item_data in equipment_data:
        item = Item(**item_data)
        db.add(item)
    
    logger.info(f"Loaded {len(equipment_data)} equipment items")


# Context manager for database sessions
class DatabaseSession:
    """Context manager for database sessions."""
    
    def __init__(self):
        self.db: Optional[Session] = None
    
    def __enter__(self) -> Session:
        self.db = get_db()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            if exc_type:
                self.db.rollback()
            else:
                self.db.commit()
            self.db.close()