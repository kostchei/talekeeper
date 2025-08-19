# D&D 2024 Web Game - MVP

A web-based implementation of D&D 2024 rules with simplified tactical combat, character creation, and dungeon crawling.

## 🎮 Features (MVP)

- **Character Creation**: Fighter & Rogue classes, Human & Dwarf races, 2 backgrounds
- **Combat System**: Round-by-round D&D combat with action/bonus action/reaction cards
- **Simplified Positioning**: Melee vs Ranged zones
- **Rest System**: Short and long rests
- **Save System**: Multiple character slots
- **Extensible Architecture**: Built for AI agents to expand

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- Ports 3000, 8000, 5432 available

### Setup Instructions

1. **Clone and Setup Project Structure**
```bash
# Create project directory
mkdir dnd-game && cd dnd-game

# Create the directory structure
mkdir -p backend/{models,routers,services,data}
mkdir -p frontend/{public,src/{components,services,styles}}
mkdir -p database

# Create .env file
cat > .env << 'EOF'
POSTGRES_DB=dnd_game
POSTGRES_USER=dnd_admin
POSTGRES_PASSWORD=secure_password_change_me
DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@db:5432/dnd_game
REACT_APP_API_URL=http://localhost:8000
EOF
```

2. **Copy All Files**
   - Copy all the provided files to their respective directories
   - Ensure docker-compose.yml is in the root directory

3. **Start the Application**
```bash
# Build and start all services
docker-compose up --build

# In another terminal, check the logs
docker-compose logs -f

# The app will be available at:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database Admin: http://localhost:8080
```

4. **First Time Setup**
   - Navigate to http://localhost:3000
   - Click "New Game"
   - Create your first character
   - Start adventuring!

## 📁 Project Structure

```
dnd-game/
├── docker-compose.yml       # Orchestrates all services
├── .env                     # Environment variables
├── backend/
│   ├── main.py             # FastAPI application
│   ├── database.py         # Database configuration
│   ├── models/             # SQLAlchemy models
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   │   ├── combat_engine.py    # D&D combat rules
│   │   ├── dice.py             # Dice rolling system
│   │   └── character_service.py # Character management
│   └── data/               # JSON game data
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React app
│   │   ├── components/     # React components
│   │   │   ├── CombatScreen.js    # Combat UI
│   │   │   ├── ActionCards.js     # Action card system
│   │   │   └── CharacterCreator.js # Character creation
│   │   └── services/       # API communication
│   └── package.json
└── database/
    ├── init.sql            # Database schema
    └── seed_data.sql       # Initial game data
```

## 🎯 How to Play

### Character Creation
1. Choose Race (Human/Dwarf)
2. Choose Class (Fighter/Rogue)
3. Choose Background (Farmer/Soldier)
4. Select Subclass at level 3
5. Pick starting equipment

### Combat
- **Actions** (Red cards): Main attacks and abilities
- **Bonus Actions** (Blue cards): Quick actions like off-hand attacks
- **Reactions** (Yellow cards): Responses to triggers
- **Movement** (Green cards): Change position between melee/ranged

Cards flip when used to show they're expended for the turn.

### Game Loop
1. Enter dungeon
2. Face random encounter
3. Win combat → gain XP and loot
4. Short rest to heal
5. Continue or return to town
6. Long rest in town to fully recover
7. Shop for equipment
8. Level up when you have enough XP

## 🔧 Development

### Adding New Features

#### Add a New Monster
1. Add monster data to `database/seed_data.sql`
2. Define AI behavior in `backend/services/combat_engine.py`
3. Create monster card variant in frontend

#### Add a New Class
1. Add class data to database
2. Implement class features in `character_service.py`
3. Add UI elements for class abilities

#### Add a New System
1. Create new database tables in `init.sql`
2. Add backend service in `services/`
3. Create API router in `routers/`
4. Build React components
5. Update main.py to include new router

### Testing
```bash
# Test backend
docker-compose exec backend pytest

# Test frontend
docker-compose exec frontend npm test

# Check database
docker-compose exec db psql -U dnd_admin -d dnd_game
```

### Common Commands
```bash
# Restart a service
docker-compose restart backend

# View logs for specific service
docker-compose logs -f backend

# Reset database
docker-compose down -v
docker-compose up --build

# Enter container shell
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port
lsof -i :3000  # or :8000, :5432
kill -9 <PID>
```

### Database Connection Issues
- Check .env file has correct credentials
- Ensure database container is healthy: `docker-compose ps`
- Check logs: `docker-compose logs db`

### Frontend Can't Connect to Backend
- Verify REACT_APP_API_URL in .env
- Check CORS settings in backend/main.py
- Ensure backend is running: http://localhost:8000/health

## 📚 Expansion Ideas

### Near Term (Level 4-10)
- [ ] More races (Elf, Halfling, Dragonborn)
- [ ] More classes (Wizard, Cleric, Barbarian)
- [ ] Spell system
- [ ] Inventory weight management
- [ ] Skill checks outside combat
- [ ] Traps and puzzles

### Medium Term (Level 11-15)
- [ ] Party system (multiple characters)
- [ ] Companion NPCs
- [ ] Crafting system
- [ ] Quest chains
- [ ] Persistent dungeon maps
- [ ] PvP arena

### Long Term (Level 16-20)
- [ ] Multiplayer co-op
- [ ] Dungeon builder/editor
- [ ] Steam Workshop integration
- [ ] Mobile app
- [ ] Voice commands for actions

## 📄 License

This project is for educational purposes. D&D is a trademark of Wizards of the Coast.

## 🤝 Contributing

This project is designed to be extended by AI agents. When adding features:

1. Follow existing patterns in the codebase
2. Add comprehensive comments for AI understanding
3. Update database schema with migration scripts
4. Test with the existing Docker setup
5. Document new endpoints in API docstrings

## 🆘 Support

For issues:
1. Check the logs: `docker-compose logs`
2. Verify all files are in place
3. Ensure Docker has enough resources (Settings > Resources)
4. Reset with: `docker-compose down -v && docker-compose up --build`

---

**Built with ❤️ for D&D enthusiasts and AI developers**