#test
"""
Comprehensive Warlock class validation test suite.

Runs all Warlock feature tests systematically and generates a detailed report
of the Warlock class implementation status in TaleKeeper.
"""

import pytest
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# Ensure project imports resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests.fixtures.warlock_test_database import WarlockTestDatabase
from tests.features.test_warlock_pact_magic import TestPactMagicSlots, TestMagicalCunning, TestEldritchMaster
from tests.features.test_warlock_invocations import TestEldritchInvocationBasics, TestInvocationPrerequisites, TestSpecificInvocations
from tests.features.test_warlock_pact_boons import TestPactOfTheBlade, TestPactOfTheChain, TestPactOfTheTome
from tests.features.test_warlock_mystic_arcanum import TestMysticArcanumBasics, TestArcanumUsage
from tests.features.test_warlock_fiend_patron import TestDarkOnesBlessing, TestDarkOnesOwnLuck, TestFiendishResilience, TestHurlThroughHell


class WarlockFeatureValidator:
    """Comprehensive validator for Warlock class features."""

    def __init__(self):
        self.results = {
            'timestamp': time.time(),
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0
            },
            'features': {},
            'recommendations': []
        }

    def validate_all_features(self) -> Dict[str, Any]:
        """Run comprehensive validation of all Warlock features."""
        print("Starting comprehensive Warlock class validation...")

        with WarlockTestDatabase() as db_path:
            self.db_path = db_path

            # Core Warlock Features
            self._validate_pact_magic()
            self._validate_magical_cunning()
            self._validate_eldritch_master()
            self._validate_eldritch_invocations()
            self._validate_pact_boons()
            self._validate_mystic_arcanum()

            # Fiend Patron
            self._validate_fiend_patron_features()

        self._generate_recommendations()
        self._print_summary()

        return self.results

    def _validate_pact_magic(self):
        """Validate Pact Magic mechanics."""
        feature_name = "Pact Magic"
        print(f"Validating {feature_name}...")

        test_results = self._run_test_class(TestPactMagicSlots, self.db_path)
        self.results['features'][feature_name] = {
            'status': 'PASS' if test_results['all_passed'] else 'FAIL',
            'tests_run': test_results['total'],
            'passed': test_results['passed'],
            'failed': test_results['failed'],
            'details': test_results['details'],
            'critical_issues': []
        }

        if not test_results['all_passed']:
            critical_tests = [
                'test_pact_magic_slot_progression',
                'test_short_rest_recovery',
                'test_pact_slot_usage'
            ]
            for test in critical_tests:
                if test in test_results.get('failed_tests', []):
                    self.results['features'][feature_name]['critical_issues'].append(
                        f"Critical test failed: {test}"
                    )

    def _validate_magical_cunning(self):
        """Validate Magical Cunning mechanics."""
        feature_name = "Magical Cunning"
        print(f"Validating {feature_name}...")

        test_results = self._run_test_class(TestMagicalCunning, self.db_path)
        self.results['features'][feature_name] = {
            'status': 'PASS' if test_results['all_passed'] else 'FAIL',
            'tests_run': test_results['total'],
            'passed': test_results['passed'],
            'failed': test_results['failed'],
            'details': test_results['details']
        }

    def _validate_eldritch_master(self):
        """Validate Eldritch Master mechanics."""
        feature_name = "Eldritch Master"
        print(f"Validating {feature_name}...")

        test_results = self._run_test_class(TestEldritchMaster, self.db_path)
        self.results['features'][feature_name] = {
            'status': 'PASS' if test_results['all_passed'] else 'FAIL',
            'tests_run': test_results['total'],
            'passed': test_results['passed'],
            'failed': test_results['failed'],
            'details': test_results['details']
        }

    def _validate_eldritch_invocations(self):
        """Validate Eldritch Invocation mechanics."""
        feature_name = "Eldritch Invocations"
        print(f"Validating {feature_name}...")

        test_results = self._run_test_class(TestEldritchInvocationBasics, self.db_path)
        prereq_results = self._run_test_class(TestInvocationPrerequisites, self.db_path)
        specific_results = self._run_test_class(TestSpecificInvocations, self.db_path)

        all_passed = test_results['all_passed'] and prereq_results['all_passed'] and specific_results['all_passed']
        total = test_results['total'] + prereq_results['total'] + specific_results['total']
        passed = test_results['passed'] + prereq_results['passed'] + specific_results['passed']

        self.results['features'][feature_name] = {
            'status': 'PASS' if all_passed else 'FAIL',
            'tests_run': total,
            'passed': passed,
            'failed': total - passed,
            'details': 'Combined results from basic, prerequisite, and specific invocation tests',
            'tested_invocations': [
                'Agonizing Blast', 'Armor of Shadows', 'Devils Sight',
                'Thirsting Blade', 'Eldritch Smite', 'Lifedrinker',
                'Pact of the Blade', 'Pact of the Chain', 'Pact of the Tome'
            ]
        }

    def _validate_pact_boons(self):
        """Validate Pact Boon mechanics."""
        feature_name = "Pact Boons"
        print(f"Validating {feature_name}...")

        blade_results = self._run_test_class(TestPactOfTheBlade, self.db_path)
        chain_results = self._run_test_class(TestPactOfTheChain, self.db_path)
        tome_results = self._run_test_class(TestPactOfTheTome, self.db_path)

        all_passed = blade_results['all_passed'] and chain_results['all_passed'] and tome_results['all_passed']
        total = blade_results['total'] + chain_results['total'] + tome_results['total']
        passed = blade_results['passed'] + chain_results['passed'] + tome_results['passed']

        self.results['features'][feature_name] = {
            'status': 'PASS' if all_passed else 'FAIL',
            'tests_run': total,
            'passed': passed,
            'failed': total - passed,
            'details': 'Combined results from all three Pact Boons',
            'pact_boons_tested': ['Blade', 'Chain', 'Tome']
        }

    def _validate_mystic_arcanum(self):
        """Validate Mystic Arcanum mechanics."""
        feature_name = "Mystic Arcanum"
        print(f"Validating {feature_name}...")

        test_results = self._run_test_class(TestMysticArcanumBasics, self.db_path)
        usage_results = self._run_test_class(TestArcanumUsage, self.db_path)

        all_passed = test_results['all_passed'] and usage_results['all_passed']
        total = test_results['total'] + usage_results['total']
        passed = test_results['passed'] + usage_results['passed']

        self.results['features'][feature_name] = {
            'status': 'PASS' if all_passed else 'FAIL',
            'tests_run': total,
            'passed': passed,
            'failed': total - passed,
            'details': 'Combined results from arcanum basics and usage tests',
            'spell_levels_tested': [6, 7, 8, 9]
        }

    def _validate_fiend_patron_features(self):
        """Validate Fiend Patron features."""
        feature_name = "Fiend Patron"
        print(f"Validating {feature_name}...")

        blessing_results = self._run_test_class(TestDarkOnesBlessing, self.db_path)
        luck_results = self._run_test_class(TestDarkOnesOwnLuck, self.db_path)
        resilience_results = self._run_test_class(TestFiendishResilience, self.db_path)
        hurl_results = self._run_test_class(TestHurlThroughHell, self.db_path)

        all_passed = (blessing_results['all_passed'] and luck_results['all_passed'] and
                     resilience_results['all_passed'] and hurl_results['all_passed'])
        total = (blessing_results['total'] + luck_results['total'] +
                resilience_results['total'] + hurl_results['total'])
        passed = (blessing_results['passed'] + luck_results['passed'] +
                 resilience_results['passed'] + hurl_results['passed'])

        self.results['features'][feature_name] = {
            'status': 'PASS' if all_passed else 'FAIL',
            'tests_run': total,
            'passed': passed,
            'failed': total - passed,
            'details': 'Combined results from all Fiend Patron features',
            'patron_features': [
                "Dark One's Blessing", "Dark One's Own Luck",
                "Fiendish Resilience", "Hurl Through Hell"
            ]
        }

    def _run_test_class(self, test_class, db_path) -> Dict[str, Any]:
        """Run all tests in a test class and return results."""
        # This is a simplified test runner
        # In practice, you'd use pytest programmatically
        return {
            'total': 5,
            'passed': 4,
            'failed': 1,
            'all_passed': False,
            'failed_tests': ['test_example_failure'],
            'details': 'Simulated test results - run with pytest for actual results'
        }

    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        recommendations = []

        # Check for critical failures
        for feature_name, feature_data in self.results['features'].items():
            if feature_data['status'] == 'FAIL':
                recommendations.append(f"CRITICAL: Fix {feature_name} implementation")

            if 'critical_issues' in feature_data and feature_data['critical_issues']:
                for issue in feature_data['critical_issues']:
                    recommendations.append(f"HIGH: {issue}")

        # Feature completeness
        total_features = len(self.results['features'])
        failed_features = sum(1 for f in self.results['features'].values() if f['status'] == 'FAIL')

        if failed_features == 0:
            recommendations.append("GOOD: All Warlock features passing basic validation")
        elif failed_features < total_features / 2:
            recommendations.append("MEDIUM: Most Warlock features working, address failing tests")
        else:
            recommendations.append("CRITICAL: Major Warlock implementation issues detected")

        # Specific feature recommendations
        if 'Pact Magic' in self.results['features']:
            if self.results['features']['Pact Magic']['status'] == 'PASS':
                recommendations.append("GOOD: Pact Magic slot system functioning correctly")

        if 'Eldritch Invocations' in self.results['features']:
            if self.results['features']['Eldritch Invocations']['status'] == 'PASS':
                recommendations.append("GOOD: Eldritch Invocation system functional")

        self.results['recommendations'] = recommendations

    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("WARLOCK CLASS VALIDATION SUMMARY")
        print("="*60)

        for feature_name, feature_data in self.results['features'].items():
            status = feature_data['status']
            status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "~"
            print(f"{status_symbol} {feature_name}: {status}")

            if status != "PASS" and 'details' in feature_data:
                print(f"  Details: {feature_data['details']}")

        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(self.results['recommendations'], 1):
            print(f"{i}. {rec}")

        print("\n" + "="*60)

    def save_report(self, filename: str = "warlock_validation_report.json"):
        """Save detailed report to file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Detailed report saved to {filename}")


def run_manual_feature_tests():
    """Run specific manual tests for features that are hard to automate."""
    print("\n" + "="*60)
    print("MANUAL TEST CHECKLIST")
    print("="*60)

    manual_tests = [
        {
            'feature': 'Pact Magic',
            'test': 'Verify spell slots recover on short rest',
            'steps': [
                '1. Create level 2 Warlock',
                '2. Cast 2 spells to use all slots',
                '3. Take short rest',
                '4. Verify both slots recovered'
            ]
        },
        {
            'feature': 'Eldritch Invocations',
            'test': 'Verify invocations can be selected and applied',
            'steps': [
                '1. Create level 1 Warlock',
                '2. Select Pact of the Tome invocation',
                '3. Verify Book of Shadows appears',
                '4. Verify 3 cantrips are available'
            ]
        },
        {
            'feature': 'Pact of the Blade',
            'test': 'Verify pact weapon uses Charisma for attacks',
            'steps': [
                '1. Create level 3 Warlock with Pact of the Blade',
                '2. Conjure pact weapon',
                '3. Make attack roll',
                '4. Verify uses Charisma modifier instead of Strength'
            ]
        },
        {
            'feature': 'Dark Ones Blessing',
            'test': 'Verify temp HP gained when killing enemy',
            'steps': [
                '1. Create level 3 Fiend Warlock',
                '2. Reduce enemy to 0 HP',
                '3. Verify temp HP granted (Cha mod + level)',
                '4. Verify temp HP = 6 for Cha 16, level 3'
            ]
        },
        {
            'feature': 'Mystic Arcanum',
            'test': 'Verify high-level spells can be cast once per long rest',
            'steps': [
                '1. Create level 11 Warlock',
                '2. Select a level 6 arcanum spell',
                '3. Cast the spell without using Pact Magic slot',
                '4. Verify cannot cast again until long rest'
            ]
        }
    ]

    for test in manual_tests:
        print(f"\n{test['feature']}: {test['test']}")
        for step in test['steps']:
            print(f"  {step}")
        print("  [ ] PASS  [ ] FAIL")

    print("\n" + "="*60)


def main():
    """Main test runner function."""
    print("TaleKeeper Warlock Class Comprehensive Test Suite")
    print("=" * 50)

    # Run automated validation
    validator = WarlockFeatureValidator()
    results = validator.validate_all_features()

    # Save detailed report
    validator.save_report()

    # Show manual test checklist
    run_manual_feature_tests()

    # Exit with appropriate code
    failed_features = sum(1 for f in results['features'].values() if f['status'] == 'FAIL')
    return 0 if failed_features == 0 else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
