#!/usr/bin/env python3
"""
Create Fighter Showcase Characters (Levels 1-20) - Version 2

Creates 20 Champion Fighters using proper level-up progression.
Uses the actual UnifiedLevelUpService to ensure correct HP and feature calculations.

Usage:
    python scripts/character_tools/create_fighter_showcase_v2.py
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
from talekeeper.services.unified_level_up import UnifiedLevelUpService
from talekeeper.services.subclass_manager import SubclassManager


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


class FighterShowcaseCreatorV2:
    """Creates 20 Fighter characters using proper level-up progression."""

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.creator = ProgrammaticCharacterCreator(db_path)
        self.level_up_service = UnifiedLevelUpService(db_path)
        self.subclass_manager = SubclassManager(db_path)
        self.created_characters = []

    def create_all_fighters(self):
        """Create all 20 fighter characters."""
        print("=" * 80)
        print("FIGHTER SHOWCASE V2 - Creating 20 Champions (Levels 1-20)")
        print("Using proper level-up progression for accurate HP/features")
        print("=" * 80)
        print()

        for target_level in range(1, 21):
            character = self.create_fighter_at_level(target_level)
            self.created_characters.append(character)
            print()

        self._print_summary()

    def create_fighter_at_level(self, target_level: int) -> dict:
        """Create a fighter and level it up to the target level."""
        name = FIGHTER_NAMES[target_level - 1]
        print(f"[{target_level}/20] Creating {name} (Target Level {target_level})...")

        # Step 1: Create level 1 character
        level_1_template = {
            'name': name,
            'class': 'Fighter',
            'species': 'Human',
            'background': 'Soldier',
            'fighting_style': 'Dueling',
            'weapon_masteries': ['Longsword', 'Shield', 'Longbow'],
            'class_skills': ['Athletics', 'Perception'],
            'feats': ['Tough'],
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
            'level': 1,
            'experience_points': 0
        }

        character = self.creator.create_from_dict(level_1_template)
        character_id = character['id']

        print(f"  [1] Created level 1 base: HP {character['hit_points_max']}, AC {character['armor_class']}")

        # Step 2: Level up using the backend service
        for level in range(2, target_level + 1):
            # Add XP for this level
            self._add_xp(character_id, XP_THRESHOLDS[level - 1])

            # Level up
            result = self.level_up_service.level_up_character(character_id)

            if not result["success"]:
                raise Exception(f"Level up to {level} failed: {result.get('error')}")

            # Get updated character data
            char_data = self._get_character_data(character_id)

            # Apply level-specific choices
            self._apply_level_choices(character_id, level, char_data)

            print(f"  [{level}] Leveled up: HP {char_data['hit_points_max']}, AC {char_data['armor_class']}")

        # Load final character state
        final_character = self._get_character_data(character_id)

        print(f"  [OK] Final: {name} | Level {target_level} | HP: {final_character['hit_points_max']} | AC: {final_character['armor_class']}")

        return final_character

    def _apply_level_choices(self, character_id: str, level: int, char_data: dict):
        """Apply choices at specific levels (ASI, subclass, etc.)."""

        # Level 3: Select Champion subclass
        if level == 3:
            self.subclass_manager.select_subclass(character_id, 'champion', class_level=3)
            self._set_critical_range(character_id, 19)
            print(f"      → Champion subclass selected (Crit 19-20)")

        # ASI levels: 4, 6, 8, 12, 14, 16
        asi_choices = {
            4: ('strength', 2),      # STR 16 → 18
            6: ('strength', 2),      # STR 18 → 20
            8: ('constitution', 2),  # CON 15 → 17
            12: ('constitution', 2), # CON 17 → 19
            14: ('dexterity', 2),    # DEX 14 → 16
            16: ('dexterity', 2),    # DEX 16 → 18
        }

        if level in asi_choices:
            ability, increase = asi_choices[level]
            self._apply_asi(character_id, ability, increase)
            new_score = char_data[ability] + increase
            print(f"      → ASI: {ability.upper()} +{increase} (now {new_score})")

        # Level 15: Superior Critical (18-20)
        if level == 15:
            self._set_critical_range(character_id, 18)
            print(f"      → Superior Critical (Crit 18-20)")

        # Level 19: Epic Boon (feat)
        if level == 19:
            self._add_feat(character_id, 'Boon of Combat Prowess', level)
            print(f"      → Epic Boon: Boon of Combat Prowess")

    def _add_xp(self, character_id: str, xp_amount: int):
        """Add XP to character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE characters SET experience_points = ? WHERE id = ?",
                (xp_amount, character_id)
            )
            conn.commit()

    def _get_character_data(self, character_id: str) -> dict:
        """Fetch character data from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
            row = cursor.fetchone()
            if not row:
                return {}
            return dict(row)

    def _apply_asi(self, character_id: str, ability: str, increase: int):
        """Apply ASI to character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE characters SET {ability} = {ability} + ? WHERE id = ?",
                (increase, character_id)
            )
            conn.commit()

    def _add_feat(self, character_id: str, feat_name: str, level: int):
        """Add feat to character."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO character_feats (character_id, feat_name, feat_id, level_acquired)
                   VALUES (?, ?, ?, ?)""",
                (character_id, feat_name, feat_name, level)
            )
            conn.commit()

    def _set_critical_range(self, character_id: str, crit_min: int):
        """Set critical hit range for Champion."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO character_combat_state (
                    character_id, critical_range_min, studied_target_id,
                    last_attack_missed, last_miss_turn,
                    heroic_warrior_active, survivor_active, tactical_shift_movement
                )
                VALUES (?, ?, NULL, 0, 0, 0, 0, 10)""",
                (character_id, crit_min)
            )
            conn.commit()

    def _print_summary(self):
        """Print summary of created characters."""
        print("=" * 80)
        print("FIGHTER SHOWCASE V2 - Summary")
        print("=" * 80)
        print(f"\nCreated {len(self.created_characters)} fighters:")
        print()
        print(f"{'Level':<8} {'Name':<25} {'HP':<8} {'AC':<6} {'STR':<5} {'CON':<5} {'DEX':<5}")
        print("-" * 80)

        for char in self.created_characters:
            level = char['level']
            name = char['name']
            hp = char['hit_points_max']
            ac = char['armor_class']
            strength = char['strength']
            constitution = char['constitution']
            dexterity = char['dexterity']

            print(f"{level:<8} {name:<25} {hp:<8} {ac:<6} {strength:<5} {constitution:<5} {dexterity:<5}")

        print()
        print("=" * 80)
        print("All characters created with proper level-up progression!")
        print("HP calculations verified by UnifiedLevelUpService backend.")
        print("=" * 80)


def main():
    """Main entry point."""
    print("\n")
    print("=" * 80)
    print(" FIGHTER SHOWCASE CHARACTER CREATOR V2")
    print("=" * 80)
    print()
    print("This script will create 20 Champion Fighters (levels 1-20)")
    print("Using proper level-up progression for accurate calculations.")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return 0

    print()

    creator = FighterShowcaseCreatorV2()

    try:
        creator.create_all_fighters()
        print()
        print("SUCCESS! All 20 fighters have been created with correct HP values.")
        print("Open the TaleKeeper UI to view and interact with them.")
        return 0

    except Exception as e:
        print(f"\nERROR: Failed to create fighters: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
