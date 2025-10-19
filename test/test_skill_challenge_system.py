# test
import sys
import os
import sqlite3
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.skill_challenge_manager import SkillChallengeManager, SkillChallengeTemplate
from services.skill_challenge_rewards import SkillChallengeRewards


def test_skill_challenge_database():
    """Test that skill challenge templates are loaded from database."""
    print("Testing skill challenge database integration...")

    manager = SkillChallengeManager()
    templates = manager.get_all_templates()

    print(f"Found {len(templates)} skill challenge templates")

    if templates:
        # Test a specific template
        scaling_template = None
        for template in templates:
            if template.id == 'scaling_climbing':
                scaling_template = template
                break

        if scaling_template:
            print(f"[PASS] Found 'Scaling and Climbing' template")
            print(f"  Skills: {scaling_template.skills}")
            print(f"  Success options: {scaling_template.success_options}")
            print(f"  Failure options: {scaling_template.failure_options}")
            print(f"  Refuse options: {scaling_template.refuse_options}")
        else:
            print("[FAIL] Could not find 'Scaling and Climbing' template")
            return False
    else:
        print("[FAIL] No templates found")
        return False

    return True


def test_skill_challenge_session():
    """Test creating and managing a skill challenge session."""
    print("\nTesting skill challenge session management...")

    manager = SkillChallengeManager()
    templates = manager.get_all_templates()

    if not templates:
        print("[FAIL] No templates available for testing")
        return False

    # Use the first template
    template = templates[0]
    character_id = "test_character_123"

    # Create a session
    session = manager.create_session(character_id, template)
    print(f"[PASS] Created session: {session.id}")
    print(f"  Challenge: {session.challenge_name}")
    print(f"  Base DC: {session.base_dc}")
    print(f"  Success revealed: {session.success_revealed}")
    print(f"  Failure revealed: {session.failure_revealed}")

    # Test DC escalation
    skill_name = template.skills[0] if template.skills else "Athletics"
    initial_dc = manager.get_skill_dc(session, skill_name)
    print(f"  Initial DC for {skill_name}: {initial_dc}")

    # Simulate skill usage
    session.skill_usage[skill_name] = 1
    escalated_dc = manager.get_skill_dc(session, skill_name)
    print(f"  DC after one use: {escalated_dc}")

    if escalated_dc == initial_dc + 1:
        print("[PASS] DC escalation working correctly")
    else:
        print(f"[FAIL] DC escalation failed: expected {initial_dc + 1}, got {escalated_dc}")
        return False

    # Test session retrieval
    retrieved_session = manager.get_active_session(character_id)
    if retrieved_session and retrieved_session.id == session.id:
        print("[PASS] Session retrieval working")
    else:
        print("[FAIL] Session retrieval failed")
        return False

    return True


def test_skill_attempt():
    """Test making skill attempts."""
    print("\nTesting skill attempts...")

    manager = SkillChallengeManager()
    templates = manager.get_all_templates()

    if not templates:
        print("[FAIL] No templates available for testing")
        return False

    template = templates[0]
    character_id = "test_character_456"

    # Create test character data
    character_data = {
        'id': character_id,
        'level': 5,
        'strength': 16,
        'dexterity': 14,
        'constitution': 15,
        'intelligence': 12,
        'wisdom': 13,
        'charisma': 10
    }

    # Create session
    session = manager.create_session(character_id, template)
    skill_name = template.skills[0] if template.skills else "Athletics"

    try:
        # Attempt the skill
        result = manager.attempt_skill(session.id, skill_name, character_data)

        print(f"[PASS] Skill attempt completed")
        print(f"  Skill: {result.skill_name}")
        print(f"  DC: {result.dc}")
        print(f"  Roll: {result.roll_result}")
        print(f"  Total: {result.total_result}")
        print(f"  Success: {result.success}")
        print(f"  Session complete: {result.session_complete}")

        return True

    except Exception as e:
        print(f"[FAIL] Skill attempt failed: {e}")
        return False


def test_reward_system():
    """Test reward and penalty application."""
    print("\nTesting reward/penalty system...")

    rewards = SkillChallengeRewards()

    # Test character data
    character_data = {
        'id': 'test_char_789',
        'level': 3,
        'hit_points_current': 15,
        'hit_points_max': 24,
        'hit_dice_current': 2,
        'hit_dice_max': 3,
        'constitution': 14
    }

    # Test rest reward
    updated_char, messages = rewards.apply_reward(character_data.copy(), "Rest")
    print(f"[PASS] Applied rest reward: {messages}")

    # Test damage penalty
    updated_char, messages = rewards.apply_penalty(character_data.copy(), "Falling damage")
    print(f"[PASS] Applied damage penalty: {messages}")

    # Test coin reward
    updated_char, messages = rewards.apply_reward(character_data.copy(), "Coin")
    print(f"[PASS] Applied coin reward: {messages}")

    return True


def cleanup_test_data():
    """Clean up test data from database."""
    print("\nCleaning up test data...")

    try:
        conn = sqlite3.connect('talekeeper.db')
        cursor = conn.cursor()

        # Remove test sessions
        cursor.execute('''
            DELETE FROM skill_challenge_sessions
            WHERE character_id LIKE 'test_character_%'
        ''')

        # Remove test attempts
        cursor.execute('''
            DELETE FROM skill_challenge_attempts
            WHERE session_id IN (
                SELECT id FROM skill_challenge_sessions
                WHERE character_id LIKE 'test_character_%'
            )
        ''')

        conn.commit()
        print("[PASS] Test data cleaned up")

    except Exception as e:
        print(f"Warning: Could not clean up test data: {e}")
    finally:
        if conn:
            conn.close()


def main():
    """Run all skill challenge system tests."""
    print("=" * 50)
    print("SKILL CHALLENGE SYSTEM TESTS")
    print("=" * 50)

    tests = [
        test_skill_challenge_database,
        test_skill_challenge_session,
        test_skill_attempt,
        test_reward_system
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
                print("[PASSED]")
            else:
                print("[FAILED]")
        except Exception as e:
            print(f"[ERROR]: {e}")
        print("-" * 30)

    cleanup_test_data()

    print(f"\nRESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! Skill challenge system is working!")
        return True
    else:
        print("Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)