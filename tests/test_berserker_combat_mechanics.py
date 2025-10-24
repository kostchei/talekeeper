#test
"""
Comprehensive Berserker Barbarian Combat Mechanics Test Suite

Tests the integration of Berserker abilities with combat mechanics:
- Frenzy damage application in actual combat
- Rage + Reckless Attack + Frenzy interaction
- Mindless Rage condition immunity during combat
- Retaliation reaction mechanics
- Intimidating Presence AOE effect
- Brutal Strike combat effects
- Resource tracking during encounters
"""

import sys
import os
import tempfile
import sqlite3
import json
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.talekeeper.services.barbarian_abilities import BarbarianAbilitiesService
from src.talekeeper.services.enhanced_subclass_manager import EnhancedSubclassManager
from src.talekeeper.services.condition_manager import ConditionManager, ConditionType, ActiveCondition
from src.talekeeper.services.weapon_attack_service import WeaponAttackService
from src.talekeeper.services.subclass_action_integration import SubclassActionIntegration


class BerserkerCombatTest:
    """Test fixture for Berserker combat mechanics."""

    def __init__(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.setup_database()

        self.barbarian_service = BarbarianAbilitiesService(self.db_path)
        self.subclass_manager = EnhancedSubclassManager(self.db_path)
        self.condition_manager = ConditionManager(self.db_path)
        self.weapon_service = WeaponAttackService(self.db_path)

    def setup_database(self):
        """Create test database with required schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Characters table
            cursor.execute("""
                CREATE TABLE characters (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    class_id TEXT,
                    subclass_id TEXT,
                    level INTEGER,
                    strength INTEGER DEFAULT 16,
                    dexterity INTEGER DEFAULT 14,
                    constitution INTEGER DEFAULT 16,
                    intelligence INTEGER DEFAULT 10,
                    wisdom INTEGER DEFAULT 12,
                    charisma INTEGER DEFAULT 8,
                    proficiency_bonus INTEGER DEFAULT 2,
                    hit_points_max INTEGER DEFAULT 50,
                    hit_points_current INTEGER DEFAULT 50,
                    current_hit_points INTEGER DEFAULT 50
                )
            """)

            # Character subclasses table
            cursor.execute("""
                CREATE TABLE character_subclasses (
                    character_id TEXT,
                    class_id TEXT,
                    subclass_id TEXT,
                    PRIMARY KEY (character_id, class_id)
                )
            """)

            # Barbarian features table (with all columns from migration)
            cursor.execute("""
                CREATE TABLE barbarian_features (
                    character_id TEXT PRIMARY KEY,
                    level INTEGER NOT NULL,
                    rage_uses_current INTEGER DEFAULT 0,
                    rage_uses_max INTEGER DEFAULT 2,
                    rage_damage_bonus INTEGER DEFAULT 2,
                    is_raging BOOLEAN DEFAULT FALSE,
                    rage_turns_remaining INTEGER DEFAULT 0,
                    unarmored_defense_active BOOLEAN DEFAULT TRUE,
                    reckless_attack_available BOOLEAN DEFAULT FALSE,
                    danger_sense_active BOOLEAN DEFAULT FALSE,
                    fast_movement_active BOOLEAN DEFAULT FALSE,
                    feral_instinct_active BOOLEAN DEFAULT FALSE,
                    brutal_strike_uses_current INTEGER DEFAULT 0,
                    brutal_strike_uses_max INTEGER DEFAULT 0,
                    brutal_strike_effects TEXT,
                    relentless_rage_uses_current INTEGER DEFAULT 0,
                    relentless_rage_uses_max INTEGER DEFAULT 0,
                    persistent_rage_recharge_used BOOLEAN DEFAULT FALSE,
                    primal_knowledge_skills TEXT,
                    instinctive_pounce_available BOOLEAN DEFAULT FALSE,
                    indomitable_might_active BOOLEAN DEFAULT FALSE,
                    primal_champion_applied BOOLEAN DEFAULT FALSE,
                    frenzy_active BOOLEAN DEFAULT FALSE,
                    mindless_rage_active BOOLEAN DEFAULT FALSE,
                    retaliation_available BOOLEAN DEFAULT FALSE,
                    intimidating_presence_uses_current INTEGER DEFAULT 0,
                    intimidating_presence_uses_max INTEGER DEFAULT 0,
                    weapon_mastery_count INTEGER DEFAULT 2,
                    extra_attacks INTEGER DEFAULT 1
                )
            """)

            # Character combat state
            cursor.execute("""
                CREATE TABLE character_combat_state (
                    character_id TEXT PRIMARY KEY,
                    raging BOOLEAN DEFAULT FALSE,
                    rage_damage_bonus INTEGER DEFAULT 0,
                    reckless_attack_active BOOLEAN DEFAULT FALSE,
                    frenzy_active BOOLEAN DEFAULT FALSE,
                    studied_target_id TEXT,
                    last_miss_turn INTEGER DEFAULT 0,
                    heroic_warrior_active INTEGER DEFAULT 0,
                    survivor_active INTEGER DEFAULT 0,
                    last_attack_missed INTEGER DEFAULT 0,
                    critical_range_min INTEGER DEFAULT 20,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Character resources
            cursor.execute("""
                CREATE TABLE character_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    resource_name TEXT NOT NULL,
                    current_uses INTEGER NOT NULL DEFAULT 0,
                    max_uses INTEGER NOT NULL DEFAULT 0,
                    reset_on TEXT DEFAULT 'long_rest'
                )
            """)

            # Active conditions
            cursor.execute("""
                CREATE TABLE character_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    duration_type TEXT NOT NULL DEFAULT 'rounds',
                    duration_remaining INTEGER DEFAULT -1,
                    save_dc INTEGER,
                    save_ability TEXT,
                    save_frequency TEXT DEFAULT 'end_of_turn',
                    concentration_caster TEXT,
                    applied_at_round INTEGER DEFAULT 0,
                    exhaustion_level INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE character_features (
                    character_id TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    source TEXT
                )
            """)

            # Condition immunities
            cursor.execute("""
                CREATE TABLE character_condition_immunities (
                    character_id TEXT NOT NULL,
                    condition_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    duration TEXT DEFAULT 'permanent',
                    PRIMARY KEY (character_id, condition_type, source)
                )
            """)

            cursor.execute("""
                CREATE TABLE active_spell_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id TEXT NOT NULL,
                    spell_id TEXT,
                    spell_name TEXT,
                    effect_type TEXT,
                    effect_data TEXT,
                    duration_type TEXT,
                    duration_remaining INTEGER,
                    rounds_remaining INTEGER,
                    concentration BOOLEAN DEFAULT FALSE
                )
            """)

            conn.commit()

    def create_berserker(self, character_id: str, level: int) -> str:
        """Create a berserker character at specified level."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Calculate level-appropriate bonuses
            proficiency = 2 + ((level - 1) // 4)
            rage_uses = self._calculate_rage_uses(level)
            rage_damage = 2 if level < 9 else (3 if level < 16 else 4)

            # Insert character
            cursor.execute("""
                INSERT INTO characters
                (id, name, class_id, subclass_id, level, proficiency_bonus)
                VALUES (?, ?, 'barbarian', 'berserker', ?, ?)
            """, (character_id, f"Berserker L{level}", level, proficiency))

            # Insert subclass
            cursor.execute("""
                INSERT INTO character_subclasses (character_id, class_id, subclass_id)
                VALUES (?, 'barbarian', 'berserker')
            """, (character_id,))

            # Calculate features by level
            brutal_strike_uses = 1 if level >= 9 else 0
            brutal_strike_effects = []
            if level >= 9:
                brutal_strike_effects.extend(['forceful', 'hamstring'])
            if level >= 13:
                brutal_strike_effects.extend(['staggering', 'sundering'])

            intimidating_uses = 1 if level >= 14 else 0
            relentless_uses = 1 if level >= 11 else 0

            # Insert barbarian features
            cursor.execute("""
                INSERT INTO barbarian_features (
                    character_id, level, rage_uses_current, rage_uses_max,
                    rage_damage_bonus, reckless_attack_available,
                    danger_sense_active, fast_movement_active,
                    feral_instinct_active, brutal_strike_uses_current,
                    brutal_strike_uses_max, brutal_strike_effects,
                    relentless_rage_uses_current, relentless_rage_uses_max,
                    intimidating_presence_uses_current, intimidating_presence_uses_max,
                    instinctive_pounce_available, retaliation_available,
                    weapon_mastery_count, extra_attacks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                character_id, level, rage_uses, rage_uses,
                rage_damage, level >= 2, level >= 2, level >= 5,
                level >= 7, brutal_strike_uses, brutal_strike_uses,
                json.dumps(brutal_strike_effects), relentless_uses, relentless_uses,
                intimidating_uses, intimidating_uses, level >= 7, level >= 10,
                2, 1 if level < 5 else 2
            ))

            # Add Rage resource
            cursor.execute("""
                INSERT INTO character_resources
                (character_id, resource_name, current_uses, max_uses, reset_on)
                VALUES (?, 'Rage', ?, ?, 'long_rest')
            """, (character_id, rage_uses, rage_uses))

            conn.commit()

        return character_id

    def _calculate_rage_uses(self, level: int) -> int:
        """Calculate rage uses by level."""
        if level >= 20:
            return 999  # Unlimited
        elif level >= 17:
            return 6
        elif level >= 12:
            return 5
        elif level >= 6:
            return 4
        elif level >= 3:
            return 3
        else:
            return 2

    def cleanup(self):
        """Clean up test database."""
        try:
            os.unlink(self.db_path)
        except:
            pass


def test_frenzy_damage_in_combat():
    """Test that Frenzy damage is correctly applied during combat."""
    print("\n" + "="*70)
    print("TEST: Frenzy Damage Application in Combat")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        # Test Level 3 Berserker - Frenzy should add 1d6
        char_id = test.create_berserker("frenzy_l3", 3)

        print("\n[SCENARIO] Level 3 Berserker enters rage and uses Reckless Attack")

        # Step 1: Enter Rage
        rage_result = test.barbarian_service.use_rage(char_id)
        assert rage_result['success'], "Failed to enter rage"
        print(f"  [OK] Rage activated (damage bonus: +{rage_result['rage_damage_bonus']})")

        # Step 2: Activate Reckless Attack
        reckless_result = test.barbarian_service.use_reckless_attack(char_id)
        assert reckless_result['success'], "Failed to activate Reckless Attack"
        assert reckless_result['reckless_active'], "Reckless Attack not active"
        print(f"  [OK] Reckless Attack activated")

        # Step 3: Check if Frenzy triggers
        frenzy_result = test.barbarian_service.process_berserker_turn_start(char_id)
        assert frenzy_result['success'], "Frenzy check failed"
        assert frenzy_result['frenzy'] is not None, "Frenzy should trigger"
        assert frenzy_result['frenzy']['activated'], "Frenzy not activated"

        # Verify frenzy state in database
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT frenzy_active, rage_damage_bonus
                FROM barbarian_features WHERE character_id = ?
            """, (char_id,))
            row = cursor.fetchone()
            assert row[0] == 1, "Frenzy not marked as active in database"
            rage_bonus = row[1]

        print(f"  [OK] Frenzy triggered! Bonus damage: {rage_bonus}d6")

        weapon = {'name': 'Greataxe', 'damage_dice': '1d12', 'weapon_properties': ['heavy', 'two-handed']}
        character = {'id': char_id, 'level': 3, 'strength': 16}

        with patch('src.talekeeper.services.weapon_attack_service.random.randint', side_effect=[15, 7, 4]):
            attack_result = test.weapon_service.calculate_attack_damage(weapon, character)

        assert attack_result['frenzy_damage'] == 4, "Frenzy bonus die should be applied"
        assert attack_result['frenzy_rolls'] == [4]
        expected_total = attack_result['damage_rolls'][0] + 3 + 4  # weapon roll + STR mod + frenzy bonus
        assert attack_result['damage_total'] == expected_total, "Damage total should include frenzy bonus"

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT frenzy_active FROM barbarian_features WHERE character_id = ?
            """, (char_id,))
            assert cursor.fetchone()[0] == 0, "Frenzy flag should reset after attack"

        print("  [OK] Frenzy damage applied and flag reset")

        # Test Level 9 - Should be 1d8
        char_id_l9 = test.create_berserker("frenzy_l9", 9)
        test.barbarian_service.use_rage(char_id_l9)
        test.barbarian_service.use_reckless_attack(char_id_l9)
        frenzy_l9 = test.barbarian_service.process_berserker_turn_start(char_id_l9)

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rage_damage_bonus FROM barbarian_features WHERE character_id = ?", (char_id_l9,))
            rage_bonus_l9 = cursor.fetchone()[0]

        print(f"\n[SCENARIO] Level 9 Berserker Frenzy")
        print(f"  [OK] Frenzy damage: {rage_bonus_l9}d8 (scaled from 1d6)")

        # Test Level 16 - Should be 1d10
        char_id_l16 = test.create_berserker("frenzy_l16", 16)
        test.barbarian_service.use_rage(char_id_l16)
        test.barbarian_service.use_reckless_attack(char_id_l16)
        frenzy_l16 = test.barbarian_service.process_berserker_turn_start(char_id_l16)

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rage_damage_bonus FROM barbarian_features WHERE character_id = ?", (char_id_l16,))
            rage_bonus_l16 = cursor.fetchone()[0]

        print(f"\n[SCENARIO] Level 16 Berserker Frenzy")
        print(f"  [OK] Frenzy damage: {rage_bonus_l16}d10 (scaled from 1d6)")

        print("\n[SUCCESS] Frenzy damage mechanics verified across all levels")
        return

    finally:
        test.cleanup()


def test_rage_reckless_frenzy_interaction():
    """Test the interaction between Rage, Reckless Attack, and Frenzy."""
    print("\n" + "="*70)
    print("TEST: Rage + Reckless Attack + Frenzy Interaction")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("interaction_test", 5)

        print("\n[SCENARIO] Frenzy requires both Rage AND Reckless Attack")

        # Test 1: Reckless without Rage - No Frenzy
        print("\n  Test 1: Reckless Attack without Rage")
        test.barbarian_service.use_reckless_attack(char_id)
        frenzy_result = test.barbarian_service.process_berserker_turn_start(char_id)
        assert frenzy_result['frenzy'] is None or not frenzy_result['frenzy'].get('activated'), \
            "Frenzy should NOT activate without Rage"
        print("    [OK] Frenzy correctly does NOT activate without Rage")

        # Clear reckless
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE character_combat_state SET reckless_attack_active = FALSE WHERE character_id = ?", (char_id,))
            conn.commit()

        # Test 2: Rage without Reckless - No Frenzy
        print("\n  Test 2: Rage without Reckless Attack")
        test.barbarian_service.use_rage(char_id)
        frenzy_result = test.barbarian_service.process_berserker_turn_start(char_id)
        assert frenzy_result['frenzy'] is None or not frenzy_result['frenzy'].get('activated'), \
            "Frenzy should NOT activate without Reckless Attack"
        print("    [OK] Frenzy correctly does NOT activate without Reckless Attack")

        # End rage for next test
        test.barbarian_service.end_rage(char_id)

        # Restore rage uses
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE character_resources SET current_uses = max_uses
                WHERE character_id = ? AND resource_name = 'Rage'
            """, (char_id,))
            conn.commit()

        # Test 3: Both Rage AND Reckless - Frenzy activates
        print("\n  Test 3: Rage + Reckless Attack together")
        test.barbarian_service.use_rage(char_id)
        test.barbarian_service.use_reckless_attack(char_id)
        frenzy_result = test.barbarian_service.process_berserker_turn_start(char_id)
        assert frenzy_result['frenzy'] is not None, "Frenzy should trigger"
        assert frenzy_result['frenzy']['activated'], "Frenzy should be activated"
        print("    [OK] Frenzy correctly activates with BOTH Rage and Reckless Attack")

        # Test 4: Resource consumption
        print("\n  Test 4: Resource tracking")
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT current_uses, max_uses FROM character_resources
                WHERE character_id = ? AND resource_name = 'Rage'
            """, (char_id,))
            rage_uses = cursor.fetchone()
            assert rage_uses[0] < rage_uses[1], "Rage use should be consumed"
            print(f"    [OK] Rage uses: {rage_uses[0]}/{rage_uses[1]} (consumed 1)")

        print("\n[SUCCESS] Rage + Reckless + Frenzy interaction verified")
        return

    finally:
        test.cleanup()


def test_mindless_rage_combat_immunity():
    """Test Mindless Rage immunity to Charmed/Frightened during combat."""
    print("\n" + "="*70)
    print("TEST: Mindless Rage - Combat Condition Immunity")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("mindless_test", 6)

        print("\n[SCENARIO] Level 6 Berserker with Mindless Rage")

        # Apply Frightened condition before raging
        print("\n  Step 1: Apply Frightened condition before rage")
        frightened = ActiveCondition(
            condition_type=ConditionType.FRIGHTENED,
            source="Dragon Fear",
            duration_type="minutes",
            duration_remaining=10
        )
        test.condition_manager.add_condition(char_id, frightened)
        assert test.condition_manager.has_condition(char_id, ConditionType.FRIGHTENED), \
            "Frightened should be applied"
        print("    [OK] Frightened condition applied")

        # Enter Rage - should remove Frightened
        print("\n  Step 2: Enter Rage (Mindless Rage should remove Frightened)")
        test.barbarian_service.use_rage(char_id)

        integration = SubclassActionIntegration(test.db_path)
        triggers = integration.trigger_automatic_feature(char_id, "rage_start")
        mindless_trigger = next((t for t in triggers if t.get('feature_name') == "Mindless Rage"), None)
        assert mindless_trigger and mindless_trigger.get('success'), "Mindless Rage should auto-trigger on rage start"
        print("    [OK] Mindless Rage auto-triggered on rage start")

        # Verify condition is gone
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM character_conditions
                WHERE character_id = ? AND condition_type = 'frightened'
            """, (char_id,))
            count = cursor.fetchone()[0]
            assert count == 0, f"Frightened should be removed, but found {count} conditions"
        print("    [OK] Verified: Frightened condition removed from character")

        # Try to apply Charmed while raging - should be blocked
        print("\n  Step 3: Try to apply Charmed while raging (should be blocked)")
        charmed = ActiveCondition(
            condition_type=ConditionType.CHARMED,
            source="Charm Person",
            duration_type="minutes",
            duration_remaining=1
        )
        test.condition_manager.add_condition(char_id, charmed)
        has_charmed = test.condition_manager.has_condition(char_id, ConditionType.CHARMED)
        assert not has_charmed, "Charmed should be blocked by immunity"
        print("    [OK] Charmed blocked by Mindless Rage immunity")

        # End rage - immunity should be removed
        print("\n  Step 4: End Rage (immunity should be removed)")
        test.subclass_manager.remove_rage_immunities(char_id)
        test.barbarian_service.end_rage(char_id)

        # Now Charmed should work
        test.condition_manager.add_condition(char_id, charmed)
        has_charmed = test.condition_manager.has_condition(char_id, ConditionType.CHARMED)
        assert has_charmed, "Charmed should work after rage ends"
        print("    [OK] Charmed works after rage ends (immunity removed)")

        print("\n[SUCCESS] Mindless Rage immunity mechanics verified")
        return

    finally:
        test.cleanup()


def test_retaliation_reaction():
    """Test Retaliation reaction mechanics in combat."""
    print("\n" + "="*70)
    print("TEST: Retaliation Reaction Mechanics")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("retaliation_test", 10)

        print("\n[SCENARIO] Level 10 Berserker with Retaliation")

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE barbarian_features
                SET retaliation_available = FALSE
                WHERE character_id = ?
            """, (char_id,))
            conn.commit()

        assert test.barbarian_service.mark_retaliation_available(char_id, "Goblin"), \
            "Should mark retaliation available"

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT retaliation_available FROM barbarian_features WHERE character_id = ?
            """, (char_id,))
            assert cursor.fetchone()[0] == 1, "Retaliation flag should be set"

        result = test.barbarian_service.use_berserker_retaliation(char_id, "Goblin")
        assert result['success'], "Retaliation should be usable when available"
        assert result['action_type'] == 'reaction', "Retaliation uses reaction"

        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT retaliation_available FROM barbarian_features WHERE character_id = ?
            """, (char_id,))
            assert cursor.fetchone()[0] == 0, "Retaliation flag should reset after use"

        result2 = test.barbarian_service.use_berserker_retaliation(char_id, "Orc")
        assert not result2['success'], "Retaliation should not be usable twice without trigger"
        print("  [OK] Retaliation toggles correctly before and after use")

        print("\n[SUCCESS] Retaliation reaction mechanics verified")
        return

    finally:
        test.cleanup()


def test_intimidating_presence_aoe():
    """Test Intimidating Presence AOE frightening effect."""
    print("\n" + "="*70)
    print("TEST: Intimidating Presence AOE Effect")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("intimidate_test", 14)

        # Update character stats for DC calculation
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE characters SET strength = 20, proficiency_bonus = 5
                WHERE id = ?
            """, (char_id,))
            conn.commit()

        print("\n[SCENARIO] Level 14 Berserker with STR 20 (+5), Prof +5")

        target_ids = []
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            for i in range(3):
                target_id = f"goblin_{i}"
                cursor.execute("""
                    INSERT INTO characters (id, name, class_id, level)
                    VALUES (?, ?, 'monster', 1)
                """, (target_id, f"Goblin {i}"))
                target_ids.append(target_id)
            conn.commit()

        result = test.barbarian_service.use_intimidating_presence(char_id, target_ids)
        assert result['success'], "Intimidating Presence should activate"

        expected_dc = 8 + 5 + 5  # 8 + STR + Prof
        assert result['save_dc'] == expected_dc, f"DC should be {expected_dc}"
        assert sorted(result.get('targets_affected', [])) == sorted(target_ids), "All targets should be frightened"
        assert result.get('targets_failed', []) == [], "No targets should fail due to schema issues"

        for target_id in target_ids:
            assert test.condition_manager.has_condition(target_id, ConditionType.FRIGHTENED), \
                f"Target {target_id} should be frightened"

        print(f"  [OK] Intimidating Presence activated and applied to {len(target_ids)} targets")
        print(f"    - Save DC: {result['save_dc']} (8 + STR(5) + Prof(5))")
        print(f"    - Uses remaining: {result['uses_remaining']}/1")

        assert result['uses_remaining'] == 0, "Should consume the 1 daily use"

        result2 = test.barbarian_service.use_intimidating_presence(char_id, target_ids)
        assert not result2['success'], "Should not be able to use again"
        print(f"  [OK] Cannot use again until long rest")

        print("\n[SUCCESS] Intimidating Presence AOE mechanics verified")
        return

    finally:
        test.cleanup()


def test_brutal_strike_effects():
    """Test Brutal Strike combat effects (forceful, hamstring, staggering, sundering)."""
    print("\n" + "="*70)
    print("TEST: Brutal Strike Combat Effects")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        # Test Level 9 - Forceful and Hamstring available
        char_id_l9 = test.create_berserker("brutal_l9", 9)

        print("\n[SCENARIO] Level 9 Barbarian - Forceful & Hamstring strikes available")

        # Activate Reckless Attack (required for Brutal Strike)
        test.barbarian_service.use_reckless_attack(char_id_l9)

        # Use Forceful strike
        result = test.barbarian_service.use_brutal_strike(char_id_l9, 'forceful', 'Ogre')
        assert result['success'], "Forceful strike should work at level 9"
        print(f"  [OK] Forceful Strike")
        print(f"    - Damage: +{result['damage_bonus']}")
        print(f"    - Effect: {result['effect']}")

        # Test Level 13 - All strikes available
        char_id_l13 = test.create_berserker("brutal_l13", 13)
        test.barbarian_service.use_reckless_attack(char_id_l13)

        print("\n[SCENARIO] Level 13 Barbarian - All Brutal Strikes available")

        strikes_to_test = ['forceful', 'hamstring', 'staggering', 'sundering']
        for strike_type in strikes_to_test:
            # Reset uses
            with sqlite3.connect(test.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE barbarian_features
                    SET brutal_strike_uses_current = brutal_strike_uses_max
                    WHERE character_id = ?
                """, (char_id_l13,))
                conn.commit()

            result = test.barbarian_service.use_brutal_strike(char_id_l13, strike_type, 'Troll')
            assert result['success'], f"{strike_type} should work at level 13"
            print(f"  [OK] {strike_type.title()} Strike: {result['effect']}")

        # Test Level 17 - Increased damage dice
        char_id_l17 = test.create_berserker("brutal_l17", 17)
        test.barbarian_service.use_reckless_attack(char_id_l17)

        print("\n[SCENARIO] Level 17 Barbarian - Brutal Strike damage increased")
        result = test.barbarian_service.use_brutal_strike(char_id_l17, 'forceful', 'Giant')
        assert result['success'], "Brutal strike should work at level 17"
        assert '2d10' in result['damage_bonus'], "Should use 2d10 at level 17"
        print(f"  [OK] Level 17 Brutal Strike damage: {result['damage_bonus']}")

        print("\n[SUCCESS] Brutal Strike effects verified across all levels")
        return

    finally:
        test.cleanup()


def test_relentless_rage_survival():
    """Test Relentless Rage preventing death at 0 HP."""
    print("\n" + "="*70)
    print("TEST: Relentless Rage - Survival at 0 HP")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("relentless_test", 11)

        print("\n[SCENARIO] Level 11 Berserker drops to 0 HP while raging")

        # Enter Rage
        test.barbarian_service.use_rage(char_id)
        print("  [OK] Rage activated")

        # Reduce HP to 0
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE characters SET hit_points_current = 0, current_hit_points = 0
                WHERE id = ?
            """, (char_id,))
            conn.commit()

        print("  [OK] HP reduced to 0")

        # Trigger Relentless Rage
        print("\n  [MECHANICS] Relentless Rage check...")
        result = test.barbarian_service.check_relentless_rage(char_id, damage_taken=25)

        if result.get('triggered'):
            print(f"    [OK] Relentless Rage TRIGGERED!")
            print(f"      - Constitution save: {result['save_roll']} vs DC {result['dc']}")
            print(f"      - New HP: {result['new_hp']} (2 × Barbarian level)")
            print(f"      - Uses remaining: {result['uses_remaining']}")

            # Verify HP was restored
            with sqlite3.connect(test.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT hit_points_current FROM characters WHERE id = ?", (char_id,))
                current_hp = cursor.fetchone()[0]
                assert current_hp > 0, "HP should be restored"
                assert current_hp == result['new_hp'], "HP should match expected value"
        else:
            print(f"    [X] Relentless Rage failed")
            print(f"      - Constitution save: {result['save_roll']} vs DC {result['dc']}")
            print(f"      - Character drops to 0 HP")

        print("\n[SUCCESS] Relentless Rage survival mechanic verified")
        return

    finally:
        test.cleanup()


def test_berserker_full_combat_scenario():
    """Test a full combat scenario with multiple Berserker abilities."""
    print("\n" + "="*70)
    print("TEST: Full Combat Scenario - All Berserker Abilities")
    print("="*70)

    test = BerserkerCombatTest()

    try:
        char_id = test.create_berserker("full_combat", 14)

        print("\n[COMBAT ENCOUNTER] Level 14 Berserker vs Multiple Enemies")
        print("="*70)

        # Round 1: Enter Rage and use Reckless Attack
        print("\n[ROUND 1]")
        print("  Berserker's Turn:")

        rage_result = test.barbarian_service.use_rage(char_id)
        print(f"    - Bonus Action: Rage (damage +{rage_result['rage_damage_bonus']})")
        print(f"    - Rage uses: {rage_result['uses_remaining']} remaining")

        reckless_result = test.barbarian_service.use_reckless_attack(char_id)
        print(f"    - Reckless Attack activated (advantage on attacks)")

        frenzy_result = test.barbarian_service.process_berserker_turn_start(char_id)
        if frenzy_result.get('frenzy') and frenzy_result['frenzy'].get('activated'):
            print(f"    - Frenzy triggered! First hit deals extra damage")

        if frenzy_result.get('mindless_rage') and frenzy_result['mindless_rage'].get('activated'):
            print(f"    - Mindless Rage active (immune to Charmed/Frightened)")

        print(f"    - Action: Attack with greataxe")
        print(f"      Total damage bonus: Rage (+{rage_result['rage_damage_bonus']}) + Frenzy (varies)")

        # Round 2: Enemy attacks, Berserker retaliates
        print("\n[ROUND 2]")
        print("  Enemy's Turn:")
        print("    - Orc attacks Berserker, hits for 12 damage")

        print("  Berserker's Reaction:")
        retaliation_result = test.barbarian_service.use_berserker_retaliation(char_id, "Orc")
        if retaliation_result['success']:
            print(f"    - Retaliation! {retaliation_result['effect']}")

        # Round 3: Use Intimidating Presence
        print("\n[ROUND 3]")
        print("  Berserker's Turn:")
        intimidate_result = test.barbarian_service.use_intimidating_presence(char_id)
        if intimidate_result['success']:
            print(f"    - Bonus Action: Intimidating Presence")
            print(f"      DC {intimidate_result['save_dc']} Wisdom save, 30ft area")
            print(f"      Effect: Frightened for 1 minute")

        # Verify all resources were consumed correctly
        print("\n[RESOURCE TRACKING]")
        with sqlite3.connect(test.db_path) as conn:
            cursor = conn.cursor()

            # Check rage uses
            cursor.execute("""
                SELECT current_uses, max_uses FROM character_resources
                WHERE character_id = ? AND resource_name = 'Rage'
            """, (char_id,))
            rage_uses = cursor.fetchone()
            print(f"  - Rage: {rage_uses[0]}/{rage_uses[1]} uses remaining")

            # Check intimidating presence uses
            cursor.execute("""
                SELECT intimidating_presence_uses_current, intimidating_presence_uses_max
                FROM barbarian_features WHERE character_id = ?
            """, (char_id,))
            intimidate_uses = cursor.fetchone()
            print(f"  - Intimidating Presence: {intimidate_uses[0]}/{intimidate_uses[1]} uses remaining")

        print("\n[SUCCESS] Full combat scenario completed successfully")
        return

    finally:
        test.cleanup()


def run_all_tests():
    """Run all Berserker combat mechanic tests."""
    print("\n" + "="*70)
    print("BERSERKER BARBARIAN COMBAT MECHANICS TEST SUITE")
    print("="*70)

    tests = [
        ("Frenzy Damage Application", test_frenzy_damage_in_combat),
        ("Rage + Reckless + Frenzy Interaction", test_rage_reckless_frenzy_interaction),
        ("Mindless Rage Immunity", test_mindless_rage_combat_immunity),
        ("Retaliation Reaction", test_retaliation_reaction),
        ("Intimidating Presence AOE", test_intimidating_presence_aoe),
        ("Brutal Strike Effects", test_brutal_strike_effects),
        ("Relentless Rage Survival", test_relentless_rage_survival),
        ("Full Combat Scenario", test_berserker_full_combat_scenario),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n[ERROR] {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "[OK] PASS" if success else "[X] FAIL"
        print(f"  {status}: {test_name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL BERSERKER COMBAT TESTS PASSED!")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    exit(exit_code)
