# unsure
"""
Normalize Monster Actions Database Script

Converts all monster action entries to consistent D&D 2024 format:
- Old format: {@atk mw} {@hit 4} to hit, reach 5 ft., one target. {@h}4 ({@damage 1d4 + 2}) slashing damage.
- New format: Melee Attack Roll: +4, reach 5 ft. Hit: 4 (1d4 + 2) Slashing damage.

This eliminates parser complexity and prevents future bugs from mixed formats.
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Tuple


class ActionNormalizer:
    """Normalizes monster action entries to D&D 2024 format."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.changes = []
        self.skipped = []

    def normalize_all_monsters(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Normalize all monster actions in the database.

        Args:
            dry_run: If True, don't actually update the database, just report changes

        Returns:
            Statistics about the normalization process
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, actions FROM monsters WHERE actions IS NOT NULL AND actions != ''")
        monsters = cursor.fetchall()

        total_monsters = len(monsters)
        monsters_changed = 0
        actions_changed = 0

        print(f"Found {total_monsters} monsters with actions")
        print("=" * 80)

        for monster_id, monster_name, actions_json in monsters:
            try:
                actions = json.loads(actions_json)
                normalized_actions = []
                monster_had_changes = False

                for action in actions:
                    normalized_action = self._normalize_action(action, monster_name)
                    normalized_actions.append(normalized_action)

                    # Check if action was changed
                    if normalized_action != action:
                        monster_had_changes = True
                        actions_changed += 1

                if monster_had_changes:
                    monsters_changed += 1
                    new_actions_json = json.dumps(normalized_actions)

                    # Log the change
                    self.changes.append({
                        'id': monster_id,
                        'name': monster_name,
                        'old': actions_json,
                        'new': new_actions_json
                    })

                    # Update database if not dry run
                    if not dry_run:
                        cursor.execute(
                            "UPDATE monsters SET actions = ? WHERE id = ?",
                            (new_actions_json, monster_id)
                        )

                    print(f"[OK] {monster_name}: Normalized {actions_changed} actions")

            except Exception as e:
                print(f"[ERROR] {monster_name}: {e}")
                self.skipped.append({'name': monster_name, 'error': str(e)})

        if not dry_run:
            conn.commit()

        conn.close()

        return {
            'total_monsters': total_monsters,
            'monsters_changed': monsters_changed,
            'actions_changed': actions_changed,
            'skipped': len(self.skipped)
        }

    def _normalize_action(self, action: Dict[str, Any], monster_name: str) -> Dict[str, Any]:
        """Normalize a single action entry."""
        if 'entries' not in action or not action['entries']:
            return action

        normalized_entries = []
        for entry in action['entries']:
            if isinstance(entry, str):
                normalized_entry = self._normalize_entry_text(entry)
                normalized_entries.append(normalized_entry)
            else:
                # Keep non-string entries as-is
                normalized_entries.append(entry)

        return {
            'name': action['name'],
            'entries': normalized_entries
        }

    def _normalize_entry_text(self, text: str) -> str:
        """
        Normalize action entry text from 5eTools format to D&D 2024 format.

        Conversions:
        - {@atk mw} {@hit X} to hit -> Melee Attack Roll: +X
        - {@atk rw} {@hit X} to hit -> Ranged Attack Roll: +X
        - {@atk mw,rw} {@hit X} to hit -> Melee or Ranged Attack Roll: +X
        - {@h}X ({@damage Y}) type damage -> Hit: X (Y) Type damage
        - {@damage X} -> X (remove tags)
        - {@dc X} -> DC X
        - {@condition X} -> X (remove tags but keep condition names)
        """
        # Already in new format? Skip
        if 'Attack Roll:' in text or 'Saving Throw:' in text:
            return text

        normalized = text

        # Convert attack roll format
        # Pattern: {@atk mw} {@hit 4} to hit, reach 5 ft., one target.
        attack_pattern = r'\{@atk\s+([^}]+)\}\s*\{@hit\s+(\d+)\}\s*to hit'
        match = re.search(attack_pattern, normalized)
        if match:
            attack_type = match.group(1)
            attack_bonus = match.group(2)

            if 'mw' in attack_type and 'rw' in attack_type:
                replacement = f"Melee or Ranged Attack Roll: +{attack_bonus}"
            elif 'mw' in attack_type:
                replacement = f"Melee Attack Roll: +{attack_bonus}"
            elif 'rw' in attack_type:
                replacement = f"Ranged Attack Roll: +{attack_bonus}"
            else:
                replacement = f"Attack Roll: +{attack_bonus}"

            normalized = normalized[:match.start()] + replacement + normalized[match.end():]

        # Convert hit/damage format
        # Pattern: {@h}4 ({@damage 1d4 + 2}) slashing damage
        hit_damage_pattern = r'\{@h\}(\d+)\s*\(\{@damage\s+([^}]+)\}\)'
        match = re.search(hit_damage_pattern, normalized)
        if match:
            average_damage = match.group(1)
            damage_dice = match.group(2)
            replacement = f"Hit: {average_damage} ({damage_dice})"
            normalized = normalized[:match.start()] + replacement + normalized[match.end():]

        # Remove other tags
        # {@damage X} -> X
        normalized = re.sub(r'\{@damage\s+([^}]+)\}', r'\1', normalized)

        # {@dc X} -> DC X
        normalized = re.sub(r'\{@dc\s+(\d+)\}', r'DC \1', normalized)

        # {@condition X} -> X (but capitalize first letter)
        def capitalize_condition(match):
            condition = match.group(1)
            return condition.capitalize() if condition else condition

        normalized = re.sub(r'\{@condition\s+([^}]+)\}', capitalize_condition, normalized)

        # Remove other common tags
        normalized = re.sub(r'\{@recharge\s*([^}]*)\}', r'(Recharge \1)', normalized)
        normalized = re.sub(r'\{@creature\s+([^}]+)\}', r'\1', normalized)
        normalized = re.sub(r'\{@status\s+([^}|]+)(?:\|[^}]*)?\}', r'\1', normalized)

        # Clean up extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Fix punctuation issues
        normalized = re.sub(r'\s+\.', '.', normalized)
        normalized = re.sub(r'\s+,', ',', normalized)

        return normalized

    def show_sample_changes(self, limit: int = 5):
        """Show sample changes for review."""
        print("\n" + "=" * 80)
        print("SAMPLE CHANGES:")
        print("=" * 80)

        for i, change in enumerate(self.changes[:limit]):
            print(f"\n{i+1}. {change['name']}:")
            print(f"   BEFORE: {change['old'][:200]}...")
            print(f"   AFTER:  {change['new'][:200]}...")

    def show_full_change(self, monster_name: str):
        """Show full before/after for a specific monster."""
        for change in self.changes:
            if change['name'].lower() == monster_name.lower():
                print("=" * 80)
                print(f"FULL CHANGE FOR: {change['name']}")
                print("=" * 80)
                print("\nBEFORE:")
                print(json.dumps(json.loads(change['old']), indent=2))
                print("\nAFTER:")
                print(json.dumps(json.loads(change['new']), indent=2))
                return
        print(f"Monster '{monster_name}' not found in changes")


def main():
    """Run the normalization script."""
    import sys

    normalizer = ActionNormalizer("talekeeper.db")

    # Determine if this is a dry run
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        dry_run = False
        print("WARNING: APPLYING CHANGES TO DATABASE")
    else:
        print("DRY RUN MODE (use --apply to actually update database)")

    print("=" * 80)

    # Run normalization
    stats = normalizer.normalize_all_monsters(dry_run=dry_run)

    print("\n" + "=" * 80)
    print("NORMALIZATION COMPLETE")
    print("=" * 80)
    print(f"Total monsters: {stats['total_monsters']}")
    print(f"Monsters changed: {stats['monsters_changed']}")
    print(f"Actions changed: {stats['actions_changed']}")
    print(f"Skipped (errors): {stats['skipped']}")

    if dry_run and stats['monsters_changed'] > 0:
        normalizer.show_sample_changes(limit=5)
        print("\n" + "=" * 80)
        print("To apply these changes, run: python normalize_monster_actions.py --apply")
        print("=" * 80)
    elif not dry_run:
        print("\nDatabase updated successfully!")


if __name__ == "__main__":
    main()
