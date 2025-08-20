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
      {/* Navigation Header */}
      <div className="screen-header">
        <button 
          className="back-btn"
          onClick={() => navigate('/')}
          title="Return to Main Menu"
        >
          ← Main Menu
        </button>
        
        <h1>Rest and Recovery</h1>
        
        {character && (
          <button 
            className="character-btn"
            onClick={() => navigate('/character')}
            title="View Character Sheet"
          >
            📋 {character.name}
          </button>
        )}
      </div>
      
      {character && (
        <div className="character-status">
          <p>Current HP: {character.hit_points_current || character.current_hit_points || 0}/{character.hit_points_max || character.max_hit_points || 0}</p>
          <p>Level: {character.level} | Gold: {character.gold || 0}</p>
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
      
      <div className="rest-actions">
        <button className="secondary-btn" onClick={() => navigate('/game')}>
          ← Return to Game
        </button>
      </div>
      
      <div className="placeholder">
        <p>Advanced rest mechanics coming soon: Hit dice, spell slots, abilities</p>
      </div>
    </div>
  );
};

export default RestScreen;