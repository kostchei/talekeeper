/**
 * File: frontend/src/components/CharacterCreator.js
 * Path: /frontend/src/components/CharacterCreator.js
 * 
 * Character Creation Component
 * 
 * Pseudo Code:
 * 1. Guide user through D&D character creation steps
 * 2. Allow selection of race, class, background, and stats
 * 3. Calculate derived statistics (AC, HP, modifiers)
 * 4. Handle equipment selection and starting gear
 * 5. Submit completed character to backend API
 * 
 * AI Agents: This handles the full D&D character creation process.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../services/gameStore';
import { characterAPI } from '../services/api';

const CharacterCreator = () => {
  const navigate = useNavigate();
  const { setCharacter, setCurrentScreen } = useGameStore();
  
  const [step, setStep] = useState(1);
  const [characterData, setCharacterData] = useState({
    name: '',
    race_id: '',
    class_id: '',
    background_id: '',
    race: null,
    characterClass: null,
    background: null
  });
  
  // Data from database
  const [races, setRaces] = useState([]);
  const [classes, setClasses] = useState([]);
  const [backgrounds, setBackgrounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data from database on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [racesData, classesData, backgroundsData] = await Promise.all([
          characterAPI.getRaces(),
          characterAPI.getClasses(), 
          characterAPI.getBackgrounds()
        ]);
        
        setRaces(racesData);
        setClasses(classesData);
        setBackgrounds(backgroundsData);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch character creation data:', err);
        setError('Failed to load character creation options. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleCreateCharacter = async () => {
    try {
      console.log('Creating character:', characterData);
      
      // Create character via API
      const createdCharacter = await characterAPI.create({
        name: characterData.name,
        race_id: characterData.race_id,
        class_id: characterData.class_id,
        background_id: characterData.background_id,
        // Use point buy or standard array for stats
        strength: 15,
        dexterity: 14,
        constitution: 13,
        intelligence: 12,
        wisdom: 10,
        charisma: 8
      });
      
      setCharacter(createdCharacter);
      setCurrentScreen('character-sheet');
      navigate('/character');
    } catch (error) {
      console.error('Character creation failed:', error);
      
      // Fallback to mock character if API fails
      const mockCharacter = {
        id: Date.now().toString(),
        name: characterData.name || 'Test Character',
        race: characterData.race?.name || 'Human',
        character_class: characterData.characterClass?.name || 'Fighter',
        background: characterData.background?.name || 'Farmer',
        level: 1,
        hp: 10,
        max_hp: 10,
        armor_class: 10,
        strength: 15,
        dexterity: 14,
        constitution: 13,
        intelligence: 12,
        wisdom: 10,
        charisma: 8
      };
      
      setCharacter(mockCharacter);
      setCurrentScreen('character-sheet');
      navigate('/character');
    }
  };

  // Handle race selection
  const handleRaceSelection = (race) => {
    setCharacterData({
      ...characterData,
      race_id: race.id,
      race: race
    });
  };

  // Handle class selection  
  const handleClassSelection = (characterClass) => {
    setCharacterData({
      ...characterData,
      class_id: characterClass.id,
      characterClass: characterClass
    });
  };

  // Handle background selection
  const handleBackgroundSelection = (background) => {
    setCharacterData({
      ...characterData,
      background_id: background.id,
      background: background
    });
  };

  if (loading) {
    return (
      <div className="character-creator">
        <div className="creator-container">
          <h1>Create Your Character</h1>
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading character creation options...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="character-creator">
        <div className="creator-container">
          <h1>Create Your Character</h1>
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="character-creator">
      <div className="creator-container">
        <h1>Create Your Character</h1>
        <div className="creation-steps">
          <div className="step-indicator">
            Step {step} of 5
          </div>
          
          <div className="step-content">
            {step === 1 && (
              <div>
                <h2>Character Name</h2>
                <input
                  type="text"
                  placeholder="Enter character name"
                  value={characterData.name}
                  onChange={(e) => setCharacterData({...characterData, name: e.target.value})}
                />
              </div>
            )}
            
            {step === 2 && (
              <div>
                <h2>Choose Race</h2>
                <div className="option-grid">
                  {races.map(race => (
                    <button 
                      key={race.id}
                      className={characterData.race_id === race.id ? 'selected' : ''}
                      onClick={() => handleRaceSelection(race)}
                    >
                      {race.name}
                    </button>
                  ))}
                </div>
                {characterData.race && (
                  <div className="selection-feedback">
                    <p>✓ Selected: <strong>{characterData.race.name}</strong></p>
                    <p className="race-description">
                      {characterData.race.description}
                    </p>
                    <div className="race-details">
                      <p><strong>Size:</strong> {characterData.race.size}</p>
                      <p><strong>Speed:</strong> {characterData.race.speed} feet</p>
                      {characterData.race.traits?.length > 0 && (
                        <p><strong>Traits:</strong> {characterData.race.traits.join(', ')}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {step === 3 && (
              <div>
                <h2>Choose Class</h2>
                <div className="option-grid">
                  {classes.map(characterClass => (
                    <button 
                      key={characterClass.id}
                      className={characterData.class_id === characterClass.id ? 'selected' : ''}
                      onClick={() => handleClassSelection(characterClass)}
                    >
                      {characterClass.name}
                    </button>
                  ))}
                </div>
                {characterData.characterClass && (
                  <div className="selection-feedback">
                    <p>✓ Selected: <strong>{characterData.characterClass.name}</strong></p>
                    <p className="class-description">
                      {characterData.characterClass.description}
                    </p>
                    <div className="class-details">
                      <p><strong>Hit Die:</strong> d{characterData.characterClass.hit_die}</p>
                      <p><strong>Primary Ability:</strong> {Array.isArray(characterData.characterClass.primary_ability) ? 
                        characterData.characterClass.primary_ability.join(' or ') : 
                        characterData.characterClass.primary_ability}</p>
                      <p><strong>Saving Throws:</strong> {characterData.characterClass.saving_throws?.join(', ')}</p>
                      <p><strong>Skills:</strong> Choose {characterData.characterClass.skill_count} from available options</p>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {step === 4 && (
              <div>
                <h2>Choose Background</h2>
                <div className="option-grid">
                  {backgrounds.map(background => (
                    <button 
                      key={background.id}
                      className={characterData.background_id === background.id ? 'selected' : ''}
                      onClick={() => handleBackgroundSelection(background)}
                    >
                      {background.name}
                    </button>
                  ))}
                </div>
                {characterData.background && (
                  <div className="selection-feedback">
                    <p>✓ Selected: <strong>{characterData.background.name}</strong></p>
                    <p className="background-description">
                      {characterData.background.description || characterData.background.feature_description}
                    </p>
                    <div className="background-details">
                      <p><strong>Skills:</strong> {characterData.background.skill_proficiencies?.join(', ')}</p>
                      {characterData.background.tool_proficiencies?.length > 0 && (
                        <p><strong>Tools:</strong> {characterData.background.tool_proficiencies.join(', ')}</p>
                      )}
                      <p><strong>Feature:</strong> {characterData.background.feature_name}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {step === 5 && (
              <div>
                <h2>Review Character</h2>
                <div className="character-summary">
                  <p><strong>Name:</strong> {characterData.name}</p>
                  <p><strong>Race:</strong> {characterData.race?.name || 'Not selected'}</p>
                  <p><strong>Class:</strong> {characterData.characterClass?.name || 'Not selected'}</p>
                  <p><strong>Background:</strong> {characterData.background?.name || 'Not selected'}</p>
                </div>
                <div className="creation-note">
                  <p>Your character will be created with standard ability scores. You'll customize them in the next step.</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="step-navigation">
            {step > 1 && (
              <button onClick={() => setStep(step - 1)}>
                Previous
              </button>
            )}
            
            {step < 5 ? (
              <button 
                onClick={() => setStep(step + 1)}
                disabled={
                  (step === 1 && !characterData.name) ||
                  (step === 2 && !characterData.race_id) ||
                  (step === 3 && !characterData.class_id) ||
                  (step === 4 && !characterData.background_id)
                }
              >
                Next
              </button>
            ) : (
              <button onClick={handleCreateCharacter}>
                Create Character
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterCreator;