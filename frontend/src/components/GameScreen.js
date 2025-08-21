import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useGameStore } from '../services/gameStore';
import { gameAPI } from '../services/api';
import CharacterSummary from './CharacterSummary';
import ActivityPanel from './ActivityPanel';
import ActionLog from './ActionLog';

const GameScreen = () => {
  const navigate = useNavigate();
  const { character, gameState, updateGameState } = useGameStore();

  const [gameTime, setGameTime] = useState(new Date());
  const [locationType, setLocationType] = useState('town');
  const [isLoading, setIsLoading] = useState(false);
  const [actionLog, setActionLog] = useState([]);

  useEffect(() => {
    if (character && character.id) {
      loadGameState();
    }
  }, [character]);

  useEffect(() => {
    const timer = setInterval(() => {
      setGameTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const loadGameState = async () => {
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
  };

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
    setActionLog(prev => [...prev, { message, timestamp: Date.now() }]);
  };

  const handleActivity = (action) => {
    switch (action) {
      case 'rest_town':
        navigate('/rest');
        addLogEntry('Rested in town.');
        break;
      case 'rest_wilderness':
        navigate('/rest', { state: { wilderness: true } });
        addLogEntry('Rested in the wilderness.');
        break;
      case 'shop':
        navigate('/town');
        addLogEntry('Visited the town shop.');
        break;
      default:
        break;
    }
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
          {gameState?.currentEncounter ? (
            <div className="encounter-panel">
              <h3>Encounter</h3>
              <p>An encounter is in progress...</p>
            </div>
          ) : (
            <ActivityPanel locationType={locationType} onAction={handleActivity} />
          )}
        </div>
        <ActionLog entries={actionLog} />
      </main>
    </div>
  );
};

export default GameScreen;

