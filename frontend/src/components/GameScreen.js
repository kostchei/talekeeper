import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useGameStore } from '../services/gameStore';
import { gameAPI } from '../services/api';
import CharacterSummary from './CharacterSummary';
import ActionLog from './ActionLog';
import MainGameView from './MainGameView';

const GameScreen = () => {
  const navigate = useNavigate();
  const { character, gameState, updateGameState } = useGameStore();

  console.log('=== GAMESCREEN RENDER ===');
  console.log('Character:', character?.name);
  console.log('GameState inCombat:', gameState?.inCombat);
  console.log('Current location:', window.location.pathname);

  const [gameTime, setGameTime] = useState(new Date());
  const [locationType, setLocationType] = useState('town');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLog, setActionLog] = useState([]);

  // Debug component lifecycle
  useEffect(() => {
    console.log('=== GAMESCREEN MOUNTED ===');
    return () => {
      console.log('=== GAMESCREEN UNMOUNTED ===');
    };
  }, []);

  const loadGameState = useCallback(async () => {
    try {
      setIsLoading(true);
      const state = await gameAPI.getGameState(character.id);
      if (state) {
        setLocationType(state.location_type || 'town');
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
  }, [character?.id, updateGameState]);

  useEffect(() => {
    if (character && character.id) {
      loadGameState();
    }
  }, [character, loadGameState]);
  useEffect(() => {
    const timer = setInterval(() => {
      setGameTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const handleNavigateToCombat = useCallback((encounterData) => {
    console.log('=== NAVIGATE TO COMBAT CALLED ===');
    console.log('Encounter data:', encounterData);
    
    // Store encounter data in game state
    updateGameState(prev => {
      const newState = {
        ...prev,
        currentEncounter: encounterData,
        inCombat: true  // Set to true so combat route is accessible
      };
      console.log('Updating game state to:', newState);
      return newState;
    });
    
    console.log('Navigating to /combat');
    // Navigate to combat screen
    navigate('/combat');
  }, [updateGameState, navigate]);

  const handleManualSave = async () => {
    if (!character?.id) return;
    try {
      setIsLoading(true);
      await gameAPI.saveGame(character.id, {
        current_location: gameState?.current_location || 'Unknown',
        location_type: locationType,
        save_name: `${character.name} - ${gameState?.current_location || 'Unknown'}`,
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

  const addLogEntry = (message) => {
    console.log('=== ADDING LOG ENTRY ===', message);
    console.log('Current actionLog length:', actionLog.length);
    setActionLog(prev => {
      const newLog = [...prev, { message, timestamp: Date.now() }];
      console.log('New actionLog length:', newLog.length);
      return newLog;
    });
  };

  return (
    <div className="game-screen">
      <header className="game-header">
        <div className="header-left">
          <h1>TaleKeeper</h1>
          <div className="game-time">
            {gameTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
        <div className="header-actions">
          <button className="btn-secondary menu-btn" onClick={() => navigate('/')}>← Menu</button>
          <button className="btn-secondary character-sheet-btn" onClick={() => navigate('/character-view')}>📋 Character</button>
          <button className="btn-primary" onClick={handleManualSave} disabled={isLoading}>💾</button>
        </div>
      </header>

      <main className="game-content">
        <CharacterSummary character={character} gameState={gameState} />
        <div className="main-panel">
          <MainGameView 
            locationType={locationType}
            character={character}
            gameState={gameState}
            onActionLog={addLogEntry}
            onNavigateToCombat={handleNavigateToCombat}
          />
        </div>
        <ActionLog entries={actionLog} />
      </main>
    </div>
  );
};

export default GameScreen;

