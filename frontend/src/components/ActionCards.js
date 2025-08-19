/**
 * File: frontend/src/components/ActionCards.js
 * Path: /frontend/src/components/ActionCards.js
 * 
 * Action Cards Container Component
 * 
 * Pseudo Code:
 * 1. Display available combat actions as cards
 * 2. Group actions by type (Action, Bonus Action, Reaction, Movement)
 * 3. Handle action selection and execution
 * 4. Show card states (available, used, disabled)
 * 5. Integrate with character abilities and equipment
 * 
 * AI Agents: Container for all combat action cards with D&D action economy.
 */

import React from 'react';
import ActionCard from './ActionCard';

const ActionCards = ({ character, combatState, onSelectAction, disabled }) => {
  // Mock actions for now
  const mockActions = [
    {
      id: 'attack',
      name: 'Attack',
      type: 'action',
      description: 'Make a weapon attack',
      requiresTarget: true
    },
    {
      id: 'dodge',
      name: 'Dodge',
      type: 'action',
      description: 'Focus entirely on avoiding attacks'
    },
    {
      id: 'dash',
      name: 'Dash',
      type: 'action',
      description: 'Move up to your speed'
    },
    {
      id: 'second-wind',
      name: 'Second Wind',
      type: 'bonus_action',
      description: 'Regain hit points'
    }
  ];

  const actionsByType = {
    action: mockActions.filter(a => a.type === 'action'),
    bonus_action: mockActions.filter(a => a.type === 'bonus_action'),
    reaction: mockActions.filter(a => a.type === 'reaction'),
    movement: mockActions.filter(a => a.type === 'movement')
  };

  return (
    <div className="action-cards">
      <div className="action-section">
        <h4>Actions</h4>
        <div className="cards-row">
          {actionsByType.action.map(action => (
            <ActionCard
              key={action.id}
              action={action}
              onSelect={onSelectAction}
              disabled={disabled}
            />
          ))}
        </div>
      </div>
      
      {actionsByType.bonus_action.length > 0 && (
        <div className="action-section">
          <h4>Bonus Actions</h4>
          <div className="cards-row">
            {actionsByType.bonus_action.map(action => (
              <ActionCard
                key={action.id}
                action={action}
                onSelect={onSelectAction}
                disabled={disabled}
              />
            ))}
          </div>
        </div>
      )}
      
      {actionsByType.reaction.length > 0 && (
        <div className="action-section">
          <h4>Reactions</h4>
          <div className="cards-row">
            {actionsByType.reaction.map(action => (
              <ActionCard
                key={action.id}
                action={action}
                onSelect={onSelectAction}
                disabled={disabled}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionCards;