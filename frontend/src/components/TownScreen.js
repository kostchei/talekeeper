/**
 * File: frontend/src/components/TownScreen.js
 * Path: /frontend/src/components/TownScreen.js
 * 
 * Town Screen Component
 * 
 * Pseudo Code:
 * 1. Display town locations and available services
 * 2. Provide access to shops, taverns, and NPCs
 * 3. Handle item buying/selling transactions
 * 4. Manage quest acquisition and turn-ins
 * 5. Show character progression and training options
 * 
 * AI Agents: Town hub for shopping, quests, and character services.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';

const TownScreen = () => {
  const navigate = useNavigate();
  const { character } = useGameStore();

  const handleShop = () => {
    console.log('Shop not yet implemented');
  };

  const handleTavern = () => {
    console.log('Tavern not yet implemented');
  };

  const handleQuests = () => {
    console.log('Quest system not yet implemented');
  };

  return (
    <div className="town-screen">
      <h1>Welcome to Starter Town</h1>
      
      {character && (
        <div className="character-info">
          <p>Welcome, {character.name}!</p>
        </div>
      )}
      
      <div className="town-locations">
        <div className="location-card">
          <h3>General Store</h3>
          <p>Buy and sell equipment, weapons, and supplies</p>
          <button onClick={handleShop}>Visit Shop</button>
        </div>
        
        <div className="location-card">
          <h3>The Prancing Pony</h3>
          <p>Rest, gather information, and meet other adventurers</p>
          <button onClick={handleTavern}>Visit Tavern</button>
        </div>
        
        <div className="location-card">
          <h3>Town Hall</h3>
          <p>Find quests and contracts from local authorities</p>
          <button onClick={handleQuests}>Check Quests</button>
        </div>
        
        <div className="location-card">
          <h3>Temple</h3>
          <p>Healing services and divine magic</p>
          <button onClick={() => navigate('/rest')}>Seek Healing</button>
        </div>
      </div>
      
      <button className="back-btn" onClick={() => navigate('/game')}>
        Leave Town
      </button>
      
      <div className="placeholder">
        <p>Advanced town features coming soon: Shopping, quests, NPCs</p>
      </div>
    </div>
  );
};

export default TownScreen;