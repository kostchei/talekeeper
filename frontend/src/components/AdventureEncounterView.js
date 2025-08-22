import React, { useState } from 'react';
import { gameAPI } from '../services/api';

const AdventureEncounterView = ({ character, gameState, locationType, onActionLog, onBackToTiles }) => {
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
    if (currentEncounter && currentEncounter.type === 'combat') {
      onActionLog(`Accepted combat with ${currentEncounter.monsters.length} monster(s)!`);
      // TODO: Navigate to CombatScreen with encounter data
      console.log('Combat started with encounter:', currentEncounter);
      onBackToTiles();
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

      <style jsx>{`
        .adventure-encounter-view {
          padding: 20px;
          max-width: 800px;
          margin: 0 auto;
        }

        .encounter-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .encounter-header h2 {
          color: #d4a574;
          margin-bottom: 10px;
        }

        .encounter-generation {
          display: flex;
          gap: 15px;
          justify-content: center;
          margin-bottom: 30px;
        }

        .generate-encounter-btn, .safe-explore-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .generate-encounter-btn {
          background: linear-gradient(135deg, #dc3545, #b02a37);
          color: white;
        }

        .generate-encounter-btn:hover {
          background: linear-gradient(135deg, #c82333, #9e2530);
          transform: translateY(-2px);
        }

        .safe-explore-btn {
          background: linear-gradient(135deg, #28a745, #218838);
          color: white;
        }

        .safe-explore-btn:hover {
          background: linear-gradient(135deg, #218838, #1e7e34);
          transform: translateY(-2px);
        }

        .encounter-loading {
          text-align: center;
          padding: 40px;
          color: #6c757d;
          font-style: italic;
        }

        .encounter-error {
          text-align: center;
          padding: 20px;
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .encounter-display {
          background: #f8f9fa;
          border: 2px solid #d4a574;
          border-radius: 12px;
          padding: 25px;
          margin-bottom: 20px;
        }

        .encounter-summary {
          text-align: center;
          margin-bottom: 25px;
        }

        .encounter-stats {
          display: flex;
          justify-content: center;
          gap: 20px;
          margin-top: 10px;
          flex-wrap: wrap;
        }

        .encounter-stats span {
          background: white;
          padding: 8px 16px;
          border-radius: 20px;
          font-weight: bold;
          border: 1px solid #dee2e6;
        }

        .encounter-difficulty {
          font-weight: bold !important;
        }

        .monsters-display {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 15px;
          margin-bottom: 25px;
        }

        .monster-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 15px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .monster-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }

        .monster-header h4 {
          margin: 0;
          color: #343a40;
        }

        .monster-cr {
          background: #6f42c1;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: bold;
        }

        .monster-stats {
          display: flex;
          gap: 15px;
          margin-bottom: 10px;
          font-size: 14px;
        }

        .monster-stats span {
          background: #e9ecef;
          padding: 2px 6px;
          border-radius: 4px;
        }

        .monster-abilities {
          font-size: 12px;
          color: #6c757d;
          font-style: italic;
        }

        .encounter-actions {
          display: flex;
          gap: 15px;
          justify-content: center;
        }

        .combat-btn, .retreat-btn {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .combat-btn {
          background: linear-gradient(135deg, #dc3545, #b02a37);
          color: white;
        }

        .combat-btn:hover {
          background: linear-gradient(135deg, #c82333, #9e2530);
          transform: translateY(-2px);
        }

        .retreat-btn {
          background: linear-gradient(135deg, #6c757d, #545b62);
          color: white;
        }

        .retreat-btn:hover {
          background: linear-gradient(135deg, #5a6268, #495057);
          transform: translateY(-2px);
        }

        .back-button {
          text-align: center;
          margin-top: 20px;
        }

        .back-button button {
          padding: 8px 16px;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }

        .back-button button:hover {
          background: #5a6268;
        }

        .encounter-message {
          font-style: italic;
          color: #6c757d;
          margin: 10px 0;
          text-align: center;
        }

        .treasure-display, .event-display {
          padding: 20px;
          background: white;
          border-radius: 8px;
          margin: 20px 0;
          text-align: center;
        }

        .treasure-item {
          font-size: 18px;
          color: #ffc107;
          font-weight: bold;
          margin: 10px 0;
        }

        .treasure-items {
          margin: 15px 0;
          color: #495057;
        }

        .event-options {
          display: flex;
          gap: 10px;
          justify-content: center;
          flex-wrap: wrap;
        }

        .event-option-btn, .accept-btn {
          padding: 10px 20px;
          background: linear-gradient(135deg, #28a745, #218838);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .event-option-btn:hover, .accept-btn:hover {
          background: linear-gradient(135deg, #218838, #1e7e34);
          transform: translateY(-2px);
        }
      `}</style>
    </div>
  );
};

export default AdventureEncounterView;
