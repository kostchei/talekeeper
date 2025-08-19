/**
 * File: frontend/src/components/RestScreen.js
 * Path: /frontend/src/components/RestScreen.js
 * 
 * Rest Screen Component
 * 
 * Pseudo Code:
 * 1. Provide options for short rest and long rest
 * 2. Handle HP recovery and resource restoration
 * 3. Show rest benefits and recovery amounts
 * 4. Manage hit dice spending and spell slot recovery
 * 5. Return to previous screen after rest completion
 * 
 * AI Agents: D&D rest mechanics with HP/resource recovery.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';

const RestScreen = () => {
  const navigate = useNavigate();
  const { character, setCharacter } = useGameStore();

  const handleShortRest = () => {
    // TODO: Implement short rest mechanics
    console.log('Short rest taken');
    navigate('/game');
  };

  const handleLongRest = () => {
    if (character) {
      // Simple long rest - restore full HP
      const restedCharacter = {
        ...character,
        hp: character.maxHp
      };
      setCharacter(restedCharacter);
    }
    console.log('Long rest taken');
    navigate('/game');
  };

  return (
    <div className="rest-screen">
      <h1>Rest and Recovery</h1>
      
      {character && (
        <div className="character-status">
          <p>Current HP: {character.hp}/{character.maxHp}</p>
        </div>
      )}
      
      <div className="rest-options">
        <div className="rest-option">
          <h3>Short Rest</h3>
          <p>Spend 1 hour to recover some HP using Hit Dice</p>
          <button className="rest-btn" onClick={handleShortRest}>
            Take Short Rest
          </button>
        </div>
        
        <div className="rest-option">
          <h3>Long Rest</h3>
          <p>Spend 8 hours to fully recover HP and restore all abilities</p>
          <button className="rest-btn" onClick={handleLongRest}>
            Take Long Rest
          </button>
        </div>
      </div>
      
      <button className="back-btn" onClick={() => navigate('/game')}>
        Cancel
      </button>
      
      <div className="placeholder">
        <p>Advanced rest mechanics coming soon: Hit dice, spell slots, abilities</p>
      </div>
    </div>
  );
};

export default RestScreen;