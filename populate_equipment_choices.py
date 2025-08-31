"""
Populate class equipment choices for all 11 D&D 2024 classes.
This creates a database-driven system for equipment selection during character creation.
"""

import sqlite3
import json

def populate_equipment_choices():
    """Populate the class_equipment_choices table with options for all classes."""
    
    # Connect to database
    conn = sqlite3.connect('talekeeper.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_equipment_choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            choice_group TEXT NOT NULL,
            choice_name TEXT NOT NULL,
            options TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(class_id, choice_group)
        )
    """)
    
    # Equipment choices for all 11 classes
    # Each class gets 2 choice groups with 3 options each
    equipment_data = [
        # Fighter
        {
            'class_id': 'fighter',
            'choice_group': 'weapon_choice',
            'choice_name': 'Martial Weapon',
            'options': json.dumps([
                {'name': 'Longsword', 'damage': '1d8 slashing', 'properties': 'Versatile (1d10)'},
                {'name': 'Greatsword', 'damage': '2d6 slashing', 'properties': 'Heavy, two-handed'},
                {'name': 'Rapier', 'damage': '1d8 piercing', 'properties': 'Finesse'}
            ])
        },
        {
            'class_id': 'fighter',
            'choice_group': 'armor_choice',
            'choice_name': 'Armor',
            'options': json.dumps([
                {'name': 'Studded Leather', 'ac': '12 + Dex', 'type': 'Light'},
                {'name': 'Breastplate', 'ac': '14 + Dex (max 2)', 'type': 'Medium'},
                {'name': 'Chain Mail', 'ac': '16', 'type': 'Heavy'}
            ])
        },
        
        # Rogue
        {
            'class_id': 'rogue',
            'choice_group': 'weapon_choice',
            'choice_name': 'Primary Weapon',
            'options': json.dumps([
                {'name': 'Rapier', 'damage': '1d8 piercing', 'properties': 'Finesse'},
                {'name': 'Shortsword', 'damage': '1d6 piercing', 'properties': 'Finesse, light'},
                {'name': 'Shortbow', 'damage': '1d6 piercing', 'properties': 'Ranged (80/320)'}
            ])
        },
        {
            'class_id': 'rogue',
            'choice_group': 'pack_choice',
            'choice_name': 'Equipment Pack',
            'options': json.dumps([
                {'name': "Burglar's Pack", 'contents': 'Backpack, ball bearings, string, bell, candles, crowbar, hammer, pitons, lantern, oil, rations, tinderbox, waterskin, rope'},
                {'name': "Dungeoneer's Pack", 'contents': 'Backpack, crowbar, hammer, pitons, torches, tinderbox, rations, waterskin, rope'},
                {'name': "Explorer's Pack", 'contents': 'Backpack, bedroll, mess kit, tinderbox, torches, rations, waterskin, rope'}
            ])
        },
        
        # Wizard
        {
            'class_id': 'wizard',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Quarterstaff', 'damage': '1d6 bludgeoning', 'properties': 'Versatile (1d8)'},
                {'name': 'Dagger', 'damage': '1d4 piercing', 'properties': 'Finesse, light, thrown (20/60)'},
                {'name': 'Light Crossbow', 'damage': '1d8 piercing', 'properties': 'Ranged (80/320), loading'}
            ])
        },
        {
            'class_id': 'wizard',
            'choice_group': 'focus_choice',
            'choice_name': 'Arcane Focus',
            'options': json.dumps([
                {'name': 'Wand', 'weight': '1 lb', 'description': 'A slender rod of wood or metal'},
                {'name': 'Orb', 'weight': '3 lb', 'description': 'A crystal sphere'},
                {'name': 'Component Pouch', 'weight': '2 lb', 'description': 'Small pouches of spell components'}
            ])
        },
        
        # Cleric
        {
            'class_id': 'cleric',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Mace', 'damage': '1d6 bludgeoning', 'properties': 'Simple melee'},
                {'name': 'Warhammer', 'damage': '1d8 bludgeoning', 'properties': 'Versatile (1d10)'},
                {'name': 'Light Crossbow', 'damage': '1d8 piercing', 'properties': 'Ranged (80/320), loading'}
            ])
        },
        {
            'class_id': 'cleric',
            'choice_group': 'armor_choice',
            'choice_name': 'Armor',
            'options': json.dumps([
                {'name': 'Leather Armor', 'ac': '11 + Dex', 'type': 'Light'},
                {'name': 'Scale Mail', 'ac': '14 + Dex (max 2)', 'type': 'Medium'},
                {'name': 'Chain Shirt', 'ac': '13 + Dex (max 2)', 'type': 'Medium'}
            ])
        },
        
        # Ranger
        {
            'class_id': 'ranger',
            'choice_group': 'weapon_choice',
            'choice_name': 'Primary Weapon',
            'options': json.dumps([
                {'name': 'Longbow', 'damage': '1d8 piercing', 'properties': 'Heavy, ranged (150/600)'},
                {'name': 'Two Shortswords', 'damage': '1d6 piercing each', 'properties': 'Finesse, light'},
                {'name': 'Longsword and Shield', 'damage': '1d8 slashing', 'properties': 'Versatile, +2 AC from shield'}
            ])
        },
        {
            'class_id': 'ranger',
            'choice_group': 'armor_choice',
            'choice_name': 'Armor',
            'options': json.dumps([
                {'name': 'Leather Armor', 'ac': '11 + Dex', 'type': 'Light'},
                {'name': 'Studded Leather', 'ac': '12 + Dex', 'type': 'Light'},
                {'name': 'Hide Armor', 'ac': '12 + Dex (max 2)', 'type': 'Medium'}
            ])
        },
        
        # Barbarian
        {
            'class_id': 'barbarian',
            'choice_group': 'weapon_choice',
            'choice_name': 'Martial Weapon',
            'options': json.dumps([
                {'name': 'Greataxe', 'damage': '1d12 slashing', 'properties': 'Heavy, two-handed'},
                {'name': 'Greatsword', 'damage': '2d6 slashing', 'properties': 'Heavy, two-handed'},
                {'name': 'Maul', 'damage': '2d6 bludgeoning', 'properties': 'Heavy, two-handed'}
            ])
        },
        {
            'class_id': 'barbarian',
            'choice_group': 'secondary_weapon',
            'choice_name': 'Secondary Weapon',
            'options': json.dumps([
                {'name': 'Two Handaxes', 'damage': '1d6 slashing each', 'properties': 'Light, thrown (20/60)'},
                {'name': 'Four Javelins', 'damage': '1d6 piercing', 'properties': 'Thrown (30/120)'},
                {'name': 'Simple Melee Weapon', 'damage': 'Varies', 'properties': 'Any simple melee weapon'}
            ])
        },
        
        # Bard
        {
            'class_id': 'bard',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Rapier', 'damage': '1d8 piercing', 'properties': 'Finesse'},
                {'name': 'Longsword', 'damage': '1d8 slashing', 'properties': 'Versatile (1d10)'},
                {'name': 'Dagger', 'damage': '1d4 piercing', 'properties': 'Finesse, light, thrown (20/60)'}
            ])
        },
        {
            'class_id': 'bard',
            'choice_group': 'instrument_choice',
            'choice_name': 'Musical Instrument',
            'options': json.dumps([
                {'name': 'Lute', 'weight': '2 lb', 'description': 'A stringed instrument'},
                {'name': 'Flute', 'weight': '1 lb', 'description': 'A wind instrument'},
                {'name': 'Drum', 'weight': '3 lb', 'description': 'A percussion instrument'}
            ])
        },
        
        # Paladin
        {
            'class_id': 'paladin',
            'choice_group': 'weapon_choice',
            'choice_name': 'Martial Weapon and Shield',
            'options': json.dumps([
                {'name': 'Longsword and Shield', 'damage': '1d8 slashing', 'properties': 'Versatile, +2 AC'},
                {'name': 'Warhammer and Shield', 'damage': '1d8 bludgeoning', 'properties': 'Versatile, +2 AC'},
                {'name': 'Greatsword', 'damage': '2d6 slashing', 'properties': 'Heavy, two-handed'}
            ])
        },
        {
            'class_id': 'paladin',
            'choice_group': 'secondary_weapon',
            'choice_name': 'Secondary Weapon',
            'options': json.dumps([
                {'name': 'Five Javelins', 'damage': '1d6 piercing', 'properties': 'Thrown (30/120)'},
                {'name': 'Simple Melee Weapon', 'damage': 'Varies', 'properties': 'Any simple melee weapon'},
                {'name': 'Light Crossbow and 20 Bolts', 'damage': '1d8 piercing', 'properties': 'Ranged (80/320)'}
            ])
        },
        
        # Warlock
        {
            'class_id': 'warlock',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Light Crossbow', 'damage': '1d8 piercing', 'properties': 'Ranged (80/320), loading'},
                {'name': 'Quarterstaff', 'damage': '1d6 bludgeoning', 'properties': 'Versatile (1d8)'},
                {'name': 'Dagger', 'damage': '1d4 piercing', 'properties': 'Finesse, light, thrown (20/60)'}
            ])
        },
        {
            'class_id': 'warlock',
            'choice_group': 'focus_choice',
            'choice_name': 'Arcane Focus',
            'options': json.dumps([
                {'name': 'Rod', 'weight': '2 lb', 'description': 'A thin baton of metal or wood'},
                {'name': 'Wand', 'weight': '1 lb', 'description': 'A slender rod'},
                {'name': 'Component Pouch', 'weight': '2 lb', 'description': 'Pouches of spell components'}
            ])
        },
        
        # Sorcerer
        {
            'class_id': 'sorcerer',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Light Crossbow', 'damage': '1d8 piercing', 'properties': 'Ranged (80/320), loading'},
                {'name': 'Dagger', 'damage': '1d4 piercing', 'properties': 'Finesse, light, thrown (20/60)'},
                {'name': 'Quarterstaff', 'damage': '1d6 bludgeoning', 'properties': 'Versatile (1d8)'}
            ])
        },
        {
            'class_id': 'sorcerer',
            'choice_group': 'pack_choice',
            'choice_name': 'Equipment Pack',
            'options': json.dumps([
                {'name': "Dungeoneer's Pack", 'contents': 'Backpack, crowbar, hammer, pitons, torches, tinderbox, rations, waterskin, rope'},
                {'name': "Explorer's Pack", 'contents': 'Backpack, bedroll, mess kit, tinderbox, torches, rations, waterskin, rope'},
                {'name': "Scholar's Pack", 'contents': 'Backpack, book of lore, ink, quill, parchment, bag of sand, small knife'}
            ])
        },
        
        # Monk
        {
            'class_id': 'monk',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Shortsword', 'damage': '1d6 piercing', 'properties': 'Finesse, light'},
                {'name': 'Quarterstaff', 'damage': '1d6 bludgeoning', 'properties': 'Versatile (1d8)'},
                {'name': 'Ten Darts', 'damage': '1d4 piercing', 'properties': 'Finesse, thrown (20/60)'}
            ])
        },
        {
            'class_id': 'monk',
            'choice_group': 'pack_choice',
            'choice_name': 'Equipment Pack',
            'options': json.dumps([
                {'name': "Dungeoneer's Pack", 'contents': 'Backpack, crowbar, hammer, pitons, torches, tinderbox, rations, waterskin, rope'},
                {'name': "Explorer's Pack", 'contents': 'Backpack, bedroll, mess kit, tinderbox, torches, rations, waterskin, rope'},
                {'name': 'Minimal Pack', 'contents': '10 darts, backpack, bedroll, rations (5 days), waterskin'}
            ])
        },
        
        # Druid
        {
            'class_id': 'druid',
            'choice_group': 'weapon_choice',
            'choice_name': 'Simple Weapon',
            'options': json.dumps([
                {'name': 'Wooden Shield and Scimitar', 'damage': '1d6 slashing', 'properties': 'Finesse, light, +2 AC'},
                {'name': 'Quarterstaff', 'damage': '1d6 bludgeoning', 'properties': 'Versatile (1d8)'},
                {'name': 'Spear', 'damage': '1d6 piercing', 'properties': 'Thrown (20/60), versatile (1d8)'}
            ])
        },
        {
            'class_id': 'druid',
            'choice_group': 'focus_choice',
            'choice_name': 'Druidic Focus',
            'options': json.dumps([
                {'name': 'Wooden Staff', 'weight': '4 lb', 'description': 'A staff drawn from a living tree'},
                {'name': 'Totem', 'weight': '1 lb', 'description': 'An object incorporating natural materials'},
                {'name': 'Sprig of Mistletoe', 'weight': '0 lb', 'description': 'A sacred plant component'}
            ])
        }
    ]
    
    # Clear existing data
    cursor.execute("DELETE FROM class_equipment_choices")
    
    # Insert all equipment choices
    for item in equipment_data:
        cursor.execute("""
            INSERT INTO class_equipment_choices (class_id, choice_group, choice_name, options)
            VALUES (?, ?, ?, ?)
        """, (item['class_id'], item['choice_group'], item['choice_name'], item['options']))
    
    conn.commit()
    print(f"Populated equipment choices for {len(set(item['class_id'] for item in equipment_data))} classes")
    print(f"Total choice groups: {len(equipment_data)}")
    
    # Verify the data
    cursor.execute("SELECT class_id, COUNT(*) FROM class_equipment_choices GROUP BY class_id")
    for class_id, count in cursor.fetchall():
        print(f"  {class_id}: {count} choice groups")
    
    conn.close()

if __name__ == "__main__":
    populate_equipment_choices()