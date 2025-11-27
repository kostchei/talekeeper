
import sys
import os
import json
import sqlite3
from pathlib import Path

# Add project root and src to path
project_root = Path(os.getcwd())
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

import unittest
from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.unified_level_up import UnifiedLevelUpService
from scripts.character_tools.programmatic_character_creator import ProgrammaticCharacterCreator

class TestWarlockInvocationsFix(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_warlock_fix.db"
        # Copy existing DB to test DB to have all static data (classes, invocations, etc.)
        import shutil
        if os.path.exists("talekeeper.db"):
            shutil.copy2("talekeeper.db", self.db_path)
        else:
            # Fallback if main db missing (unlikely in this env)
            pass
            
        self.engine = GameEngineSQLite(self.db_path)
        self.service = UnifiedLevelUpService(self.db_path)
        self.creator = ProgrammaticCharacterCreator(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass

    def test_auto_selection_on_level_up(self):
        # 1. Create Level 1 Warlock (so we can level up to 2)
        template = {
            "name": "TestWarlock",
            "class": "Warlock",
            "level": 1,
            "background": "Acolyte",
            "species": "Human",
            "ability_scores": {"charisma": 16, "constitution": 14, "dexterity": 14, "strength": 8, "intelligence": 10, "wisdom": 10},
            "cantrips": ["eldritch_blast", "mage_hand"],
            "spells_known": ["hex", "charm_person"]
        }
        character = self.creator.create_from_dict(template)
        character_id = character['id']

        # 2. Level up to 2 - This should trigger auto-selection
        print("Leveling up to 2...")
        result = self.service.level_up_character(character_id)
        print(f"Level up result: {json.dumps(result, indent=2)}")
        
        # 3. Verify warlock_invocations table
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT invocation_id FROM warlock_invocations WHERE character_id = ?", (character_id,))
            rows = cursor.fetchall()
            saved_invocations = [row[0] for row in rows]
            print(f"Saved invocations: {saved_invocations}")
            
            # Expecting defaults: agonizing_blast, devil_s_sight
            self.assertIn("agonizing_blast", saved_invocations)
            self.assertIn("devil_s_sight", saved_invocations)

            # 4. Verify warlock_features table (invocations_known JSON)
            cursor.execute("SELECT invocations_known FROM warlock_features WHERE character_id = ?", (character_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            known = json.loads(row[0])
            print(f"Known invocations (JSON): {known}")
            self.assertIn("agonizing_blast", known)
            self.assertIn("devil_s_sight", known)

            # 5. Verify character_features (Passive Effects)
            cursor.execute("SELECT feature_name, mechanics FROM character_features WHERE character_id = ?", (character_id,))
            features = cursor.fetchall()
            
            # Check for Agonizing Blast effect
            found_ab = False
            for name, mech in features:
                if "Agonizing Blast" in name:
                    found_ab = True
                    mechanics = json.loads(mech)
                    # Verify mechanics - corrected assertion
                    self.assertEqual(mechanics.get("damage_bonus"), "charisma_modifier")
            
            self.assertTrue(found_ab, "Agonizing Blast feature not found in character_features")

if __name__ == '__main__':
    unittest.main()
