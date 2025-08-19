/**
 * File: frontend/src/components/ActionCard.js
 * Path: /frontend/src/components/ActionCard.js
 * 
 * Action Cards Component
 * 
 * Pseudo Code:
 * 1. Display available combat actions as interactive cards
 * 2. Handle card flipping animations when actions are used
 * 3. Color-code cards by action type (Action/Bonus/Reaction/Movement)
 * 4. Disable cards when not player's turn or action unavailable
 * 5. Trigger action callbacks when cards are clicked
 * 
 * AI Agents: This displays available actions as cards that flip when used.
 * Cards are color-coded:
 * - Actions: Red
 * - Bonus Actions: Blue  
 * - Reactions: Yellow
 * - Movement: Green
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
// No icon dependencies - using text-based interface
import '../styles/actionCards.css';

const ActionCards = ({ character, combatState, selectedAction, onSelectAction, disabled }) => {
  const [flippedCards, setFlippedCards] = useState({});
  const [selectedCard, setSelectedCard] = useState(null);

  // Get available actions based on class and level
  const getAvailableActions = () => {
    const actions = {
      actions: [],
      bonusActions: [],
      reactions: [],
      movement: []
    };

    // Basic attack action (always available)
    if (combatState.has_action) {
      // Weapon attacks based on equipped items
      if (character.equipment?.mainHand) {
        actions.actions.push({
          id: 'main_attack',
          name: `Attack with ${character.equipment.mainHand.name}`,
          type: 'action',
          description: `${character.equipment.mainHand.damage} + ${character.strMod}`,
          requiresTarget: true,
          attack: true,
          damage: character.equipment.mainHand.damage,
          damage_bonus: character.strMod,
          damage_type: character.equipment.mainHand.damageType,
          bonus: character.proficiencyBonus + character.strMod
        });
      } else {
        // Unarmed strike
        actions.actions.push({
          id: 'unarmed',
          name: 'Unarmed Strike',
          type: 'action',
          description: `1 + ${character.strMod} bludgeoning`,
          requiresTarget: true,
          attack: true,
          damage: '1',
          damage_bonus: character.strMod,
          damage_type: 'bludgeoning',
          bonus: character.proficiencyBonus + character.strMod
        });
      }

      // Class-specific actions
      if (character.class === 'Fighter') {
        // Second Wind (once per rest)
        if (character.abilities?.secondWind?.available) {
          actions.actions.push({
            id: 'second_wind',
            name: 'Second Wind',
            type: 'action',
              description: `Heal 1d10+${character.level}`,
            requiresTarget: false,
            special: true,
            heal: `1d10+${character.level}`
          });
        }

        // Action Surge (once per rest, level 2+)
        if (character.level >= 2 && character.abilities?.actionSurge?.available) {
          actions.actions.push({
            id: 'action_surge',
            name: 'Action Surge',
            type: 'action',
              description: 'Gain an additional action this turn',
            requiresTarget: false,
            special: true
          });
        }
      }

      // Consumable items as actions
      if (character.inventory?.potions?.healing > 0) {
        actions.actions.push({
          id: 'potion_healing',
          name: 'Healing Potion',
          type: 'action',
          description: 'Heal 2d4+2 HP',
          requiresTarget: false,
          heal: '2d4+2',
          consumable: true
        });
      }
    }

    // Bonus actions
    if (combatState.has_bonus) {
      if (character.class === 'Rogue' && character.level >= 2) {
        // Cunning Action
        actions.bonusActions.push({
          id: 'cunning_dash',
          name: 'Cunning Action: Dash',
          type: 'bonus_action',
          description: 'Double your movement',
          requiresTarget: false,
          special: true,
          sub_action: 'dash'
        });

        actions.bonusActions.push({
          id: 'cunning_disengage',
          name: 'Cunning Action: Disengage',
          type: 'bonus_action',
          description: 'Move without provoking attacks',
          requiresTarget: false,
          special: true,
          sub_action: 'disengage'
        });

        actions.bonusActions.push({
          id: 'cunning_hide',
          name: 'Cunning Action: Hide',
          type: 'bonus_action',
          description: 'Attempt to hide',
          requiresTarget: false,
          special: true,
          sub_action: 'hide'
        });
      }

      // Off-hand attack if dual wielding
      if (character.equipment?.offHand?.type === 'weapon') {
        actions.bonusActions.push({
          id: 'offhand_attack',
          name: `Off-hand: ${character.equipment.offHand.name}`,
          type: 'bonus_action',
          description: `${character.equipment.offHand.damage} (no modifier)`,
          requiresTarget: true,
          attack: true,
          damage: character.equipment.offHand.damage,
          damage_bonus: 0,
          damage_type: character.equipment.offHand.damageType,
          bonus: character.proficiencyBonus + character.dexMod
        });
      }
    }

    // Reactions (available when not your turn)
    if (combatState.has_reaction) {
      actions.reactions.push({
        id: 'opportunity_attack',
        name: 'Opportunity Attack',
        type: 'reaction',
        description: 'Attack when enemy leaves your reach',
        requiresTarget: true,
        attack: true,
        trigger: 'enemy_leaves_melee'
      });
    }

    // Movement options
    if (combatState.movement > 0) {
      if (combatState.position === 'ranged') {
        actions.movement.push({
          id: 'move_melee',
          name: 'Move to Melee',
          type: 'movement',
          description: 'Engage in close combat (15ft)',
          requiresTarget: false,
          position: 'melee'
        });
      } else {
        actions.movement.push({
          id: 'move_ranged',
          name: 'Move to Range',
          type: 'movement',
          description: 'Back away from melee (15ft)',
          requiresTarget: false,
          position: 'ranged'
        });
      }
    }

    return actions;
  };

  const handleCardClick = (action) => {
    if (disabled || flippedCards[action.id]) return;

    // Flip the card
    setFlippedCards(prev => ({ ...prev, [action.id]: true }));
    setSelectedCard(action.id);

    // Execute the action
    onSelectAction(action);

    // Visual feedback - card stays flipped
    setTimeout(() => {
      // Card remains flipped to show it's been used
    }, 500);
  };

  const availableActions = getAvailableActions();

  const renderCard = (action, color) => {
    const isFlipped = flippedCards[action.id];
    const isSelected = selectedAction === action.id || selectedCard === action.id;

    return (
      <motion.div
        key={action.id}
        className={`action-card ${color} ${isFlipped ? 'flipped' : ''} ${isSelected ? 'selected' : ''}`}
        whileHover={!isFlipped && !disabled ? { scale: 1.05 } : {}}
        whileTap={!isFlipped && !disabled ? { scale: 0.95 } : {}}
        onClick={() => handleCardClick(action)}
        animate={{
          rotateY: isFlipped ? 180 : 0,
          opacity: isFlipped ? 0.5 : 1
        }}
        transition={{ duration: 0.6 }}
        style={{
          cursor: disabled || isFlipped ? 'not-allowed' : 'pointer',
          transformStyle: 'preserve-3d'
        }}
      >
        <div className="card-front">
          <div className="card-name">{action.name}</div>
          <div className="card-description">{action.description}</div>
          {action.requiresTarget && (
            <div className="card-target-indicator">Requires Target</div>
          )}
          {action.consumable && (
            <div className="card-consumable">Consumable</div>
          )}
        </div>
        <div className="card-back">
          <div className="card-used">USED</div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="action-cards-container">
      {/* Actions - Red */}
      {availableActions.actions.length > 0 && (
        <div className="card-section actions">
          <h4 className="section-title">Actions</h4>
          <div className="cards-row">
            {availableActions.actions.map(action => renderCard(action, 'red'))}
          </div>
        </div>
      )}

      {/* Bonus Actions - Blue */}
      {availableActions.bonusActions.length > 0 && (
        <div className="card-section bonus-actions">
          <h4 className="section-title">Bonus Actions</h4>
          <div className="cards-row">
            {availableActions.bonusActions.map(action => renderCard(action, 'blue'))}
          </div>
        </div>
      )}

      {/* Movement - Green */}
      {availableActions.movement.length > 0 && (
        <div className="card-section movement">
          <h4 className="section-title">Movement</h4>
          <div className="cards-row">
            {availableActions.movement.map(action => renderCard(action, 'green'))}
          </div>
        </div>
      )}

      {/* Reactions - Yellow (shown but grayed out during player turn) */}
      {availableActions.reactions.length > 0 && (
        <div className="card-section reactions">
          <h4 className="section-title">Reactions (Not Your Turn)</h4>
          <div className="cards-row">
            {availableActions.reactions.map(action => (
              <div key={action.id} className="action-card yellow disabled">
                <div className="card-front">
                  <div className="card-name">{action.name}</div>
                  <div className="card-description">{action.description}</div>
                  <div className="card-trigger">Trigger: {action.trigger}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No actions available message */}
      {!combatState.has_action && !combatState.has_bonus && combatState.movement === 0 && (
        <div className="no-actions-message">
          All actions used this turn. Click "End Turn" to continue.
        </div>
      )}
    </div>
  );
};

export default ActionCards;