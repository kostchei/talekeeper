#!/usr/bin/env python3
"""
TaleKeeper Regression Test Suite

Run this script after EVERY code change to ensure nothing breaks.
Usage: python tests/run_regression_tests.py [--quick|--full|--verbose]
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Ensure project imports resolve
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

class RegressionTestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.results = []

    def log(self, message, force=False):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        if self.verbose or force:
            print(full_message)
        return full_message

    def run_command(self, cmd, cwd=None, description=""):
        """Run a command and capture results."""
        if cwd is None:
            cwd = self.project_root

        self.log(f"Running: {description or ' '.join(cmd)}")

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=120  # 2 minute timeout per test
            )
            duration = time.time() - start_time

            success = result.returncode == 0
            self.results.append({
                'test': description or cmd[0],
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            })

            status = "PASS" if success else "FAIL"
            self.log(f"{status} ({duration:.1f}s): {description}")

            if not success and self.verbose:
                self.log(f"STDERR: {result.stderr}")

            return success, result

        except subprocess.TimeoutExpired:
            self.log(f"TIMEOUT: {description}")
            self.results.append({
                'test': description,
                'success': False,
                'duration': 120,
                'stdout': '',
                'stderr': 'Test timed out after 120 seconds'
            })
            return False, None
        except Exception as e:
            self.log(f"ERROR: {description} - {e}")
            return False, None

    def run_quick_tests(self):
        """Run essential quick tests (< 30 seconds total)."""
        self.log("=== QUICK REGRESSION TESTS ===", force=True)

        tests = [
            # Core validation (our new test)
            ([sys.executable, "tests/core/test_core_validation.py"],
             "Core system validation"),

            # Database validation (existing)
            ([sys.executable, "test/test_simple_validation.py"],
             "Database and core validation"),

            # Action economy validation
            ([sys.executable, "test/test_action_economy_enforcement.py"],
             "Action economy system"),
        ]

        for cmd, desc in tests:
            success, _ = self.run_command(cmd, description=desc)
            if not success:
                self.log(f"CRITICAL FAILURE in quick test: {desc}", force=True)
                return False

        return True

    def run_full_tests(self):
        """Run comprehensive test suite."""
        self.log("=== FULL REGRESSION TESTS ===", force=True)

        tests = [
            # Core system tests
            ([sys.executable, "test/test_scalable_subclass_architecture.py"],
             "Subclass architecture"),

            # Character progression tests
            ([sys.executable, "test/test_barbarian_level_progression.py"],
             "Barbarian level progression"),

            # Combat system tests
            ([sys.executable, "test/test_rage_resistance.py"],
             "Barbarian rage mechanics"),

            # Integration tests
            ([sys.executable, "test/test_stage_1_4_integration.py"],
             "Condition system integration"),

            # Campaign system tests
            ([sys.executable, "test/test_campaign_frame_simple.py"],
             "Campaign frame system"),
        ]

        passed = 0
        total = len(tests)

        for cmd, desc in tests:
            success, _ = self.run_command(cmd, description=desc)
            if success:
                passed += 1

        self.log(f"Full tests: {passed}/{total} passed", force=True)
        return passed == total

    def run_tests(self, mode="quick"):
        """Run regression tests based on mode."""
        start_time = time.time()
        self.log(f"Starting {mode} regression tests...", force=True)

        # Always run quick tests first
        quick_success = self.run_quick_tests()

        if mode == "full" and quick_success:
            full_success = self.run_full_tests()
        else:
            full_success = True  # Only ran quick tests

        duration = time.time() - start_time

        # Print summary
        self.print_summary(duration, mode)

        # Return overall success
        success = quick_success and full_success
        return success

    def print_summary(self, total_duration, mode):
        """Print test results summary."""
        self.log("", force=True)
        self.log("=" * 50, force=True)
        self.log("REGRESSION TEST SUMMARY", force=True)
        self.log("=" * 50, force=True)

        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)

        self.log(f"Mode: {mode.upper()}", force=True)
        self.log(f"Tests: {passed}/{total} passed", force=True)
        self.log(f"Duration: {total_duration:.1f}s", force=True)

        if passed == total:
            self.log("[PASS] ALL TESTS PASSED - Code is stable", force=True)
        else:
            self.log("[FAIL] SOME TESTS FAILED - Check output above", force=True)

        self.log("=" * 50, force=True)

        # Show failed tests
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            self.log("FAILED TESTS:", force=True)
            for test in failed_tests:
                self.log(f"  - {test['test']}", force=True)
                if test['stderr']:
                    self.log(f"    Error: {test['stderr'][:100]}...", force=True)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="TaleKeeper Regression Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run only quick tests")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Determine mode
    if args.full:
        mode = "full"
    elif args.quick:
        mode = "quick"
    else:
        mode = "quick"  # Default to quick

    runner = RegressionTestRunner(verbose=args.verbose)
    success = runner.run_tests(mode)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()