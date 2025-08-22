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
  const [saveSlots, setSaveSlots] = useState([]);
  const [showLoadMenu, setShowLoadMenu] = useState(false);

  useEffect(() => {
    loadSaveSlots();
  }, []);

  const loadSaveSlots = async () => {
    try {
      const slots = await gameAPI.getSaveSlots();
      setSaveSlots(slots);
    } catch (error) {
      console.error('Failed to load save slots:', error);
    }
  };

  const handleNewGame = () => {
    setCurrentScreen('character-creator');
    navigate('/create-character');
  };

  const handleLoadGame = () => {
    setShowLoadMenu(true);
  };

  const handleLoadSlot = async (slot) => {
    if (slot.is_empty) return;
    
    try {
      setLoading(true);
      
      // Load character directly using the character_id from the slot
      const character = await characterAPI.get(slot.character_id);
      const gameState = await gameAPI.getGameState(slot.character_id);
      
      setCharacter(character);
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
          <h1 className="game-title">Load Game</h1>
          
          <div className="save-slots">
            {saveSlots.map((slot) => (
              <div 
                key={slot.slot_number}
                className={`save-slot ${slot.is_empty ? 'empty' : 'occupied'}`}
                onClick={() => handleLoadSlot(slot)}
              >
                <div className="slot-number">Slot {slot.slot_number}</div>
                {!slot.is_empty ? (
                  <div className="slot-info">
                    <div className="character-name">{slot.character_name}</div>
                    <div className="character-details">
                      Level {slot.character_level} • {slot.location_description}
                    </div>
                    <div className="character-gold">{slot.gold} gold</div>
                    <div className="last-played">{new Date(slot.last_played).toLocaleDateString()}</div>
                  </div>
                ) : (
                  <div className="slot-empty">Empty Slot</div>
                )}
              </div>
            ))}
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