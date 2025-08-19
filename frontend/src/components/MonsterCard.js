/**
 * File: frontend/src/components/MonsterCard.js
 * Path: /frontend/src/components/MonsterCard.js
 * 
 * Monster Card Component
 * 
 * Pseudo Code:
 * 1. Display monster information and stats
 * 2. Show HP bar and status conditions
 * 3. Handle monster selection for targeting
 * 4. Display damage animations and effects
 * 5. Show monster actions and abilities
 * 
 * AI Agents: Individual monster display with targeting and combat status.
 */

import React from 'react';

const MonsterCard = ({ monster, isSelected, onSelect, lastDamage, disabled }) => {
  const hpPercentage = monster.is_alive ? (monster.hp / monster.max_hp) * 100 : 0;

  return (
    <div 
      className={`monster-card ${isSelected ? 'selected' : ''} ${!monster.is_alive ? 'defeated' : ''} ${disabled ? 'disabled' : ''}`}
      onClick={disabled ? undefined : onSelect}
    >
      <div className="monster-header">
        <h3>{monster.name}</h3>
        <span className="monster-cr">CR {monster.challenge_rating || '1/4'}</span>
      </div>
      
      <div className="monster-stats">
        <div className="hp-bar">
          <div 
            className="hp-fill"
            style={{ 
              width: `${hpPercentage}%`,
              backgroundColor: hpPercentage > 50 ? '#4ade80' : hpPercentage > 25 ? '#f59e0b' : '#ef4444'
            }}
          />
          <span className="hp-text">
            {monster.hp}/{monster.max_hp} HP
          </span>
        </div>
        
        <div className="monster-ac">
          AC {monster.armor_class || monster.ac || 11}
        </div>
      </div>
      
      {monster.conditions && monster.conditions.length > 0 && (
        <div className="monster-conditions">
          {monster.conditions.map(condition => (
            <span key={condition} className="condition-badge">
              {condition}
            </span>
          ))}
        </div>
      )}
      
      {!monster.is_alive && (
        <div className="defeated-overlay">
          DEFEATED
        </div>
      )}
      
      {lastDamage && Date.now() - (lastDamage.timestamp || 0) < 2000 && (
        <div className="damage-indicator">
          -{typeof lastDamage === 'number' ? lastDamage : lastDamage.amount || 0}
        </div>
      )}
    </div>
  );
};

export default MonsterCard;