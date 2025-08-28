# Equipment System Integration Plan for TaleKeeper

## Overview
This document outlines the plan to integrate equipment choices into the TaleKeeper character generation system, migrating from JSON files to IndexedDB with proper equipment selection functionality.

## Current State Analysis

### Data Flow (JSON → IndexedDB)
1. **JSON Files**: `data/equipment.json`, `data/classes.json`, `data/backgrounds.json` 
2. **Loading Process**: `core/database_indexeddb.py:372-384` calls `_load_indexeddb_equipment()` function
3. **Models**: `models/items_indexeddb.py` defines `Item`, `Equipment`, `CharacterInventory` dataclasses
4. **Game Engine**: `core/game_engine_indexeddb.py` coordinates equipment operations
5. **UI Integration**: Equipment panel exists but character creator lacks equipment choices

### Current Equipment Structure in JSON
```json
// data/equipment.json
{
  "name": "Longsword",
  "item_type": "weapon", 
  "damage_dice": "1d8",
  "damage_type": "slashing"
}

// data/classes.json (existing)
"starting_equipment": {
  "armor": "chain_mail",
  "weapons": ["longsword", "shield"],
  "equipment": ["dungeoneer_pack", "javelin_2"]
}
```

### Missing Equipment Choice System
- Classes have fixed `starting_equipment` - no choices offered
- Character creator (`ui/character_creator.py`) doesn't present equipment options
- No equipment choice validation or UI components
- Background equipment is fixed, not integrated into character inventory

## Integration Plan

### Phase 1: Data Model Enhancement

#### 1.1 Extend IndexedDB Models
**File**: `models/items_indexeddb.py`

Add equipment choice models:
```python
@dataclass
class EquipmentChoice:
    """Equipment choice options for classes/backgrounds."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""  # "Choice 1: Weapon", "Choice 2: Pack"
    class_id: Optional[str] = None
    background_id: Optional[str] = None
    choice_type: str = ""  # "weapon", "armor", "pack", "tool"
    
    # Choice options - list of item names or equipment packages
    options: List[str] = field(default_factory=list)
    max_selections: int = 1  # Usually 1, but could allow multiple
    is_required: bool = True
```

#### 1.2 Update Class/Background Models  
**File**: `models/character_indexeddb.py`

```python
@dataclass 
class Class:
    # ... existing fields ...
    equipment_choices: List[Dict[str, Any]] = field(default_factory=list)
    # Replace/supplement starting_equipment with choices
```

### Phase 2: Data Migration & Loading

#### 2.1 Update JSON Structure
**Files**: `data/classes.json`, `data/backgrounds.json`

```json
// New structure for classes.json
{
  "name": "Fighter",
  "equipment_choices": [
    {
      "name": "Primary Weapon", 
      "choice_type": "weapon",
      "options": ["longsword", "rapier", "scimitar", "battleaxe"],
      "max_selections": 1
    },
    {
      "name": "Ranged Option",
      "choice_type": "weapon", 
      "options": ["shortbow_with_arrows", "javelin_2"],
      "max_selections": 1
    }
  ],
  "guaranteed_equipment": {
    "armor": "chain_mail",
    "equipment": ["dungeoneer_pack"]
  }
}
```

#### 2.2 Update Loading Functions
**File**: `core/database_indexeddb.py`

Add new loader functions:
- `_load_indexeddb_equipment_choices()` 
- Update `_load_indexeddb_classes()` to handle equipment choices
- Create `_migrate_old_starting_equipment()` for backward compatibility

### Phase 3: Game Engine Integration

#### 3.1 Equipment Choice Logic
**File**: `core/game_engine_indexeddb.py`

Add methods:
```python
async def get_class_equipment_choices(self, class_id: str) -> List[EquipmentChoice]:
    """Get equipment choices for a class."""

async def get_background_equipment(self, background_id: str) -> List[Item]:
    """Get guaranteed equipment for a background."""

async def apply_equipment_choices(self, character: Character, 
                                 choices: Dict[str, List[str]]) -> None:
    """Apply selected equipment choices to character inventory."""
```

#### 3.2 Character Creation Flow
Update character creation to:
1. Load equipment choices for selected class
2. Present choices to user in UI
3. Validate selections (all required choices made)
4. Create `CharacterInventory` records for chosen items
5. Auto-add background equipment to inventory

### Phase 4: UI Enhancement

#### 4.1 Character Creator Updates
**File**: `ui/character_creator.py`

Add new step or expand existing steps:
- Equipment choice selection widgets (radio buttons, dropdowns)
- Choice validation before allowing progression
- Equipment preview/comparison functionality
- Integration with existing step workflow

#### 4.2 Equipment Choice Widgets
Create new widget components:
```python
class EquipmentChoiceWidget(QWidget):
    """Widget for selecting from equipment options."""
    
class EquipmentPreviewWidget(QWidget):
    """Widget for previewing selected equipment stats."""
```

### Phase 5: Data Population Strategy

#### 5.1 Equipment Database Seeding
**Approach**: Extend existing JSON loading process
- Update `data/equipment.json` with comprehensive D&D equipment
- Ensure all equipment referenced in choices exists
- Add equipment categories/tags for better organization

#### 5.2 Class Equipment Choices Data
**Delivery Method**: JSON paste into chat for each class
- 2 choices per class as requested
- Reference existing equipment names
- Validate against equipment database

**Example Format**:
```json
{
  "Fighter": {
    "choice_1": {
      "name": "Martial Weapon",
      "options": ["longsword", "battleaxe", "rapier", "greatsword"]
    },
    "choice_2": {
      "name": "Ranged Weapon", 
      "options": ["shortbow", "light_crossbow", "javelin_5"]
    }
  }
}
```

### Phase 6: Background Equipment Integration

#### 6.1 Automatic Equipment Grant
- Background equipment automatically added to character inventory
- No choices needed - as specified in requirements
- Equipment granted during character creation process

#### 6.2 Background Equipment Data
**Files**: `data/backgrounds.json`
- Maintain existing `starting_equipment` structure  
- Ensure equipment exists in equipment database
- Auto-create inventory records during character creation

## Implementation Order

### Priority 1: Core Infrastructure
1. Update `models/items_indexeddb.py` with choice models
2. Update loading functions in `core/database_indexeddb.py`
3. Add equipment choice methods to `core/game_engine_indexeddb.py`

### Priority 2: Data Integration  
1. Design new JSON structure for classes/backgrounds
2. Update JSON loading to handle equipment choices
3. Create data migration utilities

### Priority 3: UI Integration
1. Add equipment choice step to character creator
2. Create equipment selection widgets
3. Integrate with existing character creation flow

### Priority 4: Data Population
1. Expand equipment database with comprehensive items
2. Define equipment choices for all classes (via JSON input)
3. Update background equipment data

## Technical Considerations

### Data Consistency
- Equipment names must match between choices and equipment database
- Validation during JSON loading to catch missing items
- Migration path for existing characters with old equipment system

### Performance
- Cache equipment choices in game engine for fast access
- Index equipment by type/category for efficient filtering
- Lazy load equipment details only when needed

### User Experience
- Clear equipment choice presentation with stats/descriptions
- Validation feedback for incomplete selections
- Equipment comparison functionality for informed choices

### Error Handling
- Graceful handling of missing equipment references
- Fallback options for invalid equipment choices
- Clear error messages for validation failures

## Testing Strategy

### Unit Tests
- Equipment choice loading from JSON
- Character inventory creation with choices
- Validation of equipment selections

### Integration Tests  
- Full character creation with equipment choices
- Equipment choice persistence in IndexedDB
- Background equipment auto-granting

### UI Tests
- Equipment choice widget functionality
- Character creator flow with equipment step
- Equipment selection validation

## Migration Path

### Backward Compatibility
- Support both old `starting_equipment` and new `equipment_choices` 
- Migrate existing characters gradually
- Maintain fallback options for missing equipment

### Data Migration
- Convert old starting equipment to inventory records
- Create default choices for classes without equipment choices defined
- Preserve existing character equipment

This plan provides a comprehensive roadmap for integrating equipment choices into TaleKeeper's character generation system while maintaining compatibility with the existing IndexedDB architecture.