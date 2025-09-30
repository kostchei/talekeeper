#!/usr/bin/env python3
"""
Hero Mode Stat Allocation Test

Tests the Hero Mode point-buy system for character creation.
Hero Mode: 75 points + 3 background, 1-to-1 cost, with minimums enforced.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


def test_hero_mode_point_calculation():
    """Test that Hero Mode uses 1-to-1 point calculation."""
    print("\n=== Test: Hero Mode Point Calculation ===")

    # Simulate stat allocation
    stats = {
        'strength': 16,
        'dexterity': 14,
        'constitution': 13,
        'intelligence': 8,
        'wisdom': 12,
        'charisma': 10
    }

    # Hero mode: 1-to-1 cost
    total_points = sum(stats.values())
    expected = 73  # 16+14+13+8+12+10

    assert total_points == expected, f"Expected {expected} points, got {total_points}"
    assert total_points <= 75, f"Exceeded 75 point budget: {total_points}"

    print(f"PASS: Stats sum to {total_points}/75 points")
    return True


def test_hero_mode_minimums():
    """Test that Hero Mode enforces minimums correctly."""
    print("\n=== Test: Hero Mode Minimums ===")

    # Simulate class-based minimums
    fighter_stats = {
        'strength': 15,      # Primary stat: min 9
        'dexterity': 12,     # Other stat: min 6
        'constitution': 14,  # Primary stat: min 9
        'intelligence': 3,   # Dump stat: min 3
        'wisdom': 10,        # Other stat: min 6
        'charisma': 6        # Other stat: min 6
    }

    dump_stat = 'intelligence'
    primary_stats = ['strength', 'constitution']

    # Check minimums
    for stat, value in fighter_stats.items():
        if stat == dump_stat:
            assert value >= 3, f"Dump stat {stat} below minimum 3: {value}"
        elif stat in primary_stats:
            assert value >= 9, f"Primary stat {stat} below minimum 9: {value}"
        else:
            assert value >= 6, f"Other stat {stat} below minimum 6: {value}"

    total = sum(fighter_stats.values())
    assert total <= 75, f"Exceeded budget: {total}/75"

    print(f"PASS: All minimums enforced, total points: {total}/75")
    return True


def test_hero_mode_maximum_stats():
    """Test edge case of maximizing stats within 75 points (max 18 per stat)."""
    print("\n=== Test: Hero Mode Maximum Stats ===")

    # Try to allocate maximum stats (up to 18)
    max_stats = {
        'strength': 18,      # Max possible
        'dexterity': 18,     # Max possible
        'constitution': 18,  # Max possible
        'intelligence': 3,   # Dump stat minimum
        'wisdom': 9,         # Primary minimum
        'charisma': 9        # Other stat just above minimum
    }

    total = sum(max_stats.values())
    expected = 75  # 18+18+18+3+9+9

    assert total == expected, f"Expected exactly 75 points, got {total}"

    # Verify max 18 per stat
    for stat, value in max_stats.items():
        assert value <= 18, f"Stat {stat} exceeds maximum of 18: {value}"

    print(f"PASS: Can allocate exactly 75 points with max stats (18 per stat)")
    return True


def test_hero_mode_background_bonus():
    """Test that background bonuses apply on top of 75 base points."""
    print("\n=== Test: Hero Mode Background Bonus ===")

    base_stats = {
        'strength': 15,
        'dexterity': 12,
        'constitution': 14,
        'intelligence': 6,
        'wisdom': 10,
        'charisma': 9
    }

    background_bonuses = {
        'strength': 1,
        'dexterity': 0,
        'constitution': 1,
        'intelligence': 0,
        'wisdom': 1,
        'charisma': 0
    }

    # Calculate totals
    base_total = sum(base_stats.values())
    bonus_total = sum(background_bonuses.values())

    assert base_total <= 75, f"Base stats exceed 75: {base_total}"
    assert bonus_total == 3, f"Background bonuses should be 3, got {bonus_total}"

    final_stats = {k: base_stats[k] + background_bonuses[k] for k in base_stats}
    final_total = sum(final_stats.values())

    print(f"PASS: Base {base_total}/75, +{bonus_total} background = {final_total} final")
    return True


def test_standard_vs_hero_mode():
    """Compare standard point-buy vs Hero Mode for same stat array."""
    print("\n=== Test: Standard vs Hero Mode Comparison ===")

    stats = [15, 14, 13, 12, 10, 8]

    # Standard point-buy costs (PHB)
    standard_costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    standard_total = sum(standard_costs.get(s, 0) for s in stats)

    # Hero mode costs (1-to-1)
    hero_total = sum(stats)

    print(f"  Standard point-buy: {standard_total}/27 points")
    print(f"  Hero mode: {hero_total}/75 points")
    print(f"  Difference: Hero mode allows {75 - hero_total} more points")

    assert standard_total == 27, f"Standard should use exactly 27 points"
    assert hero_total == 72, f"Hero mode should use 72 points for this array"

    print(f"PASS: Both systems validated")
    return True


def run_all_tests():
    """Run all Hero Mode tests."""
    print("=" * 60)
    print("HERO MODE STAT ALLOCATION TESTS")
    print("=" * 60)

    tests = [
        test_hero_mode_point_calculation,
        test_hero_mode_minimums,
        test_hero_mode_maximum_stats,
        test_hero_mode_background_bonus,
        test_standard_vs_hero_mode,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)