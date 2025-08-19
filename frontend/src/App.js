/**
 * File: frontend/src/App.js
 * Path: /frontend/src/App.js
 * 
 * Main D&D Game Application
 * 
 * Pseudo Code:
 * 1. Set up React Router with all game screens (Main Menu, Character Creator, Combat, etc.)
 * 2. Manage global game state with useGameStore hook
 * 3. Handle navigation between different game phases
 * 4. Configure toast notifications for user feedback
 * 5. Provide authentication and character loading logic
 * 
 * AI Agents: This is the root component. Add new screens to the router.
 * Game flow: Main Menu -> Character Creation/Load -> Game -> Combat/Rest/Town
 */

import React, { useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import './styles/main.css';

// Import components
import MainMenu from './components/MainMenu';
import CharacterCreator from './components/CharacterCreator';
import CharacterSheet from './components/CharacterSheet';
import CombatScreen from './components/CombatScreen';
import RestScreen from './components/RestScreen';
import TownScreen from './components/TownScreen';
import GameScreen from './components/GameScreen';
import LootScreen from './components/LootScreen';

// Import services
import { gameAPI } from './services/api';
import { useGameStore } from './services/gameStore';

function App() {
  const { 
    character, 
    setCharacter, 
    gameState, 
    setGameState,
    isLoading,
    setLoading 
  } = useGameStore();

  const checkExistingSaves = useCallback(async () => {
    try {
      setLoading(true);
      const saves = await gameAPI.getSaveSlots();
      console.log('Available saves:', saves);
      
      // Auto-load the most recent character if available
      if (saves && saves.length > 0) {
        const mostRecent = saves.reduce((latest, save) => 
          new Date(save.last_played) > new Date(latest.last_played) ? save : latest
        );
        
        // Load the character and game state
        const loadedCharacter = await gameAPI.loadCharacter(mostRecent.character_id);
        const loadedGameState = await gameAPI.getGameState(mostRecent.character_id);
        
        setCharacter(loadedCharacter);
        setGameState(loadedGameState);
      }
    } catch (error) {
      console.error('Error checking saves:', error);
    } finally {
      setLoading(false);
    }
  }, [setLoading, setCharacter, setGameState]);

  useEffect(() => {
    // Check for existing save on mount
    checkExistingSaves();
  }, [checkExistingSaves]);

  // Loading screen
  if (isLoading) {
    return (
      <div className="app loading-screen">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading D&D Game...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        {/* Toast notifications for game events */}
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#2a2a2a',
              color: '#fff',
              border: '1px solid #444',
            },
            success: {
              iconTheme: {
                primary: '#4ade80',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />

        {/* Main routing */}
        <Routes>
          {/* Main Menu - Entry point */}
          <Route path="/" element={<MainMenu />} />
          
          {/* Character Creation */}
          <Route path="/create-character" element={<CharacterCreator />} />
          
          {/* Main Game Screen - Hub for all game activities */}
          <Route path="/game" element={
            character ? <GameScreen /> : <Navigate to="/" />
          } />
          
          {/* Combat Screen */}
          <Route path="/combat" element={
            character && gameState?.inCombat ? 
              <CombatScreen /> : 
              <Navigate to="/game" />
          } />
          
          {/* Rest Screen */}
          <Route path="/rest" element={
            character ? <RestScreen /> : <Navigate to="/" />
          } />
          
          {/* Town Screen - Shop, Train, Long Rest */}
          <Route path="/town" element={
            character ? <TownScreen /> : <Navigate to="/" />
          } />
          
          {/* Character Sheet - View/Edit character */}
          <Route path="/character" element={
            character ? <CharacterSheet /> : <Navigate to="/" />
          } />
          
          {/* Loot Screen - Post-combat loot pickup */}
          <Route path="/loot" element={
            character ? <LootScreen /> : <Navigate to="/" />
          } />
          
          {/* Catch all - redirect to main menu */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>

        {/* Global UI Elements */}
        {character && (
          <div className="global-hud">
            {/* Quick stats display */}
            <div className="quick-stats">
              <span className="stat-hp">
                HP: {character.currentHp}/{character.maxHp}
              </span>
              <span className="stat-level">
                Level {character.level}
              </span>
              <span className="stat-xp">
                XP: {character.experience}
              </span>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;