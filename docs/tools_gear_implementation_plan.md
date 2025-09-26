# Tools and Adventuring Gear Implementation Plan

## Overview
This document outlines the mechanical implementation of D&D 2024 tools and adventuring gear in TaleKeeper, focusing on their gameplay impacts beyond simple inventory management.

## Core Systems Required

### 1. Tool Proficiency System
- **Database Tables**:
  - `tool_proficiencies` (character_id, tool_type, proficient)
  - `tool_definitions` (tool_id, name, ability, dc_values, craftable_items)
- **Mechanical Impact**:
  - Add Proficiency Bonus to ability checks using the tool
  - Grant Advantage if also proficient in the relevant skill
  - Enable Utilize action options with DCs

### 2. Utilize Action Framework
- New action type alongside Attack, Dash, Dodge, etc.
- Context-sensitive based on equipped/accessible items
- Turn-based economy tracking (action vs bonus action usage)

### 3. Environmental Hazard System
- Fall damage calculation and mitigation
- Terrain difficulty modifiers
- Environmental condition tracking (extreme cold, etc.)

## Priority 1: Combat-Relevant Items

### Offensive Items
**Acid (25 GP)**
- Replace attack with throw action
- Range: 20 feet
- DC: 8 + Dex modifier + Proficiency Bonus
- Damage: 2d6 acid on failed save
- Implementation: New action card, consumable tracking

**Alchemist's Fire (50 GP)**
- Replace attack with throw action
- Range: 20 feet
- DC: 8 + Dex modifier + Proficiency Bonus
- Damage: 1d4 fire + burning condition
- Implementation: Condition system integration for burning

**Holy Water (25 GP)**
- Replace attack with throw action
- Range: 20 feet
- DC: 8 + Dex modifier + Proficiency Bonus
- Damage: 2d8 radiant (Fiend/Undead only)
- Implementation: Target type validation

**Oil (1 SP)**
- Multiple uses: throw, pour, fuel
- Thrown: DC save or covered in oil (+5 fire damage if ignited)
- Poured: 5-foot area, 5 fire damage/turn for 2 rounds
- Implementation: Area effect system, duration tracking

**Basic Poison (100 GP)**
- Bonus action to apply
- +1d4 poison damage for 1 minute or first hit
- Implementation: Weapon enhancement system, timer

**Net (1 GP)**
- Replace attack with throw
- Range: 15 feet
- DC: 8 + Dex modifier + Proficiency Bonus
- Effect: Restrained condition (auto-fail if Huge+)
- Escape: DC 10 Strength check or destroy (AC 10, 5 HP)

### Defensive/Utility Combat Items
**Ball Bearings (1 GP)**
- Utilize action to deploy
- 10-foot square area
- DC 10 Dex save or Prone condition
- Implementation: Area hazard system

**Caltrops (1 GP)**
- Utilize action to deploy
- 5-foot square area
- DC 15 Dex save or 1 piercing damage + speed 0
- Implementation: Movement penalty system

**Hunting Trap (5 GP)**
- Utilize action to set
- DC 13 Dex save or 1d4 piercing + speed 0
- Escape: DC 13 Strength check (1 damage on fail)
- Implementation: Persistent trap objects

## Priority 2: Exploration & Skill Items

### Climbing/Movement
**Climber's Kit (25 GP)**
- **Critical Mechanic**: Limits fall to 25 feet (max 2d6 damage)
- Utilize action to anchor
- Movement restricted to 25 feet from anchor
- Bonus action to remove anchor
- Implementation: Fall damage override, movement range limiter

**Grappling Hook (2 GP)**
- DC 13 Dexterity (Acrobatics) to secure
- Range: 50 feet
- Enables rope climbing
- Implementation: Terrain interaction system

**Rope (1 GP)**
- DC 10 Sleight of Hand to tie knots
- DC 20 Strength to burst
- Can bind Grappled/Incapacitated/Restrained creatures
- DC 15 Acrobatics to escape

### Vision/Detection
**Torch (1 CP)**
- Bright light: 20-foot radius
- Dim light: additional 20 feet
- Duration: 1 hour
- Can attack for 1 fire damage

**Lantern, Hooded (5 GP)**
- Bright light: 30-foot radius
- Dim light: additional 30 feet
- Bonus action to hood (5-foot dim only)

**Lantern, Bullseye (10 GP)**
- Bright light: 60-foot cone
- Dim light: additional 60 feet

**Spyglass (1,000 GP)**
- 2x magnification
- Implementation: Perception check bonuses

### Skill Enhancement Items
**Crowbar (2 GP)**
- Advantage on Strength checks where leverage applies
- Implementation: Context-sensitive advantage

**Magnifying Glass (100 GP)**
- Advantage on appraise/inspect checks
- Can start fires with sunlight (5 minutes)

**Thieves' Tools (25 GP)**
- DC 15 to pick locks or disarm traps
- Add proficiency bonus if proficient
- Implementation: Lock/trap interaction system

**Healer's Kit (5 GP)**
- 10 uses
- Stabilize at 0 HP without Medicine check
- Implementation: Death save bypass

**Portable Ram (4 GP)**
- +4 to Strength checks to break doors
- Advantage if assisted
- Implementation: Door/barrier system

### Environmental Protection
**Bedroll (1 GP)**
- Auto-succeed saves vs extreme cold
- Implementation: Environmental condition immunity

**Blanket (5 SP)**
- Advantage on saves vs extreme cold
- Implementation: Environmental save modifier

**Tent (2 GP)**
- Sleeps 2 Small/Medium creatures
- Implementation: Rest system enhancement

## Priority 3: Restraint & Control Items

**Manacles (2 GP)**
- DC 13 Sleight of Hand to apply
- Disadvantage on attacks
- Restrained if attached to fixed point
- Escape: DC 20 Sleight of Hand or DC 25 Strength

**Chain (5 GP)**
- DC 13 Athletics to wrap
- Restrained condition if legs bound
- Escape: DC 18 Acrobatics or DC 20 Strength

## Priority 4: Tool Utilize Actions

### Artisan's Tools
**Alchemist's Supplies**
- Identify substance (DC 15)
- Start fire (DC 15)

**Carpenter's Tools**
- Seal/pry door (DC 20)

**Cook's Utensils**
- Detect poisoned food (DC 15)
- Improve flavor (DC 10)

**Cobbler's Tools**
- Grant Advantage on next Acrobatics check (DC 10)

**Mason's Tools**
- Chisel symbols in stone (DC 10)

### Specialized Tools
**Disguise Kit**
- Apply makeup (DC 10)
- Craft costumes

**Forgery Kit**
- Mimic handwriting (DC 15)
- Duplicate wax seal (DC 20)

**Herbalism Kit**
- Identify plants (DC 10)
- Craft healing potions

**Poisoner's Kit**
- Detect poisoned objects (DC 10)
- Craft basic poison

## Implementation Phases

### Phase 1: Core Systems (Week 1-2)
1. Utilize action framework
2. Tool proficiency system
3. Item consumption tracking
4. Basic thrown weapon attacks (acid, alchemist's fire, holy water)

### Phase 2: Combat Items (Week 3-4)
1. Area effect system (ball bearings, caltrops, oil)
2. Condition application (net, burning, poisoned)
3. Trap mechanics (hunting trap)
4. Weapon coating system (poison)

### Phase 3: Exploration Tools (Week 5-6)
1. Climbing/fall damage mitigation (climber's kit)
2. Light source management (torches, lanterns)
3. Skill check modifiers (crowbar, magnifying glass)
4. Lock/trap interaction (thieves' tools)

### Phase 4: Advanced Mechanics (Week 7-8)
1. Restraint system (manacles, chain, rope)
2. Environmental protection (bedroll, tent)
3. Tool crafting system
4. Tool utilize action DCs

## Database Schema Additions

```sql
-- Tool definitions
CREATE TABLE tool_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    ability TEXT NOT NULL, -- STR, DEX, INT, WIS, CHA
    weight REAL,
    cost_gp INTEGER
);

-- Character tool proficiencies
CREATE TABLE character_tool_proficiencies (
    character_id TEXT,
    tool_type_id TEXT,
    proficient BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (tool_type_id) REFERENCES tool_types(id)
);

-- Gear special properties
CREATE TABLE gear_properties (
    item_id TEXT,
    property_type TEXT, -- 'thrown', 'area', 'light', 'protection', etc.
    property_data TEXT, -- JSON for flexible property storage
    FOREIGN KEY (item_id) REFERENCES equipment(id)
);

-- Active environmental effects
CREATE TABLE active_effects (
    id TEXT PRIMARY KEY,
    encounter_id TEXT,
    effect_type TEXT, -- 'caltrops', 'ball_bearings', 'oil_fire', etc.
    position_x INTEGER,
    position_y INTEGER,
    duration_rounds INTEGER,
    effect_data TEXT -- JSON
);
```

## UI Integration Points

### Action Panel
- New "Utilize" action category
- Context-sensitive item actions
- Thrown weapon attack cards
- Tool use action cards

### Equipment Panel
- Quick-use item slots
- Consumable quantity tracking
- Tool proficiency indicators
- Active coating/preparation status

### Combat UI
- Area effect visualization
- Trap/hazard markers
- Light radius display
- Environmental condition indicators

### Character Sheet
- Tool proficiency list
- Environmental save modifiers
- Active item effects

## Testing Requirements

### Combat Mechanics
- Thrown item attack calculations
- Area effect damage application
- Condition application/removal
- Duration tracking

### Skill Interactions
- Tool proficiency bonus application
- Advantage/disadvantage stacking
- DC calculations
- Context-sensitive modifiers

### Environmental Systems
- Fall damage with/without climber's kit
- Light source radius calculation
- Temperature protection
- Rest quality modifiers

### Edge Cases
- Multiple overlapping area effects
- Stacking protection items
- Tool proficiency with skill proficiency
- Consumable depletion
- Large/Huge creature immunities

## Performance Considerations
- Cache frequently accessed tool properties
- Batch area effect calculations
- Optimize light source visibility checks
- Lazy-load crafting recipes

## Future Expansions
- Crafting system using tool Craft entries
- Vehicle mechanics (carts, boats)
- Mount system with barding
- Advanced trap creation
- Improvised tool use
- Magic item identification with tools