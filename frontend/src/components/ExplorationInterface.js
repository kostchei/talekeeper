/**
 * File: frontend/src/components/ExplorationInterface.js
 * Path: /frontend/src/components/ExplorationInterface.js
 * 
 * Exploration Interface Component - Core game interaction hub
 * 
 * Pseudo Code:
 * 1. Display location-specific actions based on current area type
 * 2. Handle action requirements and cooldowns
 * 3. Integrate with encounter generation API
 * 4. Provide visual feedback for action results
 * 5. Navigate to appropriate screens based on action selection
 * 
 * AI Agents: This is the main interaction point between combat encounters.
 * Provides context-sensitive actions and handles the exploration loop.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { gameAPI } from '../services/api';
import { useGameStore } from '../services/gameStore';

const ExplorationInterface = ({ 
  currentLocation = "Starting Town",
  locationType = "town",
  character,
  gameState,
  onLocationChange
}) => {
  const navigate = useNavigate();
  const { updateGameState } = useGameStore();
  
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [recentAction, setRecentAction] = useState(null);
  const [actionCooldowns, setActionCooldowns] = useState({});
  const [encounterPreview, setEncounterPreview] = useState(null);

  // Location-based available actions
  const getActionsForLocation = (locationType) => {
    const actionMap = {
      town: [
        {
          id: 'shop',
          name: 'Visit Shop',
          description: 'Browse and purchase equipment',
          icon: '🏪',
          requiresGold: false,
          cooldown: 0
        },
        {
          id: 'inn',
          name: 'Rest at Inn',
          description: 'Take a long rest and recover fully',
          icon: '🛌',
          requiresGold: true,
          goldCost: 5,
          cooldown: 0
        },
        {
          id: 'information',
          name: 'Gather Information',
          description: 'Listen for rumors and quest hooks',
          icon: '👂',
          requiresGold: false,
          cooldown: 300000 // 5 minutes
        },
        {
          id: 'dungeon',
          name: 'Enter Dungeon',
          description: 'Begin dungeon exploration',
          icon: '🏰',
          requiresGold: false,
          cooldown: 0
        }
      ],
      dungeon: [
        {
          id: 'explore',
          name: 'Explore Room',
          description: 'Search the current area for encounters',
          icon: '🔍',
          requiresGold: false,
          cooldown: 0
        },
        {
          id: 'search',
          name: 'Search for Treasure',
          description: 'Carefully look for hidden items',
          icon: '💎',
          requiresGold: false,
          cooldown: 60000 // 1 minute
        },
        {
          id: 'listen',
          name: 'Listen at Door',
          description: 'Try to detect what lies ahead',
          icon: '👂',
          requiresGold: false,
          cooldown: 30000 // 30 seconds
        },
        {
          id: 'rest',
          name: 'Short Rest',
          description: 'Rest briefly to recover some resources',
          icon: '⏸️',
          requiresGold: false,
          cooldown: 0
        },
        {
          id: 'leave',
          name: 'Exit Dungeon',
          description: 'Return to town safely',
          icon: '🚪',
          requiresGold: false,
          cooldown: 0
        }
      ],
      wilderness: [
        {
          id: 'travel',
          name: 'Travel',
          description: 'Move to a new location',
          icon: '🥾',
          requiresGold: false,
          cooldown: 0
        },
        {
          id: 'camp',
          name: 'Make Camp',
          description: 'Set up camp for a long rest',
          icon: '🏕️',
          requiresGold: false,
          cooldown: 0
        },
        {
          id: 'forage',
          name: 'Forage',
          description: 'Search for food and supplies',
          icon: '🌿',
          requiresGold: false,
          cooldown: 120000 // 2 minutes
        },
        {
          id: 'encounter',
          name: 'Seek Adventure',
          description: 'Actively look for encounters',
          icon: '⚔️',
          requiresGold: false,
          cooldown: 0
        }
      ]
    };

    return actionMap[locationType] || actionMap.town;
  };

  const availableActions = getActionsForLocation(locationType);

  // Check if character can perform an action
  const canPerformAction = (action) => {
    if (isLoading) return false;
    
    // Check cooldowns
    if (actionCooldowns[action.id] && Date.now() < actionCooldowns[action.id]) {
      return false;
    }
    
    // Check gold requirements
    if (action.requiresGold && gameState?.inventory_gold < (action.goldCost || 0)) {
      return false;
    }
    
    // Check character state
    if (!character) return false;
    
    return true;
  };

  // Get cooldown remaining time in seconds
  const getCooldownRemaining = (action) => {
    if (!actionCooldowns[action.id]) return 0;
    const remaining = actionCooldowns[action.id] - Date.now();
    return Math.max(0, Math.ceil(remaining / 1000));
  };

  // Handle action selection
  const handleActionSelect = async (action) => {
    if (!canPerformAction(action)) {
      if (action.requiresGold && gameState?.inventory_gold < (action.goldCost || 0)) {
        toast.error(`Need ${action.goldCost} gold for this action`);
      } else if (getCooldownRemaining(action) > 0) {
        toast.error(`Action on cooldown (${getCooldownRemaining(action)}s remaining)`);
      }
      return;
    }

    setSelectedAction(action);
    setIsLoading(true);

    try {
      await processAction(action);
    } catch (error) {
      console.error('Action failed:', error);
      toast.error('Action failed. Please try again.');
    } finally {
      setIsLoading(false);
      setSelectedAction(null);
    }
  };

  // Process the selected action
  const processAction = async (action) => {
    switch (action.id) {
      case 'shop':
        navigate('/town');
        break;
        
      case 'inn':
      case 'camp':
      case 'rest':
        navigate('/rest');
        break;
        
      case 'dungeon':
        // Enter dungeon - change location
        if (onLocationChange) {
          onLocationChange('dungeon', 'Ancient Ruins');
        }
        toast.success('Entered the Ancient Ruins');
        setRecentAction({ 
          action: action.name, 
          result: 'You step into the shadowy depths of ancient stone corridors.' 
        });
        break;
        
      case 'leave':
        // Exit dungeon - return to town
        if (onLocationChange) {
          onLocationChange('town', 'Starting Town');
        }
        toast.success('Returned to town safely');
        setRecentAction({ 
          action: action.name, 
          result: 'You emerge from the dungeon back into the safety of town.' 
        });
        break;
        
      case 'explore':
      case 'encounter':
        // Generate encounter
        await handleEncounterGeneration();
        break;
        
      case 'search':
        await handleTreasureSearch();
        break;
        
      case 'listen':
        await handleListenAtDoor();
        break;
        
      case 'information':
        await handleGatherInformation();
        break;
        
      case 'forage':
        await handleForage();
        break;
        
      case 'travel':
        // TODO: Implement location selection
        toast.info('Travel system coming soon');
        break;
        
      default:
        toast.info(`${action.name} not yet implemented`);
    }

    // Set cooldown
    if (action.cooldown > 0) {
      setActionCooldowns(prev => ({
        ...prev,
        [action.id]: Date.now() + action.cooldown
      }));
    }
  };

  // Handle encounter generation
  const handleEncounterGeneration = async () => {
    try {
      const encounterData = await gameAPI.generateRandomEncounter(
        character.id,
        locationType
      );
      
      if (encounterData.type === 'combat') {
        setEncounterPreview(encounterData);
      } else if (encounterData.type === 'treasure') {
        toast.success(`Found treasure: ${encounterData.gold_found} gold!`);
        setRecentAction({
          action: 'Explore',
          result: `You discovered ${encounterData.gold_found} gold pieces hidden away.`
        });
        // Update gold in game state
        if (updateGameState) {
          updateGameState(prev => ({
            ...prev,
            inventory_gold: (prev.inventory_gold || 0) + encounterData.gold_found
          }));
        }
      } else if (encounterData.type === 'event') {
        toast.info('Special event discovered!');
        setRecentAction({
          action: 'Explore',
          result: encounterData.message
        });
      }
    } catch (error) {
      console.error('Encounter generation failed:', error);
      toast.error('Failed to generate encounter');
    }
  };

  // Handle treasure searching
  const handleTreasureSearch = async () => {
    // Simple treasure roll
    const treasureRoll = Math.random();
    if (treasureRoll < 0.3) { // 30% chance
      const goldFound = Math.floor(Math.random() * 20) + 5;
      toast.success(`Found ${goldFound} gold!`);
      setRecentAction({
        action: 'Search for Treasure',
        result: `Your careful search reveals ${goldFound} gold pieces.`
      });
      
      if (updateGameState) {
        updateGameState(prev => ({
          ...prev,
          inventory_gold: (prev.inventory_gold || 0) + goldFound
        }));
      }
    } else {
      toast.info('No treasure found this time.');
      setRecentAction({
        action: 'Search for Treasure',
        result: 'Despite your careful search, you find nothing of value.'
      });
    }
  };

  // Handle listening at door
  const handleListenAtDoor = async () => {
    const sounds = [
      'You hear the shuffling of feet beyond the door.',
      'Strange chittering sounds echo from within.',
      'All is quiet... perhaps too quiet.',
      'You detect the sound of dripping water.',
      'Low growls can be heard in the distance.'
    ];
    
    const randomSound = sounds[Math.floor(Math.random() * sounds.length)];
    toast.info('You listen carefully...');
    setRecentAction({
      action: 'Listen at Door',
      result: randomSound
    });
  };

  // Handle information gathering
  const handleGatherInformation = async () => {
    const rumors = [
      'Strange lights have been seen in the old ruins to the north.',
      'A merchant caravan went missing on the eastern road.',
      'The local lord is offering a reward for clearing out the goblin caves.',
      'An ancient treasure is said to be hidden in the haunted mansion.',
      'Travelers report seeing a dragon flying over the mountain peaks.'
    ];
    
    const randomRumor = rumors[Math.floor(Math.random() * rumors.length)];
    toast.success('You overhear some interesting information...');
    setRecentAction({
      action: 'Gather Information',
      result: `A local tells you: "${randomRumor}"`
    });
  };

  // Handle foraging
  const handleForage = async () => {
    const forageRoll = Math.random();
    if (forageRoll < 0.4) { // 40% success
      const foodFound = Math.floor(Math.random() * 3) + 1;
      toast.success(`Found ${foodFound} day${foodFound > 1 ? 's' : ''} of rations!`);
      setRecentAction({
        action: 'Forage',
        result: `You successfully forage ${foodFound} day${foodFound > 1 ? 's' : ''} worth of food.`
      });
    } else {
      toast.info('Foraging attempt unsuccessful.');
      setRecentAction({
        action: 'Forage',
        result: 'You search for food but find nothing edible.'
      });
    }
  };

  // Handle encounter preview acceptance
  const handleAcceptEncounter = () => {
    if (encounterPreview) {
      // Store encounter data for combat screen
      updateGameState(prev => ({
        ...prev,
        currentEncounter: encounterPreview
      }));
      navigate('/combat');
    }
  };

  // Handle encounter decline
  const handleDeclineEncounter = () => {
    setEncounterPreview(null);
    toast.info('You decide to avoid the encounter for now.');
    setRecentAction({
      action: 'Avoid Encounter',
      result: 'You quietly retreat and avoid potential danger.'
    });
  };

  return (
    <div className="exploration-interface">
      {/* Location Header */}
      <div className="location-header">
        <h2 className="location-name">{currentLocation}</h2>
        <p className="location-type">{locationType.charAt(0).toUpperCase() + locationType.slice(1)}</p>
      </div>

      {/* Action Grid */}
      <div className="action-grid">
        {availableActions.map((action) => {
          const canAct = canPerformAction(action);
          const cooldownRemaining = getCooldownRemaining(action);
          const isSelected = selectedAction?.id === action.id;
          
          return (
            <motion.button
              key={action.id}
              className={`exploration-action ${!canAct ? 'disabled' : ''} ${isSelected ? 'loading' : ''}`}
              onClick={() => handleActionSelect(action)}
              disabled={!canAct || isLoading}
              whileHover={canAct ? { scale: 1.05 } : {}}
              whileTap={canAct ? { scale: 0.95 } : {}}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="action-icon">{action.icon}</div>
              <div className="action-content">
                <h3 className="action-name">{action.name}</h3>
                <p className="action-description">{action.description}</p>
                {action.requiresGold && (
                  <p className="action-cost">Cost: {action.goldCost} gold</p>
                )}
                {cooldownRemaining > 0 && (
                  <p className="action-cooldown">Cooldown: {cooldownRemaining}s</p>
                )}
              </div>
              {isSelected && (
                <div className="action-loading">
                  <div className="loading-spinner" />
                </div>
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Recent Action Feedback */}
      <AnimatePresence>
        {recentAction && (
          <motion.div
            className="action-feedback"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <h4>Recent Action: {recentAction.action}</h4>
            <p>{recentAction.result}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Encounter Preview Modal */}
      <AnimatePresence>
        {encounterPreview && (
          <motion.div
            className="encounter-preview-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleDeclineEncounter}
          >
            <motion.div
              className="encounter-preview"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3>Encounter Ahead!</h3>
              <div className="encounter-info">
                <p className="encounter-difficulty">
                  Difficulty: <span className={`difficulty-${encounterPreview.difficulty}`}>
                    {encounterPreview.difficulty.toUpperCase()}
                  </span>
                </p>
                <p className="encounter-xp">Expected XP: {encounterPreview.total_xp}</p>
                <p className="encounter-monsters">
                  {encounterPreview.monsters.length} monster{encounterPreview.monsters.length !== 1 ? 's' : ''}
                </p>
              </div>
              <div className="encounter-actions">
                <button 
                  className="btn-danger"
                  onClick={handleAcceptEncounter}
                >
                  Enter Combat
                </button>
                <button 
                  className="btn-secondary"
                  onClick={handleDeclineEncounter}
                >
                  Retreat
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ExplorationInterface;