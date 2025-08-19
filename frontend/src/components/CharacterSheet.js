/**
 * File: frontend/src/components/CharacterSheet.js
 * Path: /frontend/src/components/CharacterSheet.js
 * 
 * Character Ability Score Allocation Screen
 * 
 * CUSTOM ABILITY SCORE SYSTEM:
 * Phase 1 - Strategic Allocation:
 *   - Players allocate 15, 14, 13 to class primary stats + one choice
 *   - Fighter: (STR or DEX choice) + CON + one choice, minimums: WIS 6, CHA 6, INT 3
 *   - Rogue: DEX + (INT or CHA choice) + one choice, minimums: CON 6, STR 6, WIS 3
 *   - Unallocated stats default to 8
 * 
 * Phase 2 - Enhancement Rolls:
 *   - Roll 4d6 drop lowest, six times in order (STR→DEX→CON→INT→WIS→CHA)
 *   - Final ability score = MAX(allocated/minimum value, rolled value)
 *   - Rolls can only improve stats, never worsen them
 * 
 * Pseudo Code:
 * 1. Show current character basic info (name, race, class, background)
 * 2. Phase 1: Allow strategic allocation of 15, 14, 13 values based on class
 * 3. Display current allocation with minimums and defaults
 * 4. Phase 2: Roll 4d6 drop lowest for each ability in order
 * 5. Show final stats using MAX(allocated, rolled) formula
 * 6. Calculate and display derived stats (modifiers, HP, AC, etc.)
 * 7. Finalize character and proceed to game
 * 
 * AI Agents: This implements the custom two-phase ability score system.
 * Extend with skill proficiency selection and equipment assignment.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';
import { characterAPI } from '../services/api';

const CharacterSheet = () => {
  const navigate = useNavigate();
  const { character, updateCharacter } = useGameStore();
  
  // Allocation state
  const [allocations, setAllocations] = useState({
    str: 8, dex: 8, con: 8, int: 8, wis: 8, cha: 8
  });
  const [availableValues] = useState([15, 14, 13]);
  const [usedValues, setUsedValues] = useState([]);
  
  // Rolling state  
  const [rolls, setRolls] = useState(null);
  const [finalStats, setFinalStats] = useState(null);
  const [phase, setPhase] = useState(1); // 1 = allocation, 2 = rolling, 3 = final
  const [isRolling, setIsRolling] = useState(false);

  // Class-specific configurations
  const classConfigs = {
    Fighter: {
      primaryChoices: ['str', 'dex'], // Choose one
      required: ['con'], // Required second allocation
      minimums: { int: 3, wis: 6, cha: 6 }
    },
    Rogue: {
      primaryChoices: ['dex'], // Fixed primary
      secondaryChoices: ['int', 'cha'], // Choose one  
      required: [], // No additional required
      minimums: { str: 6, con: 6, wis: 3 }
    }
  };

  useEffect(() => {
    if (!character) {
      navigate('/');
      return;
    }
    
    // Set up initial allocations based on class
    initializeAllocations();
  }, [character]);

  const initializeAllocations = () => {
    const config = classConfigs[character.character_class] || classConfigs.Fighter;
    const newAllocations = { str: 8, dex: 8, con: 8, int: 8, wis: 8, cha: 8 };
    
    // Apply class minimums
    Object.entries(config.minimums).forEach(([ability, value]) => {
      newAllocations[ability] = Math.max(newAllocations[ability], value);
    });
    
    setAllocations(newAllocations);
  };

  const canAllocateValue = (ability, value) => {
    // Check if this value is already used elsewhere
    const currentlyUsedAt = Object.entries(allocations).find(([abil, val]) => 
      abil !== ability && availableValues.includes(val) && val === value
    );
    
    return !currentlyUsedAt;
  };

  const handleStatAllocation = (ability, value) => {
    if (!canAllocateValue(ability, value)) return;
    
    const oldValue = allocations[ability];
    const newAllocations = { ...allocations, [ability]: value };
    
    // Update used values tracking
    const newUsedValues = Object.values(newAllocations).filter(v => availableValues.includes(v));
    setUsedValues(newUsedValues);
    setAllocations(newAllocations);
  };

  const rollAbilityScores = async () => {
    setIsRolling(true);
    
    try {
      // Call backend to roll 4d6 drop lowest, six times
      const response = await characterAPI.rollAbilityScores('standard');
      const rolledValues = response.scores; // [STR, DEX, CON, INT, WIS, CHA]
      
      setRolls(rolledValues);
      
      // Calculate final stats: MAX(allocated, rolled)
      const abilities = ['str', 'dex', 'con', 'int', 'wis', 'cha'];
      const final = {};
      
      abilities.forEach((ability, index) => {
        final[ability] = Math.max(allocations[ability], rolledValues[index]);
      });
      
      setFinalStats(final);
      setPhase(2);
      
    } catch (error) {
      console.error('Failed to roll ability scores:', error);
      
      // Fallback: simulate rolls locally
      const simulatedRolls = Array.from({length: 6}, () => {
        const rolls = Array.from({length: 4}, () => Math.floor(Math.random() * 6) + 1);
        rolls.sort((a, b) => b - a);
        return rolls.slice(0, 3).reduce((sum, roll) => sum + roll, 0);
      });
      
      setRolls(simulatedRolls);
      
      const abilities = ['str', 'dex', 'con', 'int', 'wis', 'cha'];
      const final = {};
      abilities.forEach((ability, index) => {
        final[ability] = Math.max(allocations[ability], simulatedRolls[index]);
      });
      
      setFinalStats(final);
      setPhase(2);
    } finally {
      setIsRolling(false);
    }
  };

  const calculateModifier = (score) => Math.floor((score - 10) / 2);

  const finalizCharacter = async () => {
    try {
      const updatedCharacter = {
        ...character,
        strength: finalStats.str,
        dexterity: finalStats.dex,
        constitution: finalStats.con,
        intelligence: finalStats.int,
        wisdom: finalStats.wis,
        charisma: finalStats.cha,
        // Calculate derived stats
        hit_points: 10 + calculateModifier(finalStats.con), // Base fighter HP
        max_hit_points: 10 + calculateModifier(finalStats.con),
        armor_class: 10 + calculateModifier(finalStats.dex)
      };
      
      await characterAPI.update(character.id, updatedCharacter);
      updateCharacter(updatedCharacter);
      
      navigate('/game');
    } catch (error) {
      console.error('Failed to finalize character:', error);
      // Still proceed with local state
      updateCharacter({
        ...character,
        strength: finalStats.str,
        dexterity: finalStats.dex,
        constitution: finalStats.con,
        intelligence: finalStats.int,
        wisdom: finalStats.wis,
        charisma: finalStats.cha
      });
      navigate('/game');
    }
  };

  if (!character) {
    return <div>Loading character...</div>;
  }

  const config = classConfigs[character.character_class] || classConfigs.Fighter;
  const remainingValues = availableValues.filter(v => !usedValues.includes(v));

  return (
    <div className="character-sheet">
      <div className="sheet-container">
        <div className="character-header">
          <h1>{character.name}</h1>
          <div className="character-basics">
            <span>{character.race}</span>
            <span>{character.character_class}</span>
            <span>{character.background}</span>
          </div>
        </div>

        {phase === 1 && (
          <div className="allocation-phase">
            <h2>Phase 1: Ability Score Allocation</h2>
            <p className="phase-instructions">
              Allocate your three highest values (15, 14, 13) to your most important abilities.
              {character.character_class === 'Fighter' && 
                " Choose STR or DEX as primary, CON is required, then pick one more."
              }
              {character.character_class === 'Rogue' && 
                " DEX is your primary, choose INT or CHA as secondary, then pick one more."
              }
            </p>
            
            <div className="allocation-grid">
              {['str', 'dex', 'con', 'int', 'wis', 'cha'].map(ability => (
                <div key={ability} className="ability-row">
                  <div className="ability-name">
                    {ability.toUpperCase()}
                  </div>
                  <div className="ability-value">
                    {allocations[ability]}
                  </div>
                  <div className="ability-modifier">
                    ({calculateModifier(allocations[ability]) >= 0 ? '+' : ''}{calculateModifier(allocations[ability])})
                  </div>
                  <div className="allocation-buttons">
                    {availableValues.map(value => (
                      <button
                        key={value}
                        className={`allocation-btn ${allocations[ability] === value ? 'selected' : ''}`}
                        onClick={() => handleStatAllocation(ability, value)}
                        disabled={!canAllocateValue(ability, value) && allocations[ability] !== value}
                      >
                        {value}
                      </button>
                    ))}
                    {config.minimums[ability] && (
                      <span className="minimum-note">min: {config.minimums[ability]}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="allocation-status">
              <p>Remaining values to allocate: {remainingValues.join(', ') || 'All allocated!'}</p>
              <button 
                className="phase-btn"
                onClick={() => setPhase(1.5)}
                disabled={remainingValues.length > 0}
              >
                Proceed to Rolling
              </button>
            </div>
          </div>
        )}

        {phase === 1.5 && (
          <div className="roll-confirmation">
            <h2>Ready to Roll Enhancement Dice?</h2>
            <div className="current-allocations">
              <h3>Your Current Allocations:</h3>
              {['str', 'dex', 'con', 'int', 'wis', 'cha'].map(ability => (
                <div key={ability} className="allocation-summary">
                  {ability.toUpperCase()}: {allocations[ability]} 
                  ({calculateModifier(allocations[ability]) >= 0 ? '+' : ''}{calculateModifier(allocations[ability])})
                </div>
              ))}
            </div>
            <p>
              Now we'll roll 4d6 (drop lowest) for each ability in order. 
              Your final score will be the HIGHER of your allocated value or rolled value.
            </p>
            <button 
              className="roll-btn"
              onClick={rollAbilityScores}
              disabled={isRolling}
            >
              {isRolling ? 'Rolling...' : 'Roll Enhancement Dice!'}
            </button>
          </div>
        )}

        {phase === 2 && finalStats && (
          <div className="final-stats">
            <h2>Final Ability Scores</h2>
            <div className="stats-comparison">
              {['str', 'dex', 'con', 'int', 'wis', 'cha'].map((ability, index) => (
                <div key={ability} className="stat-comparison">
                  <div className="ability-name">{ability.toUpperCase()}</div>
                  <div className="comparison">
                    <span className="allocated">Allocated: {allocations[ability]}</span>
                    <span className="rolled">Rolled: {rolls[index]}</span>
                    <span className={`final ${finalStats[ability] > allocations[ability] ? 'improved' : ''}`}>
                      Final: {finalStats[ability]} 
                      ({calculateModifier(finalStats[ability]) >= 0 ? '+' : ''}{calculateModifier(finalStats[ability])})
                      {finalStats[ability] > allocations[ability] && ' ✓'}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="derived-stats">
              <h3>Derived Statistics</h3>
              <div className="derived-grid">
                <div>Hit Points: {10 + calculateModifier(finalStats.con)}</div>
                <div>Armor Class: {10 + calculateModifier(finalStats.dex)}</div>
                <div>Initiative: {calculateModifier(finalStats.dex) >= 0 ? '+' : ''}{calculateModifier(finalStats.dex)}</div>
                <div>Proficiency Bonus: +2</div>
              </div>
            </div>

            <button className="finalize-btn" onClick={finalizCharacter}>
              Complete Character Creation
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default CharacterSheet;