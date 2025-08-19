/**
 * File: frontend/src/services/api.js
 * Path: /frontend/src/services/api.js
 * 
 * API Service Layer
 * 
 * Pseudo Code:
 * 1. Configure Axios client with base URL and error handling
 * 2. Organize API calls by feature domain (character, combat, items, game)
 * 3. Handle authentication tokens and request/response interceptors
 * 4. Provide error handling with toast notifications
 * 5. Return structured data for React components to consume
 * 
 * AI Agents: This handles all backend communication.
 * Add new API endpoints here as you expand features.
 * All methods return promises and handle errors.
 */

import axios from 'axios';
import toast from 'react-hot-toast';

// Base API URL from environment or default
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for auth tokens (future feature)
api.interceptors.request.use(
  (config) => {
    // AI Agents: Add auth token here when implementing user accounts
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Don't show toast for expected errors (like validation)
    if (error.response?.status >= 500) {
      toast.error(`Server Error: ${message}`);
    }
    
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Character API
export const characterAPI = {
  /**
   * Create a new character
   * @param {Object} characterData - Character creation data
   */
  create: async (characterData) => {
    const response = await api.post('/api/character/create', characterData);
    return response.data;
  },

  /**
   * Get character by ID
   * @param {string} characterId - Character UUID
   */
  get: async (characterId) => {
    const response = await api.get(`/api/character/${characterId}`);
    return response.data;
  },

  /**
   * Update character
   * @param {string} characterId - Character UUID
   * @param {Object} updates - Fields to update
   */
  update: async (characterId, updates) => {
    const response = await api.patch(`/api/character/${characterId}`, updates);
    return response.data;
  },

  /**
   * Level up character
   * @param {string} characterId - Character UUID
   * @param {Object} choices - Level up choices (HP roll, ability increases, etc.)
   */
  levelUp: async (characterId, choices) => {
    const response = await api.post(`/api/character/${characterId}/level-up`, choices);
    return response.data;
  },

  /**
   * Get available races
   */
  getRaces: async () => {
    const response = await api.get('/api/character/races');
    return response.data;
  },

  /**
   * Get available classes
   */
  getClasses: async () => {
    const response = await api.get('/api/character/classes');
    return response.data;
  },

  /**
   * Get available backgrounds
   */
  getBackgrounds: async () => {
    const response = await api.get('/api/character/backgrounds');
    return response.data;
  },

  /**
   * Get subclasses for a class
   * @param {number} classId - Class ID
   */
  getSubclasses: async (classId) => {
    const response = await api.get(`/api/character/classes/${classId}/subclasses`);
    return response.data;
  },
};

// Combat API
export const combatAPI = {
  /**
   * Start a new combat encounter
   * @param {string} characterId - Character UUID
   * @param {Object} encounter - Encounter data with monsters
   */
  startCombat: async (characterId, encounter) => {
    const response = await api.post('/api/combat/start', {
      character_id: characterId,
      encounter: encounter
    });
    return response.data;
  },

  /**
   * Process a combat action
   * @param {string} characterId - Character UUID
   * @param {Object} action - Action to perform
   * @param {string} targetId - Target combatant ID (optional)
   */
  processAction: async (characterId, action, targetId = null) => {
    const response = await api.post('/api/combat/action', {
      character_id: characterId,
      action: action,
      target_id: targetId
    });
    return response.data;
  },

  /**
   * End current turn
   * @param {string} characterId - Character UUID
   */
  endTurn: async (characterId) => {
    const response = await api.post('/api/combat/end-turn', {
      character_id: characterId
    });
    return response.data;
  },

  /**
   * Process monster turn (AI)
   * @param {string} monsterId - Monster combatant ID
   */
  processMonsterTurn: async (monsterId) => {
    const response = await api.post('/api/combat/monster-turn', {
      monster_id: monsterId
    });
    return response.data;
  },

  /**
   * Flee from combat
   * @param {string} characterId - Character UUID
   */
  fleeCombat: async (characterId) => {
    const response = await api.post('/api/combat/flee', {
      character_id: characterId
    });
    return response.data;
  },

  /**
   * Get current combat state
   * @param {string} characterId - Character UUID
   */
  getCombatState: async (characterId) => {
    const response = await api.get(`/api/combat/state/${characterId}`);
    return response.data;
  },
};

// Game State API
export const gameAPI = {
  /**
   * Get all save slots
   */
  getSaveSlots: async () => {
    const response = await api.get('/api/game/save-slots');
    return response.data;
  },

  /**
   * Load a save slot
   * @param {number} slotNumber - Save slot number (1-10)
   */
  loadSave: async (slotNumber) => {
    const response = await api.get(`/api/game/load/${slotNumber}`);
    return response.data;
  },

  /**
   * Save game to slot
   * @param {number} slotNumber - Save slot number (1-10)
   * @param {string} characterId - Character UUID
   * @param {string} saveName - Optional save name
   * @param {boolean} overwrite - Whether to overwrite existing save
   */
  saveGame: async (slotNumber, characterId, saveName = null, overwrite = false) => {
    const response = await api.post('/api/game/save', {
      slot_number: slotNumber,
      character_id: characterId,
      save_name: saveName,
      overwrite: overwrite
    });
    return response.data;
  },

  /**
   * Delete a save slot (TODO: Not implemented in backend yet)
   * @param {number} slotNumber - Save slot number (1-10)
   */
  // deleteSave: async (slotNumber) => {
  //   const response = await api.delete(`/api/game/save/${slotNumber}`);
  //   return response.data;
  // },

  /**
   * Get next encounter
   * @param {string} characterId - Character UUID
   */
  getNextEncounter: async (characterId) => {
    const response = await api.get(`/api/game/encounter/${characterId}`);
    return response.data;
  },

  /**
   * Rest (short or long)
   * @param {string} characterId - Character UUID
   * @param {string} restType - 'short' or 'long'
   */
  rest: async (characterId, restType) => {
    const response = await api.post('/api/game/rest', {
      character_id: characterId,
      rest_type: restType
    });
    return response.data;
  },

  /**
   * Return to town
   * @param {string} characterId - Character UUID
   */
  returnToTown: async (characterId) => {
    const response = await api.post('/api/game/town', {
      character_id: characterId
    });
    return response.data;
  },
};

// Items/Inventory API
export const itemsAPI = {
  /**
   * Get character inventory
   * @param {string} characterId - Character UUID
   */
  getInventory: async (characterId) => {
    const response = await api.get(`/api/items/inventory/${characterId}`);
    return response.data;
  },

  /**
   * Equip an item
   * @param {string} characterId - Character UUID
   * @param {number} itemId - Item ID
   * @param {string} slot - Equipment slot
   */
  equipItem: async (characterId, itemId, slot) => {
    const response = await api.post('/api/items/equip', {
      character_id: characterId,
      item_id: itemId,
      slot: slot
    });
    return response.data;
  },

  /**
   * Unequip an item
   * @param {string} characterId - Character UUID
   * @param {string} slot - Equipment slot
   */
  unequipItem: async (characterId, slot) => {
    const response = await api.post('/api/items/unequip', {
      character_id: characterId,
      slot: slot
    });
    return response.data;
  },

  /**
   * Use a consumable item
   * @param {string} characterId - Character UUID
   * @param {number} itemId - Item ID
   */
  useItem: async (characterId, itemId) => {
    const response = await api.post('/api/items/use', {
      character_id: characterId,
      item_id: itemId
    });
    return response.data;
  },

  /**
   * Get shop inventory
   * @param {string} location - 'town' or dungeon level
   */
  getShopItems: async (location = 'town') => {
    const response = await api.get(`/api/items/shop/${location}`);
    return response.data;
  },

  /**
   * Buy an item from shop
   * @param {string} characterId - Character UUID
   * @param {number} itemId - Item ID
   * @param {number} quantity - Quantity to buy
   */
  buyItem: async (characterId, itemId, quantity = 1) => {
    const response = await api.post('/api/items/buy', {
      character_id: characterId,
      item_id: itemId,
      quantity: quantity
    });
    return response.data;
  },

  /**
   * Sell an item to shop
   * @param {string} characterId - Character UUID
   * @param {number} itemId - Item ID
   * @param {number} quantity - Quantity to sell
   */
  sellItem: async (characterId, itemId, quantity = 1) => {
    const response = await api.post('/api/items/sell', {
      character_id: characterId,
      item_id: itemId,
      quantity: quantity
    });
    return response.data;
  },

  /**
   * Get loot from encounter
   * @param {string} characterId - Character UUID
   * @param {Object} encounter - Completed encounter data
   */
  generateLoot: async (characterId, encounter) => {
    const response = await api.post('/api/items/loot', {
      character_id: characterId,
      encounter: encounter
    });
    return response.data;
  },
};

// Export all APIs as a combined object
const combinedAPI = {
  character: characterAPI,
  combat: combatAPI,
  game: gameAPI,
  items: itemsAPI,
  // Raw axios instance for custom requests
  raw: api
};

export default combinedAPI;