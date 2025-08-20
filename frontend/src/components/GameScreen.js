/**
 * File: frontend/src/components/GameScreen.js
 * Path: /frontend/src/components/GameScreen.js
 * 
 * Enhanced Game Screen Component with ExplorationInterface
 * 
 * Pseudo Code:
 * 1. Display main game interface with character status and location info
 * 2. Integrate ExplorationInterface for contextual actions
 * 3. Handle location changes and game state management
 * 4. Provide access to character sheet and quick actions
 * 5. Manage game state persistence and auto-save
 * 
 * AI Agents: Central hub for game world interaction and navigation.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { useGameStore } from '../services/gameStore';
import { gameAPI } from '../services/api';
import ExplorationInterface from './ExplorationInterface';

const GameScreen = () => {
  const navigate = useNavigate();
  const { character, gameState, updateGameState } = useGameStore();
  
  const [currentLocation, setCurrentLocation] = useState('Starting Town');
  const [locationType, setLocationType] = useState('town');
  const [gameTime, setGameTime] = useState(new Date());
  const [isLoading, setIsLoading] = useState(false);

  // Initialize game state on component mount
  useEffect(() => {
    if (character && character.id) {
      loadGameState();
    }
  }, [character]); // eslint-disable-line react-hooks/exhaustive-deps

  // Update game time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setGameTime(new Date());
    }, 60000);

    return () => clearInterval(timer);
  }, []);

  // Load current game state from backend
  const loadGameState = async () => {
    try {
      setIsLoading(true);
      const state = await gameAPI.getGameState(character.id);
      
      if (state) {
        setCurrentLocation(state.current_location || 'Starting Town');
        setLocationType(state.location_type || 'town');
        
        // Update global game state
        updateGameState(prev => ({
          ...prev,
          ...state
        }));
      }
    } catch (error) {
      console.error('Failed to load game state:', error);
      toast.error('Failed to load game state');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle location changes
  const handleLocationChange = async (newLocationType, newLocationName) => {
    try {
      setIsLoading(true);
      setLocationType(newLocationType);
      setCurrentLocation(newLocationName);

      // Update backend game state
      await gameAPI.updateLocation(character.id, {
        location_type: newLocationType,
        current_location: newLocationName
      });

      // Update local state
      updateGameState(prev => ({
        ...prev,
        location_type: newLocationType,
        current_location: newLocationName
      }));

      toast.success(`Moved to ${newLocationName}`);
    } catch (error) {
      console.error('Failed to update location:', error);
      toast.error('Failed to update location');
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-save game state periodically
  useEffect(() => {
    if (!character?.id) return;

    const autoSave = setInterval(async () => {
      try {
        await gameAPI.autoSave(character.id, {
          current_location: currentLocation,
          location_type: locationType,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, 300000); // Auto-save every 5 minutes

    return () => clearInterval(autoSave);
  }, [character?.id, currentLocation, locationType]);

  // Manual save
  const handleManualSave = async () => {
    if (!character?.id) return;
    
    try {
      setIsLoading(true);
      await gameAPI.saveGame(character.id, {
        current_location: currentLocation,
        location_type: locationType,
        save_name: `${character.name} - ${currentLocation}`,
        timestamp: new Date().toISOString()
      });
      toast.success('Game saved successfully');
    } catch (error) {
      console.error('Manual save failed:', error);
      toast.error('Failed to save game');
    } finally {
      setIsLoading(false);
    }
  };

  // Get location description
  const getLocationDescription = (location, type) => {
    const descriptions = {
      town: "A bustling settlement with shops, an inn, and friendly faces. A safe haven for adventurers.",
      dungeon: "Ancient stone corridors echo with distant sounds. Danger and treasure await in equal measure.",
      wilderness: "Vast open lands stretch before you. Nature's beauty hides both opportunity and peril."
    };
    
    return descriptions[type] || "An unknown location full of mystery.";
  };

  if (isLoading && !gameState) {
    return (
      <div className="game-screen loading">
        <div className="loading-spinner" />
        <p>Loading game state...</p>
      </div>
    );
  }

  return (
    <div className="game-screen">
      {/* Game Header */}
      <header className="game-header">
        <div className="header-left">
          <h1>TaleKeeper</h1>
          <div className="game-time">
            {gameTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
        
        {character && (
          <div className="character-status-summary">
            <div className="character-name">{character.name}</div>
            <div className="character-stats">
              <span className="hp">
                HP: {character.hit_points_current || character.current_hit_points || 0}/
                {character.hit_points_max || character.max_hit_points || 0}
              </span>
              <span className="level">Level {character.level}</span>
              <span className="gold">💰 {gameState?.inventory_gold || 0}</span>
            </div>
          </div>
        )}

        <div className="header-actions">
          <button 
            className="btn-secondary menu-btn"
            onClick={() => navigate('/')}
            title="Return to Main Menu"
          >
            ← Menu
          </button>
          <button 
            className="btn-secondary character-sheet-btn"
            onClick={() => navigate('/character-view')}
            title="View Character Sheet"
          >
            📋 Character
          </button>
          <button 
            className="btn-primary"
            onClick={handleManualSave}
            disabled={isLoading}
            title="Save Game"
          >
            💾
          </button>
        </div>
      </header>

      {/* Game Content */}
      <main className="game-content">
        {/* Location Info Panel */}
        <div className="location-panel">
          <div className="location-header">
            <h2>{currentLocation}</h2>
            <span className="location-badge">{locationType}</span>
          </div>
          <p className="location-description">
            {getLocationDescription(currentLocation, locationType)}
          </p>
        </div>

        {/* Main Exploration Interface */}
        <div className="exploration-panel">
          <ExplorationInterface
            currentLocation={currentLocation}
            locationType={locationType}
            character={character}
            gameState={gameState}
            onLocationChange={handleLocationChange}
          />
        </div>

        {/* Quick Status Panel */}
        <div className="status-panel">
          <h3>Quick Status</h3>
          <div className="status-grid">
            {character && (
              <>
                <div className="status-item">
                  <span className="label">HP</span>
                  <span className="value">
                    {character.hit_points_current || character.current_hit_points || 0}/
                    {character.hit_points_max || character.max_hit_points || 0}
                  </span>
                </div>
                <div className="status-item">
                  <span className="label">AC</span>
                  <span className="value">{character.armor_class || 10}</span>
                </div>
                <div className="status-item">
                  <span className="label">XP</span>
                  <span className="value">{character.experience_points || 0}</span>
                </div>
                <div className="status-item">
                  <span className="label">Hit Dice</span>
                  <span className="value">
                    {character.hit_dice_current || character.level}/
                    {character.hit_dice_max || character.level}
                  </span>
                </div>
              </>
            )}
          </div>
          
          {/* Quick Actions */}
          <div className="quick-actions">
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/rest')}
              title="Rest"
            >
              🛌 Rest
            </button>
            <button 
              className="quick-action-btn"
              onClick={() => navigate('/town')}
              title="Town Services"
              disabled={locationType !== 'town'}
            >
              🏪 Town
            </button>
          </div>
        </div>
      </main>

      {/* Loading Overlay */}
      {isLoading && (
        <motion.div 
          className="loading-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="loading-spinner" />
          <p>Processing...</p>
        </motion.div>
      )}
    </div>
  );
};

export default GameScreen;