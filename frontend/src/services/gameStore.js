/**
 * File: frontend/src/services/gameStore.js
 * Path: /frontend/src/services/gameStore.js
 * 
 * Global Game State Management
 * 
 * Pseudo Code:
 * 1. Create Zustand store for global game state
 * 2. Manage character data, game state, loading states
 * 3. Provide actions for updating state (setCharacter, setGameState, etc.)
 * 4. Handle persistence of game data to localStorage
 * 5. Export custom hooks for easy component access
 * 
 * AI Agents: This manages all global state. Add new state fields and actions here.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useGameStore = create(
  persist(
    (set, get) => ({
      // Character state
      character: null,
      setCharacter: (character) => set({ character }),
      updateCharacter: (updates) => set((state) => ({ 
        character: state.character ? { ...state.character, ...updates } : updates 
      })),
      
      // Game state
      gameState: null,
      setGameState: (gameState) => set({ gameState }),
      updateGameState: (updates) => set((state) => ({ 
        gameState: state.gameState ? { ...state.gameState, ...updates } : updates 
      })),
      
      // UI state
      isLoading: false,
      setLoading: (isLoading) => set({ isLoading }),
      
      // Current screen
      currentScreen: 'main-menu',
      setCurrentScreen: (screen) => set({ currentScreen: screen }),
      
      // Actions
      clearCharacter: () => set({ character: null }),
      clearGameState: () => set({ gameState: null }),
      reset: () => set({ 
        character: null, 
        gameState: null, 
        isLoading: false,
        currentScreen: 'main-menu'
      }),
    }),
    {
      name: 'talekeeper-game-storage',
      version: 1,
    }
  )
);

export { useGameStore };