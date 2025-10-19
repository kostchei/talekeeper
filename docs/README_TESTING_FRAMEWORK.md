# TaleKeeper UI Testing Framework

**TESTING FRAMEWORK - Exclude from ongoing work**

Comprehensive PyQt6 UI automation framework for testing TaleKeeper's complex interface interactions, with specialized focus on spell action card functionality.

## Overview

This framework provides automated testing capabilities for:

- ✅ **Spell Action Cards** - Validate spell cards appear, work correctly, consume slots
- ✅ **Character Creation** - Automate full character creation including spell selection
- ✅ **Combat Interactions** - Test spell casting, action economy, concentration
- ✅ **UI Navigation** - Programmatic interaction with PyQt6 widgets
- ✅ **Test Reporting** - HTML reports with screenshots and detailed results

## Quick Start

### Test Spell Action Cards for Existing Character
```bash
# Test Nathlas's spell action cards
python testing_framework_master.py --focus spell_cards --character a32ee99b-a49f-4cf5-adc7-86edc1711922

# Quick validation test
python testing_framework_master.py --quick-spell-test
```

### Test Character Creation with Spell Selection
```bash
# Test all spellcasting classes
python testing_framework_master.py --focus character_creation --spellcasters-only

# Test specific class
python testing_framework_character_creation.py --class wizard --name TestWizard
```

### Test Combat Mechanics
```bash
# Test combat interactions
python testing_framework_master.py --focus combat --character CHARACTER_ID

# Test specific combat feature
python testing_framework_combat_interactions.py --test spell_casting
```

### Run Complete Test Suite
```bash
# Full comprehensive testing
python testing_framework_master.py --full-suite

# Create test data and run all tests
python testing_framework_master.py --setup-and-test
```

## Framework Components

### 1. Master Controller (`testing_framework_master.py`)
Central orchestrator that coordinates all testing components.

**Key Features:**
- Unified test execution interface
- Comprehensive reporting
- Test data management
- Cross-component coordination

### 2. UI Automation Core (`testing_framework_ui_automation.py`)
Base automation framework for PyQt6 interaction.

**Key Features:**
- Widget discovery and interaction
- Screenshot capture
- Wait conditions and timing
- Element visibility management

### 3. Spell Action Card Testing (`testing_framework_spell_actions.py`)
Specialized tests for spell action card functionality.

**Test Cases:**
- Spell card generation validation
- Spell slot consumption verification
- Cantrip unlimited casting
- Concentration spell handling

### 4. Character Creation Automation (`testing_framework_character_creation.py`)
Automated character creation with spell selection.

**Test Cases:**
- Complete character creation flow
- Spell selection UI validation
- Class-specific feature selection
- Database integration verification

### 5. Combat Interaction Testing (`testing_framework_combat_interactions.py`)
Combat mechanics and spell casting validation.

**Test Cases:**
- Spell casting in combat
- Action economy enforcement
- Concentration tracking
- Weapon attack mechanics
- Class feature activation

## Usage Examples

### Fix Spell Action Card Issues
```bash
# 1. Test current state
python testing_framework_master.py --quick-spell-test

# 2. Run comprehensive spell tests
python testing_framework_spell_actions.py --test-all

# 3. Validate character creation spell flow
python testing_framework_character_creation.py --validate-spells
```

### Validate New Character Creation
```bash
# Create test wizard and validate spells
python testing_framework_character_creation.py --class wizard --name ValidationWizard

# Test that created character has working spell cards
python testing_framework_spell_actions.py --character RETURNED_CHARACTER_ID
```

### Test Combat Integration
```bash
# Test spell casting mechanics in combat
python testing_framework_combat_interactions.py --test spell_casting --character CHARACTER_ID

# Test action economy
python testing_framework_combat_interactions.py --test action_economy --character CHARACTER_ID
```

## Test Data Management

### Create Test Characters
```bash
# Create test wizard with predefined spells
python testing_framework_spell_actions.py --create-test-wizard

# Clean up test characters
python testing_framework_master.py --cleanup
```

### Manual Test Data
```python
from testing_framework_spell_actions import TestDataCreator

creator = TestDataCreator()
wizard_id = creator.create_test_wizard_with_spells("TestWizard")
# Returns character ID for testing
```

## Test Scenarios

### Scenario 1: New Wizard Character
1. Create wizard character with spell selection
2. Validate cantrips and spells saved to database
3. Load character in encounter
4. Verify spell action cards appear
5. Test spell casting and slot consumption

### Scenario 2: Spell Action Card Validation
1. Find existing spellcaster character
2. Enter encounter mode
3. Validate spell cards match database spells
4. Test cantrip unlimited usage
5. Test spell slot consumption

### Scenario 3: Combat Spell Mechanics
1. Enter combat with spellcaster
2. Cast concentration spell
3. Verify concentration tracking
4. Cast conflicting concentration spell
5. Validate concentration replacement

## Configuration

### Test Settings
The framework automatically detects and adapts to:
- Available characters in database
- UI layout and widget positioning
- Screen resolution and scaling
- PyQt6 version compatibility

### Custom Test Data
```python
# Custom spell selection for testing
test_spells = [
    ('fire_bolt', 0, True, True),      # Cantrip, always prepared
    ('magic_missile', 1, True, False), # Level 1, prepared
    ('shield', 1, False, False),       # Level 1, not prepared
]
```

## Troubleshooting

### Common Issues

**"No spell cards found"**
- Character may not have spells in database
- Use `--create-test-wizard` to create known-good character
- Check character_spells table in database

**"Failed to enter encounter mode"**
- UI may not be in expected state
- Try manual navigation first
- Check for popup dialogs blocking interaction

**"Widget not found"**
- UI layout may have changed
- Update widget discovery logic
- Use screenshot analysis to debug

### Debug Mode
```bash
# Enable verbose output
python testing_framework_master.py --quick-spell-test --verbose

# Generate screenshots at each step
python testing_framework_ui_automation.py --test spell_action_cards --debug
```

## Reporting

Test results are automatically saved to:
- `testing_framework_report_TIMESTAMP.html` - Detailed test report
- `testing_framework_screenshots/` - Screenshots for each test
- Console output with real-time pass/fail status

### Report Contents
- Test execution summary
- Individual test results with timing
- Screenshots for visual verification
- Error details and stack traces
- Database state validation

## Integration with Development

### Pre-commit Testing
```bash
# Quick validation before committing spell changes
python testing_framework_master.py --quick-spell-test
```

### Regression Testing
```bash
# Full regression after major changes
python testing_framework_master.py --full-suite
```

### Feature Development
```bash
# Test specific new feature
python testing_framework_combat_interactions.py --test concentration
```

## Framework Architecture

```
testing_framework_master.py
├── testing_framework_ui_automation.py (Core UI automation)
├── testing_framework_spell_actions.py (Spell-specific tests)
├── testing_framework_character_creation.py (Creation automation)
└── testing_framework_combat_interactions.py (Combat testing)
```

Each component is self-contained and can be run independently or through the master controller.

## Contributing

When adding new tests:
1. Use the base `UIAutomationFramework` for UI interactions
2. Follow the `TestResult` pattern for consistent reporting
3. Include both positive and negative test cases
4. Add screenshot capture for visual verification
5. Update this documentation with new test scenarios

## Performance

The framework is designed for thorough testing rather than speed:
- Full suite: ~5-10 minutes
- Spell card tests: ~2-3 minutes
- Character creation: ~3-5 minutes per class
- Combat tests: ~2-4 minutes

Use `--quick-spell-test` for rapid validation during development.