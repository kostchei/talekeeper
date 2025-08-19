"""
File: backend/database.py
Path: /backend/database.py

Database configuration and session management.

Pseudo Code:
1. Configure SQLAlchemy engine for PostgreSQL
2. Create session factory with proper error handling
3. Initialize database tables from all imported models
4. Provide dependency injection for database sessions
5. Include game-specific query utilities (XP calculations, modifiers)

AI Agents: This handles all database connections. Uses PostgreSQL for all environments.
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dnd_admin:password@localhost:5432/dnd_game"
)

# Configure SQLAlchemy engine for PostgreSQL
# AI Agents: Adjust pool settings for production load
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Number of persistent connections
    max_overflow=40,  # Maximum overflow connections
    pool_pre_ping=True,  # Test connections before using
    echo=False,  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for database introspection
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Usage in FastAPI: db: Session = Depends(get_db)
    
    AI Agents: This ensures proper session cleanup. Always use this for DB access.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database with tables.
    Called on application startup.
    
    AI Agents: Add any seed data or initial setup here.
    """
    try:
        # Import all models to ensure they're registered with Base
        from models import (
            Character, Item, CharacterInventory, ShopInventory, LootTable,
            Monster, CombatEncounter, CombatAction, CombatLog,
            GameState, SaveSlot, Race, Class, Subclass, Background
        )
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def test_connection():
    """
    Test database connection.
    Useful for health checks and debugging.
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Database utilities for game-specific queries
class GameQueries:
    """
    Centralized location for complex game queries.
    AI Agents: Add new query methods here rather than in routers.
    """
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calculate character level from XP using D&D 2024 progression"""
        # D&D 2024 XP thresholds
        thresholds = [
            0,      # Level 1
            300,    # Level 2
            900,    # Level 3
            2700,   # Level 4
            6500,   # Level 5
            14000,  # Level 6
            23000,  # Level 7
            34000,  # Level 8
            48000,  # Level 9
            64000,  # Level 10
            85000,  # Level 11
            100000, # Level 12
            120000, # Level 13
            140000, # Level 14
            165000, # Level 15
            195000, # Level 16
            225000, # Level 17
            265000, # Level 18
            305000, # Level 19
            355000, # Level 20
        ]
        
        for level, threshold in enumerate(thresholds):
            if xp < threshold:
                return level
        return 20  # Max level
    
    @staticmethod
    def get_proficiency_bonus(level: int) -> int:
        """Calculate proficiency bonus from level"""
        return (level - 1) // 4 + 2
    
    @staticmethod
    def ability_modifier(score: int) -> int:
        """Calculate ability modifier from ability score"""
        return (score - 10) // 2

# Export commonly used items
__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'init_db',
    'test_connection',
    'GameQueries'
]