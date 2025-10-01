"""
Create a Level 5 Rogue with enough XP for Level 6

Creates a fully functional level 5 rogue character with:
- All level 5 features
- Cunning Strike available
- Enough XP to level up to 6
- Basic equipment
"""

import sqlite3
import uuid
import json

DB_PATH = "talekeeper.db"

def create_level5_rogue():
    """Create a level 5 rogue character"""

    character_id = str(uuid.uuid4())
    character_name = "Shadowblade"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # XP thresholds for D&D 5e/2024:
        # Level 5: 6,500 XP
        # Level 6: 14,000 XP
        # Give them 14,500 XP so they can level up
        xp = 14500

        print(f"Creating Level 5 Rogue: {character_name}")
        print(f"Character ID: {character_id}")
        print(f"XP: {xp} (enough for level 6)")

        # Create character
        cursor.execute("""
            INSERT INTO characters (
                id, name, class_id, level, experience_points,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_max, hit_points_current, armor_class,
                race_id, background_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, character_name, 'rogue', 5, xp,
            10, 18, 14, 13, 12, 10,  # Ability scores (DEX primary)
            38, 38, 15,  # HP, AC
            'human', 'criminal'
        ))

        print("[OK] Character created")

        # Create rogue_features entry
        cursor.execute("""
            INSERT INTO rogue_features (
                character_id, level, sneak_attack_dice,
                expertise_skills, cunning_action_available,
                uncanny_dodge_available, uncanny_dodge_used,
                evasion_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_id, 5, 3,  # Level 5 = 3d6 sneak attack
            json.dumps(['Stealth', 'Perception']),  # Starting expertise
            True, True, False, False
        ))

        print("[OK] Rogue features created")

        # Add character features
        features = [
            ('Sneak Attack', 1, 'passive', 'Deal extra damage when you have advantage'),
            ('Thieves\' Cant', 1, 'passive', 'Secret language'),
            ('Cunning Action', 2, 'bonus_action', 'Dash, Disengage, or Hide as bonus action'),
            ('Steady Aim', 3, 'bonus_action', 'Gain advantage, speed becomes 0'),
            ('Expertise', 1, 'passive', 'Double proficiency bonus on 2 skills'),
            ('Cunning Strike', 5, 'triggered', 'Trade Sneak Attack dice for effects'),
            ('Uncanny Dodge', 5, 'reaction', 'Halve damage from one attack')
        ]

        for feature_name, level_gained, usage_type, description in features:
            cursor.execute("""
                INSERT INTO character_features (
                    character_id, feature_name, level_gained,
                    feature_type, usage_type, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (character_id, feature_name, level_gained, 'class', usage_type, description))

        print(f"[OK] Added {len(features)} class features")

        # Add proficiencies
        proficiencies = [
            ('skill', 'Acrobatics'),
            ('skill', 'Stealth'),
            ('skill', 'Perception'),
            ('skill', 'Investigation'),
            ('skill', 'Sleight of Hand'),
            ('armor', 'Light Armor'),
            ('weapon', 'Simple Weapons'),
            ('weapon', 'Hand Crossbows'),
            ('weapon', 'Longswords'),
            ('weapon', 'Rapiers'),
            ('weapon', 'Shortswords'),
            ('save', 'Dexterity'),
            ('save', 'Intelligence'),
        ]

        for prof_type, prof_name in proficiencies:
            cursor.execute("""
                INSERT INTO character_proficiencies (
                    character_id, proficiency_type, proficiency_name
                ) VALUES (?, ?, ?)
            """, (character_id, prof_type, prof_name))

        print(f"[OK] Added {len(proficiencies)} proficiencies")

        # Expertise is stored in rogue_features.expertise_skills (already done above)
        expertise_skills = ['Stealth', 'Perception']
        print(f"[OK] Expertise set in rogue_features for: {', '.join(expertise_skills)}")

        # Add starting equipment
        equipment = [
            ('Shortsword', 'weapon', 1),
            ('Shortsword', 'weapon', 1),  # Two shortswords
            ('Leather Armor', 'armor', 1),
            ("Thieves' Tools", 'tool', 1),
            ("Burglar's Pack", 'gear', 1),
        ]

        for item_name, item_type, quantity in equipment:
            cursor.execute("""
                INSERT INTO character_inventory (
                    character_id, item_name, item_type, quantity, equipped
                ) VALUES (?, ?, ?, ?, ?)
            """, (character_id, item_name, item_type, quantity, 1 if item_type in ['weapon', 'armor'] else 0))

        print(f"[OK] Added {len(equipment)} items to inventory")

        # Create combat state entry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_combat_state (
                character_id TEXT PRIMARY KEY,
                cunning_strike_selection TEXT,
                steady_aim_active BOOLEAN DEFAULT 0,
                sneak_attack_used_this_turn BOOLEAN DEFAULT 0,
                last_updated TEXT DEFAULT (datetime('now'))
            )
        """)

        cursor.execute("""
            INSERT INTO character_combat_state (character_id)
            VALUES (?)
        """, (character_id,))

        print("[OK] Created combat state")

        conn.commit()

        print("\n" + "="*60)
        print(f"SUCCESS! Created Level 5 Rogue: {character_name}")
        print("="*60)
        print(f"Character ID: {character_id}")
        print(f"Level: 5")
        print(f"XP: {xp} (Level 6 requires 14,000)")
        print(f"Sneak Attack: 3d6")
        print(f"Features: Sneak Attack, Cunning Action, Steady Aim,")
        print(f"          Cunning Strike, Uncanny Dodge")
        print(f"Expertise: {', '.join(expertise_skills)}")
        print(f"Equipment: Dual Shortswords, Leather Armor, Thieves' Tools")
        print("\nReady to level up to 6 and test Expertise selection!")
        print("="*60)

        return character_id

if __name__ == '__main__':
    try:
        char_id = create_level5_rogue()
        print(f"\nTo test in-game, look for character: Shadowblade")
        print(f"Character ID: {char_id}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
