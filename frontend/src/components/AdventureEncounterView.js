import React, { useState } from 'react';
import { gameAPI } from '../services/api';
import '../styles/adventure.css';

const AdventureEncounterView = ({ character, gameState, locationType, onActionLog, onBackToTiles, onNavigateToCombat }) => {
  const [currentEncounter, setCurrentEncounter] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateEncounter = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('Generating encounter with:', { characterId: character.id, locationType: locationType || 'wilderness' });
      const response = await gameAPI.generateRandomEncounter(character.id, locationType || 'wilderness');
      if (response.success) {
        setCurrentEncounter(response);
        if (response.type === 'combat') {
          onActionLog(`Generated encounter: ${response.monsters.length} monster(s), ${response.total_xp} XP`);
        } else {
          onActionLog(`Encounter generated: ${response.message}`);
        }
      } else {
        setError(response.message || 'Failed to generate encounter');
      }
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Encounter generation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const acceptCombat = () => {
    if (currentEncounter && currentEncounter.type === 'combat' && onNavigateToCombat) {
      onActionLog(`Accepted combat with ${currentEncounter.monsters.length} monster(s)!`);
      
      // Convert encounter data to combat format
      const combatEncounter = {
        monsters: currentEncounter.monsters.map(monster => ({
          id: monster.id,
          name: monster.name,
          challenge_rating: monster.challenge_rating,
          hit_points: monster.hit_points,
          armor_class: monster.armor_class,
          xp_value: monster.xp_value,
          special_abilities: monster.special_abilities,
          actions: monster.actions
        })),
        difficulty: currentEncounter.difficulty,
        total_xp: currentEncounter.total_xp,
        xp_budget: currentEncounter.xp_budget,
        environment: locationType || 'wilderness'
      };
      
      // Navigate to combat with encounter data
      onNavigateToCombat(combatEncounter);
    }
  };

  const handleEncounterAction = (action) => {
    if (currentEncounter) {
      onActionLog(`${action}: ${currentEncounter.message}`);
      if (currentEncounter.type === 'treasure' && currentEncounter.gold_found) {
        onActionLog(`Found ${currentEncounter.gold_found} gold!`);
      }
      setCurrentEncounter(null);
    }
  };

  const retreat = () => {
    onActionLog('Retreated from encounter');
    setCurrentEncounter(null);
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'trivial': '#28a745',
      'easy': '#6f42c1', 
      'medium': '#fd7e14',
      'hard': '#dc3545',
      'deadly': '#6f0000'
    };
    return colors[difficulty?.toLowerCase()] || '#6c757d';
  };

  return (
    <div className="adventure-encounter-view">
      <div className="encounter-header">
        <h2>⚔️ Seek Adventure</h2>
        <p>Search for monsters and treasure in the {locationType || 'wilderness'}...</p>
      </div>

      {!currentEncounter && !isLoading && (
        <div className="encounter-generation">
          <button 
            className="generate-encounter-btn"
            onClick={generateEncounter}
            disabled={isLoading}
          >
            🎲 Generate Random Encounter
          </button>
          <button className="safe-explore-btn" onClick={onBackToTiles}>
            🔍 Explore Safely
          </button>
        </div>
      )}

      {isLoading && (
        <div className="encounter-loading">
          <p>🎲 Generating encounter...</p>
        </div>
      )}

      {error && (
        <div className="encounter-error">
          <p style={{color: '#dc3545'}}>❌ {error}</p>
          <button onClick={() => setError(null)}>Try Again</button>
        </div>
      )}

      {currentEncounter && (
        <div className="encounter-display">
          <div className="encounter-summary">
            <h3>{currentEncounter.type === 'combat' ? 'Combat Encounter!' : 
                 currentEncounter.type === 'treasure' ? 'Treasure Found!' : 'Special Event!'}</h3>
            <p className="encounter-message">{currentEncounter.message}</p>
          </div>

          {currentEncounter.type === 'combat' && (
            <>
              <div className="encounter-stats">
                <span className="encounter-difficulty" 
                      style={{color: getDifficultyColor(currentEncounter.difficulty)}}>
                  Difficulty: {currentEncounter.difficulty || 'Unknown'}
                </span>
                <span className="encounter-xp">
                  Total XP: {currentEncounter.total_xp}
                </span>
                <span className="monster-count">
                  Monsters: {currentEncounter.monsters.length}
                </span>
              </div>

              <div className="monsters-display">
                {currentEncounter.monsters.map((monster, index) => (
                  <div key={index} className="monster-card">
                    <div className="monster-header">
                      <h4>{monster.name}</h4>
                      <span className="monster-cr">CR {monster.challenge_rating}</span>
                    </div>
                    <div className="monster-stats">
                      <span>HP: {monster.hit_points}</span>
                      <span>AC: {monster.armor_class}</span>
                      <span>XP: {monster.xp_value}</span>
                    </div>
                    {monster.special_abilities && monster.special_abilities.length > 0 && (
                      <div className="monster-abilities">
                        <strong>Special:</strong> {monster.special_abilities.slice(0, 2).join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="encounter-actions">
                <button className="combat-btn" onClick={acceptCombat}>
                  ⚔️ Accept Combat
                </button>
                <button className="retreat-btn" onClick={retreat}>
                  🏃 Retreat
                </button>
              </div>
            </>
          )}

          {currentEncounter.type === 'treasure' && (
            <div className="treasure-display">
              {currentEncounter.gold_found && (
                <div className="treasure-item">
                  💰 Gold Found: {currentEncounter.gold_found}
                </div>
              )}
              {currentEncounter.items_found && currentEncounter.items_found.length > 0 && (
                <div className="treasure-items">
                  <strong>Items:</strong> {currentEncounter.items_found.join(', ')}
                </div>
              )}
              <div className="encounter-actions">
                <button className="accept-btn" onClick={() => handleEncounterAction('Collected treasure')}>
                  💰 Collect Treasure
                </button>
              </div>
            </div>
          )}

          {currentEncounter.type === 'event' && (
            <div className="event-display">
              {currentEncounter.options && (
                <div className="event-options">
                  {currentEncounter.options.map((option, index) => (
                    <button key={index} className="event-option-btn" 
                            onClick={() => handleEncounterAction(option)}>
                      {option}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="back-button">
        <button onClick={onBackToTiles}>← Back to Activities</button>
      </div>

    </div>
  );
};

export default AdventureEncounterView;
