# Monster XML Database Guide

## Overview

TaleKeeper's monster database uses XML format to store D&D 2024 SRD monsters with support for images and database validation.

## File Locations

- **Complete Monster Database**: `database/seeds/monsters_complete.xml` (all 331 SRD monsters)
- **Source JSON**: `monsters_extracted.json` (raw extraction from SRD)
- **Generator Tool**: `tools/generate_monsters_xml.py`
- **Sample Template**: `database/seeds/monsters.xml` (first 2 monsters as examples)

## XML Structure

```xml
<monster id="aboleth" validate_stats="true">
  <name>Aboleth</name>
  <image_path>images/monsters/aboleth.png</image_path>

  <basic_info>
    <size>Large</size>
    <type>Aberration</type>
    <alignment>Lawful Evil</alignment>
  </basic_info>

  <combat_stats>
    <ac>17</ac>
    <initiative>+7</initiative>
    <initiative_score>17</initiative_score>
    <hp>150</hp>
    <hp_dice>20d10 + 40</hp_dice>
    <speed>10 ft., Swim 40 ft.</speed>
  </combat_stats>

  <ability_scores>
    <str value="21" mod="+5" save="+5"/>
    <dex value="9" mod="-1" save="+3"/>
    <con value="15" mod="+2" save="+6"/>
    <int value="18" mod="+4" save="+8"/>
    <wis value="15" mod="+2" save="+6"/>
    <cha value="18" mod="+4" save="+4"/>
  </ability_scores>

  <skills>History +12, Perception +10</skills>
  <resistances></resistances>
  <vulnerabilities></vulnerabilities>
  <immunities></immunities>
  <senses>Darkvision 120 ft.; Passive Perception 20</senses>
  <languages>Deep Speech; telepathy 120 ft.</languages>

  <cr>10</cr>
  <xp>5900</xp>
  <xp_in_lair>7200</xp_in_lair>
  <pb>+4</pb>

  <traits>
    <trait>
      <name>Amphibious</name>
      <description>The aboleth can breathe air and water.</description>
    </trait>
    <trait>
      <name>Legendary Resistance</name>
      <usage>3/Day, or 4/Day in Lair</usage>
      <description>If the aboleth fails a saving throw, it can choose to succeed instead.</description>
    </trait>
  </traits>

  <actions>
    <action type="multiattack">
      <name>Multiattack</name>
      <description>The aboleth makes two Tentacle attacks and uses either Consume Memories or Dominate Mind if available.</description>
    </action>
    <action type="melee">
      <name>Tentacle</name>
      <attack_bonus>+9</attack_bonus>
      <reach>15 ft.</reach>
      <description>Melee Attack Roll: +9, reach 15 ft. Hit: 12 (2d6 + 5) Bludgeoning damage...</description>
    </action>
    <action type="special">
      <name>Dominate Mind</name>
      <usage>2/Day</usage>
      <save_dc>16</save_dc>
      <save_type>Wisdom</save_type>
      <description>Wisdom Saving Throw: DC 16...</description>
    </action>
  </actions>

  <bonus_actions>
    <bonus_action>
      <name>Cunning Action</name>
      <description>The monster can take the Dash, Disengage, or Hide action.</description>
    </bonus_action>
  </bonus_actions>

  <reactions>
    <reaction>
      <name>Parry</name>
      <description>The monster adds 2 to its AC against one melee attack that would hit it.</description>
    </reaction>
  </reactions>

  <legendary_actions uses="3" uses_in_lair="4">
    <legendary_action>
      <name>Lash</name>
      <description>The aboleth makes one Tentacle attack.</description>
    </legendary_action>
  </legendary_actions>
</monster>
```

## Adding Images

1. Place monster images in `images/monsters/` directory
2. Update the `<image_path>` element:
   ```xml
   <image_path>images/monsters/aboleth.png</image_path>
   ```
3. Supported formats: PNG, JPG, WEBP

## Usage Commands

### Generate XML from JSON
```bash
python tools/generate_monsters_xml.py generate monsters_extracted.json database/seeds/monsters_complete.xml
```

### Validate Monster Against Database
```bash
python tools/generate_monsters_xml.py validate "Aboleth"
python tools/generate_monsters_xml.py validate "Ancient Red Dragon" talekeeper.db
```

## Monster Attributes

### Required Fields
- `id` - Unique identifier (lowercase, underscores)
- `name` - Monster name
- `size` - Tiny/Small/Medium/Large/Huge/Gargantuan
- `type` - Creature type (Aberration, Beast, etc.)
- `ac` - Armor Class
- `hp` - Hit Points
- `speed` - Movement speeds
- `ability_scores` - All 6 abilities with mods and saves
- `cr` - Challenge Rating
- `xp` - Experience Points

### Optional Fields
- `image_path` - Path to image file
- `xp_in_lair` - XP when fought in lair
- `skills` - Skill bonuses
- `resistances` - Damage resistances
- `vulnerabilities` - Damage vulnerabilities
- `immunities` - Damage and condition immunities
- `traits` - Passive abilities
- `actions` - Standard actions
- `bonus_actions` - Bonus action options
- `reactions` - Reaction options
- `legendary_actions` - Legendary action options

## Action Types

Actions are categorized:
- `type="multiattack"` - Multiattack action
- `type="melee"` - Melee weapon attack
- `type="ranged"` - Ranged weapon attack
- `type="special"` - Special ability or spell

## Usage Notations

- `<usage>3/Day</usage>` - Limited daily uses
- `<usage>Recharge 5-6</usage>` - Recharge on d6 roll
- `<usage>Recharge after Short or Long Rest</usage>` - Rest recharge

## Monster Statistics

### Total Monsters: 331

### By Challenge Rating
- CR 0: 29 monsters
- CR 1/8 to 1/2: 78 monsters
- CR 1-5: 132 monsters
- CR 6-10: 37 monsters
- CR 11-20: 28 monsters
- CR 21-30: 12 monsters

### By Type
- Beast: 77
- Monstrosity: 30
- Humanoid: 21
- Dragon (Chromatic): 20
- Dragon (Metallic): 20
- Elemental: 15
- Undead: 12
- Fiend (Devils + Demons): 11
- Celestial: 10
- Construct: 10
- Others: 105

## Custom Monsters

To add custom monsters, use `source="custom"`:

```xml
<monster id="custom_basilisk" validate_stats="false" source="custom">
  <name>Volcanic Basilisk</name>
  <image_path>images/monsters/custom/volcanic_basilisk.png</image_path>
  <!-- rest of monster definition -->
</monster>
```

## Database Integration

When `validate_stats="true"`, the monster can be checked against the database:

1. Ensure monster exists in `monsters` table
2. Compare XML stats with DB stats
3. Flag discrepancies for review

## Best Practices

1. Always provide complete stat blocks
2. Include image paths even if empty (for future use)
3. Use descriptive action type attributes
4. Document custom abilities clearly
5. Validate against SRD for official monsters
6. Use `validate_stats="false"` for homebrew content

## Notes

- All 331 SRD monsters are included in `monsters_complete.xml`
- Images can be added incrementally as needed
- XML can be parsed by Python, C#, or any XML parser
- Consider breaking into multiple files by CR or type for easier management

## Future Enhancements

- Monster tags/keywords for searching
- Encounter difficulty calculator
- Lair actions section
- Regional effects section
- Monster variant support
- Scaling options for different party levels
