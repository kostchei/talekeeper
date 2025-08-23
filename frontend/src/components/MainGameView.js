/**
 * File: frontend/src/components/MainGameView.js
 * Path: /frontend/src/components/MainGameView.js
 * 
 * Main Game View Component - Central interface with 4 activity tiles and activity views.
 * 
 * Pseudo Code:
 * 1. Display 4 clickable activity tiles when no activity is selected
 * 2. Show activity-specific view when tile is clicked (shop, rest town, rest nature, encounter)
 * 3. Provide back navigation to return to tile selection
 * 4. Handle activity completion and state updates
 * 5. Log activities and pass data to parent components
 * 
 * AI Agents: Core game interface with tile-based activity selection.
 */

import React, { useState } from 'react';
import { gameAPI } from '../services/api';
import AdventureEncounterView from './AdventureEncounterView';

const MainGameView = ({ 
  locationType, 
  character, 
  gameState, 
  onActionLog,
  onNavigateToCombat 
}) => {
  const [activeView, setActiveView] = useState(null);

  const activityTiles = [
    {
      id: 'shop',
      title: 'Shop in Town',
      description: 'Buy and sell equipment',
      icon: '🏪',
      enabled: locationType === 'town',
      className: 'shop-tile'
    },
    {
      id: 'rest_town',
      title: 'Rest in Town',
      description: 'Full rest with inn comforts',
      icon: '🏨',
      enabled: locationType === 'town',
      className: 'rest-town-tile'
    },
    {
      id: 'rest_nature',
      title: 'Rest in Nature',
      description: 'Camp under the stars',
      icon: '🏕️',
      enabled: locationType === 'wilderness',
      className: 'rest-nature-tile'
    },
    {
      id: 'encounter',
      title: 'Seek Adventure',
      description: 'Look for monsters and treasure',
      icon: '⚔️',
      enabled: true,
      className: 'encounter-tile'
    }
  ];

  const handleTileClick = async (tileId) => {
    if (tileId === 'encounter') {
      // Skip the intermediate step - directly generate encounter and start combat
      onActionLog('Seeking adventure...');
      try {
        console.log('Generating encounter directly from tile click');
        const response = await gameAPI.generateRandomEncounter(character.id, locationType || 'wilderness');
        if (response.success && response.type === 'combat') {
          onActionLog(`Generated encounter: ${response.monsters.length} monster(s), ${response.total_xp} XP`);
          onActionLog('Starting combat...');
          console.log('Calling onNavigateToCombat from MainGameView');
          onNavigateToCombat(response);
        } else {
          // For non-combat encounters, show the encounter view
          setActiveView(tileId);
        }
      } catch (error) {
        console.error('Failed to generate encounter:', error);
        onActionLog('Failed to find adventure...');
        setActiveView(tileId); // Fall back to encounter view
      }
    } else {
      setActiveView(tileId);
      onActionLog(`Started ${activityTiles.find(t => t.id === tileId)?.title}`);
    }
  };

  const handleBackToTiles = () => {
    setActiveView(null);
    onActionLog('Returned to main area');
  };

  const renderActivityView = () => {
    switch (activeView) {
      case 'shop':
        return (
          <div className="activity-view shop-view">
            <div className="activity-header">
              <button className="back-btn" onClick={handleBackToTiles}>← Back</button>
              <h2>🏪 Town Shop</h2>
            </div>
            <div className="activity-content">
              <p>Welcome to the town shop! Here you can buy and sell equipment.</p>
              <div className="shop-sections">
                <div className="shop-section">
                  <h3>Buy Items</h3>
                  <p>Shop inventory coming soon...</p>
                </div>
                <div className="shop-section">
                  <h3>Sell Items</h3>
                  <p>Character inventory coming soon...</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'rest_town':
        return (
          <div className="activity-view rest-town-view">
            <div className="activity-header">
              <button className="back-btn" onClick={handleBackToTiles}>← Back</button>
              <h2>🏨 Rest in Town</h2>
            </div>
            <div className="activity-content">
              <p>You rest comfortably in the town inn, recovering all your strength.</p>
              <div className="rest-benefits">
                <h3>Full Rest Benefits:</h3>
                <ul>
                  <li>Restore all hit points</li>
                  <li>Recover all spell slots</li>
                  <li>Reset all abilities</li>
                  <li>Remove exhaustion</li>
                </ul>
              </div>
              <button className="primary-btn" onClick={() => {
                onActionLog('Completed full rest in town');
                handleBackToTiles();
              }}>
                Complete Rest
              </button>
            </div>
          </div>
        );

      case 'rest_nature':
        return (
          <div className="activity-view rest-nature-view">
            <div className="activity-header">
              <button className="back-btn" onClick={handleBackToTiles}>← Back</button>
              <h2>🏕️ Rest in Nature</h2>
            </div>
            <div className="activity-content">
              <p>You make camp in the wilderness. The rest is less comfortable but still restorative.</p>
              <div className="rest-benefits">
                <h3>Wilderness Rest Benefits:</h3>
                <ul>
                  <li>Restore half hit points</li>
                  <li>Recover some spell slots</li>
                  <li>Reset short rest abilities</li>
                  <li>Risk of random encounters</li>
                </ul>
              </div>
              <button className="primary-btn" onClick={() => {
                onActionLog('Completed wilderness rest');
                handleBackToTiles();
              }}>
                Complete Rest
              </button>
            </div>
          </div>
        );

      case 'encounter':
        return <AdventureEncounterView 
          character={character}
          gameState={gameState}
          locationType={locationType}
          onActionLog={onActionLog}
          onBackToTiles={handleBackToTiles}
          onNavigateToCombat={onNavigateToCombat}
        />;

      default:
        return null;
    }
  };

  if (activeView) {
    return renderActivityView();
  }

  return (
    <div className="main-game-view">
      <div className="activity-tiles">
        <h2>Choose Your Activity</h2>
        <div className="tiles-grid">
          {activityTiles.map((tile) => (
            <div
              key={tile.id}
              className={`activity-tile ${tile.className} ${!tile.enabled ? 'disabled' : ''}`}
              onClick={() => tile.enabled && handleTileClick(tile.id)}
            >
              <div className="tile-icon">{tile.icon}</div>
              <div className="tile-content">
                <h3>{tile.title}</h3>
                <p>{tile.description}</p>
                {!tile.enabled && <span className="disabled-text">Not available here</span>}
              </div>
            </div>
          ))}
        </div>
        <div className="location-info">
          <p>Current Location: <strong>{locationType === 'town' ? 'Town' : 'Wilderness'}</strong></p>
        </div>
      </div>
    </div>
  );
};

export default MainGameView;