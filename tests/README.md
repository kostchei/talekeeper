# TaleKeeper Regression Testing Suite

**Run this after EVERY code change to ensure nothing breaks.**

## Quick Start

```bash
# Quick validation (30 seconds) - Run this after every change
python tests/run_regression_tests.py --quick

# Full test suite (2-3 minutes) - Run before commits
python tests/run_regression_tests.py --full

# Windows batch file
run_tests.bat quick
run_tests.bat full

# Unix/Linux
./run_tests.sh quick
./run_tests.sh full
```

## What Gets Tested

### Quick Tests (Always Run These)
- **Core System Validation**: Database, imports, basic data
- **Database Validation**: Schema integrity and game data
- **Action Economy**: Action/bonus action/reaction tracking

### Full Test Suite (Run Before Commits)
- All quick tests PLUS:
- **Subclass Architecture**: Character subclass system
- **Barbarian Progression**: Level 1-20 advancement
- **Spell System**: Spell registry and mechanics
- **Condition Integration**: D&D 2024 conditions
- **Character Creation**: Automated UI flow testing

## Integration with Development

### After Every Code Change
```bash
# Always run quick tests
python tests/run_regression_tests.py --quick
```

### Before Git Commits
```bash
# Run full suite to catch issues
python tests/run_regression_tests.py --full
```

### When Tests Fail
- **NEVER commit failing tests**
- Fix the issue or update the test
- Re-run to confirm fixes

## Test Structure

```
tests/
├── run_regression_tests.py    # Main test runner
├── core/                      # Core system tests
│   └── test_core_validation.py
├── services/                  # Service layer tests
├── ui/                        # UI component tests
└── integration/               # End-to-end tests
```

## Adding New Tests

1. **For new features**: Add tests in appropriate subdirectory
2. **Update the runner**: Add your test to `run_regression_tests.py`
3. **Test your test**: Ensure it passes and fails appropriately

### Example: Adding a New Feature Test

```python
# tests/services/test_my_feature.py
def test_my_new_feature():
    # Test implementation
    assert True

if __name__ == "__main__":
    test_my_new_feature()
    print("[PASS] My feature test passed")
```

Then add to `tests/run_regression_tests.py`:
```python
([sys.executable, "tests/services/test_my_feature.py"],
 "My new feature validation"),
```

## Test Categories

### Must Pass (Quick Tests)
These tests validate core functionality that MUST work:
- Database connection and schema
- Core module imports
- Basic game data loading
- Action economy enforcement

### Should Pass (Full Tests)
These tests validate complex features:
- Character progression systems
- Combat mechanics
- Spell systems
- UI automation

## Troubleshooting

### "All tests passed but feature broken"
- **Solution**: Add a specific test for your feature
- Tests only catch what they're designed to catch

### "Test passes locally but fails in regression"
- **Check**: Database state differences
- **Check**: File paths and imports
- **Check**: Test isolation issues

### "Tests too slow"
- Quick tests should complete in <30 seconds
- Move slow tests to full suite
- Consider mocking expensive operations

## Best Practices

1. **Run quick tests after every change**
2. **Run full tests before commits**
3. **Write tests for new features immediately**
4. **Keep quick tests fast (<30s total)**
5. **Fix failing tests immediately**

## Success Criteria

### Green Build ✓
```
[PASS] ALL TESTS PASSED - Code is stable
Tests: 3/3 passed
Duration: 0.4s
```

### Red Build ✗
```
[FAIL] SOME TESTS FAILED - Check output above
Tests: 2/3 passed
FAILED TESTS:
  - Core system validation
```

**Never commit on red builds.**