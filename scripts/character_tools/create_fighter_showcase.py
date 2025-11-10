#!/usr/bin/env python3
"""
Create Fighter Showcase Characters (Levels 1-20)

Creates 20 Champion Fighters, one at each level from 1 to 20.
Each has a unique fantasy name and is viewable in the UI.

Usage:
    python scripts/character_tools/create_fighter_showcase.py
"""

import sys
import sqlite3
from pathlib import Path
from uuid import uuid4

# Add project paths
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator


# Unique fighter names for levels 1-20
FIGHTER_NAMES = [
    "Aldric Ironforge",      # Level 1 - Rookie
    "Brenna Steelheart",     # Level 2 - Veteran
    "Cedric the Bold",       # Level 3 - Champion
    "Diana Stormbreaker",    # Level 4 - Warrior
    "Erik Battleborn",       # Level 5 - Seasoned
    "Fiona Shieldmaiden",    # Level 6 - Defender
    "Gareth Dragonbane",     # Level 7 - Knight
    "Helena Valorheart",     # Level 8 - Captain
    "Ivan Warforge",         # Level 9 - Tactical Master
    "Jenna Dawnblade",       # Level 10 - Heroic Champion
    "Kael Thunderstrike",    # Level 11 - Elite Warrior
    "Lyra Moonguard",        # Level 12 - Master Fighter
    "Marcus Stonefist",      # Level 13 - Battle Lord
    "Nora Flameheart",       # Level 14 - War Champion
    "Owen Grimshield",       # Level 15 - Legendary Fighter
    "Petra Ironclad",        # Level 16 - Grand Champion
    "Quinn Stormbringer",    # Level 17 - Warlord
    "Rowan the Unbreakable", # Level 18 - Survivor
    "Sera Mythril",          # Level 19 - Epic Champion
    "Theron Godslayer",      # Level 20 - Ultimate Warrior
]

# D&D 5e XP thresholds for levels 1-20
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
    100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]


class FighterShowcaseCreator:
    """Creates 20 Fighter characters (levels 1-20) for showcase/testing."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.creator = ProgrammaticCharacterCreator(db_path)
        self.created_characters = []

    def create_all_fighters(self):
        """Create all 20 fighter characters."""
        print("=" * 80)
        print("FIGHTER SHOWCASE - Creating 20 Champions (Levels 1-20)")
        print("=" * 80)
        print()

        for level in range(1, 21):
            character = self.create_fighter_at_level(level)
            self.created_characters.append(character)
            print()

        self._print_summary()

    def create_fighter_at_level(self, level: int) -> dict:
        """Create a single fighter at the specified level."""
        print(f"[{level}/20] Creating {FIGHTER_NAMES[level - 1]} (Level {level})...")

        # Base template - same for all fighters
        template = {
            'name': FIGHTER_NAMES[level - 1],
            'class': 'Fighter',
            'species': 'Human',
            'background': 'Soldier',
            'fighting_style': 'Dueling',  # All use Dueling for consistency
            'weapon_masteries': ['Longsword', 'Shield', 'Longbow'],
            'class_skills': ['Athletics', 'Perception'],
            'feats': ['Tough'],  # Human bonus feat
            'ability_scores': {
                'strength': 16,
                'dexterity': 14,
                'constitution': 15,
                'intelligence': 10,
                'wisdom': 12,
                'charisma': 8
            },
            'equipment_choices': {
                'weapon': 'Longsword',
                'armor': 'Chain Mail',
                'shield': 'Shield',
                'pack': 'Explorer\'s Pack'
            },
            'level': level,
            'experience_points': XP_THRESHOLDS[level - 1]
        }

        # Apply level-specific modifications
        template = self._apply_level_progression(template, level)

        # Create the character
        character = self.creator.create_from_dict(template)

        # Apply level-specific features to database
        self._apply_post_creation_features(character['id'], level)

        print(f"  [OK] Created: {character['name']} | Level {level} | HP: {character['hit_points_max']} | AC: {character['armor_class']}")

        return character

    def _apply_level_progression(self, template: dict, level: int) -> dict:
        """Apply ability score improvements and other level-based changes."""
        # ASI at levels 4, 6, 8, 12, 14, 16, 19
        asi_levels = [4, 6, 8, 12, 14, 16]
        feat_levels = [19]  # Epic Boon

        # Track ASI applications
        str_increases = 0
        con_increases = 0
        dex_increases = 0

        for asi_level in asi_levels:
            if level >= asi_level:
                if str_increases < 2:
                    # First two ASIs go to STR (16 -> 18 -> 20)
                    template['ability_scores']['strength'] = min(20, template['ability_scores']['strength'] + 2)
                    str_increases += 1
                elif con_increases < 2:
                    # Next two go to CON (15 -> 17 -> 19)
                    template['ability_scores']['constitution'] = min(20, template['ability_scores']['constitution'] + 2)
                    con_increases += 1
                elif dex_increases < 2:
                    # Last two go to DEX (14 -> 16 -> 18)
                    template['ability_scores']['dexterity'] = min(20, template['ability_scores']['dexterity'] + 2)
                    dex_increases += 1

        return template

    def _apply_post_creation_features(self, character_id: str, level: int):
        """Apply level-specific features directly to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update fighter-specific resources based on level
        second_wind_uses = 4 if level >= 10 else (3 if level >= 4 else 2)
        action_surge_uses = 2 if level >= 17 else (1 if level >= 2 else 0)
        indomitable_uses = 3 if level >= 17 else (2 if level >= 13 else (1 if level >= 9 else 0))

        cursor.execute("""
            UPDATE characters
            SET second_wind_uses_current = ?,
                second_wind_uses_max = ?,
                action_surge_uses_current = ?,
                action_surge_uses_max = ?,
                indomitable_uses_current = ?,
                indomitable_uses_max = ?
            WHERE id = ?
        """, (second_wind_uses, second_wind_uses, action_surge_uses, action_surge_uses,
              indomitable_uses, indomitable_uses, character_id))

        # Add Champion subclass if level >= 3
        if level >= 3:
            cursor.execute("""
                INSERT OR REPLACE INTO character_subclasses (character_id, class_id, subclass_id, class_level)
                VALUES (?, 'fighter', 'champion', ?)
            """, (character_id, level))

            # Set critical range based on level
            crit_range = 18 if level >= 15 else (19 if level >= 3 else 20)

            cursor.execute("""
                INSERT OR REPLACE INTO character_combat_state (
                    character_id, critical_range_min, studied_target_id,
                    last_attack_missed, last_miss_turn,
                    heroic_warrior_active, survivor_active, tactical_shift_movement
                )
                VALUES (?, ?, NULL, 0, 0, ?, ?, 10)
            """, (character_id, crit_range, 1 if level >= 10 else 0, 1 if level >= 18 else 0))

        # Set extra attacks based on level
        if level >= 5:
            extra_attacks = 4 if level >= 20 else (3 if level >= 11 else 2)

            # Store in fighter_features table if it exists
            cursor.execute("""
                INSERT OR REPLACE INTO fighter_features (
                    character_id, level, fighting_style, extra_attacks,
                    action_surge_uses_max, indomitable_uses_max
                )
                VALUES (?, ?, 'Dueling', ?, ?, ?)
            """, (character_id, level, extra_attacks, action_surge_uses, indomitable_uses))

        conn.commit()
        conn.close()

    def _print_summary(self):
        """Print summary of created characters."""
        print("=" * 80)
        print("FIGHTER SHOWCASE - Summary")
        print("=" * 80)
        print(f"\nCreated {len(self.created_characters)} fighters:")
        print()
        print(f"{'Level':<8} {'Name':<25} {'HP':<8} {'AC':<6} {'Save Slot':<10}")
        print("-" * 80)

        for char in self.created_characters:
            level = char['level']
            name = char['name']
            hp = f"{char['hit_points_max']}"
            ac = char['armor_class']
            slot = char.get('save_slot', 'N/A')

            print(f"{level:<8} {name:<25} {hp:<8} {ac:<6} {slot:<10}")

        print()
        print("=" * 80)
        print("All characters are now viewable in the TaleKeeper UI!")
        print("=" * 80)


def main():
    """Main entry point."""
    print("\n")
    print("=" * 80)
    print(" FIGHTER SHOWCASE CHARACTER CREATOR")
    print("=" * 80)
    print()
    print("This script will create 20 Champion Fighters (levels 1-20)")
    print("Each character will be saved to the database and viewable in the UI.")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    print()

    creator = FighterShowcaseCreator()

    try:
        creator.create_all_fighters()
        print()
        print("SUCCESS! All 20 fighters have been created.")
        print("Open the TaleKeeper UI to view and interact with them.")
        return 0

    except Exception as e:
        print(f"\nERROR: Failed to create fighters: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
