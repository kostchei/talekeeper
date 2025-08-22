/**
 * File: frontend/src/components/CharacterSummary.js
 * Path: /frontend/src/components/CharacterSummary.js
 * 
 * Character Summary Component - Displays condensed character info for game screen.
 * 
 * Pseudo Code:
 * 1. Check if character exists, show fallback if not
 * 2. Extract character stats from multiple possible data sources
 * 3. Calculate current/max HP, AC, XP, and gold values
 * 4. Display character name prominently
 * 5. Show key combat and progression stats in labeled format
 * 
 * AI Agents: Compact character display for game UI sidebar.
 */

import React from 'react';

const CharacterSummary = ({ character, gameState }) => {
  if (!character) {
    return (
      <div className="character-summary">
        <h3>No Character</h3>
      </div>
    );
  }

  const currentHP = character.hit_points_current || character.current_hit_points || character.combat_stats?.hit_points_current || 0;
  const maxHP = character.hit_points_max || character.max_hit_points || character.combat_stats?.hit_points_max || 0;
  const ac = character.armor_class || character.combat_stats?.armor_class || 10;
  const xp = character.experience_points || 0;
  const gold = gameState?.inventory_gold || character.gold || 0;

  return (
    <div className="character-summary">
      <h3>{character.name}</h3>
      <div className="summary-item">
        <span className="label">HP:</span>
        <span className="value">{currentHP}/{maxHP}</span>
      </div>
      <div className="summary-item">
        <span className="label">AC:</span>
        <span className="value">{ac}</span>
      </div>
      <div className="summary-item">
        <span className="label">XP:</span>
        <span className="value">{xp}</span>
      </div>
      <div className="summary-item">
        <span className="label">Gold:</span>
        <span className="value">{gold} gp</span>
      </div>
    </div>
  );
};

export default CharacterSummary;

