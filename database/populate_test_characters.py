# test
#utility
#!/usr/bin/env python3
# test
"""
Populate database with test characters.
This script ensures all test characters are properly created with:
- Save slots
- Character data
- Inventory items
- Character features
- Proper linking between all tables
"""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Test character definitions
TEST_CHARACTERS = [
    {
        "name": "Valerius",
        "slot": 1,
        "race": "human",
        "class": "fighter",
        "background": "sage",
        "stats": {"str": 10, "dex": 20, "con": 16, "int": 12, "wis": 8, "cha": 12},
        "saving_throws": ["str", "con"],
        "feats": ["Alert", "Lucky"],
        "fighting_style": "Dueling",
        "skills": ["Investigation", "Arcana", "Acrobatics", "Persuasion", "History"],
        "tools": ["Language"],
        "equipment": {
            "main_hand": "Rapier",
            "armor": "Studded Leather",
            "inventory": ["Rations", "Sack", "Potion of Healing"]
        }
    },
    {
        "name": "Achilles",
        "slot": 2,
        "race": "human",
        "class": "fighter",
        "background": "noble",
        "stats": {"str": 16, "dex": 14, "con": 18, "int": 8, "wis": 10, "cha": 12},
        "saving_throws": ["str", "con"],
        "feats": ["Tough", "Lucky"],
        "fighting_style": "Defense",
        "skills": ["Persuasion", "Animal Handling", "Athletics", "Perception", "Survival"],
        "tools": ["Gaming set"],
        "equipment": {
            "main_hand": "Spear",
            "armor": "Scale Mail",
            "shield": "Shield",
            "inventory": ["Rations", "Sack", "Potion of Healing"]
        }
    },
    {
        "name": "Roland",
        "slot": 3,
        "race": "human",
        "class": "fighter",
        "background": "acolyte",
        "stats": {"str": 18, "dex": 10, "con": 18, "int": 10, "wis": 12, "cha": 10},
        "saving_throws": ["str", "con"],
        "feats": ["Tough", "Savage Attacker"],
        "fighting_style": "Defense",
        "skills": ["Animal Handling", "Athletics", "Insight", "Perception", "Medicine"],
        "tools": ["Healer's Kit"],
        "equipment": {
            "main_hand": "Longsword",
            "armor": "Plate Armor",
            "shield": "Shield",
            "inventory": ["Rations", "Backpack", "Potion of Healing", "Healer's Kit"]
        }
    },
    {
        "name": "Ragnar",
        "slot": 4,
        "race": "human",
        "class": "barbarian",
        "background": "farmer",
        "stats": {"str": 18, "dex": 16, "con": 18, "int": 4, "wis": 12, "cha": 10},
        "saving_throws": ["str", "con"],
        "feats": ["Tough", "Lucky"],
        "skills": ["Nature", "Athletics", "Intimidation", "Persuasion", "Insight"],
        "equipment": {
            "main_hand": "Longsword",
            "shield": "Shield",
            "inventory": ["Rations", "Sack"]
        }
    },
    {
        "name": "Thrud",
        "slot": 5,
        "race": "human",
        "class": "barbarian",
        "background": "soldier",
        "stats": {"str": 20, "dex": 20, "con": 20, "int": 3, "wis": 6, "cha": 9},
        "saving_throws": ["str", "con"],
        "feats": ["Tough", "Savage Attacker"],
        "skills": ["Athletics", "Intimidation", "Persuasion", "Survival", "Animal Handling"],
        "equipment": {
            "main_hand": "Greataxe",
            "inventory": ["Rations", "Sack"]
        }
    },
    {
        "name": "Gath",
        "slot": 6,
        "race": "human",
        "class": "barbarian",
        "background": "farmer",
        "stats": {"str": 20, "dex": 14, "con": 18, "int": 4, "wis": 12, "cha": 10},
        "saving_throws": ["str", "con"],
        "feats": ["Tough", "Savage Attacker"],
        "skills": ["Nature", "Athletics", "Intimidation", "Perception", "Insight"],
        "tools": ["Healer's Kit"],
        "equipment": {
            "main_hand": "Battleaxe",
            "off_hand": "Handaxe",
            "armor": "Scale Mail",
            "inventory": ["Handaxe", "Rations", "Sack", "Potion of Healing"]
        }
    },
    {
        "name": "Gurnison",
        "slot": 7,
        "race": "dwarf",
        "class": "barbarian",
        "background": "artist",
        "stats": {"str": 18, "dex": 20, "con": 20, "int": 8, "wis": 8, "cha": 4},
        "saving_throws": ["str", "con"],
        "feats": ["Tough"],
        "skills": ["Athletics", "Intimidation", "Perception", "Survival"],
        "tools": ["Weaponsmithing Kit"],
        "equipment": {
            "main_hand": "Greataxe",
            "inventory": ["Handaxe", "Handaxe", "Rations", "Sack", "Potion of Healing"]
        }
    }
]

class TestCharacterPopulator:
    def __init__(self, db_path='talekeeper.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def cleanup_existing(self):
        """Remove any existing test characters."""
        print("Cleaning up existing test characters...")
        
        # Get test character IDs
        self.cursor.execute("SELECT id FROM characters WHERE id LIKE 'test_%'")
        char_ids = [row[0] for row in self.cursor.fetchall()]
        
        if char_ids:
            # Delete from all related tables
            placeholders = ','.join('?' * len(char_ids))
            self.cursor.execute(f"DELETE FROM character_inventory WHERE character_id IN ({placeholders})", char_ids)
            self.cursor.execute(f"DELETE FROM character_features WHERE character_id IN ({placeholders})", char_ids)
            self.cursor.execute(f"DELETE FROM character_proficiencies WHERE character_id IN ({placeholders})", char_ids)
            self.cursor.execute(f"DELETE FROM characters WHERE id IN ({placeholders})", char_ids)
            
        # Delete test save slots
        self.cursor.execute("DELETE FROM save_slots WHERE slot_number BETWEEN 1 AND 7")
        
        self.conn.commit()
        print(f"Cleaned up {len(char_ids)} test characters")
        
    def calculate_hp(self, char_data):
        """Calculate HP for a character."""
        con_mod = (char_data['stats']['con'] - 10) // 2
        
        if char_data['class'] == 'fighter':
            base_hp = 10
        elif char_data['class'] == 'barbarian':
            base_hp = 12
        else:
            base_hp = 8
            
        hp = base_hp + con_mod
        
        # Apply racial bonuses
        if char_data['race'] == 'dwarf':
            hp += 1  # Dwarven Toughness: +1 HP per level
        
        # Apply Tough feat
        if 'Tough' in char_data.get('feats', []):
            hp += 2  # +2 per level, level 1
            
        return max(1, hp)
        
    def calculate_ac(self, char_data):
        """Calculate AC for a character."""
        dex_mod = (char_data['stats']['dex'] - 10) // 2
        con_mod = (char_data['stats']['con'] - 10) // 2
        
        armor = char_data['equipment'].get('armor', '')
        shield = char_data['equipment'].get('shield', '')
        
        if char_data['class'] == 'barbarian' and not armor:
            # Unarmored Defense for Barbarian
            ac = 10 + dex_mod + con_mod
        elif armor == 'Studded Leather':
            ac = 12 + dex_mod
        elif armor == 'Scale Mail':
            ac = 14 + min(2, dex_mod)
        elif armor == 'Plate Armor':
            ac = 18
        else:
            ac = 10 + dex_mod
            
        if shield:
            ac += 2
            
        # Apply Defense fighting style
        if char_data.get('fighting_style') == 'Defense' and armor:
            ac += 1
            
        return ac
        
    def create_save_slot(self, char_data):
        """Create a save slot for the character."""
        slot_id = str(char_data['slot'])
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO save_slots (
                id, slot_number, character_name, character_level, 
                last_played, is_occupied, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            slot_id,
            char_data['slot'],
            char_data['name'],
            1,  # Level 1
            datetime.now().isoformat(),
            1,  # Occupied
            datetime.now().isoformat()
        ))
        
        return slot_id
        
    def create_character(self, char_data):
        """Create the character record."""
        char_id = f"test_{char_data['name'].lower()}"
        hp = self.calculate_hp(char_data)
        ac = self.calculate_ac(char_data)
        
        # Determine hit dice based on class
        hit_dice = 1
        if char_data['class'] == 'barbarian':
            hit_dice_type = 'd12'
        elif char_data['class'] == 'fighter':
            hit_dice_type = 'd10'
        else:
            hit_dice_type = 'd8'
            
        # Calculate resource uses
        lucky_uses = 3 if 'Lucky' in char_data.get('feats', []) else 0
        inspiration_uses = 1 if char_data['race'] == 'human' else 0
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO characters (
                id, save_slot_id, name, race_id, class_id, background_id,
                level, experience_points,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                armor_class, hit_points_max, hit_points_current, 
                max_hit_points, current_hit_points,
                hit_dice_max, hit_dice_current,
                equipment_main_hand, equipment_off_hand, equipment_armor, equipment_shield,
                lucky_uses_current, lucky_uses_max, inspiration_uses_current, inspiration_uses_max,
                created_at, notes
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?
            )
        """, (
            char_id,
            str(char_data['slot']),
            char_data['name'],
            char_data['race'],
            char_data['class'],
            char_data['background'],
            1, 0,  # Level 1, 0 XP
            char_data['stats']['str'],
            char_data['stats']['dex'],
            char_data['stats']['con'],
            char_data['stats']['int'],
            char_data['stats']['wis'],
            char_data['stats']['cha'],
            ac,
            hp, hp,  # Current and max HP
            hp, hp,  # Legacy HP fields
            hit_dice, hit_dice,  # Hit dice
            char_data['equipment'].get('main_hand', ''),
            char_data['equipment'].get('off_hand', ''),
            char_data['equipment'].get('armor', ''),
            char_data['equipment'].get('shield', ''),
            lucky_uses, lucky_uses,  # Lucky current/max
            inspiration_uses, inspiration_uses,  # Inspiration current/max
            datetime.now().isoformat(),
            f"Test character: {', '.join(char_data.get('feats', []))}"
        ))
        
        return char_id
        
    def add_inventory(self, char_id, char_data):
        """Add inventory items for the character."""
        items_to_add = []
        
        # Add equipped items
        if char_data['equipment'].get('main_hand'):
            items_to_add.append({
                'name': char_data['equipment']['main_hand'],
                'type': 'weapon',
                'equipped': 1
            })
            
        if char_data['equipment'].get('off_hand'):
            items_to_add.append({
                'name': char_data['equipment']['off_hand'],
                'type': 'weapon',
                'equipped': 1
            })
            
        if char_data['equipment'].get('armor'):
            items_to_add.append({
                'name': char_data['equipment']['armor'],
                'type': 'armor',
                'equipped': 1
            })
            
        if char_data['equipment'].get('shield'):
            items_to_add.append({
                'name': char_data['equipment']['shield'],
                'type': 'shield',
                'equipped': 1
            })
            
        # Add inventory items
        for item_name in char_data['equipment'].get('inventory', []):
            item_type = 'consumable' if 'Potion' in item_name else 'gear'
            items_to_add.append({
                'name': item_name,
                'type': item_type,
                'equipped': 0
            })
            
        # Insert all items
        for item in items_to_add:
            item_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO character_inventory (
                    id, character_id, item_name, item_type, 
                    quantity, weight_lb, value_gp, equipped, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_id,
                char_id,
                item['name'],
                item['type'],
                1,  # Quantity
                1.0,  # Default weight
                1.0,  # Default value
                item['equipped'],
                datetime.now().isoformat()
            ))
            
    def add_proficiencies(self, char_id, char_data):
        """Add character proficiencies (saving throws, skills, tools)."""
        # Add saving throw proficiencies (convert abbreviations to full names)
        save_mapping = {
            'str': 'strength',
            'dex': 'dexterity', 
            'con': 'constitution',
            'int': 'intelligence',
            'wis': 'wisdom',
            'cha': 'charisma'
        }
        
        for save in char_data.get('saving_throws', []):
            full_name = save_mapping.get(save.lower(), save)
            self.cursor.execute("""
                INSERT OR IGNORE INTO character_proficiencies (
                    character_id, proficiency_type, proficiency_name, source
                ) VALUES (?, ?, ?, ?)
            """, (char_id, 'saving_throw', full_name, 'class'))
            
        # Add skill proficiencies
        for skill in char_data.get('skills', []):
            self.cursor.execute("""
                INSERT OR IGNORE INTO character_proficiencies (
                    character_id, proficiency_type, proficiency_name
                ) VALUES (?, ?, ?)
            """, (char_id, 'skill', skill))
            
        # Add tool proficiencies
        for tool in char_data.get('tools', []):
            self.cursor.execute("""
                INSERT OR IGNORE INTO character_proficiencies (
                    character_id, proficiency_type, proficiency_name
                ) VALUES (?, ?, ?)
            """, (char_id, 'tool', tool))
    
    def add_features(self, char_id, char_data):
        """Add character features and feats."""
        # Add class features
        if char_data['class'] == 'fighter':
            self.cursor.execute("""
                INSERT INTO character_features (
                    character_id, feature_name, feature_type, 
                    usage_type, level_gained, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                char_id,
                'Second Wind',
                'bonus_action',
                'short_rest',
                1,
                'Regain 1d10+1 hit points as a bonus action'
            ))
            
            # Add fighting style
            if char_data.get('fighting_style'):
                self.cursor.execute("""
                    INSERT INTO character_features (
                        character_id, feature_name, feature_type, 
                        usage_type, level_gained, description
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    char_id,
                    f"Fighting Style: {char_data['fighting_style']}",
                    'passive',
                    'permanent',
                    1,
                    self.get_fighting_style_description(char_data['fighting_style'])
                ))
                
        elif char_data['class'] == 'barbarian':
            self.cursor.execute("""
                INSERT INTO character_features (
                    character_id, feature_name, feature_type, 
                    usage_type, level_gained, description
                ) VALUES 
                (?, 'Rage', 'bonus_action', 'long_rest', 1, 
                 'Advantage on Strength checks, resistance to physical damage'),
                (?, 'Unarmored Defense', 'passive', 'permanent', 1,
                 'AC = 10 + Dex + Con when not wearing armor')
            """, (char_id, char_id))
            
        # Add feats
        for feat in char_data.get('feats', []):
            self.cursor.execute("""
                INSERT INTO character_features (
                    character_id, feature_name, feature_type, 
                    usage_type, level_gained, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                char_id,
                feat,
                'feat',
                'permanent',
                1,
                self.get_feat_description(feat)
            ))
            
    def get_fighting_style_description(self, style):
        """Get description for fighting style."""
        descriptions = {
            'Defense': '+1 to AC while wearing armor',
            'Dueling': '+2 damage with one-handed weapon',
            'Great Weapon Fighting': 'Reroll 1-2 on damage dice',
            'Two-Weapon Fighting': 'Add ability modifier to off-hand damage'
        }
        return descriptions.get(style, '')
        
    def get_feat_description(self, feat):
        """Get description for feat."""
        descriptions = {
            'Alert': 'Add proficiency bonus to initiative, advantage on initiative rolls (solo play)',
            'Lucky': '3 luck points per long rest',
            'Tough': '+2 HP per level',
            'Savage Attacker': 'Reroll damage dice once per turn'
        }
        return descriptions.get(feat, '')
        
    def populate_all(self):
        """Populate all test characters."""
        print("Starting test character population...")
        
        # Clean up first
        self.cleanup_existing()
        
        # Create each character
        for char_data in TEST_CHARACTERS:
            print(f"Creating {char_data['name']}...")
            
            # Create save slot
            slot_id = self.create_save_slot(char_data)
            
            # Create character
            char_id = self.create_character(char_data)
            
            # Add inventory
            self.add_inventory(char_id, char_data)
            
            # Add features
            self.add_features(char_id, char_data)
            
            # Add proficiencies
            self.add_proficiencies(char_id, char_data)
            
        self.conn.commit()
        print(f"Successfully created {len(TEST_CHARACTERS)} test characters!")
        
        # Verify
        self.cursor.execute("SELECT COUNT(*) FROM characters WHERE id LIKE 'test_%'")
        char_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM save_slots WHERE slot_number BETWEEN 1 AND 7")
        slot_count = self.cursor.fetchone()[0]
        
        print(f"Verification: {char_count} characters, {slot_count} save slots")
        
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate TaleKeeper database with test characters')
    parser.add_argument('--db-path', default='talekeeper.db', help='Path to database file')
    parser.add_argument('--verify', action='store_true', help='Only verify existing characters')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.db_path):
        print(f"Error: Database not found at {args.db_path}")
        sys.exit(1)
        
    populator = TestCharacterPopulator(args.db_path)
    
    try:
        if args.verify:
            # Just verify
            populator.cursor.execute("SELECT name, level, class_id FROM characters WHERE id LIKE 'test_%'")
            chars = populator.cursor.fetchall()
            print(f"Found {len(chars)} test characters:")
            for char in chars:
                print(f"  - {char[0]} (Level {char[1]} {char[2].title()})")
        else:
            # Populate
            populator.populate_all()
            
    finally:
        populator.close()


if __name__ == '__main__':
    main()