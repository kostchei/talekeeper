/**
 * File: frontend/src/components/CharacterView.js
 * Path: /frontend/src/components/CharacterView.js
 * 
 * Character View Component - Read-Only Character Sheet
 * 
 * Pseudo Code:
 * 1. Display completed character's basic information (name, race, class, background)
 * 2. Show all ability scores in clean card format
 * 3. Display derived stats (HP, AC, initiative, proficiency bonus)
 * 4. Show equipment, skills, and features (when implemented)
 * 5. Provide navigation back to game or main menu
 * 
 * AI Agents: Pure view component for completed characters only.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';

const CharacterView = () => {
  const navigate = useNavigate();
  const { character } = useGameStore();

  const calculateModifier = (score) => Math.floor((score - 10) / 2);

  if (!character) {
    navigate('/');
    return null;
  }

  // Check if character has finalized stats
  const hasStats = character.strength > 0 && character.dexterity > 0 && 
                   character.constitution > 0 && character.intelligence > 0 && 
                   character.wisdom > 0 && character.charisma > 0;

  if (!hasStats) {
    // Redirect incomplete characters to the generation sheet
    navigate('/character');
    return null;
  }

  const finalStats = {
    str: character.strength,
    dex: character.dexterity,
    con: character.constitution,
    int: character.intelligence,
    wis: character.wisdom,
    cha: character.charisma
  };

  return (
    <div className="character-view">
      {/* Navigation Header */}
      <div className="screen-header">
        <button 
          className="back-btn"
          onClick={() => navigate('/')}
          title="Return to Main Menu"
        >
          ← Main Menu
        </button>
        
        <h1>Character Sheet</h1>
        
        <button 
          className="game-btn"
          onClick={() => navigate('/game')}
          title="Return to Game"
        >
          🎮 Game
        </button>
      </div>
      
      <div className="view-container">
        {/* Character Header */}
        <div className="character-header">
          <h1>{character.name}</h1>
          <div className="character-basics">
            <span className="race">{character.race}</span>
            <span className="class">{character.character_class}</span>
            <span className="background">{character.background}</span>
            <span className="level">Level {character.level}</span>
          </div>
        </div>

        {/* Ability Scores Grid */}
        <div className="abilities-section">
          <h2>Ability Scores</h2>
          <div className="ability-scores-grid">
            {['str', 'dex', 'con', 'int', 'wis', 'cha'].map((ability) => (
              <div key={ability} className="ability-score-card">
                <div className="ability-name">{ability.toUpperCase()}</div>
                <div className="ability-score">{finalStats[ability]}</div>
                <div className="ability-modifier">
                  {calculateModifier(finalStats[ability]) >= 0 ? '+' : ''}{calculateModifier(finalStats[ability])}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Derived Stats */}
        <div className="derived-section">
          <h2>Combat Statistics</h2>
          <div className="derived-stats-grid">
            <div className="stat-card">
              <div className="stat-label">Hit Points</div>
              <div className="stat-value">
                {character.hit_points_current || character.current_hit_points || 0} / {character.hit_points_max || character.max_hit_points || 0}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Armor Class</div>
              <div className="stat-value">{character.armor_class || (10 + calculateModifier(finalStats.dex))}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Initiative</div>
              <div className="stat-value">
                {calculateModifier(finalStats.dex) >= 0 ? '+' : ''}{calculateModifier(finalStats.dex)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Proficiency Bonus</div>
              <div className="stat-value">+{character.proficiency_bonus || 2}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Speed</div>
              <div className="stat-value">{character.speed || 30} ft</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Hit Dice</div>
              <div className="stat-value">
                {character.hit_dice_current || character.level} / {character.hit_dice_max || character.level}
              </div>
            </div>
          </div>
        </div>

        {/* Experience and Progression */}
        <div className="progression-section">
          <h2>Character Progression</h2>
          <div className="progression-stats">
            <div className="stat-card">
              <div className="stat-label">Experience Points</div>
              <div className="stat-value">{character.experience_points || character.experience || 0}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Gold</div>
              <div className="stat-value">{character.gold || 0} gp</div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="character-actions">
          <button className="primary-btn" onClick={() => navigate('/game')}>
            Return to Game
          </button>
          <button className="secondary-btn" onClick={() => navigate('/')}>
            Main Menu
          </button>
        </div>
      </div>
    </div>
  );
};

export default CharacterView;