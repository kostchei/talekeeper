"""
File: backend/main.py
Path: /backend/main.py

D&D 2024 Game Backend - Main Application

Pseudo Code:
1. Configure FastAPI app with CORS and lifecycle management
2. Include all feature routers (character, combat, game, items)
3. Set up error handlers and health check endpoints
4. Initialize database on startup
5. Run with Uvicorn server for development

AI Agents: This is the entry point. Add new routers in the routers/ directory and import them here.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime
from loguru import logger

# Import database and models
from database import engine, Base, get_db, init_db
from routers import character, combat, game, items

# Configure logging
logger.add("logs/dnd_game.log", rotation="10 MB", level="INFO")

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application lifecycle.
    AI Agents: Add any startup tasks here (cache warming, connection pools, etc.)
    """
    # Startup
    logger.info("Starting D&D Game Backend...")
    # Create database tables if they don't exist
    init_db()
    logger.info("Database tables verified/created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down D&D Game Backend...")

# Create FastAPI app
app = FastAPI(
    title="D&D 2024 Game API",
    description="""
    Backend API for D&D 2024 web game.
    
    ## Features
    - Character creation and management
    - Combat engine with D&D 2024 rules
    - Save/load system with multiple slots
    - Rest and recovery mechanics
    - Monster encounters with AI
    
    ## For AI Agents
    - All endpoints return JSON
    - Use /docs for interactive testing
    - Database models are in models/
    - Game logic is in services/
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://frontend:3000",   # Docker container name
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# AI Agents: Add new feature routers here
app.include_router(character.router, prefix="/api/character", tags=["Character"])
app.include_router(combat.router, prefix="/api/combat", tags=["Combat"])
app.include_router(game.router, prefix="/api/game", tags=["Game"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])

# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "D&D 2024 Game API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check for Docker and monitoring.
    AI Agents: Extend this to check database connection, cache status, etc.
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handlers
@app.exception_handler(404)
async def not_found(request, exc):
    """Custom 404 handler"""
    return {"error": "Endpoint not found", "path": request.url.path}

@app.exception_handler(500)
async def server_error(request, exc):
    """Custom 500 handler"""
    logger.error(f"Server error on {request.url.path}: {str(exc)}")
    return {"error": "Internal server error", "message": "Check server logs for details"}

if __name__ == "__main__":
    # For local development without Docker
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)