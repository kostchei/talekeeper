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

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';
import { gameAPI, characterAPI } from '../services/api';

const MainMenu = () => {
  const navigate = useNavigate();
  const { setCurrentScreen, setCharacter, setGameState, setLoading } = useGameStore();
  const [characters, setCharacters] = useState([]);
  const [showLoadMenu, setShowLoadMenu] = useState(false);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      const allCharacters = await characterAPI.list();
      setCharacters(allCharacters);
    } catch (error) {
      console.error('Failed to load characters:', error);
    }
  };

  const handleNewGame = () => {
    setCurrentScreen('character-creator');
    navigate('/create-character');
  };

  const handleLoadGame = () => {
    setShowLoadMenu(true);
  };

  const handleLoadCharacter = async (character) => {
    try {
      setLoading(true);
      
      // Load character and game state
      const fullCharacter = await characterAPI.get(character.id);
      const gameState = await gameAPI.getGameState(character.id);
      
      setCharacter(fullCharacter);
      setGameState(gameState);
      navigate('/game');
    } catch (error) {
      console.error('Failed to load character:', error);
      alert('Failed to load character. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (showLoadMenu) {
    return (
      <div className="main-menu">
        <div className="menu-container">
          <h1 className="game-title">Load Character</h1>
          
          <div className="character-list">
            {characters.length === 0 ? (
              <div className="no-characters">
                <p>No characters found. Create a new character to get started!</p>
              </div>
            ) : (
              characters.map((character) => (
                <div 
                  key={character.id}
                  className="character-card"
                  onClick={() => handleLoadCharacter(character)}
                >
                  <div className="character-info">
                    <div className="character-name">{character.name}</div>
                    <div className="character-details">
                      Level {character.level} {character.race_name} {character.class_name}
                    </div>
                    <div className="character-stats">
                      HP: {character.current_hit_points}/{character.max_hit_points} • 
                      Gold: {character.gold}
                    </div>
                    <div className="character-created">
                      Created: {new Date(character.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <button className="menu-btn secondary" onClick={() => setShowLoadMenu(false)}>
            Back to Main Menu
          </button>
        </div>
      </div>
    );
  }

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