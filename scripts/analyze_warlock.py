"""
Warlock Level 1-20 Analysis Script

Creates a Warlock, levels them to 20, and reports on missing/broken features.
Does NOT restore the database automatically, allowing for manual inspection.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project paths
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

from tests.helpers.database_archiver import DatabaseArchiver
from tests.helpers.choice_loader import ChoiceLoader
from tests.helpers.progression_recorder import ProgressionRecorder
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator
from talekeeper.services.unified_level_up import UnifiedLevelUpService
from talekeeper.services.subclass_manager import SubclassManager
from talekeeper.core.game_engine_sqlite import GameEngineSQLite

# XP Table
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000,
    100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
]

class WarlockAnalyzer:
    def __init__(self, db_path="talekeeper.db"):
        self.db_path = db_path
        self.character_id = None
        self.recorder = None
        self.issues = []
        self.engine = GameEngineSQLite(db_path)

    def setup(self):
        print(f"Archiving database {self.db_path} (safety backup)...")
        # We still archive for safety, but we won't auto-restore
        self.archive_path = DatabaseArchiver.archive(self.db_path, description="Warlock Analysis Start")
        print(f"Archive created: {self.archive_path}")

    def create_character(self):
        print("\n=== Creating Level 1 Warlock ===")
        
        # Template for a Fiend Warlock
        template = {
            "name": "Malphas the Analyzed",
            "race_id": "human_id", # Will need to resolve actual ID or use creator logic
            "class_id": "warlock",
            "background_id": "acolyte_id", # Placeholder
            "strength": 8,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 16,
            "level": 1,
            "experience_points": 0,
            # Warlock specifics
            "patron": "fiend",
            "cantrips": ["eldritch_blast", "mage_hand"],
            "spells_known": ["hex", "burning_hands"],
            "equipment_choices": {
                "main_hand": "dagger",
                "off_hand": "arcane_focus"
            }
        }

        # Use the programmatic creator which handles ID resolution better
        # We'll use a simplified template compatible with ProgrammaticCharacterCreator
        pcc_template = {
            "name": "Malphas",
            "class": "Warlock",
            "species": "Human",
            "background": "Acolyte",
            "ability_scores": {
                "strength": 8, "dexterity": 14, "constitution": 14,
                "intelligence": 12, "wisdom": 10, "charisma": 16
            },
            "patron": "The Fiend", # Name matching DB
            "pact_boon": "Pact of the Blade", # Future proofing
            "invocations": [], # Lvl 2
            "cantrips": ["Eldritch Blast", "Mage Hand"],
            "spells_known": ["Hex", "Burning Hands"]
        }

        creator = ProgrammaticCharacterCreator(self.db_path)
        try:
            char_data = creator.create_from_dict(pcc_template)
            self.character_id = char_data['id']
            print(f"Character created: {char_data['name']} (ID: {self.character_id})")
            
            # Initialize recorder
            self.recorder = ProgressionRecorder("warlock_analysis", "Malphas", "tests/output")
            self.recorder.set_initial_state(
                character_class="warlock",
                species="Human",
                background="Acolyte",
                ability_scores=pcc_template["ability_scores"],
                fighting_style=None,
                starting_hp=char_data['hit_points_max']
            )
            
        except Exception as e:
            print(f"FATAL: Failed to create character: {e}")
            self.issues.append(f"Character creation failed: {e}")
            raise

    def grant_resources(self):
        print("\n=== Granting Resources ===")
        # Grant XP for Level 20
        target_xp = 355000
        self.engine.update_character_xp_sync(self.character_id, target_xp)
        print(f"Granted {target_xp} XP")

        # Grant Gold
        gold = 50000
        import sqlite3
        import uuid
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Insert gold as an inventory item
            cursor.execute("""
                INSERT INTO character_inventory (
                    id, character_id, item_name, item_type, quantity, 
                    weight_lb, description, value_gp, equipped, 
                    stored_in_bag, treasure_type, unit_value_gp
                ) VALUES (
                    ?, ?, 'Gold Pieces', 'currency', ?, 
                    0.02, 'Standard currency', ?, 0, 
                    0, 'coins', 1
                )
            """, (str(uuid.uuid4()), self.character_id, gold, gold))
            conn.commit()
        print(f"Granted {gold} GP")

    def analyze_progression(self):
        print("\n=== Starting Progression Analysis (1 -> 20) ===")
        
        level_up_service = UnifiedLevelUpService(self.db_path)
        
        for level in range(2, 21):
            print(f"\n--- Leveling to {level} ---")
            try:
                # 1. Perform Level Up
                result = level_up_service.level_up_character(self.character_id)
                if not result['success']:
                    error = f"Level {level} failed: {result.get('error')}"
                    print(f"ERROR: {error}")
                    self.issues.append(error)
                    continue
                
                print(f"Level up successful.")
                
                # 2. Simulate Choices (ASI, Invocations, Spells)
                # This is where we'd normally use a ChoiceLoader, but for analysis we might
                # want to just pick *something* to keep going, or log if we're prompted.
                # For now, we'll check what features were granted.
                
                # TODO: Check for pending choices in DB?
                # The UnifiedLevelUpService usually applies automatic features.
                # Choices like Invocations are often handled by UI dialogs that call specific services.
                # We need to programmatically make those choices to fully simulate a Warlock.
                
                self._handle_level_choices(level)
                
                # 3. Verify Features
                self._verify_level_features(level)
                
            except Exception as e:
                print(f"EXCEPTION at Level {level}: {e}")
                self.issues.append(f"Exception at Level {level}: {e}")

    def _handle_level_choices(self, level):
        """
        Make programmatic choices for the Warlock to ensure they have a valid state.
        """
        # Warlock Choices:
        # Lvl 2: 2 Invocations
        # Lvl 3: Pact Boon, 1 Invocation replacement? (No, just new spell/retrain)
        # Lvl 4: ASI/Feat
        # Lvl 5: Invocation
        # ...
        
        # This is a simplified handler. In a full test we'd map this out in a YAML.
        # Here we just want to see if the *slots* for these choices open up or if features break.
        pass

    def _verify_level_features(self, level):
        """
        Check if expected features for this level exist in the DB.
        """
        # We can query the character_features or class_features tables
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feature_name, feature_type 
                FROM character_features 
                WHERE character_id = ?
            """, (self.character_id,))
            features = cursor.fetchall()
            feature_names = [f[0] for f in features]
            
            print(f"Features found: {len(feature_names)}")
            # We could verify specific expected strings here
            
            # Also check warlock_features table if it exists
            try:
                cursor.execute("SELECT * FROM warlock_features WHERE character_id = ?", (self.character_id,))
                warlock_data = cursor.fetchone()
                if warlock_data:
                    print(f"Warlock specific data: {warlock_data}")
            except:
                pass

            # Check character_spell_slots for pact slots
            try:
                cursor.execute("""
                    SELECT spell_level, max_slots, slot_type 
                    FROM character_spell_slots 
                    WHERE character_id = ? AND slot_type = 'pact'
                """, (self.character_id,))
                pact_slots = cursor.fetchall()
                if pact_slots:
                    print(f"Pact Slots found: {pact_slots}")
                else:
                    print("WARNING: No Pact Slots found in character_spell_slots")
            except Exception as e:
                print(f"Error checking spell slots: {e}")

            # Check feature_states (new system)
            try:
                cursor.execute("""
                    SELECT feature_name, feature_type, uses_current, uses_max 
                    FROM feature_states 
                    WHERE character_id = ?
                """, (self.character_id,))
                new_features = cursor.fetchall()
                if new_features:
                    print(f"New System Features (feature_states): {len(new_features)} found")
                    for nf in new_features:
                        print(f"  - {nf[0]} ({nf[1]})")
                else:
                    print("WARNING: No features found in feature_states")
            except Exception as e:
                print(f"Error checking feature_states: {e}")

    def report(self):
        print("\n=== Analysis Report ===")
        if not self.issues:
            print("No obvious errors detected during leveling.")
        else:
            print(f"Found {len(self.issues)} issues:")
            for issue in self.issues:
                print(f"- {issue}")
        
        # Write to file
        with open("warlock_improvement.md", "w") as f:
            f.write("# Warlock Implementation Analysis\n\n")
            f.write("## Issues Found\n")
            if not self.issues:
                f.write("No critical errors during automated leveling.\n")
            else:
                for issue in self.issues:
                    f.write(f"- {issue}\n")
            
            f.write("\n## Manual Inspection Required\n")
            f.write("The database has been left in a leveled-up state.\n")
            f.write(f"Character ID: {self.character_id}\n")
            f.write("Please open the application and verify:\n")
            f.write("1. Invocations selection UI.\n")
            f.write("2. Pact Boon functionality.\n")
            f.write("3. Mystic Arcanum usage.\n")
            f.write("4. Spell slot scaling.\n")

if __name__ == "__main__":
    analyzer = WarlockAnalyzer()
    try:
        analyzer.setup()
        analyzer.create_character()
        analyzer.grant_resources()
        analyzer.analyze_progression()
        analyzer.report()
        print("\nDone. Database NOT restored (per user request).")
    except Exception as e:
        print(f"\nCRITICAL FAILURE: {e}")
