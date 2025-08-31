#!/usr/bin/env python3
"""
Add new classes to classes.json file.
"""

import json

def add_classes_to_json():
    """Add the 5 new classes to classes.json."""
    
    # Load existing classes
    with open('data/classes.json', 'r') as f:
        classes = json.load(f)
    
    # New classes to add
    new_classes = [
        {
            "name": "Barbarian",
            "description": "A fierce warrior of primitive background who can enter a battle rage.",
            "hit_die": 12,
            "primary_ability": "Strength",
            "saving_throw_proficiencies": ["strength", "constitution"],
            "armor_proficiencies": ["light", "medium", "shields"],
            "weapon_proficiencies": ["simple", "martial"],
            "skill_proficiencies": [
                "Animal Handling", "Athletics", "Intimidation", "Nature", 
                "Perception", "Survival"
            ],
            "skill_choices": 2
        },
        {
            "name": "Paladin", 
            "description": "A holy warrior bound to a sacred oath, wielding divine magic.",
            "hit_die": 10,
            "primary_ability": "Strength and Charisma",
            "saving_throw_proficiencies": ["wisdom", "charisma"],
            "armor_proficiencies": ["light", "medium", "heavy", "shields"],
            "weapon_proficiencies": ["simple", "martial"],
            "skill_proficiencies": [
                "Athletics", "Insight", "Intimidation", "Medicine", 
                "Persuasion", "Religion"
            ],
            "skill_choices": 2
        },
        {
            "name": "Warlock",
            "description": "A wielder of magic derived from a bargain with an extraplanar entity.",
            "hit_die": 8,
            "primary_ability": "Charisma",
            "saving_throw_proficiencies": ["wisdom", "charisma"],
            "armor_proficiencies": ["light"],
            "weapon_proficiencies": ["simple"],
            "skill_proficiencies": [
                "Arcana", "Deception", "History", "Intimidation", 
                "Investigation", "Nature", "Religion"
            ],
            "skill_choices": 2
        },
        {
            "name": "Wizard",
            "description": "A scholarly magic-user capable of manipulating the structures of spellcasting.",
            "hit_die": 6,
            "primary_ability": "Intelligence", 
            "saving_throw_proficiencies": ["intelligence", "wisdom"],
            "armor_proficiencies": [],
            "weapon_proficiencies": ["daggers", "darts", "slings", "quarterstaffs", "light crossbows"],
            "skill_proficiencies": [
                "Arcana", "History", "Insight", "Investigation", 
                "Medicine", "Religion"
            ],
            "skill_choices": 2
        },
        {
            "name": "Cleric",
            "description": "A priestly champion who wields divine magic in service of a higher power.",
            "hit_die": 8,
            "primary_ability": "Wisdom",
            "saving_throw_proficiencies": ["wisdom", "charisma"],
            "armor_proficiencies": ["light", "medium", "shields"],
            "weapon_proficiencies": ["simple"],
            "skill_proficiencies": [
                "History", "Insight", "Medicine", "Persuasion", "Religion"
            ],
            "skill_choices": 2
        }
    ]
    
    # Add new classes to existing list
    for new_class in new_classes:
        # Check if class already exists
        if not any(cls['name'] == new_class['name'] for cls in classes):
            classes.append(new_class)
            print(f"Added {new_class['name']}")
        else:
            print(f"{new_class['name']} already exists, skipping")
    
    # Save updated classes
    with open('data/classes.json', 'w') as f:
        json.dump(classes, f, indent=2)
    
    print(f"\nClasses.json updated! Total classes: {len(classes)}")

if __name__ == "__main__":
    add_classes_to_json()