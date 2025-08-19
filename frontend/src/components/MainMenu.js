/**
 * File: frontend/src/components/MainMenu.js
 * Path: /frontend/src/components/MainMenu.js
 * 
 * Main Menu Component - Game Entry Point
 * 
 * Pseudo Code:
 * 1. Display game title and main menu options
 * 2. Handle new game, load game, and settings navigation
 * 3. Show available save slots and character previews
 * 4. Provide access to game settings and documentation
 * 5. Navigate to character creation or game loading
 * 
 * AI Agents: This is the first screen players see. Add new menu options here.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';

const MainMenu = () => {
  const navigate = useNavigate();
  const { setCurrentScreen } = useGameStore();

  const handleNewGame = () => {
    setCurrentScreen('character-creator');
    navigate('/create-character');
  };

  const handleLoadGame = () => {
    // TODO: Implement load game functionality
    console.log('Load game not yet implemented');
  };

  return (
    <div className="main-menu">
      <div className="menu-container">
        <h1 className="game-title">TaleKeeper</h1>
        <h2 className="game-subtitle">D&D 2024 Adventure</h2>
        
        <div className="menu-buttons">
          <button className="menu-btn primary" onClick={handleNewGame}>
            New Game
          </button>
          <button className="menu-btn secondary" onClick={handleLoadGame}>
            Load Game
          </button>
          <button className="menu-btn secondary" onClick={() => console.log('Settings')}>
            Settings
          </button>
          <button className="menu-btn secondary" onClick={() => console.log('Help')}>
            Help
          </button>
        </div>
        
        <div className="version-info">
          <p>Version 1.0.0 - MVP</p>
        </div>
      </div>
    </div>
  );
};

export default MainMenu;