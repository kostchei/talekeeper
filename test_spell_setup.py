#!/usr/bin/env python3
"""
Test script to set up spellcasting for existing characters and test the spell slot system.
"""

import sqlite3
from services.spellcasting_service import SpellcastingService
from services.spell_registry import SpellRegistry, SpellDefinition, SpellSchool

def setup_test_spells():
    """Add our target spells to the database if they don't exist."""
    print("Setting up test spells...")

    spell_registry = SpellRegistry('talekeeper.db')

    # Define our core test spells
    test_spells = [
        # Cleric Cantrips
        SpellDefinition(
            id='sacred_flame', name='Sacred Flame', level=0, school=SpellSchool.EVOCATION,
            casting_time='1 action', range_value='60 feet', components='V, S',
            duration='Instantaneous', concentration=False, ritual=False,
            description='A creature you can see must make a Dexterity saving throw. It takes 1d8 radiant damage on failure.',
            classes=['cleric']
        ),
        SpellDefinition(
            id='guidance', name='Guidance', level=0, school=SpellSchool.DIVINATION,
            casting_time='1 action', range_value='Touch', components='V, S',
            duration='Concentration, up to 1 minute', concentration=True, ritual=False,
            description='Touch a creature. Once before the spell ends, it can roll 1d4 and add to one ability check.',
            classes=['cleric']
        ),

        # Cleric Level 1 Spells
        SpellDefinition(
            id='cure_wounds', name='Cure Wounds', level=1, school=SpellSchool.EVOCATION,
            casting_time='1 action', range_value='Touch', components='V, S',
            duration='Instantaneous', concentration=False, ritual=False,
            description='Touch a creature and heal 1d8 + spellcasting modifier hit points.',
            higher_levels='When cast using higher level slots, heal an additional 1d8 per slot level.',
            classes=['cleric']
        ),
        SpellDefinition(
            id='bless', name='Bless', level=1, school=SpellSchool.ENCHANTMENT,
            casting_time='1 action', range_value='30 feet', components='V, S, M',
            duration='Concentration, up to 1 minute', concentration=True, ritual=False,
            description='Choose up to 3 creatures. They add 1d4 to attack rolls and saving throws.',
            classes=['cleric']
        ),

        # Wizard Cantrips
        SpellDefinition(
            id='fire_bolt', name='Fire Bolt', level=0, school=SpellSchool.EVOCATION,
            casting_time='1 action', range_value='120 feet', components='V, S',
            duration='Instantaneous', concentration=False, ritual=False,
            description='Make a ranged spell attack. On hit, deal 1d10 fire damage.',
            classes=['wizard']
        ),
        SpellDefinition(
            id='mage_hand', name='Mage Hand', level=0, school=SpellSchool.CONJURATION,
            casting_time='1 action', range_value='30 feet', components='V, S',
            duration='1 minute', concentration=False, ritual=False,
            description='Create a spectral hand that can manipulate objects within range.',
            classes=['wizard']
        ),
    ]

    # Add spells to registry
    for spell in test_spells:
        success = spell_registry.add_spell(spell)
        if success:
            print(f"Added spell: {spell.name}")
        else:
            print(f"Failed to add spell: {spell.name}")

def setup_character_spellcasting(character_id: str, class_name: str):
    """Initialize spellcasting for a character."""
    print(f"Setting up spellcasting for character {character_id} ({class_name})")

    service = SpellcastingService('talekeeper.db')
    success = service.initialize_character_spellcasting(character_id, class_name)

    if success:
        print("Spellcasting initialized successfully")
    else:
        print("Failed to initialize spellcasting")

    return success

def add_character_spells(character_id: str, spell_ids: list):
    """Add spells to a character's spell list."""
    print(f"Adding spells to character {character_id}: {spell_ids}")

    with sqlite3.connect('talekeeper.db') as conn:
        cursor = conn.cursor()

        for spell_id in spell_ids:
            # Get spell level
            cursor.execute("SELECT level FROM spells WHERE id = ?", (spell_id,))
            row = cursor.fetchone()
            if not row:
                print(f"Spell {spell_id} not found")
                continue

            spell_level = row[0]

            # Add to character spells (prepared for clerics, always prepared for cantrips)
            is_prepared = spell_level == 0 or True  # For testing, prepare all spells
            always_prepared = spell_level == 0  # Cantrips are always prepared

            cursor.execute("""
                INSERT OR REPLACE INTO character_spells
                (character_id, spell_id, spell_level, is_prepared, always_prepared, source, source_level)
                VALUES (?, ?, ?, ?, ?, 'class', 1)
            """, (character_id, spell_id, spell_level, is_prepared, always_prepared))

            print(f"Added {spell_id} (level {spell_level}) to character")

        conn.commit()

def test_spell_system():
    """Test the complete spell system."""
    print("=== Testing Spell System ===")

    # Character info
    character_id = 'd2bf003a-68e8-4125-97dd-078320c1ded3'
    class_name = 'cleric'

    # Step 1: Set up spells in database
    setup_test_spells()

    # Step 2: Initialize character spellcasting
    setup_character_spellcasting(character_id, class_name)

    # Step 3: Add spells to character
    cleric_spells = ['sacred_flame', 'guidance', 'cure_wounds', 'bless']
    add_character_spells(character_id, cleric_spells)

    # Step 4: Test spell slot retrieval
    service = SpellcastingService('talekeeper.db')
    slots = service.get_character_spell_slots(character_id)

    print(f"\nSpell slots for character:")
    for slot in slots:
        print(f"  Level {slot.level}: {slot.available_slots}/{slot.max_slots} ({slot.slot_type.value})")

    # Step 5: Test spell casting capability
    spells = service.get_character_spells(character_id) if hasattr(service, 'get_character_spells') else []
    print(f"\nCharacter spells: {len(spells)}")

    print("\n=== Test Complete ===")

if __name__ == '__main__':
    test_spell_system()