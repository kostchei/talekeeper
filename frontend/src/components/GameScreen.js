/**
 * File: frontend/src/components/GameScreen.js
 * Path: /frontend/src/components/GameScreen.js
 * 
 * Main Game Screen Component
 * 
 * Pseudo Code:
 * 1. Display main game interface with character status
 * 2. Handle dungeon exploration and encounter generation
 * 3. Provide access to combat, rest, and town screens
 * 4. Show game world map and location information
 * 5. Manage random encounters and story progression
 * 
 * AI Agents: Central hub for game world interaction and navigation.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';

const GameScreen = () => {
  const navigate = useNavigate();
  const { character } = useGameStore();

  const handleEnterCombat = () => {
    navigate('/combat');
  };

  const handleRest = () => {
    navigate('/rest');
  };

  const handleTown = () => {
    navigate('/town');
  };

  return (
    <div className="game-screen">
      <div className="game-header">
        <h1>Adventure Continues</h1>
        {character && (
          <div className="character-status">
            <h2>{character.name}</h2>
            <p>HP: {character.hp}/{character.maxHp}</p>
          </div>
        )}
      </div>
      
      <div className="game-content">
        <div className="location-info">
          <h3>Current Location: Starter Town</h3>
          <p>You stand at the entrance to adventure. What will you do?</p>
        </div>
        
        <div className="action-buttons">
          <button className="action-btn" onClick={handleEnterCombat}>
            Enter Combat (Demo)
          </button>
          <button className="action-btn" onClick={handleRest}>
            Rest
          </button>
          <button className="action-btn" onClick={handleTown}>
            Visit Town
          </button>
          <button className="action-btn" onClick={() => navigate('/character')}>
            Character Sheet
          </button>
        </div>
      </div>
      
      <div className="placeholder">
        <p>Game World - Coming Soon</p>
        <p>This will include dungeon exploration, random encounters, and story progression.</p>
      </div>
    </div>
  );
};

export default GameScreen;