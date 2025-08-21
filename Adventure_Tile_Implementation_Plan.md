# Adventure Tile Encounter Implementation Plan

## Overview

This document outlines the implementation plan for enhancing the "Seek Adventure" tile in TaleKeeper to display and interact with monsters for combat encounters.

## Current State Analysis

### Adventure Tile Location
- **File**: `frontend/src/components/MainGameView.js:52-59`
- **Current Status**: Placeholder with basic buttons for "Random Encounter" and "Explore Safely"
- **Current Functionality**: Only logs actions, no actual encounter generation

### Encounter System Status
- **Backend**: Full encounter service implemented (`backend/services/encounter_service.py`)
- **API Endpoint**: `/random-encounter` in `backend/routers/game.py:480-559`
- **Random Bag System**: Implemented to ensure encounter variety
- **D&D 2024 Balance**: XP budgets and CR constraints properly implemented

### Monster System
- **Database**: 8+ monsters available in `database/seed_data.sql`
- **Models**: Complete monster stat blocks in `backend/models/monsters.py`
- **Available Monsters**: Cultist (CR 1/8), Cockatrice (CR 1/2), and others

### Data Folder Analysis
- **Result**: No `data` folder exists in project root
- **Backend/data**: Empty directory, not used by PostgreSQL
- **Database**: Uses PostgreSQL in Docker with initialization from `database/init.sql`

## Implementation Plan

### Phase 1: Frontend Encounter Integration (Priority: High)

#### 1.1 Update MainGameView Adventure Tile
**File**: `frontend/src/components/MainGameView.js`
**Changes**:
- Replace placeholder "Random Encounter" button with API integration
- Add monster display when encounter is generated
- Show encounter difficulty, XP value, and monster count
- Add "Accept Combat" and "Retreat" options

```javascript
// In encounter case (line 163-186), replace with:
case 'encounter':
  return <AdventureEncounterView 
    character={character}
    gameState={gameState}
    locationType={locationType}
    onActionLog={onActionLog}
    onBackToTiles={handleBackToTiles}
  />
```

#### 1.2 Create AdventureEncounterView Component
**File**: `frontend/src/components/AdventureEncounterView.js` (NEW)
**Features**:
- Generate encounter button
- Display generated monsters with stat previews
- Show encounter difficulty indicator
- Combat confirmation UI
- Monster card components

### Phase 2: Monster Display System (Priority: High)

#### 2.1 Create MonsterCard Component
**File**: `frontend/src/components/MonsterCard.js` (NEW)
**Features**:
- Monster name, image, and basic stats
- CR and XP display
- HP, AC, and attack preview
- Expandable detailed stats
- Visual threat level indicator

#### 2.2 Create MonsterDisplay Component
**File**: `frontend/src/components/MonsterDisplay.js` (NEW)
**Features**:
- Layout multiple monsters in encounter
- Group duplicate monsters
- Show total encounter XP and difficulty
- Battle-ready status indicators

### Phase 3: API Integration (Priority: High)

#### 3.1 Add Encounter API Methods
**File**: `frontend/src/services/api.js`
**New Methods**:
```javascript
// Add to gameAPI object:
generateRandomEncounter: (characterId, locationType) => 
  api.post('/random-encounter', { character_id: characterId, location_type: locationType }),

getMonsterDetails: (monsterId) => 
  api.get(`/monsters/${monsterId}`),
```

#### 3.2 Update GameStore for Encounter State
**File**: `frontend/src/services/gameStore.js`
**Add State**:
- `currentEncounter`: Store generated encounter data
- `encounterHistory`: Track recent encounters for variety

### Phase 4: Combat Integration (Priority: Medium)

#### 4.1 Combat Transition
- Store encounter data in game state
- Navigate to existing CombatScreen
- Pre-populate monsters in combat system

#### 4.2 Combat Screen Enhancement
**File**: `frontend/src/components/CombatScreen.js`
- Accept encounter data from adventure tile
- Display monsters using new MonsterCard components
- Use existing combat engine integration

### Phase 5: UI/UX Enhancements (Priority: Medium)

#### 5.1 Adventure Tile Visual Updates
- Add adventure-themed styling
- Encounter difficulty color coding
- Monster type icons and imagery
- Loading states during generation

#### 5.2 Monster Images (Optional)
**Directory**: `frontend/public/images/monsters/`
- Add default monster images
- Fallback to text-based display

### Phase 6: Advanced Features (Priority: Low)

#### 6.1 Encounter Filters
- Filter by location type (dungeon, wilderness, town)
- Difficulty preference settings
- Monster type preferences

#### 6.2 Encounter Statistics
- Track encounter history
- Monster defeat counts
- Favorite encounter types

## Technical Implementation Details

### Database Schema
- **Monsters Table**: Already complete with all necessary fields
- **Game States**: `encounter_bag_remaining` and `encounter_bag_history` for variety
- **XP Budget Table**: `encounter_xp_budgets` for balance

### API Endpoints
- **POST** `/random-encounter`: Generate balanced encounter (IMPLEMENTED)
- **GET** `/monsters/{id}`: Get monster details (NEEDS IMPLEMENTATION)
- **GET** `/game-state/{character_id}`: Current game state (IMPLEMENTED)

### Component Hierarchy
```
MainGameView
├── AdventureEncounterView (NEW)
    ├── MonsterDisplay (NEW)
    │   └── MonsterCard (NEW) x N
    ├── EncounterControls (NEW)
    └── DifficultyIndicator (NEW)
```

## File Structure Impact

### New Files to Create
1. `frontend/src/components/AdventureEncounterView.js`
2. `frontend/src/components/MonsterCard.js`
3. `frontend/src/components/MonsterDisplay.js`
4. `frontend/src/components/EncounterControls.js`
5. `frontend/src/styles/adventure.css` (optional)

### Files to Modify
1. `frontend/src/components/MainGameView.js` (encounter case)
2. `frontend/src/services/api.js` (add encounter methods)
3. `frontend/src/services/gameStore.js` (add encounter state)
4. `backend/routers/monsters.py` (add individual monster endpoint)

### Files Not Impacted
- Database schema (complete)
- Encounter service (complete)
- Combat engine (ready for integration)

## Success Metrics

### Phase 1 Complete
- [x] Adventure tile generates real encounters
- [x] Monsters display with basic info
- [x] User can accept or decline encounters

### Phase 2 Complete
- [x] Monster cards show detailed stats
- [x] Multiple monsters display properly
- [x] Encounter difficulty clearly indicated

### Phase 3 Complete
- [x] Seamless API integration
- [x] Error handling for failed encounters
- [x] Loading states during generation

## Risk Assessment

### Low Risk
- Backend encounter system is complete and tested
- Database has sufficient monster data
- API endpoints mostly exist

### Medium Risk
- UI component complexity for monster display
- State management for encounter data
- Integration with existing combat system

### High Risk
- None identified - well-defined scope with existing foundation

## Development Timeline

### Sprint 1 (Week 1)
- Implement AdventureEncounterView component
- Add basic monster display
- API integration for encounter generation

### Sprint 2 (Week 2)  
- Create detailed MonsterCard components
- Implement encounter acceptance/decline flow
- Combat system integration

### Sprint 3 (Week 3)
- UI polish and styling
- Error handling and edge cases
- Testing and optimization

## Testing Strategy

### Unit Tests
- MonsterCard component rendering
- API integration methods
- State management updates

### Integration Tests
- Adventure tile → encounter generation → combat flow
- Database query performance with monster filtering
- Random bag system variety validation

### User Experience Tests
- Encounter generation responsiveness
- Monster information clarity
- Combat transition smoothness

## Conclusion

The implementation plan leverages TaleKeeper's existing, well-architected encounter system to enhance the adventure tile with rich monster display and interaction. The modular approach ensures maintainability while the phased implementation allows for iterative development and testing.

The foundation is solid - the encounter service, monster models, and combat system are already implemented. This plan focuses on creating the user interface components to surface this functionality through the adventure tile.