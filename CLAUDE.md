# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TaleKeeper** is a D&D 2024 web-based tactical RPG with a FastAPI backend, React frontend, and PostgreSQL database. The project implements D&D 2024 combat mechanics, character creation, and dungeon exploration in a simplified tactical format.

## Version Control Standards

### File Management Policy
- **USE GIT VERSIONING**: Never create multiple physical files with version suffixes (e.g., `file_v2.js`, `backup_file.sql`, `old_component.tsx`)
- **EDIT IN PLACE**: Always modify existing files directly and commit changes to Git
- **SINGLE SOURCE OF TRUTH**: Each feature should have one authoritative file, managed through Git history
- **NO VERSION SUFFIXES**: Avoid file names like `seed_data_2024.sql`, `component_new.js`, `backup_*.anything`

### Correct Approach:
```bash
# ✅ CORRECT: Edit existing files
git add database/seed_data.sql
git commit -m "Update to D&D 2024 rules with weapon mastery"

# ❌ WRONG: Create versioned files  
# seed_data_2024.sql
# seed_data_old.sql
# seed_data_backup.sql
```

### Exception Cases:
- **Configuration variants**: `docker-compose.yml` vs `docker-compose.prod.yml` (different environments)
- **Template files**: `template.js` vs actual implementation files
- **Documentation**: Multiple `.md` files for different topics are acceptable

## Architecture

The system follows a three-tier architecture:

1. **Frontend** (`frontend/`): React application with component-based UI
2. **Backend** (`backend/`): FastAPI REST API with SQLAlchemy ORM
3. **Database**: PostgreSQL with initialization scripts

### Key Components

- **Models** (`backend/models/`): SQLAlchemy database models and Pydantic schemas
- **Services** (`backend/services/`): Business logic layer (combat engine, dice system, character management)
- **Routers** (`backend/routers/`): API endpoints organized by feature domain
- **Combat Engine** (`backend/services/combat_engine.py`): Core D&D 5e mechanics implementation
- **Dice System** (`backend/services/dice.py`): Comprehensive dice notation parsing and rolling

## Development Commands

### Initial Setup
```bash
# Quick start with Docker (recommended)
docker-compose up --build

# Local development mode (uses SQLite)
start-game.bat

# Backend only (API development)
cd backend && python main.py
```

### Database Management
```bash
# Reset database completely
docker-compose down -v
docker-compose up --build

# Access database directly
docker-compose exec db psql -U dnd_admin -d dnd_game

# View database logs
docker-compose logs -f db
```

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# Check health
curl http://localhost:8000/health
```

### Frontend Development
```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Testing & Diagnostics
```bash
# Full system diagnostics
start-game.bat # Choose option 4

# Check all services
docker-compose ps

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Core Architecture Patterns

### Database Layer
- **SQLAlchemy ORM** with declarative models
- **PostgreSQL** for production, **SQLite** for local development
- **Foreign key constraints** ensure referential integrity
- **JSON columns** for flexible character stats and equipment

### API Layer
- **FastAPI** with automatic OpenAPI documentation at `/docs`
- **Dependency Injection** using `Depends(get_db)` for database sessions
- **Router-based organization** by feature domain (character, combat, game, items)
- **Pydantic models** for request/response validation

### Business Logic
- **Service layer** separates business logic from API endpoints
- **Combat engine** implements D&D 5e rules deterministically
- **Dice system** supports complex notation parsing ("2d6+3", advantage/disadvantage)
- **Character progression** with XP thresholds and automatic level calculation

### Frontend Architecture
- **React** with functional components and hooks
- **Component-based design** with reusable UI elements
- **API service layer** (`frontend/src/services/api.js`) centralizes backend communication
- **Action card system** with visual feedback for combat actions

## Key Design Decisions

### Combat System
- **Simplified positioning**: Melee vs Ranged zones instead of grid-based movement
- **Action cards**: Visual representation of D&D action economy (Action/Bonus/Reaction)
- **Turn-based processing**: Full D&D initiative and turn order
- **AI monsters** with scriptable behavior patterns

### Character System
- **Race/Class/Background** selection following D&D 5e structure
- **Equipment system** with slot-based inventory
- **Rest mechanics** (short/long rest) for resource recovery
- **Experience tracking** with automatic level progression

### Data Management
- **Save system** with multiple character slots
- **Combat logging** for action history and debugging
- **Loot tables** for randomized treasure distribution

## External Dependencies

### Required Services
- **Docker & Docker Compose**: Container orchestration
- **PostgreSQL 15**: Primary database
- **Node.js**: Frontend build system
- **Python 3.11+**: Backend runtime

### Key Python Packages
- **FastAPI**: Web framework with automatic documentation
- **SQLAlchemy**: Database ORM and migrations
- **Pydantic**: Data validation and serialization
- **Loguru**: Advanced logging system
- **Uvicorn**: ASGI server for FastAPI

### Key Node.js Packages
- **React 18**: Frontend framework
- **Axios**: HTTP client for API communication
- **React Router**: Client-side routing
- **Framer Motion**: Animation library for UI effects

## Environment Configuration

### Development (.env)
```
DATABASE_URL=sqlite:///./talekeeper.db
REACT_APP_API_URL=http://localhost:8000
```

### Production (.env)
```
POSTGRES_DB=dnd_game
POSTGRES_USER=dnd_admin
POSTGRES_PASSWORD=secure_password_change_me
DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@db:5432/dnd_game
REACT_APP_API_URL=http://localhost:8000
```

## Important File Locations

### Entry Points
- **Backend**: `backend/main.py` - FastAPI application with all router imports
- **Frontend**: `frontend/src/App.js` - Main React component
- **Database**: `database/init.sql` - Schema initialization
- **Startup**: `start-game.bat` - Windows startup script with diagnostics

### Core Business Logic
- **Combat Engine**: `backend/services/combat_engine.py:CombatEngine` - D&D rules implementation
- **Dice System**: `backend/services/dice.py:DiceRoller` - Dice notation parsing and rolling
- **Character Service**: `backend/services/character_service.py` - Character lifecycle management
- **Database Queries**: `backend/database.py:GameQueries` - Centralized game-specific queries

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (when running)
- **Health Check**: http://localhost:8000/health
- **API Routes**: Organized in `backend/routers/` by feature domain

## Common Development Workflows

### Adding New D&D Features
1. **Database**: Add tables/columns in `database/init.sql` and seed data in `database/seed_data.sql`
2. **Models**: Create SQLAlchemy models in `backend/models/` and Pydantic schemas
3. **Services**: Implement business logic in appropriate service file
4. **Routes**: Add API endpoints in relevant router
5. **Frontend**: Create/update React components and API service calls

### Adding New Monsters
1. Add monster data to `database/seed_data.sql`
2. Define AI behavior in `backend/services/combat_engine.py`
3. Update frontend monster display components

### Adding New Character Options
1. Add race/class/background data to database seed files
2. Implement class features in `backend/services/character_service.py`
3. Update character creation UI components

## Random Bag System

The project is designed to use a "random bag" distribution system for encounters and other randomized content to ensure fair, varied gameplay without frustrating streaks.

### Random Bag Concept
- **Traditional Random**: Each roll is independent, can result in streaks (same monster 5 times in a row)
- **Random Bag**: Fill a "bag" with one of each item, draw randomly without replacement, refill when empty

### Benefits
- **No Streaks**: Prevents same monster/event appearing multiple times consecutively
- **Guaranteed Variety**: Ensures all content gets seen before repeats
- **Still Feels Random**: Players can't predict what's next, just know they won't get immediate repeats
- **Fair Distribution**: Each option appears exactly once per bag cycle

### Implementation Design
```python
# Per-character bag state stored in GameState model
encounter_bag_remaining = Column(JSON, default=dict)  # location_type -> [monster_ids]
encounter_bag_history = Column(JSON, default=dict)    # location_type -> [used_monster_ids]

# Usage pattern:
class RandomBagService:
    def draw_from_bag(self, character_id, bag_type, available_items):
        # 1. Get character's bag state for this type
        # 2. If bag empty, refill with all available_items
        # 3. Randomly select and remove one item from bag
        # 4. Return selected item, update database
```

### Planned Applications
- **Monster Encounters**: Ensure variety in combat encounters per location type
- **Treasure Generation**: Prevent same loot appearing consecutively  
- **Random Events**: Vary story events and exploration encounters
- **NPC Interactions**: Diversify social encounters and dialogue

### Database Schema
```sql
-- In game_states table:
encounter_bag_remaining JSONB DEFAULT '{}',  -- {"dungeon": [1,3,7], "wilderness": [2,4]}
encounter_bag_history JSONB DEFAULT '{}',    -- {"dungeon": [5,6,8], "wilderness": [1,9]}
```

### Future Implementation Notes
- Each character maintains separate bag state
- Bags are categorized by context (dungeon vs wilderness encounters)
- System automatically refills bags when depleted
- Can be applied to any randomized game system (encounters, loot, events)
- Maintains randomness while ensuring fair distribution

## File Header Standards

All code files in this project follow a standardized header format for consistency and documentation:

### Python Files
```python
"""
File: backend/path/to/file.py
Path: /backend/path/to/file.py

Brief description of the file's purpose.

Pseudo Code:
1. Step-by-step description of main functionality
2. Key operations or algorithms implemented
3. Important data flow or processing steps
4. Integration points with other components
5. Error handling or validation logic

AI Agents: Specific guidance for AI development.
"""
```

### JavaScript/React Files
```javascript
/**
 * File: frontend/src/path/to/file.js
 * Path: /frontend/src/path/to/file.js
 * 
 * Brief description of the component/module.
 * 
 * Pseudo Code:
 * 1. Component initialization and state management
 * 2. Event handling and user interactions
 * 3. API calls and data processing
 * 4. Rendering logic and UI updates
 * 5. Cleanup and lifecycle management
 * 
 * AI Agents: Component-specific development guidance.
 */
```

### Header Requirements
- **File/Path**: Always include the actual file path for easy navigation
- **Description**: Clear, concise explanation of the file's purpose
- **Pseudo Code**: 3-6 numbered steps describing main functionality
- **AI Agents**: Specific guidance for future AI development work

This standardization ensures:
- Quick understanding of file purpose and location
- Consistent documentation across the codebase
- Easy navigation for development tools
- Clear development guidance for AI agents

## Port Configuration
- **Frontend**: 3000 (React development server)
- **Backend**: 8000 (FastAPI/Uvicorn)
- **Database**: 5432 (PostgreSQL)
- **Admin Interface**: 8080 (Adminer database management)