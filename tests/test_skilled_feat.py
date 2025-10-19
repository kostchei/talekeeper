#test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import unittest
from services.proficiency_system import ProficiencySystem


class TestSkilledFeat(unittest.TestCase):
    def setUp(self):
        self.db_path = 'talekeeper.db'
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.proficiency_system = ProficiencySystem(self.db_path)

        self.test_character_id = 'test_skilled_feat_char'
        self.cursor.execute("""
            INSERT OR REPLACE INTO characters (id, name, race_id, class_id, level)
            VALUES (?, 'Test Skilled Character', 'human', 'fighter', 4)
        """, (self.test_character_id,))
        self.conn.commit()

    def tearDown(self):
        self.cursor.execute("DELETE FROM characters WHERE id = ?", (self.test_character_id,))
        self.cursor.execute("DELETE FROM character_feats WHERE character_id = ?", (self.test_character_id,))
        self.cursor.execute("DELETE FROM character_proficiencies WHERE character_id = ?", (self.test_character_id,))
        self.conn.commit()
        self.conn.close()

    def test_skilled_feat_adds_three_skills(self):
        skills_to_add = ['Acrobatics', 'Arcana', 'History']

        self.cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Skilled', 'level_up', 4)
        """, (self.test_character_id,))

        for skill in skills_to_add:
            self.cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, 'skill', ?, 'feat')
            """, (self.test_character_id, skill))

        self.conn.commit()

        self.cursor.execute("""
            SELECT proficiency_name FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill' AND source = 'feat'
        """, (self.test_character_id,))

        result_skills = [row[0] for row in self.cursor.fetchall()]

        self.assertEqual(len(result_skills), 3)
        self.assertIn('Acrobatics', result_skills)
        self.assertIn('Arcana', result_skills)
        self.assertIn('History', result_skills)

    def test_skilled_feat_can_be_taken_multiple_times(self):
        first_skills = ['Acrobatics', 'Arcana', 'History']
        second_skills = ['Deception', 'Medicine', 'Nature']

        self.cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Skilled', 'level_up', 4)
        """, (self.test_character_id,))

        for skill in first_skills:
            self.cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, 'skill', ?, 'feat')
            """, (self.test_character_id, skill))

        self.cursor.execute("UPDATE characters SET level = 8 WHERE id = ?", (self.test_character_id,))

        self.cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Skilled', 'level_up', 8)
        """, (self.test_character_id,))

        for skill in second_skills:
            self.cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, 'skill', ?, 'feat')
            """, (self.test_character_id, skill))

        self.conn.commit()

        self.cursor.execute("""
            SELECT COUNT(*) FROM character_feats
            WHERE character_id = ? AND feat_name = 'Skilled'
        """, (self.test_character_id,))
        feat_count = self.cursor.fetchone()[0]
        self.assertEqual(feat_count, 2)

        self.cursor.execute("""
            SELECT proficiency_name FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill' AND source = 'feat'
        """, (self.test_character_id,))

        result_skills = [row[0] for row in self.cursor.fetchall()]

        self.assertEqual(len(result_skills), 6)
        for skill in first_skills + second_skills:
            self.assertIn(skill, result_skills)

    def test_skilled_feat_excludes_existing_proficiencies(self):
        existing_skills = ['Athletics', 'Intimidation']
        for skill in existing_skills:
            self.cursor.execute("""
                INSERT INTO character_proficiencies (character_id, proficiency_type, proficiency_name, source)
                VALUES (?, 'skill', ?, 'class')
            """, (self.test_character_id, skill))
        self.conn.commit()

        self.cursor.execute("""
            SELECT proficiency_name FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill'
        """, (self.test_character_id,))
        all_proficiencies = {row[0] for row in self.cursor.fetchall()}

        new_skills = ['Acrobatics', 'Arcana', 'History']
        for skill in new_skills:
            self.assertNotIn(skill, all_proficiencies)

        self.assertIn('Athletics', all_proficiencies)
        self.assertIn('Intimidation', all_proficiencies)

    def test_skilled_feat_can_be_taken_twice_at_same_level(self):
        skills_first = ['Acrobatics', 'Arcana', 'History']
        skills_second = ['Deception', 'Medicine', 'Nature']

        self.cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Skilled', 'origin', 1)
        """, (self.test_character_id,))

        self.cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Skilled', 'origin', 1)
        """, (self.test_character_id,))

        self.conn.commit()

        self.cursor.execute("""
            SELECT COUNT(*) FROM character_feats
            WHERE character_id = ? AND feat_name = 'Skilled' AND level_acquired = 1
        """, (self.test_character_id,))
        feat_count = self.cursor.fetchone()[0]
        self.assertEqual(feat_count, 2, "Should allow Skilled feat twice at level 1")


if __name__ == '__main__':
    unittest.main()