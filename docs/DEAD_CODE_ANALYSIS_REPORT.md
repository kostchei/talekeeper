# Dead Code and Duplication Analysis Report

## Summary

Analysis of the TaleKeeper codebase has identified several areas of dead code and duplication. A temporary system was built to mark suspected dead code with `POTENTIAL_DEAD_CODE` comments, and testing was performed to verify assumptions.

## Findings

### 1. CONFIRMED DUPLICATIONS

#### `_get_character_gold` in town_encounter.py
- **Status**: CONFIRMED DUPLICATE
- **Location**: Lines 431 and 983
- **Classes**: TrainingHallInterface and ShopInterface
- **Impact**: Exact duplicate code in same file
- **Recommendation**: Extract to a shared base class or utility function

#### `update_theme` methods
- **Status**: LIKELY DUPLICATE (110+ lines each)
- **Location**: 
  - encounter_panel.py:881-991
  - equipment_panel.py:434-556
- **Impact**: Large duplicate theme update code
- **Recommendation**: Move to base class or theme utility

### 2. POTENTIALLY DEAD CODE

#### services/dice.py functions
- **Functions**: `attack_roll`, `saving_throw`, `skill_check`
- **Status**: EXPORTED BUT UNUSED
- **Evidence**: 
  - Exported in `__all__`
  - Referenced in database schema/seeds
  - Used in test files
  - NOT used in main application code
- **Recommendation**: Keep as they appear to be part of public API

#### services/proficiency_bonus.py
- **Function**: `get_proficiency_bonus_from_character`
- **Status**: LIKELY DEAD
- **Evidence**: No usage found except in module itself
- **Recommendation**: Can be safely removed

#### ui/themes.py
- **Function**: `get_theme_names`
- **Status**: LIKELY DEAD
- **Evidence**: No usage found in codebase
- **Recommendation**: Can be safely removed

#### encounter_pane/web_form.py
- **Function**: `index`
- **Status**: FLASK ROUTE (Special Case)
- **Evidence**: Flask web route decorator
- **Recommendation**: Keep if web interface is planned, otherwise remove entire file

### 3. REDUNDANT IMPORTS

Most common redundant imports across the codebase:
- `sqlite3` - 27 files
- `json` - 23 files
- `sys` - 19 files
- `pathlib.Path` - 17 files
- `os` - 16 files

These are standard library imports and not problematic, but could be centralized for database operations.

## Verification Results

The verification system confirmed:
1. Dice functions are exported in `__all__` but never called in production code
2. Duplicate `_get_character_gold` exists in two different classes
3. Database references exist to dice functions (may be for future features)
4. Test files use some of the "dead" functions

## Recommendations

### Immediate Actions
1. **Remove duplicate `_get_character_gold`** - Extract to shared method
2. **Consolidate `update_theme` methods** - Create base theme handler
3. **Remove `get_proficiency_bonus_from_character`** - Truly unused
4. **Remove `get_theme_names`** - Truly unused

### Consider for Removal
1. **web_form.py** - Entire file if web interface not needed
2. **Dice utility functions** - If not planning to use them

### Code Organization
1. Create base classes for common UI patterns (theme updates)
2. Extract database utilities to reduce connection code duplication
3. Consider a shared inventory utility for gold/item management

## Files Modified

The following files have been marked with `POTENTIAL_DEAD_CODE` comments:
- encounter_pane/web_form.py
- services/dice.py
- services/proficiency_bonus.py
- ui/themes.py

These comments can be searched and removed once decisions are made about each piece of code.

## Testing Impact

No breaking changes were observed when running:
- Main application (`python main.py --dev`)
- Test suite (`python testing/run_tests.py`)

The marked code appears to be genuinely unused or duplicate.