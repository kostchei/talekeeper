import React from 'react';

const CharacterSummary = ({ character, gameState }) => {
  if (!character) {
    return (
      <div className="character-summary">
        <h3>No Character</h3>
      </div>
    );
  }

  const currentHP = character.hit_points_current || character.current_hit_points || 0;
  const maxHP = character.hit_points_max || character.max_hit_points || 0;
  const ac = character.armor_class || 10;
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

