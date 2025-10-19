# core
#utility
# core
"""
Comprehensive Monster Attack Migration

Converts ALL monsters from D&D Beyond JSON format to standardized format.
Uses the existing MonsterAttackParser to extract effects, then converts to standardized structure.
"""

import sqlite3
import json
import sys
import os
from typing import Dict, List, Any, Optional

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

try:
    from monster_attack_parser import MonsterAttackParser, AttackEffect
except ImportError:
    print("Error: Could not import MonsterAttackParser")
    print("Make sure you're running from the TaleKeeper root directory")
    sys.exit(1)


class ComprehensiveMonsterMigration:
    """Migrates all monsters to standardized attack format."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.parser = MonsterAttackParser()
        self.conversion_stats = {
            "total_monsters": 0,
            "already_converted": 0,
            "successfully_converted": 0,
            "failed_conversions": 0,
            "no_actions": 0
        }

    def migrate_all_monsters(self, dry_run: bool = True):
        """Migrate all monsters in the database."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get all monsters
            cursor.execute("SELECT id, name, actions FROM monsters ORDER BY name")
            all_monsters = cursor.fetchall()

            self.conversion_stats["total_monsters"] = len(all_monsters)

            print(f"Found {len(all_monsters)} monsters to process")
            print("=" * 60)

            for monster_id, name, actions_json in all_monsters:
                self._process_monster(cursor, monster_id, name, actions_json, dry_run)

            if not dry_run:
                conn.commit()

            self._print_migration_summary()

    def _process_monster(self, cursor, monster_id: str, name: str, actions_json: str, dry_run: bool):
        """Process a single monster."""

        if not actions_json or actions_json.strip() in ['', '[]', 'null']:
            self.conversion_stats["no_actions"] += 1
            return

        try:
            actions_data = json.loads(actions_json)
        except json.JSONDecodeError:
            print(f"ERROR {name}: Invalid JSON")
            self.conversion_stats["failed_conversions"] += 1
            return

        # Check if already converted
        if self._is_already_converted(actions_data):
            self.conversion_stats["already_converted"] += 1
            return

        # Convert using parser
        try:
            standardized_actions = self._convert_monster_actions(name, actions_data)

            if standardized_actions:
                print(f"OK {name}: Converted {len(actions_data)} -> {len(standardized_actions)} attacks")

                if not dry_run:
                    new_actions_json = json.dumps(standardized_actions, indent=2)
                    cursor.execute(
                        "UPDATE monsters SET actions = ? WHERE id = ?",
                        (new_actions_json, monster_id)
                    )

                self.conversion_stats["successfully_converted"] += 1
            else:
                print(f"WARN {name}: No attacks found to convert")

        except Exception as e:
            print(f"ERROR {name}: Conversion failed - {e}")
            self.conversion_stats["failed_conversions"] += 1

    def _is_already_converted(self, actions_data: List[Dict]) -> bool:
        """Check if monster already uses standardized format."""
        if not actions_data:
            return False

        # Look for standardized format indicators
        for action in actions_data:
            if "attack_type" in action:
                return True

        return False

    def _convert_monster_actions(self, monster_name: str, actions_data: List[Dict]) -> List[Dict]:
        """Convert monster actions from old to new format."""

        standardized_actions = []

        for action in actions_data:
            # Skip non-attack actions
            if not self._is_attack_action(action):
                continue

            # Use existing parser to extract attack data
            try:
                parsed_attacks = self.parser.parse_monster_actions(json.dumps([action]))

                for parsed_attack in parsed_attacks:
                    standardized_attack = self._convert_parsed_attack_to_standard(parsed_attack)
                    if standardized_attack:
                        standardized_actions.append(standardized_attack)

            except Exception as e:
                print(f"  Warning: Could not parse {action.get('name', 'unnamed')} - {e}")
                continue

        return standardized_actions

    def _is_attack_action(self, action: Dict) -> bool:
        """Determine if an action is an attack."""
        entries = action.get('entries', [])
        if not entries:
            return False

        # Look for attack indicators in text
        attack_indicators = [
            '{@atk', '{@hit', '{@damage',
            'saving throw', 'must succeed', 'must make',
            'to hit', 'damage'
        ]

        text = ' '.join(entries).lower()
        return any(indicator in text for indicator in attack_indicators)

    def _convert_parsed_attack_to_standard(self, parsed_attack) -> Optional[Dict]:
        """Convert ParsedAttack to standardized format."""

        try:
            # Determine attack type
            attack_type = self._determine_attack_type(parsed_attack)

            standardized = {
                "name": parsed_attack.name,
                "attack_type": attack_type,
                "description": getattr(parsed_attack, 'description', '') or f"{parsed_attack.name} attack"
            }

            # Add attack bonus if available
            if hasattr(parsed_attack, 'attack_bonus') and parsed_attack.attack_bonus:
                standardized["attack_bonus"] = parsed_attack.attack_bonus

            # Add range/reach
            if hasattr(parsed_attack, 'reach') and parsed_attack.reach:
                standardized["reach"] = parsed_attack.reach
            if hasattr(parsed_attack, 'range_normal') and parsed_attack.range_normal:
                standardized["range_normal"] = parsed_attack.range_normal
            if hasattr(parsed_attack, 'range_long') and parsed_attack.range_long:
                standardized["range_long"] = parsed_attack.range_long

            # Add recharge if available
            if hasattr(parsed_attack, 'recharge') and parsed_attack.recharge:
                standardized["recharge"] = parsed_attack.recharge

            # Convert damage
            damage_info = {}
            if hasattr(parsed_attack, 'damage_dice') and parsed_attack.damage_dice:
                primary_damage = {
                    "dice": parsed_attack.damage_dice,
                    "type": parsed_attack.damage_type or "untyped"
                }
                damage_info["primary"] = primary_damage

            if hasattr(parsed_attack, 'additional_damage') and parsed_attack.additional_damage:
                additional = []
                for add_dmg in parsed_attack.additional_damage:
                    dmg_obj = self._parse_damage_string(add_dmg)
                    if dmg_obj:
                        additional.append(dmg_obj)
                if additional:
                    damage_info["additional"] = additional

            if damage_info:
                standardized["damage"] = damage_info

            # Convert effects
            effects = []
            if hasattr(parsed_attack, 'effects') and parsed_attack.effects:
                for effect in parsed_attack.effects:
                    std_effect = self._convert_effect_to_standard(effect)
                    if std_effect:
                        effects.append(std_effect)

            if effects:
                standardized["effects"] = effects

            return standardized

        except Exception as e:
            print(f"    Error converting {parsed_attack.name}: {e}")
            return None

    def _determine_attack_type(self, parsed_attack) -> str:
        """Determine attack type from parsed attack."""
        name = parsed_attack.name.lower()

        # Check for specific patterns
        if any(word in name for word in ['breath', 'cone', 'area', 'burst']):
            return "breath_weapon" if 'breath' in name else "area"
        elif any(word in name for word in ['gaze', 'presence', 'aura']):
            return "aura"
        elif any(word in name for word in ['bow', 'javelin', 'dart', 'sling']):
            return "ranged"
        elif hasattr(parsed_attack, 'range') and parsed_attack.range:
            return "ranged"
        else:
            return "melee"

    def _parse_damage_string(self, damage_str) -> Optional[Dict]:
        """Parse damage string like '2d6+3 slashing' into standardized format."""
        if not damage_str:
            return None

        # Handle tuple input from parser
        if isinstance(damage_str, tuple):
            if len(damage_str) >= 2:
                return {
                    "dice": str(damage_str[0]),
                    "type": str(damage_str[1])
                }
            elif len(damage_str) == 1:
                return {
                    "dice": str(damage_str[0]),
                    "type": "untyped"
                }
            return None

        # Handle string input
        if isinstance(damage_str, str):
            parts = damage_str.strip().split()
            if len(parts) >= 2:
                dice = parts[0]
                damage_type = parts[1]
                return {
                    "dice": dice,
                    "type": damage_type
                }
            elif len(parts) == 1 and any(c.isdigit() for c in parts[0]):
                # Just dice, assume no type
                return {
                    "dice": parts[0],
                    "type": "untyped"
                }

        return None

    def _convert_effect_to_standard(self, effect: AttackEffect) -> Optional[Dict]:
        """Convert AttackEffect to standardized format."""
        try:
            std_effect = {
                "type": effect.effect_type  # Use effect_type, not type
            }

            # Add all non-None attributes
            if effect.condition:
                std_effect["condition"] = effect.condition
            if effect.save_dc:
                std_effect["save_dc"] = effect.save_dc
            if effect.save_ability:
                std_effect["save_ability"] = effect.save_ability
            if effect.duration:
                std_effect["duration"] = effect.duration
            if effect.escape_dc:
                std_effect["escape_dc"] = effect.escape_dc
            if effect.damage_on_fail:
                fail_dmg = self._parse_damage_string(effect.damage_on_fail)
                if fail_dmg:
                    std_effect["damage_fail"] = fail_dmg
            if effect.damage_on_success:
                success_dmg = self._parse_damage_string(effect.damage_on_success)
                if success_dmg:
                    std_effect["damage_success"] = success_dmg

            return std_effect

        except Exception as e:
            print(f"      Error converting effect: {e}")
            return None

    def _print_migration_summary(self):
        """Print summary of migration results."""
        stats = self.conversion_stats

        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Total monsters: {stats['total_monsters']}")
        print(f"Already converted: {stats['already_converted']}")
        print(f"Successfully converted: {stats['successfully_converted']}")
        print(f"Failed conversions: {stats['failed_conversions']}")
        print(f"No actions: {stats['no_actions']}")
        print("=" * 60)

        if stats['failed_conversions'] > 0:
            print(f"WARNING: {stats['failed_conversions']} monsters failed conversion")
        if stats['successfully_converted'] > 0:
            print(f"SUCCESS: {stats['successfully_converted']} monsters successfully converted")


def test_sample():
    """Test migration on a small sample first."""
    print("Testing migration on sample monsters...")

    migrator = ComprehensiveMonsterMigration()

    # Test on just a few monsters first
    with sqlite3.connect(migrator.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, actions FROM monsters WHERE name IN ('Aarakocra', 'Aboleth', 'Adult Brass Dragon') ORDER BY name")
        test_monsters = cursor.fetchall()

        print(f"Testing with {len(test_monsters)} monsters")

        for monster_id, name, actions_json in test_monsters:
            print(f"\n--- {name} ---")
            migrator._process_monster(cursor, monster_id, name, actions_json, dry_run=True)


def main():
    """Main migration function."""
    print("Comprehensive Monster Attack Migration")
    print("=" * 60)

    # Test on sample first
    test_sample()

    print("\n" + "=" * 60)
    print("Proceeding with full migration...")
    # Auto-proceed for testing

    migrator = ComprehensiveMonsterMigration()

    # Run dry run first
    print("Running dry run to preview changes...")
    migrator.migrate_all_monsters(dry_run=True)

    # Auto-apply for testing
    print("\nApplying migration...")
    migrator = ComprehensiveMonsterMigration()  # Fresh instance for real run
    migrator.migrate_all_monsters(dry_run=False)
    print("\nMigration complete!")


if __name__ == "__main__":
    main()