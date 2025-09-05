# TaleKeeper Testing Framework

Comprehensive testing system for TaleKeeper using Qt6's native testing capabilities.

## Features

### 🎯 Core Testing Framework
- **Widget Discovery**: Automatically find and interact with UI elements
- **Screenshot Capture**: Visual verification of UI states
- **Event Simulation**: Click, type, drag operations
- **State Validation**: Check widget properties and data

### 🗡️ Game-Specific Testing
- **Fighting Styles**: Test all D&D fighting style implementations
- **Character Creation**: Validate character creation flow
- **Combat Mechanics**: Test attack rolls, damage calculations
- **Equipment System**: Verify equipment effects on stats
- **Action Cards**: Test combat action availability and effects
- **Feats & Features**: Validate feat implementations

## Quick Start

### Basic Usage

```bash
# Run all tests
python testing/run_tests.py

# Run specific feature tests (fighting styles, feats, etc.)
python testing/run_tests.py --mode specific

# Interactive mode with visual feedback
python testing/run_tests.py --mode interactive

# Visual debugging mode
python testing/run_tests.py --mode visual
```

## Test Structure

### 1. Base Framework (`test_framework.py`)

The foundation provides:
- `TaleKeeperTestBase`: Base class for all tests
- Widget interaction methods
- Screenshot capabilities
- Result recording and reporting

### 2. Specific Features (`test_specific_features.py`)

Focused testing for:
- Fighting Styles (Defense, Dueling, Great Weapon Fighting, etc.)
- Feats (Tough, Alert, etc.)
- Combat mechanics
- Level progression
- Weapon masteries

### 3. Test Runner (`run_tests.py`)

Main entry point with modes:
- **Full**: Run complete test suite
- **Specific**: Test specific game features
- **Interactive**: Step-through testing with pauses
- **Visual**: Enhanced visual debugging

## Writing New Tests

### Example Test Class

```python
from test_framework import TaleKeeperTestBase

class MyFeatureTester(TaleKeeperTestBase):
    def __init__(self):
        super().__init__("MyFeature")
    
    def test_feature_behavior(self):
        try:
            # Find widget
            widget = self.find_widget_by_name("myWidget")
            
            # Interact with it
            self.click_widget(widget)
            
            # Verify result
            success = self.wait_for_condition(
                lambda: widget.text() == "Expected"
            )
            
            # Record result
            self.record_result("feature_test", success, 
                             "Feature behaved as expected")
            
            return success
            
        except Exception as e:
            self.record_result("feature_test", False, 
                             f"Error: {str(e)}", error=e)
            return False
```

## Test Reports

Tests generate:
- **HTML Report**: `testing/test_report.html`
- **Screenshots**: `testing/screenshots/`
- **Console Output**: Real-time test results

### HTML Report Features
- Test summary with pass/fail counts
- Individual test results with messages
- Screenshot links for visual verification
- Error details for failed tests

## Fighting Style Testing

The framework specifically tests D&D fighting styles:

### Defense
- ✅ +1 AC when wearing armor
- ✅ No bonus without armor

### Dueling
- ✅ +2 damage with one-handed weapon
- ✅ No off-hand weapon equipped
- ✅ No bonus with two-handed weapons

### Great Weapon Fighting
- ✅ Reroll 1s and 2s on damage dice
- ✅ Two-handed weapons only

### Two-Weapon Fighting
- ✅ Add ability modifier to off-hand damage
- ✅ Light weapons in both hands

### Archery
- ✅ +2 to attack rolls with ranged weapons
- ✅ Bows and crossbows only

### Protection
- ✅ Impose disadvantage on attacks against allies
- ✅ Requires shield

## Debugging Failed Tests

### 1. Check Screenshots
Screenshots are automatically taken for failed tests:
```
testing/screenshots/TestName_fail_timestamp.png
```

### 2. Use Interactive Mode
Step through tests manually:
```bash
python testing/run_tests.py --mode interactive
```

### 3. Visual Debug Mode
Highlights UI elements during testing:
```bash
python testing/run_tests.py --mode visual
```

### 4. Check Error Details
HTML report includes full stack traces for errors.

## Common Issues & Solutions

### Issue: Widget Not Found
```python
# Use multiple search methods
widget = self.find_widget_by_name("widgetName")
if not widget:
    widget = self.find_widget_by_text("Widget Text")
if not widget:
    widgets = self.find_widgets_by_type(QPushButton)
    widget = widgets[0] if widgets else None
```

### Issue: Timing Problems
```python
# Wait for conditions
success = self.wait_for_condition(
    lambda: widget.isEnabled(),
    timeout_ms=5000
)
```

### Issue: Screenshot Quality
```python
# Take multiple screenshots
self.take_screenshot("before_action")
self.click_widget(widget)
QTest.qWait(500)  # Wait for animation
self.take_screenshot("after_action")
```

## Test Coverage

Current test coverage includes:

### ✅ Implemented
- Character sheet display
- Equipment panel
- Action cards display
- Fighting style mechanics
- Basic combat calculations

### 🚧 In Progress
- Spell system testing
- Monster AI testing
- Save/load functionality
- Network multiplayer (if applicable)

### 📝 Planned
- Performance testing
- Memory leak detection
- Stress testing (many monsters)
- Edge case handling

## Performance Considerations

- Tests run in ~30-60 seconds for full suite
- Screenshots add ~100ms per capture
- Interactive mode allows manual inspection
- Visual mode adds highlighting delays

## Contributing

To add new tests:
1. Create test class inheriting from `TaleKeeperTestBase`
2. Implement `test_*` methods
3. Add to appropriate test suite
4. Document expected behavior
5. Include error handling

## Requirements

- Python 3.8+
- PyQt6
- TaleKeeper application
- 100MB disk space for screenshots

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Test TaleKeeper
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python testing/run_tests.py
      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v2
        with:
          name: test-screenshots
          path: testing/screenshots/
```

## Support

For issues or questions:
- Check existing test implementations
- Review HTML test reports
- Use visual debug mode
- Add detailed logging in tests