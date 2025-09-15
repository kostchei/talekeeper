# TaleKeeper Item Properties & Mechanics Implementation Plan
## Common & Uncommon Items Only

## Overview
This document outlines the item property system for TaleKeeper's COMMON and UNCOMMON rarity items, defining how items provide mechanical benefits, which equipment slots they occupy, and how to implement their effects in the game engine. This covers all items available as treasure drops from CR 0-4 monsters.

## Equipment Slot Assignments

### Current Slots Available
- **main_hand**: Primary weapon slot
- **off_hand**: Secondary weapon/shield slot
- **armor**: Body armor slot
- **helmet**: Head protection slot
- **gloves**: Hand protection slot
- **boots**: Foot protection slot
- **cloak**: Back/shoulder slot
- **ring_1**: First ring slot
- **ring_2**: Second ring slot
- **amulet**: Neck slot
- **belt**: Waist slot

### Item Type to Slot Mapping (Common & Uncommon Only)

#### Weapons (Common & Uncommon)
**Common Weapons:**
- All basic weapons (longsword, rapier, bow, etc.) → main_hand
- Light weapons (dagger, handaxe) → main_hand or off_hand
- Two-handed weapons (greatsword, longbow) → main_hand (blocks off_hand)
- Silvered weapons → same as base weapon type

**Uncommon Weapons:**
- Greataxe +1 → main_hand (two-handed)
- Greatsword +1 → main_hand (two-handed)
- Longsword +1 → main_hand
- Rapier +1 → main_hand
- Scimitar +1 → main_hand
- Spear +1 → main_hand (versatile)
- Staff +1 → main_hand (quarterstaff, versatile)

#### Armor & Shields (Common & Uncommon)
**Common Armor:**
- Leather Armor, Studded Leather → armor slot
- Chain Mail, Chain Shirt, Scale Mail → armor slot
- Hide Armor, Ring Mail → armor slot
- Shield → off_hand

**Uncommon Armor:**
- Breastplate, Splint Armor, Plate Armor → armor slot
- Half Plate → armor slot
- Adamantine variants (Breastplate, Half Plate, Plate) → armor slot
- Mithral Chain Mail → armor slot
- Shield +1 → off_hand

#### Accessories by Slot (Uncommon Only)
**Helmet Slot:**
- Dread Helm (uncommon)

**Gloves Slot:**
- Gloves of Thievery (uncommon)

**Boots Slot:**
- Boots of Elvenkind (uncommon)

**Cloak Slot:**
- Cloak of Elvenkind (uncommon)
- Cloak of Protection (uncommon)

**Ring Slots:**
- None at common/uncommon rarity in current item list

**Amulet Slot:**
- Holy Symbol (common) - when worn as amulet
- Luckstone (uncommon) - worn as amulet/pocket item

**Belt Slot:**
- None at common/uncommon rarity in current item list

#### Special Items (Common & Uncommon)
**Spellcasting Focus (Common):**
- Holy Symbol → amulet (when worn) OR inventory (when carried)
- Arcane Focus → inventory OR main_hand (if staff)

**Spellcasting Implements (Uncommon):**
- Wand of the War Mage +1 → main_hand
- Rod of the Pact Keeper +1 → main_hand
- Book of the Devout +1 → inventory (held when casting)

**Storage/Utility:**
- Bag of Holding (uncommon) → belt OR inventory
- Backpack (common) → no slot (carried)
- Spellbook (common) → inventory

**Tools (Uncommon):**
- Thieves' Tools → inventory (used when needed)
- Herbalism Kit → inventory (used when needed)
- Poisoner's Kit → inventory (used when needed)
- All artisan tools → inventory
- Musical Instruments → main_hand (when playing) OR inventory

## Item Mechanical Effects (Common & Uncommon Only)

### Common Item Effects

#### Basic Armor AC
```
Padded: AC 11 + Dex modifier
Leather: AC 11 + Dex modifier
Studded Leather: AC 12 + Dex modifier
Hide: AC 12 + Dex modifier (max Dex +2)
Chain Shirt: AC 13 + Dex modifier (max Dex +2)
Scale Mail: AC 14 + Dex modifier (max Dex +2), Disadvantage on Stealth
Ring Mail: AC 14, Disadvantage on Stealth
Chain Mail: AC 16, Str 13 required, Disadvantage on Stealth
Shield: +2 AC
```

#### Common Weapon Properties
```
Silvered Weapons: Overcomes resistance to non-magical attacks (lycanthropes, etc.)
Light weapons: Can dual-wield
Two-handed: Uses both hands, typically higher damage
Versatile: Can use one or two hands (damage increases with two)
Finesse: Can use Dex instead of Str for attack/damage
Ranged: Uses Dex for attack/damage
```

#### Common Consumables
```
Potion of Healing: Restore 2d4+2 HP
Torch: Light 20ft bright, 20ft dim
Oil (flask): Can ignite for fire damage
Rations: Sustenance for travel
```

### Uncommon Item Effects

#### Combat Bonuses
```
+1 Weapons: +1 to attack rolls and damage rolls
Shield +1: +3 AC total (+2 base, +1 enhancement)
Wand of the War Mage +1: +1 to spell attack rolls
Rod of the Pact Keeper +1: +1 to spell attack rolls and spell save DC
```

#### Armor Properties
```
Breastplate: AC 14 + Dex modifier (max Dex +2)
Half Plate: AC 15 + Dex modifier (max Dex +2), Disadvantage on Stealth
Splint: AC 17, Str 15 required, Disadvantage on Stealth
Plate: AC 18, Str 15 required, Disadvantage on Stealth
Adamantine Armor: Immune to critical hits
Mithral Chain Mail: AC 16, No stealth disadvantage, no Str requirement
```

#### Skill & Check Bonuses
```
Gloves of Thievery: +5 to Sleight of Hand checks and Dex checks to pick locks
Boots of Elvenkind: Advantage on Dexterity (Stealth) checks
Cloak of Elvenkind: Disadvantage on Perception checks to see you
Luckstone: +1 to ability checks and saving throws (requires attunement)
```

#### Saving Throw Bonuses
```
Cloak of Protection: +1 AC and +1 to all saving throws (requires attunement)
Luckstone: +1 to all saving throws (requires attunement)
```

#### Special Properties
```
Bag of Holding: 500 lbs capacity, weighs 15 lbs, 64 cubic feet volume
Boots of Elvenkind: Steps make no sound
Cloak of Elvenkind: Hood up = heavily obscured to sight
Dread Helm: Intimidation advantage (assumed effect)
Potion of Greater Healing: Restore 4d4+4 HP
```

## Implementation Architecture

### Database Schema Additions Needed

```sql
-- Add to equipment table
ALTER TABLE equipment ADD COLUMN slot_type TEXT;
ALTER TABLE equipment ADD COLUMN ac_bonus INTEGER DEFAULT 0;
ALTER TABLE equipment ADD COLUMN attack_bonus INTEGER DEFAULT 0;
ALTER TABLE equipment ADD COLUMN damage_bonus INTEGER DEFAULT 0;
ALTER TABLE equipment ADD COLUMN saving_throw_bonus INTEGER DEFAULT 0;
ALTER TABLE equipment ADD COLUMN ability_overrides TEXT; -- JSON: {"strength": 19}
ALTER TABLE equipment ADD COLUMN skill_bonuses TEXT; -- JSON: {"sleight_of_hand": 5}
ALTER TABLE equipment ADD COLUMN special_properties TEXT; -- JSON array of effects
```

### Effect Processing Order

1. **Base Stats** - Character's natural abilities
2. **Ability Overrides** - Items that set abilities to specific values (e.g., Headband of Intellect)
3. **Ability Bonuses** - Items that add to abilities
4. **AC Calculation**:
   - Base AC (10 + Dex or armor base)
   - Shield bonus (+2 or more)
   - Item bonuses (rings, cloaks)
   - Class features (Defense fighting style)
5. **Attack/Damage Bonuses**:
   - Ability modifier
   - Proficiency bonus
   - Magic weapon bonus
   - Class features
6. **Saving Throws**:
   - Ability modifier
   - Proficiency (if applicable)
   - Item bonuses
7. **Skill Checks**:
   - Ability modifier
   - Proficiency/expertise
   - Item bonuses

### Code Implementation Points

#### 1. Equipment Panel (equipment_panel.py)
- Validate slot compatibility when equipping
- Display item bonuses in tooltips
- Show cumulative bonuses in UI

#### 2. Game Engine (game_engine_sqlite.py)
- Add `calculate_item_bonuses()` method
- Modify `get_character_stats()` to include item effects
- Update attack/damage calculations

#### 3. Character Sheet (character_sheet.py)
- Display effective stats (base + items)
- Show item bonus breakdown on hover
- Update in real-time when equipment changes

#### 4. Combat Engine (combat_engine.py)
- Apply weapon bonuses to attack rolls
- Apply armor/shield bonuses to AC
- Check for special properties (silvered, adamantine)

### Priority Implementation Order (Common & Uncommon Items)

1. **Phase 1 - Basic Combat Items**
   - Basic armor AC calculations (all common armors)
   - Shield AC bonus (+2)
   - +1 weapons (attack & damage)
   - Shield +1 (+3 AC total)
   - Silvered weapon property

2. **Phase 2 - Uncommon Armor**
   - Breastplate, Half Plate, Splint, Plate AC
   - Adamantine armor (crit immunity)
   - Mithral Chain Mail (no stealth disadvantage)

3. **Phase 3 - Skill/Save Items**
   - Cloak of Protection (+1 AC, +1 saves)
   - Gloves of Thievery (+5 Sleight of Hand)
   - Boots of Elvenkind (Stealth advantage)
   - Luckstone (+1 to checks and saves)

4. **Phase 4 - Special Items**
   - Bag of Holding (weight reduction)
   - Wand of the War Mage +1 (spell attacks)
   - Rod of the Pact Keeper +1 (spell attacks & DC)
   - Potions (healing effects)

## Testing Checklist (Common & Uncommon Items)

- [ ] Common armor provides correct base AC
- [ ] Shield provides +2 AC
- [ ] Shield +1 provides +3 AC total
- [ ] +1 weapons add +1 to attack and damage rolls
- [ ] Cloak of Protection provides +1 AC and +1 saves
- [ ] Gloves of Thievery provide +5 to Sleight of Hand
- [ ] Boots of Elvenkind grant advantage on Stealth
- [ ] Luckstone provides +1 to ability checks and saves
- [ ] Two-handed weapons prevent off-hand use
- [ ] Silvered weapons bypass resistances
- [ ] Adamantine armor prevents critical hits
- [ ] Mithral armor has no stealth disadvantage
- [ ] Item bonuses persist through save/load
- [ ] Unequipping items removes their bonuses
- [ ] Potions can be consumed from inventory

## Notes for Implementation

1. **Stacking Rules**:
   - AC bonuses from different sources stack (armor + shield + Cloak of Protection)
   - Same type bonuses use highest (can't wear two armors)
   - Cloak of Protection and Luckstone saves would stack (+2 total)

2. **Attunement** (Uncommon items requiring attunement):
   - Cloak of Protection
   - Luckstone
   - Bag of Holding
   - Wand of the War Mage +1
   - Rod of the Pact Keeper +1

3. **Weapon Properties to Implement**:
   - Light: Enable dual-wielding
   - Two-handed: Block off-hand slot
   - Versatile: Allow damage die change
   - Finesse: Allow Dex for attack/damage
   - Silvered: Note for resistance bypass

4. **Consumables**:
   - Potions don't use slots
   - Used from inventory directly
   - Healing potions restore HP immediately

5. **Future Considerations**:
   - Scroll casting (requires spell on class list)
   - Tool proficiency checks
   - Musical instrument performance