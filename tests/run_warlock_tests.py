#test
"""
Warlock class test runner script.

Executes all Warlock-related tests in the correct order and generates
a comprehensive report of the test results.
"""

import sys
import subprocess
import time
from pathlib import Path

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def run_pytest_with_output(test_files, markers=None):
    """Run pytest on specific test files and return results."""
    cmd = [sys.executable, '-m', 'pytest', '-v', '--tb=short']

    if markers:
        cmd.extend(['-m', markers])

    cmd.extend(test_files)

    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def main():
    """Main test execution function."""
    print("TaleKeeper Warlock Class Test Suite")
    print("=" * 50)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    test_categories = [
        {
            'name': 'Warlock Core Features',
            'files': [
                'tests/features/test_warlock_pact_magic.py',
                'tests/features/test_warlock_invocations.py',
                'tests/features/test_warlock_pact_boons.py'
            ],
            'required': True
        },
        {
            'name': 'High-Level Features',
            'files': [
                'tests/features/test_warlock_mystic_arcanum.py',
            ],
            'required': True
        },
        {
            'name': 'Fiend Patron',
            'files': [
                'tests/features/test_warlock_fiend_patron.py'
            ],
            'required': True
        },
        {
            'name': 'Existing Service Tests',
            'files': [
                'tests/services/test_warlock_fiend.py'
            ],
            'required': False
        }
    ]

    total_categories = len(test_categories)
    passed_categories = 0
    failed_categories = []

    for i, category in enumerate(test_categories, 1):
        print(f"\n[{i}/{total_categories}] Running {category['name']} Tests")
        print("-" * 40)

        # Check if test files exist
        existing_files = []
        for test_file in category['files']:
            file_path = Path(__file__).parent.parent / test_file
            if file_path.exists():
                existing_files.append(str(file_path))
            else:
                print(f"WARNING: Test file not found: {test_file}")

        if not existing_files:
            if category['required']:
                print(f"ERROR: No test files found for required category: {category['name']}")
                failed_categories.append(category['name'])
            else:
                print(f"SKIP: No test files found for optional category: {category['name']}")
            continue

        # Run tests
        result = run_pytest_with_output(existing_files)

        if result['returncode'] == 0:
            print(f"[PASS] {category['name']}")
            passed_categories += 1
        else:
            print(f"[FAIL] {category['name']}")
            failed_categories.append(category['name'])

            # Show failure details
            if result['stdout']:
                print("STDOUT:")
                print(result['stdout'][-1000:])  # Last 1000 chars

            if result['stderr']:
                print("STDERR:")
                print(result['stderr'][-500:])   # Last 500 chars

        print()

    # Run comprehensive validation
    print(f"\n[{total_categories + 1}/{total_categories + 1}] Running Comprehensive Validation")
    print("-" * 40)

    try:
        from tests.test_warlock_comprehensive import WarlockFeatureValidator
        validator = WarlockFeatureValidator()
        validation_results = validator.validate_all_features()
        validator.save_report()
        print("[OK] Comprehensive Validation: COMPLETED")
    except Exception as e:
        print(f"[ERROR] Comprehensive Validation: {e}")
        failed_categories.append("Comprehensive Validation")

    # Final Summary
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)

    print(f"Categories Passed: {passed_categories}/{total_categories}")
    print(f"Categories Failed: {len(failed_categories)}")

    if failed_categories:
        print("\nFailed Categories:")
        for category in failed_categories:
            print(f"  - {category}")
    else:
        print("\n[SUCCESS] All test categories passed!")

    print(f"\nCompleted at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Manual testing reminder
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Review any failed tests and fix implementation issues")
    print("2. Run manual UI tests using the checklist in test_warlock_comprehensive.py")
    print("3. Test Warlock features in actual gameplay scenarios")
    print("4. Verify integration with other game systems (encounters, spellcasting, etc.)")

    # Exit with error code if any required categories failed
    required_failures = [c for c in failed_categories
                        if any(cat['name'] == c and cat.get('required', True)
                              for cat in test_categories)]

    return 0 if not required_failures else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
