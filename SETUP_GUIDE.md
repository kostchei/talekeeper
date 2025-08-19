# TaleKeeper - D&D 2024 Game Setup Guide

## 🚀 Quick Start (Single Command)

**Just run the startup script:**
```bash
start-game.bat
```

The script will:
- Check system requirements 
- Install dependencies automatically
- Set up the database
- Start the game servers
- Open the game in your browser

## 📋 System Requirements

### Required
- **Windows 10/11** (batch script)
- **Python 3.11+** - [Download here](https://python.org)
- **Node.js 18+** - [Download here](https://nodejs.org)

### Optional (for full stack)
- **Docker Desktop** - [Download here](https://docker.com/products/docker-desktop)

## 🎮 Startup Options

The `start-game.bat` script offers 3 modes:

### 1. Docker Mode (Recommended for Production)
- ✅ Full PostgreSQL database
- ✅ All services containerized
- ✅ Production-like environment
- ✅ Database admin interface at localhost:8080

### 2. Local Development Mode (Fastest Setup)
- ✅ SQLite database (no Docker needed)
- ✅ Direct Python/Node execution
- ✅ Fastest startup time
- ✅ Automatic dependency installation

### 3. Backend Only Mode
- ✅ API server only for testing
- ✅ Access API docs at localhost:8000/docs
- ✅ Perfect for API development

## 🛠️ Manual Setup (If Needed)

### Option A: Local Development (SQLite)

1. **Install Dependencies:**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend  
   cd ..\frontend
   npm install
   ```

2. **Configure Environment:**
   ```bash
   # Create .env file with:
   DATABASE_URL=sqlite:///./talekeeper.db
   REACT_APP_API_URL=http://localhost:8000
   ```

3. **Start Services:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   venv\Scripts\activate
   python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

### Option B: Docker Setup

1. **Install Docker Desktop**
2. **Start Everything:**
   ```bash
   docker-compose up --build
   ```

## 🌐 Access Points

After startup, access the game at:

- **Game Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Database Admin** (Docker only): http://localhost:8080

## 🎯 Testing the Setup

### Automatic Tests
The startup script includes built-in diagnostics, or run comprehensive testing:
```bash
start-game.bat
# Select option 4: Run Full Diagnostics
```

This will check:
- ✅ Python/Node installation with version details
- ✅ Dependency installation and verification
- ✅ Database connection and API testing
- ✅ Docker configuration and build testing
- ✅ Port availability checking
- ✅ File system structure validation

### Manual Verification

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", "database": "healthy"}
   ```

2. **API Test:**
   ```bash
   curl http://localhost:8000/api/items/equipment
   # Should return: [] (empty array initially)
   ```

3. **Frontend Test:**
   - Navigate to http://localhost:3000
   - Should see TaleKeeper game interface

## 🐛 Troubleshooting

### Common Issues

**"Python is not installed"**
- Install Python 3.11+ from python.org
- Ensure "Add to PATH" is checked during installation

**"Node.js is not installed"**  
- Install Node.js 18+ from nodejs.org
- Restart command prompt after installation

**"Failed to install dependencies"**
- Check internet connection
- Try running as Administrator
- Clear npm cache: `npm cache clean --force`

**"Database setup failed"**
- Delete `backend/talekeeper.db` and restart
- Check write permissions in backend folder

**"Backend health check failed"**
- Wait 10-15 seconds for startup
- Check if port 8000 is available
- Look for error messages in backend window

**"Frontend won't start"**
- Delete `frontend/node_modules` and `package-lock.json`
- Run `npm install` again
- Check if port 3000 is available

**Docker Issues**
- Ensure Docker Desktop is running
- Run `fix-docker.bat` to clean up corrupted images
- Try: `docker-compose down -v && docker-compose up --build`
- Check Docker has enough resources (4GB+ RAM)

### Advanced Troubleshooting

**Reset Everything:**
```bash
# Stop all processes
# Delete these if they exist:
backend/talekeeper.db
backend/venv/
frontend/node_modules/
frontend/package-lock.json

# Run start-game.bat again
```

**Check Logs:**
```bash
# Backend logs
cd backend && python main.py

# Frontend logs  
cd frontend && npm start

# Docker logs
docker-compose logs -f
```

## 🎲 Game Features Ready to Test

### Character System
- Create Fighter or Rogue characters
- Human and Dwarf races
- Full D&D 2024 ability scores and modifiers

### Items & Equipment  
- Browse equipment catalog
- Equip weapons and armor
- Shop system with dynamic pricing
- Inventory management

### Combat System
- Turn-based D&D combat
- Initiative rolling
- Action/bonus action/reaction system
- Damage and healing

### Game Progression
- Save/load system
- Experience points and leveling
- Rest mechanics
- Random encounters

## 📁 Project Structure

```
TaleKeeper/
├── start-game.bat          # Single-command startup with diagnostics
├── fix-docker.bat          # Docker cleanup utility  
├── docker-compose.yml      # Docker configuration
├── .env                    # Environment variables
├── backend/               
│   ├── main.py            # FastAPI application
│   ├── database.py        # Database setup
│   ├── models/            # D&D data models
│   ├── routers/           # API endpoints
│   └── services/          # Business logic
├── frontend/
│   ├── src/
│   │   ├── App.js         # React application
│   │   ├── components/    # UI components
│   │   └── services/      # API client
│   └── package.json
└── database/
    ├── init.sql           # Database schema
    └── seed_data.sql      # Initial data
```

## 🚀 Development Tips

- Use **Local Development Mode** for fastest iteration
- Use **Docker Mode** for testing full stack
- Backend auto-reloads on code changes
- Frontend auto-reloads on code changes  
- Check API docs at localhost:8000/docs for endpoint testing

## 📞 Support

If you encounter issues:

1. Run `start-game.bat` → Option 4 (Full Diagnostics) to identify problems
2. Check this troubleshooting guide
3. Look for error messages in the console
4. Try the "Reset Everything" steps
5. Create an issue with full error logs

---

**Happy adventuring in TaleKeeper! 🐉⚔️**