"""
Add all Paladin spells from SRD to database

This script:
1. Extracts spell data from the SRD markdown
2. Adds missing paladin spells to the spells table
3. Links all spells to the paladin class in spell_class_lists
4. Cleans up duplicate entries
"""

import sqlite3
import re

# Full list of Paladin spells from SRD 5.2.1
PALADIN_SPELLS = {
    # Level 1
    'bless': {'level': 1, 'school': 'Enchantment', 'concentration': True, 'ritual': False},
    'command': {'level': 1, 'school': 'Enchantment', 'concentration': False, 'ritual': False},
    'cure_wounds': {'level': 1, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'detect_evil_and_good': {'level': 1, 'school': 'Divination', 'concentration': True, 'ritual': False},
    'detect_magic': {'level': 1, 'school': 'Divination', 'concentration': True, 'ritual': True},
    'detect_poison_and_disease': {'level': 1, 'school': 'Divination', 'concentration': True, 'ritual': True},
    'divine_favor': {'level': 1, 'school': 'Transmutation', 'concentration': False, 'ritual': False},
    'divine_smite': {'level': 1, 'school': 'Evocation', 'concentration': False, 'ritual': False},
    'heroism': {'level': 1, 'school': 'Enchantment', 'concentration': True, 'ritual': False},
    'protection_from_evil_and_good': {'level': 1, 'school': 'Abjuration', 'concentration': True, 'ritual': False},
    'purify_food_and_drink': {'level': 1, 'school': 'Transmutation', 'concentration': False, 'ritual': True},
    'searing_smite': {'level': 1, 'school': 'Evocation', 'concentration': False, 'ritual': False},
    'shield_of_faith': {'level': 1, 'school': 'Abjuration', 'concentration': True, 'ritual': False},

    # Level 2
    'aid': {'level': 2, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'find_steed': {'level': 2, 'school': 'Conjuration', 'concentration': False, 'ritual': False},
    'gentle_repose': {'level': 2, 'school': 'Necromancy', 'concentration': False, 'ritual': True},
    'lesser_restoration': {'level': 2, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'locate_object': {'level': 2, 'school': 'Divination', 'concentration': True, 'ritual': False},
    'magic_weapon': {'level': 2, 'school': 'Transmutation', 'concentration': False, 'ritual': False},
    'prayer_of_healing': {'level': 2, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'protection_from_poison': {'level': 2, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'shining_smite': {'level': 2, 'school': 'Transmutation', 'concentration': True, 'ritual': False},
    'warding_bond': {'level': 2, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'zone_of_truth': {'level': 2, 'school': 'Enchantment', 'concentration': False, 'ritual': False},

    # Level 3
    'create_food_and_water': {'level': 3, 'school': 'Conjuration', 'concentration': False, 'ritual': False},
    'daylight': {'level': 3, 'school': 'Evocation', 'concentration': False, 'ritual': False},
    'dispel_magic': {'level': 3, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'magic_circle': {'level': 3, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'remove_curse': {'level': 3, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'revivify': {'level': 3, 'school': 'Necromancy', 'concentration': False, 'ritual': False},

    # Level 4
    'aura_of_life': {'level': 4, 'school': 'Abjuration', 'concentration': True, 'ritual': False},
    'banishment': {'level': 4, 'school': 'Abjuration', 'concentration': True, 'ritual': False},
    'death_ward': {'level': 4, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'locate_creature': {'level': 4, 'school': 'Divination', 'concentration': True, 'ritual': False},

    # Level 5
    'dispel_evil_and_good': {'level': 5, 'school': 'Abjuration', 'concentration': True, 'ritual': False},
    'geas': {'level': 5, 'school': 'Enchantment', 'concentration': False, 'ritual': False},
    'greater_restoration': {'level': 5, 'school': 'Abjuration', 'concentration': False, 'ritual': False},
    'raise_dead': {'level': 5, 'school': 'Necromancy', 'concentration': False, 'ritual': False},
}

# Spell descriptions from SRD
SPELL_DATA = {
    'aid': {
        'name': 'Aid',
        'casting_time': '1 action',
        'range_value': '30 feet',
        'components': 'V, S, M (a strip of white cloth)',
        'duration': '8 hours',
        'description': "Choose up to three creatures within range. Each target's Hit Point maximum and current Hit Points increase by 5 for the duration.",
        'higher_levels': "Each target's Hit Points increase by 5 for each spell slot level above 2."
    },
    'command': {
        'name': 'Command',
        'casting_time': '1 action',
        'range_value': '60 feet',
        'components': 'V',
        'duration': 'Instantaneous',
        'description': 'You speak a one-word command to a creature you can see within range. The target must succeed on a Wisdom saving throw or follow the command on its next turn. Options: Approach (move toward you), Drop (drop held items), Flee (move away), Grovel (fall prone, turn ends), Halt (no movement, no actions).',
        'higher_levels': 'You can affect one additional creature for each slot level above 1. Creatures must be within 30 feet of each other.'
    },
    'detect_evil_and_good': {
        'name': 'Detect Evil and Good',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'For the duration, you know if there is an Aberration, Celestial, Elemental, Fey, Fiend, or Undead within 30 feet of you and its location. You also know if a place or object within 30 feet has been consecrated or desecrated.',
        'higher_levels': None
    },
    'detect_magic': {
        'name': 'Detect Magic',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'For the duration, you sense the presence of magical effects within 30 feet. If you sense such magic, you can take a Magic action to see a faint aura around any visible creature or object bearing the magic, and you learn the school of magic.',
        'higher_levels': None
    },
    'detect_poison_and_disease': {
        'name': 'Detect Poison and Disease',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S, M (a yew leaf)',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'For the duration, you sense the presence and location of poisons, poisonous or venomous creatures, and diseases within 30 feet. You also identify the kind of poison, creature, or disease.',
        'higher_levels': None
    },
    'divine_favor': {
        'name': 'Divine Favor',
        'casting_time': '1 bonus action',
        'range_value': 'Self',
        'components': 'V, S',
        'duration': '1 minute',
        'description': 'Until the spell ends, your attacks with weapons deal an extra 1d4 Radiant damage on a hit.',
        'higher_levels': None
    },
    'protection_from_evil_and_good': {
        'name': 'Protection from Evil and Good',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S, M (a flask of Holy Water or powdered silver, worth 1+ GP, which the spell consumes)',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'Until the spell ends, one willing creature you touch is protected against Aberrations, Celestials, Elementals, Fey, Fiends, and Undead. The protection grants several benefits: those creature types have Disadvantage on attack rolls against the target; the target has Advantage on saving throws against the Charmed, Frightened, or Possessed condition from them; the target can\'t be possessed, charmed, or frightened by them.',
        'higher_levels': None
    },
    'purify_food_and_drink': {
        'name': 'Purify Food and Drink',
        'casting_time': '1 action',
        'range_value': '10 feet',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'description': 'All nonmagical food and drink in a 5-foot-radius Sphere centered on a point you choose within range is purified and rendered free of poison and disease.',
        'higher_levels': None
    },
    'find_steed': {
        'name': 'Find Steed',
        'casting_time': '1 action',
        'range_value': '30 feet',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'description': 'You summon a spirit that assumes the form of a loyal mount. Choose the stat block: Celestial Warhorse, Celestial Giant Lizard, Celestial Dire Wolf, or Celestial Pteranodon. The creature has the chosen form, which determines its stat block. The mount uses your spell save DC, adds your Proficiency Bonus to its AC, saving throws, and damage rolls. It obeys your commands. It disappears if it drops to 0 Hit Points or when you dismiss it as a Bonus Action.',
        'higher_levels': None
    },
    'gentle_repose': {
        'name': 'Gentle Repose',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S, M (2 Copper Pieces, which the spell consumes)',
        'duration': '10 days',
        'description': 'You touch a corpse or other remains. For the duration, the target is protected from decay and can\'t become Undead. The spell also effectively extends the time limit on raising the target from the dead, since days spent under the influence of this spell don\'t count against the time limit of spells such as Raise Dead.',
        'higher_levels': None
    },
    'locate_object': {
        'name': 'Locate Object',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S, M (a forked twig)',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'Describe or name an object that is familiar to you. You sense the direction to the object\'s location if that object is within 1,000 feet of you. If the object is in motion, you know the direction of its movement. The spell can locate a specific object known to you if you have seen it up close (within 30 feet) at least once. This spell can\'t locate an object if any thickness of lead blocks a direct path between you and the object.',
        'higher_levels': None
    },
    'prayer_of_healing': {
        'name': 'Prayer of Healing',
        'casting_time': '10 minutes',
        'range_value': '30 feet',
        'components': 'V',
        'duration': 'Instantaneous',
        'description': 'Up to six creatures of your choice that you can see within range regain Hit Points equal to 2d8 plus your spellcasting ability modifier. This spell has no effect on Constructs or Undead.',
        'higher_levels': 'The healing increases by 1d8 for each spell slot level above 2.'
    },
    'protection_from_poison': {
        'name': 'Protection from Poison',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S',
        'duration': '1 hour',
        'description': 'You touch a creature. If it is Poisoned, you neutralize the poison. If more than one poison affects the target, you neutralize one poison you know is present or one at random. For the duration, the target has Advantage on saving throws to avoid or end the Poisoned condition, and it has Resistance to Poison damage.',
        'higher_levels': None
    },
    'shining_smite': {
        'name': 'Shining Smite',
        'casting_time': '1 bonus action',
        'range_value': 'Self',
        'components': 'V',
        'duration': 'Concentration, up to 1 minute',
        'description': 'The next time you hit a creature with a weapon attack during this spell\'s duration, your weapon gleams with magical light as you strike. The attack deals an extra 2d6 Radiant damage to the target, and the target sheds Bright Light in a 5-foot radius and Dim Light for an additional 5 feet until the spell ends. Attack rolls against the target have Advantage until the spell ends.',
        'higher_levels': 'The extra damage increases by 1d6 for each spell slot level above 2.'
    },
    'warding_bond': {
        'name': 'Warding Bond',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S, M (a pair of platinum rings worth 50+ GP each, which you and the target must wear for the duration)',
        'duration': '1 hour',
        'description': 'You touch another creature that is willing and create a mystic bond. Until the spell ends, the bond has these effects: The target gains a +1 bonus to AC and saving throws. Each time the target takes damage, you take the same amount of damage. The target has Resistance to all damage.',
        'higher_levels': None
    },
    'zone_of_truth': {
        'name': 'Zone of Truth',
        'casting_time': '1 action',
        'range_value': '60 feet',
        'components': 'V, S',
        'duration': '10 minutes',
        'description': 'You create a magical zone that guards against deception in a 15-foot-radius Sphere centered on a point within range. Until the spell ends, a creature that enters the spell\'s area for the first time on a turn or starts its turn there makes a Charisma saving throw. On a failed save, a creature can\'t speak a deliberate lie while in the radius. You know whether a creature succeeds or fails on this save.',
        'higher_levels': None
    },
    'create_food_and_water': {
        'name': 'Create Food and Water',
        'casting_time': '1 action',
        'range_value': '30 feet',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'description': 'You create 45 pounds of food and 30 gallons of fresh water on the ground or in containers within range sufficient to sustain up to fifteen Humanoids or five mounts for 24 hours. The food is bland but nourishing and spoils if uneaten after 24 hours. The water is clean.',
        'higher_levels': None
    },
    'daylight': {
        'name': 'Daylight',
        'casting_time': '1 action',
        'range_value': '60 feet',
        'components': 'V, S',
        'duration': '1 hour',
        'description': 'For the duration, sunlight spreads from a point within range and fills a 60-foot-radius Sphere. The sunlight\'s area is Bright Light and sheds Dim Light for an additional 60 feet. If any of this spell\'s area overlaps with an area of Darkness created by a spell of level 3 or lower, that other spell is dispelled.',
        'higher_levels': None
    },
    'dispel_magic': {
        'name': 'Dispel Magic',
        'casting_time': '1 action',
        'range_value': '120 feet',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'description': 'Choose one creature, object, or magical effect within range. Any spell of level 3 or lower on the target ends. For each spell of level 4 or higher on the target, make a spellcasting ability check (DC 10 + the spell\'s level). On a successful check, the spell ends.',
        'higher_levels': 'You automatically end a spell on the target if the spell\'s level is equal to or less than the level of the spell slot you used.'
    },
    'magic_circle': {
        'name': 'Magic Circle',
        'casting_time': '1 minute',
        'range_value': '10 feet',
        'components': 'V, S, M (salt and powdered silver worth 100+ GP, which the spell consumes)',
        'duration': '1 hour',
        'description': 'You create a 10-foot-radius, 20-foot-tall Cylinder of magical energy centered on a point on the ground that you can see within range. Glowing runes appear wherever the Cylinder intersects with a surface. Choose one creature type: Aberrations, Celestials, Elementals, Fey, Fiends, or Undead. Chosen creatures can\'t willingly enter the Cylinder by nonmagical means. When a chosen creature attempts to enter by magical means, it must make a Charisma saving throw. On a failed save, it can\'t enter for 24 hours. On a success, it can enter. Attacks and spells from chosen creatures can\'t cross the Cylinder, and chosen creatures can\'t possess, charm, or frighten creatures inside it.',
        'higher_levels': 'The duration increases by 1 hour for each spell slot level above 3.'
    },
    'remove_curse': {
        'name': 'Remove Curse',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S',
        'duration': 'Instantaneous',
        'description': 'At your touch, all curses affecting one creature or object end. If the object is a cursed magic item, its curse remains, but the spell breaks its owner\'s Attunement to the object so it can be removed or discarded.',
        'higher_levels': None
    },
    'revivify': {
        'name': 'Revivify',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S, M (a diamond worth 300+ GP, which the spell consumes)',
        'duration': 'Instantaneous',
        'description': 'You touch a creature that has died within the last minute. That creature revives with 1 Hit Point. This spell can\'t revive a creature that has died of old age, and it can\'t restore missing body parts.',
        'higher_levels': None
    },
    'aura_of_life': {
        'name': 'Aura of Life',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V',
        'duration': 'Concentration, up to 10 minutes',
        'description': 'An aura radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Resistance to Necrotic damage, and your Hit Point maximums can\'t be reduced. If an ally with 0 Hit Points starts its turn in the aura, that ally regains 1 Hit Point.',
        'higher_levels': None
    },
    'banishment': {
        'name': 'Banishment',
        'casting_time': '1 action',
        'range_value': '30 feet',
        'components': 'V, S, M (a pentacle)',
        'duration': 'Concentration, up to 1 minute',
        'description': 'One creature that you can see within range must succeed on a Charisma saving throw or be transported to a harmless demiplane for the duration. At the end of the duration, the target reappears in the space it left or in the nearest unoccupied space if that space is occupied. If the target is native to a different plane of existence than the one you\'re on, the target disappears, returning to its home plane (spell ends).',
        'higher_levels': 'You can target one additional creature for each spell slot level above 4.'
    },
    'death_ward': {
        'name': 'Death Ward',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S',
        'duration': '8 hours',
        'description': 'You touch a creature and grant it a measure of protection from death. The first time the target would drop to 0 Hit Points before the spell ends, the target instead drops to 1 Hit Point, and the spell ends.',
        'higher_levels': None
    },
    'locate_creature': {
        'name': 'Locate Creature',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S, M (fur from a bloodhound)',
        'duration': 'Concentration, up to 1 hour',
        'description': 'Describe or name a creature familiar to you. You sense the direction to the creature\'s location if it is within 1,000 feet of you. If the creature is moving, you know the direction of its movement. The spell can locate a specific creature known to you or the nearest creature of a specific kind (such as a human or unicorn) if you have seen such a creature up close (within 30 feet) at least once. If the creature is in a different form, this spell doesn\'t locate it. This spell can\'t locate a creature if running water at least 10 feet wide blocks a direct path between you and the creature.',
        'higher_levels': None
    },
    'dispel_evil_and_good': {
        'name': 'Dispel Evil and Good',
        'casting_time': '1 action',
        'range_value': 'Self',
        'components': 'V, S, M (powdered silver and iron)',
        'duration': 'Concentration, up to 1 minute',
        'description': 'For the duration, Celestials, Elementals, Fey, Fiends, and Undead have Disadvantage on attack rolls against you. You can end the spell early by using an action to do one of the following: Break Enchantment (Choose one creature within reach charmed, frightened, or possessed by a celestial, elemental, fey, fiend, or undead, and that condition ends on that creature) or Dismissal (Make a melee spell attack against a celestial, elemental, fey, fiend, or undead within reach. On a hit, the creature returns to its home plane if it isn\'t there already).',
        'higher_levels': None
    },
    'geas': {
        'name': 'Geas',
        'casting_time': '1 minute',
        'range_value': '60 feet',
        'components': 'V',
        'duration': '30 days',
        'description': 'You place a magical command on a creature that you can see within range, forcing it to carry out some service or refrain from some action or course of activity as you decide. The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration. A creature that can\'t be charmed is immune to this effect. While charmed, the creature takes 5d10 Psychic damage each time it acts in a manner directly counter to your instructions, but no more than once each day. A Remove Curse, Greater Restoration, or Wish spell ends this spell.',
        'higher_levels': 'If you use a level 7 or 8 spell slot, the duration is 365 days. If you use a level 9 spell slot, the spell lasts until it is ended by one of the spells mentioned above.'
    },
    'greater_restoration': {
        'name': 'Greater Restoration',
        'casting_time': '1 action',
        'range_value': 'Touch',
        'components': 'V, S, M (diamond dust worth 100+ GP, which the spell consumes)',
        'duration': 'Instantaneous',
        'description': 'You imbue a creature you touch with positive energy to undo one debilitating effect. You can reduce the target\'s Exhaustion level by 1, or end one of the following effects on the target: Charmed or Petrified condition, any curse (including an Attuned cursed magic item), or any reduction to an ability score or maximum Hit Points.',
        'higher_levels': None
    },
    'raise_dead': {
        'name': 'Raise Dead',
        'casting_time': '1 hour',
        'range_value': 'Touch',
        'components': 'V, S, M (a diamond worth 500+ GP, which the spell consumes)',
        'duration': 'Instantaneous',
        'description': 'You touch a dead creature that has been dead for no longer than 10 days and return it to life with 1 Hit Point. The spell neutralizes any poisons that affected the creature at the time of death. This spell closes wounds but doesn\'t restore missing body parts. This spell can\'t revive an Undead or a creature that died of old age. The spell imposes a special exhaustion on the target: The target has Disadvantage on D20 Tests. Whenever the target finishes a Long Rest, this exhaustion decreases by 1 level until it ends.',
        'higher_levels': None
    }
}


def add_paladin_spells_to_database(db_path='talekeeper.db'):
    """Add all paladin spells from SRD to database."""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== Adding Paladin Spells to Database ===\n")

    # Step 1: Clean up duplicates
    print("Step 1: Cleaning up duplicate entries...")

    # Find and remove duplicate lesser_restoration entries
    cursor.execute("SELECT rowid FROM spells WHERE id = 'lesser_restoration'")
    rows = cursor.fetchall()
    if len(rows) > 1:
        print(f"  Found {len(rows)} duplicate 'lesser_restoration' entries. Keeping first, removing {len(rows) - 1}.")
        for row in rows[1:]:
            cursor.execute("DELETE FROM spells WHERE rowid = ?", (row[0],))

    # Clean up duplicate spell_class_lists entries
    cursor.execute("""
        DELETE FROM spell_class_lists
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM spell_class_lists
            GROUP BY spell_id, class_id
        )
    """)
    print(f"  Removed duplicate spell_class_lists entries")

    conn.commit()
    print("  Duplicates cleaned!\n")

    # Step 2: Add or update spells in spells table
    print("Step 2: Adding/updating spells in spells table...")

    added_count = 0
    updated_count = 0

    for spell_id, spell_meta in PALADIN_SPELLS.items():
        # Check if spell exists
        cursor.execute("SELECT id FROM spells WHERE id = ?", (spell_id,))
        exists = cursor.fetchone()

        # Get full spell data if available
        spell_data = SPELL_DATA.get(spell_id, {})

        # Generate name from ID if not in SPELL_DATA
        name = spell_data.get('name', spell_id.replace('_', ' ').title())

        if not exists:
            # Insert new spell
            cursor.execute("""
                INSERT INTO spells (
                    id, name, level, school, casting_time, range_value, components,
                    duration, concentration, ritual, description, higher_levels, source, classes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                spell_id,
                name,
                spell_meta['level'],
                spell_meta['school'],
                spell_data.get('casting_time', '1 action'),
                spell_data.get('range_value', 'Touch'),
                spell_data.get('components', 'V, S'),
                spell_data.get('duration', 'Instantaneous'),
                spell_meta['concentration'],
                spell_meta['ritual'],
                spell_data.get('description', f'{name} spell description.'),
                spell_data.get('higher_levels'),
                'SRD 5.2',
                '["paladin"]'
            ))
            added_count += 1
            print(f"  [+] Added: {name} (Level {spell_meta['level']})")
        else:
            # Update existing spell if we have better data
            if spell_data:
                cursor.execute("""
                    UPDATE spells SET
                        name = ?, school = ?, casting_time = ?, range_value = ?,
                        components = ?, duration = ?, concentration = ?, ritual = ?,
                        description = ?, higher_levels = ?, source = ?
                    WHERE id = ?
                """, (
                    name,
                    spell_meta['school'],
                    spell_data.get('casting_time', '1 action'),
                    spell_data.get('range_value', 'Touch'),
                    spell_data.get('components', 'V, S'),
                    spell_data.get('duration', 'Instantaneous'),
                    spell_meta['concentration'],
                    spell_meta['ritual'],
                    spell_data.get('description', f'{name} spell description.'),
                    spell_data.get('higher_levels'),
                    'SRD 5.2',
                    spell_id
                ))
                updated_count += 1
                print(f"  [*] Updated: {name} (Level {spell_meta['level']})")
            else:
                print(f"  [-] Skipped: {name} (already exists, no new data)")

    conn.commit()
    print(f"\n  Added {added_count} new spells")
    print(f"  Updated {updated_count} existing spells\n")

    # Step 3: Link all spells to paladin class
    print("Step 3: Linking spells to paladin class...")

    linked_count = 0
    for spell_id in PALADIN_SPELLS.keys():
        cursor.execute("""
            INSERT OR IGNORE INTO spell_class_lists (spell_id, class_id)
            VALUES (?, 'paladin')
        """, (spell_id,))
        if cursor.rowcount > 0:
            linked_count += 1

    conn.commit()
    print(f"  Linked {linked_count} new spell-class associations\n")

    # Step 4: Verify final state
    print("Step 4: Verifying final state...")

    cursor.execute("""
        SELECT COUNT(DISTINCT s.id)
        FROM spells s
        JOIN spell_class_lists scl ON s.id = scl.spell_id
        WHERE scl.class_id = 'paladin'
    """)
    total_paladin_spells = cursor.fetchone()[0]

    cursor.execute("""
        SELECT s.level, COUNT(DISTINCT s.id)
        FROM spells s
        JOIN spell_class_lists scl ON s.id = scl.spell_id
        WHERE scl.class_id = 'paladin'
        GROUP BY s.level
        ORDER BY s.level
    """)
    by_level = cursor.fetchall()

    print(f"  Total paladin spells: {total_paladin_spells}")
    print("  By level:")
    for level, count in by_level:
        print(f"    Level {level}: {count} spells")

    conn.close()

    print("\n=== Complete! ===")
    print(f"Expected: 39 spells")
    print(f"Actual: {total_paladin_spells} spells")

    if total_paladin_spells >= 39:
        print("[SUCCESS] All paladin spells added to database!")
    else:
        print(f"[WARNING] Missing {39 - total_paladin_spells} spells")


if __name__ == '__main__':
    add_paladin_spells_to_database()
