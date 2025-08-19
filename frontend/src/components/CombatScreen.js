/**
 * File: frontend/src/components/CombatScreen.js
 * Path: /frontend/src/components/CombatScreen.js
 * 
 * Combat Screen Component
 * 
 * Pseudo Code:
 * 1. Initialize combat encounter with monsters and turn order
 * 2. Display character status, monster cards, and action interface
 * 3. Handle player action selection and processing
 * 4. Automatically process monster turns with AI
 * 5. Show combat log and damage/healing animations
 * 6. Handle combat end conditions (victory/defeat/flee)
 * 
 * AI Agents: This handles the round-by-round combat UI.
 * Key features:
 * - Action/Bonus/Reaction cards that flip when used
 * - Character sheet display (top left)
 * - Monster cards (center)
 * - Combat log (right)
 * - Turn order tracker
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
// No icon dependencies needed - using text-based interface
import toast from 'react-hot-toast';
import { combatAPI } from '../services/api';
import { useGameStore } from '../services/gameStore';
import ActionCards from './ActionCards';
import MonsterCard from './MonsterCard';
import CombatLog from './CombatLog';
import '../styles/combat.css';

const CombatScreen = () => {
  const navigate = useNavigate();
  const { character, updateCharacter, gameState, updateGameState } = useGameStore();
  
  // Combat state
  const [combatState, setCombatState] = useState(null);
  const [selectedTarget, setSelectedTarget] = useState(null);
  const [selectedAction, setSelectedAction] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [combatLog, setCombatLog] = useState([]);
  
  // Animation states
  const [lastDamageDealt, setLastDamageDealt] = useState({});
  const [lastHeal, setLastHeal] = useState({});

  // Define callback functions first
  const initializeCombat = useCallback(async () => {
    try {
      setIsProcessing(true);
      // Get current encounter from game state
      const encounter = gameState?.currentEncounter || { monsters: ['zombie'] };
      
      const response = await combatAPI.startCombat(character.id, encounter);
      setCombatState(response.combatState);
      setCombatLog(response.combatState.log || []);
      
      // Update character with any combat-related changes
      if (response.updatedCharacter) {
        updateCharacter(response.updatedCharacter);
      }
      
      // Update game state with combat status
      updateGameState({ 
        ...gameState, 
        inCombat: true, 
        currentEncounter: encounter 
      });
      
      toast.success('Combat begins!');
    } catch (error) {
      console.error('Failed to initialize combat:', error);
      toast.error('Failed to start combat');
      navigate('/game');
    } finally {
      setIsProcessing(false);
    }
  }, [character.id, gameState, updateCharacter, updateGameState, navigate]);

  const handleCombatEnd = useCallback((outcome) => {
    if (outcome === 'victory') {
      toast.success('Victory! You defeated all enemies!');
      // Navigate to loot screen after victory
      setTimeout(() => {
        navigate('/loot', { state: { combatResult: 'victory' } });
      }, 2000);
    } else if (outcome === 'defeat') {
      toast.error('You have been defeated...');
      setTimeout(() => {
        navigate('/', { state: { gameOver: true } });
      }, 2000);
    }
  }, [navigate]);

  const processMonsterTurn = useCallback(async () => {
    // Delay for dramatic effect
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    try {
      setIsProcessing(true);
      const monsterId = combatState.currentTurn;
      const response = await combatAPI.processMonsterTurn(monsterId);
      
      // Update combat state
      setCombatState(response.combatState);
      setCombatLog(prev => [...prev, ...response.newLogEntries]);
      
      // Show damage animation if player was hit
      if (response.damageDealt && response.target === character.id) {
        setLastDamageDealt({
          [character.id]: response.damageDealt,
          timestamp: Date.now()
        });
        toast.error(`You take ${response.damageDealt} damage!`);
      }
      
    } catch (error) {
      console.error('Monster turn failed:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [combatState, character.id]);

  // useEffect hooks after all callback definitions
  useEffect(() => {
    // Initialize combat if not already started
    if (!combatState) {
      initializeCombat();
    }
  }, [combatState, initializeCombat]);

  useEffect(() => {
    // Check for combat end
    if (combatState?.outcome) {
      handleCombatEnd(combatState.outcome);
    }
  }, [combatState?.outcome, handleCombatEnd]);

  useEffect(() => {
    // Auto-process monster turns
    if (combatState?.currentTurn && 
        combatState.combatants?.[combatState.currentTurn]?.type === 'monster' &&
        combatState.is_active) {
      processMonsterTurn();
    }
  }, [combatState?.combatants, combatState?.is_active, combatState?.currentTurn, processMonsterTurn]);

  const handleAction = async (action) => {
    if (!action || isProcessing) return;
    
    // Check if we need a target
    if (action.requiresTarget && !selectedTarget) {
      toast.error('Select a target first!');
      return;
    }
    
    try {
      setIsProcessing(true);
      
      const response = await combatAPI.processAction(
        character.id,
        action,
        selectedTarget
      );
      
      // Update combat state
      setCombatState(response.combatState);
      setCombatLog(prev => [...prev, ...response.newLogEntries]);
      
      // Update character with any changes (HP, resources, etc.)
      if (response.updatedCharacter) {
        updateCharacter(response.updatedCharacter);
      }
      
      // Handle animations and feedback
      if (response.damage && selectedTarget) {
        setLastDamageDealt({
          [selectedTarget]: response.damage,
          timestamp: Date.now()
        });
        toast.success(`Hit for ${response.damage} damage!`);
      } else if (response.healing) {
        setLastHeal({
          [character.id]: response.healing,
          timestamp: Date.now()
        });
        toast.success(`Healed for ${response.healing} HP!`);
      } else if (response.miss) {
        toast.error('Attack missed!');
      }
      
      // Store the selected action for reference
      setSelectedAction(action.id);
      
      // Clear selections after a delay
      setTimeout(() => setSelectedAction(null), 1000);
      
    } catch (error) {
      console.error('Action failed:', error);
      toast.error('Action failed!');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEndTurn = async () => {
    if (isProcessing) return;
    
    try {
      setIsProcessing(true);
      const response = await combatAPI.endTurn(character.id);
      setCombatState(response.combatState);
      setCombatLog(prev => [...prev, ...response.newLogEntries]);
      
      // Clear selections for next turn
      setSelectedTarget(null);
      setSelectedAction(null);
      
    } catch (error) {
      console.error('Failed to end turn:', error);
      toast.error('Failed to end turn');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFlee = async () => {
    if (isProcessing) return;
    
    const confirmFlee = window.confirm('Flee from combat? You will lose the encounter.');
    if (!confirmFlee) return;
    
    try {
      setIsProcessing(true);
      await combatAPI.fleeCombat(character.id);
      toast.warning('You fled from combat!');
      navigate('/game', { state: { combatResult: 'fled' } });
    } catch (error) {
      console.error('Failed to flee:', error);
      toast.error('Cannot flee!');
    } finally {
      setIsProcessing(false);
    }
  };

  if (!combatState) {
    return <div className="loading">Loading combat...</div>;
  }

  const playerCombatant = combatState.combatants[character.id];
  const monsters = Object.values(combatState.combatants).filter(c => c.type === 'monster');
  const isPlayerTurn = combatState.currentTurn === character.id;

  return (
    <div className="combat-screen">
      {/* Character Info Panel - Top Left */}
      <div className="character-panel">
        <div className="character-status">
          <h3>{character.name}</h3>
          <div className="status-bars">
            <div className="hp-bar">
              <div 
                className="hp-fill"
                style={{ 
                  width: `${(playerCombatant.hp / playerCombatant.max_hp) * 100}%`,
                  backgroundColor: playerCombatant.hp < playerCombatant.max_hp * 0.3 ? '#ef4444' : '#4ade80'
                }}
              />
              <span className="hp-text">
                {playerCombatant.hp}/{playerCombatant.max_hp} HP
              </span>
            </div>
            <div className="ac-display">
              AC {playerCombatant.ac}
            </div>
          </div>
          <div className="status-conditions">
            {playerCombatant.conditions?.map(condition => (
              <span key={condition} className="condition-badge">
                {condition}
              </span>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="quick-stats-combat">
          <div className="stat-row">
            <span>STR: {character.strength} ({character.strMod >= 0 ? '+' : ''}{character.strMod})</span>
            <span>DEX: {character.dexterity} ({character.dexMod >= 0 ? '+' : ''}{character.dexMod})</span>
          </div>
          <div className="stat-row">
            <span>CON: {character.constitution} ({character.conMod >= 0 ? '+' : ''}{character.conMod})</span>
            <span>INT: {character.intelligence} ({character.intMod >= 0 ? '+' : ''}{character.intMod})</span>
          </div>
          <div className="stat-row">
            <span>WIS: {character.wisdom} ({character.wisMod >= 0 ? '+' : ''}{character.wisMod})</span>
            <span>CHA: {character.charisma} ({character.chaMod >= 0 ? '+' : ''}{character.chaMod})</span>
          </div>
        </div>

        {/* Turn Order */}
        <div className="turn-order">
          <h4>Turn Order</h4>
          <div className="turn-list">
            {combatState.turn_order.map((id, index) => {
              const combatant = combatState.combatants[id];
              return (
                <div 
                  key={id}
                  className={`turn-item ${combatState.currentTurn === id ? 'active' : ''} ${!combatant.is_alive ? 'defeated' : ''}`}
                >
                  <span className="turn-number">{index + 1}</span>
                  <span className="turn-name">{combatant.name}</span>
                  <span className="turn-initiative">{combatant.initiative}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Monster Area - Center */}
      <div className="monster-area">
        <div className="round-tracker">
          Round {combatState.round}
        </div>
        
        <div className="monsters-container">
          {monsters.map(monster => (
            <MonsterCard
              key={monster.id}
              monster={monster}
              isSelected={selectedTarget === monster.id}
              onSelect={() => setSelectedTarget(monster.id)}
              lastDamage={lastDamageDealt[monster.id]}
              disabled={!isPlayerTurn || !monster.is_alive}
            />
          ))}
        </div>

        {/* Position indicator with icons */}
        <div className="position-indicator">
          <span className={`position-badge ${playerCombatant.position}`}>
            {playerCombatant.position === 'melee' ? 'In Melee' : 'At Range'}
          </span>
          
          {/* Movement indicator */}
          <span className="movement-left">
            Movement: {combatState.movement || 30}ft
          </span>
        </div>

        {/* Action status indicators */}
        <div className="action-status">
          <div className={`action-indicator ${combatState.has_action ? 'available' : 'used'}`}>
            Action {combatState.has_action ? 'Available' : 'Used'}
          </div>
          <div className={`action-indicator ${combatState.has_bonus ? 'available' : 'used'}`}>
            Bonus Action {combatState.has_bonus ? 'Available' : 'Used'}
          </div>
          <div className={`action-indicator ${combatState.has_reaction ? 'available' : 'used'}`}>
            Reaction {combatState.has_reaction ? 'Available' : 'Used'}
          </div>
        </div>
      </div>

      {/* Combat Log - Right */}
      <CombatLog entries={combatLog} />

      {/* Action Cards - Bottom */}
      <div className="action-area">
        {isPlayerTurn ? (
          <>
            <ActionCards
              character={character}
              combatState={playerCombatant}
              selectedAction={selectedAction}
              onSelectAction={handleAction}
              disabled={isProcessing}
            />
            
            <div className="turn-controls">
              <button 
                className="btn-end-turn"
                onClick={handleEndTurn}
                disabled={isProcessing}
              >
                End Turn
              </button>
              <button 
                className="btn-flee"
                onClick={handleFlee}
                disabled={isProcessing}
              >
                Flee
              </button>
            </div>
          </>
        ) : (
          <div className="waiting-turn">
            <div className="waiting-message">
              {combatState.combatants[combatState.currentTurn]?.name}'s Turn
              {isProcessing && <div className="spinner-small" />}
            </div>
          </div>
        )}
      </div>

      {/* Damage/Heal Animations */}
      <AnimatePresence>
        {Object.entries(lastDamageDealt).map(([id, damage]) => (
          Date.now() - (damage.timestamp || 0) < 2000 && (
            <motion.div
              key={`damage-${id}-${damage.timestamp}`}
              className="floating-damage"
              initial={{ opacity: 1, y: 0 }}
              animate={{ opacity: 0, y: -50 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                fontSize: '2rem',
                color: '#ef4444',
                fontWeight: 'bold',
                pointerEvents: 'none',
                zIndex: 1000
              }}
            >
              -{damage}
            </motion.div>
          )
        ))}
        
        {Object.entries(lastHeal).map(([id, heal]) => (
          Date.now() - (heal.timestamp || 0) < 2000 && (
            <motion.div
              key={`heal-${id}-${heal.timestamp}`}
              className="floating-heal"
              initial={{ opacity: 1, y: 0 }}
              animate={{ opacity: 0, y: -50 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
              style={{
                position: 'absolute',
                top: '30%',
                left: '20%',
                fontSize: '2rem',
                color: '#4ade80',
                fontWeight: 'bold',
                pointerEvents: 'none',
                zIndex: 1000
              }}
            >
              +{heal}
            </motion.div>
          )
        ))}
      </AnimatePresence>
    </div>
  );
};

export default CombatScreen;