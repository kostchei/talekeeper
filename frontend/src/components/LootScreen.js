/**
 * File: frontend/src/components/LootScreen.js
 * Path: /frontend/src/components/LootScreen.js
 * 
 * Post-Combat Loot Pickup Screen
 * 
 * Pseudo Code:
 * 1. Display numbered list of available loot items
 * 2. Allow selection by number or "All Items" option
 * 3. Handle individual item pickup or mass collection
 * 4. Update character inventory with selected items
 * 5. Navigate to next screen after looting complete
 * 
 * AI Agents: Simple text-based loot interface with numbered selection.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';
import { gameAPI } from '../services/api';
import '../styles/loot.css';

const LootScreen = () => {
  const navigate = useNavigate();
  const { character, updateCharacter } = useGameStore();
  
  // Mock loot for demonstration (would come from combat result)
  const [availableLoot, setAvailableLoot] = useState([
    { id: 1, name: 'longsword', type: 'weapon', value: 15 },
    { id: 2, name: 'bag of 10 gold coins', type: 'currency', value: 10 },
    { id: 3, name: 'half eaten apple', type: 'consumable', value: 1 },
  ]);
  
  const [selectedItems, setSelectedItems] = useState([]);
  const [isLooting, setIsLooting] = useState(false);

  const handleItemSelect = (itemNumber) => {
    if (itemNumber === availableLoot.length + 1) {
      // "All Items" option
      setSelectedItems([...availableLoot]);
    } else {
      const item = availableLoot[itemNumber - 1];
      if (item && !selectedItems.find(selected => selected.id === item.id)) {
        setSelectedItems([...selectedItems, item]);
      }
    }
  };

  const handleItemRemove = (itemId) => {
    setSelectedItems(selectedItems.filter(item => item.id !== itemId));
  };

  const handleTakeLoot = async () => {
    if (selectedItems.length === 0) {
      alert('No items selected!');
      return;
    }
    
    try {
      setIsLooting(true);
      
      // Add items to character inventory
      let updatedCharacter = { ...character };
      for (const item of selectedItems) {
        const result = await gameAPI.addItemToInventory(character.id, item);
        if (result.updatedCharacter) {
          updatedCharacter = result.updatedCharacter;
        }
      }
      
      // Update character state with new inventory
      updateCharacter(updatedCharacter);
      
      // Remove taken items from available loot
      const remainingLoot = availableLoot.filter(
        loot => !selectedItems.find(selected => selected.id === loot.id)
      );
      setAvailableLoot(remainingLoot);
      
      // Clear selection
      setSelectedItems([]);
      
      alert(`Picked up ${selectedItems.length} items!`);
      
      // If no loot remains, move to next screen
      if (remainingLoot.length === 0) {
        navigate('/game');
      }
      
    } catch (error) {
      console.error('Failed to take loot:', error);
      alert('Failed to take items. Items added to inventory anyway.');
      
      // Fallback: still clear the selection
      setSelectedItems([]);
    } finally {
      setIsLooting(false);
    }
  };

  const handleSkipLoot = () => {
    const confirmSkip = window.confirm('Leave without taking any loot?');
    if (confirmSkip) {
      navigate('/game');
    }
  };

  return (
    <div className="loot-screen">
      <div className="loot-container">
        <h1>Loot Found</h1>
        <p>Items discovered after combat:</p>
        
        {/* Available Loot List */}
        <div className="loot-list">
          <h3>Available Items:</h3>
          <div className="loot-items">
            {availableLoot.map((item, index) => (
              <div key={item.id} className="loot-item">
                <button 
                  className="loot-number-btn"
                  onClick={() => handleItemSelect(index + 1)}
                  disabled={selectedItems.find(selected => selected.id === item.id)}
                >
                  {index + 1}
                </button>
                <span className="loot-name">{item.name}</span>
                <span className="loot-type">({item.type})</span>
              </div>
            ))}
            <div className="loot-item all-items">
              <button 
                className="loot-number-btn all-btn"
                onClick={() => handleItemSelect(availableLoot.length + 1)}
                disabled={selectedItems.length === availableLoot.length}
              >
                {availableLoot.length + 1}
              </button>
              <span className="loot-name">All Items</span>
            </div>
          </div>
        </div>
        
        {/* Selected Items */}
        {selectedItems.length > 0 && (
          <div className="selected-items">
            <h3>Selected for Pickup:</h3>
            <div className="selected-list">
              {selectedItems.map(item => (
                <div key={item.id} className="selected-item">
                  <span>{item.name}</span>
                  <button 
                    className="remove-btn"
                    onClick={() => handleItemRemove(item.id)}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="loot-actions">
          <button 
            className="take-loot-btn"
            onClick={handleTakeLoot}
            disabled={selectedItems.length === 0 || isLooting}
          >
            {isLooting ? 'Taking Items...' : `Take Selected Items (${selectedItems.length})`}
          </button>
          
          <button 
            className="skip-loot-btn"
            onClick={handleSkipLoot}
            disabled={isLooting}
          >
            Leave Items
          </button>
        </div>
        
        {/* Instructions */}
        <div className="loot-instructions">
          <p>Click numbers to select items, or choose "All Items" to take everything.</p>
        </div>
      </div>
    </div>
  );
};

export default LootScreen;