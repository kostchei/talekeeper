# TaleKeeper Implementation Guide

**Last Updated:** 2025-10-19
**Purpose:** Comprehensive reference for understanding the current codebase implementation
**Audience:** Developers working on TaleKeeper

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Systems](#core-systems)
3. [Character Classes](#character-classes)
4. [Spell System](#spell-system)
5. [Combat & Monsters](#combat--monsters)
6. [Campaign & Exploration](#campaign--exploration)
7. [UI Components](#ui-components)
8. [Database Schema](#database-schema)
9. [Testing](#testing)

---

## Architecture Overview

### Project Structure

**NEW STRUCTURE** (as of Oct 2025 - reorganized for exe conversion):

```
TaleKeeper/
├── main.py                      # Entry point (ONLY .py in root)
├── setup.py                     # Package metadata
│
├── src/talekeeper/              # Main application package
│   ├── __init__.py
│   ├── __main__.py              # Allows: python -m talekeeper
│   ├── paths.py                 # Path helpers (dev + exe)
│   ├── core/                    # Game engine & systems
│   │   ├── game_engine_sqlite.py
│   │   ├── feature_integration.py
│   │   ├── combat_manager.py
│   │   ├── config.py
│   │   └── debug_commands.py
│   ├── services/                # Game services (50+ modules)
│   │   ├── feat_effects.py
│   │   ├── condition_manager.py
│   │   ├── subclass_registry.py
│   │   └── ...
│   ├── ui/                      # PyQt6 UI components
│   │   ├── main_window.py
│   │   ├── themes.py
│   │   ├── action_cards/
│   │   ├── character_sheet/
│   │   ├── encounter_pane/
│   │   ├── equipment_layout/
│   │   └── menu/
│   ├── audio/                   # TTS & narration
│   ├── database/                # DB initialization
│   │   └── database_init.py
│   └── models/                  # Data models
│
├── data/                        # Game data & runtime files
│   ├── monsters/                # Monster JSON data
│   ├── config/                  # Runtime configuration
│   │   └── talekeeper_config.json
│   └── assets/                  # Images, fonts, art
│
├── talekeeper.db                # SQLite database (root directory)
│
├── scripts/                     # Dev tools (excluded from exe)
│   ├── monster_tools/           # Monster data utilities
│   ├── database_tools/          # DB utilities
│   ├── character_tools/         # Character utilities
│   └── utilities/               # General utilities
│
├── tests/                       # Consolidated test suite
│   ├── run_regression_tests.py
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── qt_framework/
│
└── docs/                        # Documentation
    ├── development/
    └── reports/
```

### Import Pattern Changes
```python
# OLD (pre-Oct 2025)
from core.game_engine_sqlite import GameEngine
from services.feat_effects import FeatEffects

# NEW (current)
from talekeeper.core.game_engine_sqlite import GameEngine
from talekeeper.services.feat_effects import FeatEffects
```

### Key Technologies

- **Frontend:** PyQt6 with fixed-position UI panels
- **Backend:** SQLite database with game_engine_sqlite.py coordinator
- **Game Rules:** D&D 2024 (One D&D) ruleset implementation
- **Platform:** Windows (single-player)

---

## Core Systems

### Action Economy System

**Implementation:** Enforces D&D 5e action economy rules in combat

**Files:**
- `src/talekeeper/models/action_economy.py` - Data models
- `src/talekeeper/services/action_economy_enforcer.py` - Enforcement logic

**Core Rules:**
- 1 Action per turn (unless Action Surge)
- 1 Bonus Action per turn (if available)
- 1 Reaction per round (resets on creature's turn)
- Movement pool per turn

**Data Model:**
```python
@dataclass
class ActionEconomyState:
    combatant_id: str
    current_round: int
    action_available: bool          # Resets each turn
    bonus_action_available: bool    # Resets each turn
    reaction_available: bool        # Resets at start of creature's turn
    movement_used: int              # Out of movement_speed, resets each turn
    actions_taken_this_turn: List[Dict]
```

**UI Integration:**
- Action Panel displays: `"R3 | Action: ✗ | Bonus: ✓ | Reaction: ✓ | Move: 25ft"`
- Action cards disabled when action type not available
- Visual feedback for failed action attempts

### Feature System

**Implementation:** Scalable, professional implementation of D&D 2024 class features

**Files:**
- `src/talekeeper/core/class_features.py` - Base feature classes
- `src/talekeeper/core/feature_definitions.py` - Feature data (Fighter, Barbarian, Rogue)
- `src/talekeeper/core/feature_integration.py` - Database integration

**Feature Types:**
- **Resource Features:** Limited uses (Second Wind, Rage, Action Surge)
- **Passive Features:** Always active (Fighting Style, Unarmored Defense)
- **Triggered Features:** Activate on conditions (Sneak Attack, Brutal Strike)
- **Modal Features:** Change character state (Rage mode, Reckless Attack)
- **Action Features:** Use actions/bonus actions/reactions

**Usage:**
```python
from talekeeper.core.feature_integration import get_feature_integration

integration = get_feature_integration()

# Initialize features for a new character
success = integration.initialize_character_features(character_id)

# Get available features
features = integration.get_available_features(character_id)

# Use a feature
result = integration.use_feature(character_id, "Second Wind")
```

**Database Schema:**
```sql
CREATE TABLE feature_states (
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    uses_current INTEGER,
    uses_max INTEGER,
    configuration TEXT,  -- JSON config
    last_used TEXT,
    PRIMARY KEY (character_id, feature_name)
);
```

### Condition System

**Implementation:** Complete D&D 2024 condition support with mechanical effects

**File:** `src/talekeeper/services/condition_manager.py`

**Condition Types:** All 15 D&D 2024 conditions (Blinded, Charmed, Deafened, Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious, Exhausted)

**Features:**
- Advantage/disadvantage on attacks and saves
- Movement speed modifications
- Action restrictions
- Automatic condition saves
- Condition immunity tracking
- Exhaustion levels 1-6 with cumulative effects

**Usage:**
```python
from talekeeper.services.condition_manager import ConditionManager, ConditionType, ActiveCondition

manager = ConditionManager()
condition = ActiveCondition(
    condition_type=ConditionType.STUNNED,
    source="Hold Person spell",
    duration_type="save_ends",
    save_dc=15,
    save_ability="wisdom"
)
manager.add_condition(character_id, condition)

if manager.has_incapacitating_condition(character_id):
    # Block Danger Sense, prevent actions, etc.
```

### Scalable Subclass Architecture

**Implementation:** Modular system for 44+ subclasses across 11 classes

**Files:**
- `src/talekeeper/services/enhanced_subclass_manager.py` - Core manager
- `src/talekeeper/services/subclass_registry.py` - Registration system
- `src/talekeeper/services/subclasses/` - Modular subclass definitions

**Directory Structure:**
```
services/subclasses/
├── barbarian/
│   ├── berserker.py
│   ├── totem_warrior.py
│   └── ...
├── fighter/
│   ├── champion.py
│   ├── battle_master.py
│   └── ...
├── rogue/
│   ├── thief.py
│   ├── assassin.py
│   └── ...
└── ...
```

**Feature Types:**
- **Passive:** Always active (Brutal Critical)
- **Activated:** Player triggers (Intimidating Presence)
- **Triggered:** Automatic under conditions (Frenzy with Reckless Attack)
- **Reaction:** Response to events (Retaliation)

**Usage:**
```python
from talekeeper.services.enhanced_subclass_manager import EnhancedSubclassManager

manager = EnhancedSubclassManager()

# Get all features for a character's subclass
features = manager.get_character_subclass_features(character_id, "barbarian")

# Check if feature is available
available = manager.is_feature_available(character_id, "intimidating_presence")

# Use a feature (consumes resources)
result = manager.use_subclass_feature(character_id, "intimidating_presence")
```

### Proficiency System

**Implementation:** D&D 2024 proficiency rules for weapons, armor, skills, and saving throws

**File:** `src/talekeeper/services/proficiency_system.py`

**Main Class:** `ProficiencySystem`

**Key Methods:**
- `initialize_character_proficiencies(character_id, class_id, background, race_id, conn=None)`
- `get_character_proficiencies(character_id)`
- `is_proficient_with_weapon(character_id, weapon_name)`
- `calculate_skill_bonus(character_id, skill_name, ability_mod)`
- `get_saving_throw_bonus(character_id, ability)`
- `get_attack_bonus(character_id, weapon_name, ability_mod)`

**Proficiency Bonus Scaling (D&D 2024):**
- Levels 1-4: +2
- Levels 5-8: +3
- Levels 9-12: +4
- Levels 13-16: +5
- Levels 17-20: +6

**Database Schema:**
```sql
CREATE TABLE character_proficiencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'weapon', 'armor', 'saving_throw', 'tool', 'language'
    proficiency_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'unknown', -- 'class', 'background', 'race', 'feat', 'manual'
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, proficiency_name)
);
```

**Five Sources of Proficiencies:**
1. **Class Proficiencies** (choice-based) - Player selects from skill list
2. **Background Proficiencies** (fixed) - Auto-granted based on background
3. **Species Proficiencies** (fixed + choices) - Race-based proficiencies
4. **Feat Proficiencies** - Granted by feats (Skilled, Weapon Master, etc.)
5. **Level-up Features** (future) - Class features granting proficiencies

### Unified Class Abilities System

**Implementation:** Database-driven class abilities system replacing 6 separate services (86% code reduction)

**File:** `src/talekeeper/services/class_abilities_service.py` (500 lines)

**Database Tables:**
```sql
class_abilities (93 abilities across 5 classes)
├─ Fighter: 11 abilities
├─ Barbarian: 17 abilities
├─ Rogue: 11 abilities
├─ Paladin: 18 abilities
└─ Warlock: 26 abilities + 10 invocations

character_ability_usage (per-character resource tracking)
├─ current_uses / max_uses
├─ is_active / turns_remaining
└─ last_used / last_reset timestamps

ability_scaling_formulas (5 formulas)
├─ rage_uses_by_level (2→3→4→5→6→999)
├─ rage_damage (+2→+3→+4)
├─ proficiency_bonus (+2→+6)
└─ sneak_attack_dice (1d6→10d6)
```

**Key Methods:**
- `get_character_abilities()` - Query all abilities for a character
- `use_ability()` - Execute any class ability
- `restore_abilities()` - Short/long rest recovery
- `calculate_max_uses()` - Level-based scaling
- `update_ability_resources_for_level()` - Handle level up

**Benefits:**
- Single source of truth (database-driven)
- No code for new abilities (1 SQL INSERT)
- Easy balancing (update database values)
- Consistent mechanics across all classes
- Future-proof for all 11 D&D classes

---

## Character Classes

### Fighter

**Implementation Status:** Core features complete (levels 1-20)

**Files:**
- `src/talekeeper/services/fighter_abilities.py` - Fighter-specific abilities
- `src/talekeeper/services/weapon_attack_service.py` - Weapon attack calculations
- `src/talekeeper/services/weapon_mastery_service.py` - Weapon mastery mechanics
- `docs/Fighter_Class.md` - Complete documentation

**Core Features:**
- **Level 1:** Fighting Style, Second Wind, Weapon Mastery
- **Level 2:** Action Surge, Tactical Mind
- **Level 3:** Fighter Subclass
- **Level 5:** Extra Attack, Tactical Shift
- **Level 9:** Indomitable, Tactical Master
- **Level 11:** Two Extra Attacks
- **Level 13:** Studied Attacks
- **Level 19:** Epic Boon
- **Level 20:** Three Extra Attacks

**Champion Subclass:**
- **Level 3:** Improved Critical (19-20), Remarkable Athlete
- **Level 7:** Additional Fighting Style
- **Level 10:** Heroic Warrior
- **Level 15:** Superior Critical (18-20)
- **Level 18:** Survivor

**Weapon Mastery:**
- Fighter, Barbarian, Rogue, and Paladin have UNLIMITED access to all weapon mastery properties
- No slot tracking - all masteries always available
- Tactical Master (level 9+) allows substituting Push/Sap/Slow on any attack

**WeaponAttackService:**
- Centralized weapon attack calculations
- Fighting style effects (Defense, Dueling, Great Weapon Fighting, Two-Weapon Fighting, Archery)
- Weapon mastery effects (Push, Sap, Slow, Cleave, Graze, Nick, Topple, Vex)
- Critical hit damage calculations
- Feat effects (Savage Attacker)

**Database Integration:**
```sql
-- Fighter features tracked in character_resources
character_resources (
    character_id,
    resource_name,      -- 'Second Wind', 'Action Surge', 'Indomitable'
    current_uses,
    max_uses,
    recharge_type       -- 'short_rest', 'long_rest'
)
```

### Barbarian

**Implementation Status:** Core features complete (levels 1-20)

**Files:**
- `src/talekeeper/services/barbarian_abilities.py` - Barbarian-specific abilities
- `docs/Barbarian_Class.md` - Complete documentation

**Core Features:**
- **Level 1:** Rage, Unarmored Defense
- **Level 2:** Reckless Attack, Danger Sense
- **Level 3:** Primal Path (subclass)
- **Level 5:** Extra Attack, Fast Movement
- **Level 7:** Feral Instinct, Instinctive Pounce
- **Level 9:** Brutal Strike
- **Level 11:** Relentless Rage
- **Level 13:** Persistent Rage
- **Level 15:** Indomitable Might
- **Level 20:** Primal Champion

**Berserker Subclass:**
- **Level 3:** Frenzy, Mindless Rage
- **Level 6:** Intimidating Presence
- **Level 10:** Retaliation
- **Level 14:** (not yet implemented)

**Rage Mechanics:**
- +2/+3/+4 damage bonus (scales with level)
- Resistance to bludgeoning, piercing, slashing damage
- Advantage on Strength checks and saves
- 2/3/4/5/6/unlimited uses per long rest
- 10 rounds duration (can extend with attacks/damage)

### Rogue

**Implementation Status:** Core features complete (levels 1-20)

**Files:**
- `src/talekeeper/services/rogue_abilities.py` - Rogue-specific abilities
- `docs/Rogue_Class.md` - Complete documentation

**Core Features:**
- **Level 1:** Sneak Attack (1d6), Thieves' Cant, Expertise
- **Level 2:** Cunning Action
- **Level 3:** Roguish Archetype (subclass), Steady Aim
- **Level 5:** Uncanny Dodge
- **Level 7:** Evasion
- **Level 11:** Reliable Talent
- **Level 14:** Blindsense
- **Level 15:** Slippery Mind
- **Level 18:** Elusive
- **Level 20:** Stroke of Luck

**Thief Subclass:**
- **Level 3:** Fast Hands, Second-Story Work
- **Level 9:** Supreme Sneak
- **Level 13:** Use Magic Device
- **Level 17:** Thief's Reflexes

**Sneak Attack:**
- Scales from 1d6 (level 1) to 10d6 (level 19)
- Requires advantage OR ally within 5ft of target
- Once per turn
- Applies to first hit that qualifies

### Paladin

**Implementation Status:** Core features complete, 2 subclasses implemented

**Files:**
- `src/talekeeper/services/paladin_abilities.py` - Paladin-specific abilities
- `src/talekeeper/services/subclass_feature_manager.py` - Subclass feature management
- `docs/PALADIN_SUBCLASS_COMPLETE.md` - Complete documentation

**Core Features:**
- **Level 1:** Lay on Hands, Divine Sense
- **Level 2:** Fighting Style, Spellcasting, Divine Smite
- **Level 3:** Sacred Oath (subclass), Channel Divinity, Divine Health
- **Level 5:** Extra Attack
- **Level 6:** Aura of Protection
- **Level 10:** Aura of Courage
- **Level 11:** Improved Divine Smite
- **Level 14:** Cleansing Touch

**Oath of Devotion:**
- **Level 3:** Sacred Weapon, Turn the Unholy (Channel Divinity)
- **Level 7:** Aura of Devotion
- **Level 15:** Smite of Protection
- **Level 20:** Holy Nimbus

**Oath of the Unbroken (Custom):**
- **Level 3:** Mind's Razor, Unbroken Resolve (Channel Divinity)
- **Level 7:** Aura of Defiance
- **Level 15:** Wasteland Survivor
- **Level 20:** Sand Wraith's Mantle

**Oath Spells:**
- 10 oath spells per subclass (2 per tier at levels 3, 5, 9, 13, 17)
- Auto-granted on level up
- Always prepared (don't count against limit)
- Stored with `source='oath'` in character_spells table

**Divine Smite:**
- Expend spell slot for extra radiant damage
- 2d8 base + 1d8 per slot level above 1st
- +1d8 vs undead/fiends
- Maximum 5d8 (6d8 vs undead/fiends)

### Warlock

**Implementation Status:** In Progress - Foundation complete, mechanics implementation phase

**Files:**
- `src/talekeeper/services/warlock_service.py` - Warlock-specific abilities
- `src/talekeeper/services/warlock_patrons/` - Patron implementations
- `docs/WARLOCK_IMPLEMENTATION_STATUS.md` - Current status

**Core Features (Implemented):**
- **Level 1:** Eldritch Invocations (1), Pact Magic
- **Level 2:** Magical Cunning
- **Level 3:** Warlock Subclass (Patron), Pact Boon
- **Level 9:** Contact Patron
- **Level 11-17:** Mystic Arcanum (6th, 7th, 8th, 9th level spells)
- **Level 20:** Eldritch Master

**Fiend Patron:**
- **Level 3:** Dark One's Blessing, Fiend Spells
- **Level 6:** Dark One's Own Luck
- **Level 10:** Fiendish Resilience
- **Level 14:** Hurl Through Hell

**Pact Magic:**
- Short rest recovery (ALL slots recovered)
- Slots all same level (auto-upcast)
- Separate from standard spellcasting
- 1-4 slots at levels 1-20
- Slot level progresses to 5th level

**Invocations:**
- Learn 1-10 invocations over levels 1-20
- Prerequisites (level, pact boon, etc.)
- At-will spellcasting (Armor of Shadows, Fiendish Vigor, etc.)
- Passive bonuses (Agonizing Blast, Devil's Sight, etc.)
- Combat abilities (Eldritch Smite, Thirsting Blade, etc.)

**TODO:**
- Invocation selection UI during character creation
- Pact Magic short rest recovery
- Invocation effect implementation
- Mystic Arcanum system
- Pact Boon selection

---

## Spell System

**Implementation Status:** Foundation complete (18% spell coverage), 7 spells working

**Files:**
- `src/talekeeper/services/spell_effects_service.py` - Core spell effects (650+ lines)
- `src/talekeeper/services/spell_handlers/` - Spell handler implementations
  - `base_handler.py` - Base spell handler class
  - `healing_handlers.py` - Cure Wounds, Prayer of Healing
  - `buff_handlers.py` - Shield of Faith, Divine Favor, Aid, Bless
  - `concentration_handlers.py` - Heroism (temp HP + fear immunity)
  - `utility_handlers.py` - (future)
  - `advanced_handlers.py` - (future)
- `docs/SPELL_SYSTEM_COMPLETE_STATUS.md` - Complete status

**Database Schema:**
```sql
-- Migration 023_spell_effects_system.sql
active_spell_effects (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    spell_id INTEGER,
    spell_name TEXT,
    effect_type TEXT,           -- 'ac_bonus', 'damage_bonus', 'temp_hp', etc.
    effect_data TEXT,            -- JSON
    rounds_remaining INTEGER,
    concentration BOOLEAN,
    caster_id TEXT,
    created_at TEXT
);

spell_summons (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    spell_name TEXT,
    summon_name TEXT,
    summon_hp INTEGER,
    summon_ac INTEGER,
    duration_rounds INTEGER,
    created_at TEXT
);
```

**Implemented Spells:**

**Healing (2 spells):**
1. **Cure Wounds** - 1d8+CHA healing, upcasts +1d8/level
2. **Prayer of Healing** - 2d8+CHA healing, 10 min cast

**Buff Spells (4 spells):**
1. **Shield of Faith** - +2 AC, concentration, 10 min
2. **Divine Favor** - +1d4 radiant/hit, concentration, 1 min
3. **Aid** - +5 HP max/level, 8 hours (no concentration)
4. **Bless** - +1d4 attack/saves, concentration, 1 min

**Concentration Spells (1 spell):**
1. **Heroism** - Temp HP each turn, fear immunity, concentration, 1 min

**SpellEffectsService Features:**
- Healing, damage, temp HP management
- Buff/debuff tracking
- Turn processing (duration decrements)
- Bonus calculations (AC, attack, damage)
- Concentration tracking and breaking
- Database persistence

**Integration Points:**
- **AC Calculation:** `game_engine_sqlite.py:1850-1859`
- **Attack Rolls:** `weapon_attack_service.py:151-172`
- **Damage Calculation:** `weapon_attack_service.py:216-255`
- **Turn Processing:** `combat_manager.py:482-504`

**UI Display:**
- **SpellEffectBadge** widget - Compact 3-letter badges
- Color-coded by effect type (blue/pink/orange/green/purple)
- Concentration indicator (asterisk)
- Rich tooltips (spell name, effect, duration)
- Integrated into character sheet conditions row
- Up to 8 badges displayed (conditions + spells)

**Auto-Targeting:**
- Solo play buff spells auto-target self (no dialog needed)
- Touch-range healing spells auto-target self
- `is_buff` flag determines auto-targeting behavior

**Remaining Work (31 spells):**
- Smite spells (Searing Smite, Shining Smite) - need on-hit triggers
- Condition removal spells (Lesser Restoration, etc.)
- Detection & utility spells (Detect Magic, Command, etc.)
- Advanced spells (Death Ward, Dispel Magic, Banishment, etc.)
- High-level spells (Revivify, Raise Dead, Find Steed, etc.)

---

## Combat & Monsters

### Combat Manager

**Implementation:** Turn-based combat system with D&D 2024 rules

**File:** `src/talekeeper/core/combat_manager.py`

**Features:**
- Initiative tracking
- Turn order management
- Hit point tracking
- Attack resolution
- Damage calculation
- Condition application
- Turn processing (spell effects, conditions, etc.)

**Combat Flow:**
1. Roll Initiative
2. Create Combat Session
3. Add Combatants
4. Start First Turn
5. Process Actions (attacks, spells, abilities)
6. End Turn → Next Combatant
7. Round Transition → Reset reactions
8. Combat End → XP/Loot distribution

**Attack Resolution:**
```python
def resolve_attack(attacker, target, weapon_data):
    # Calculate attack bonus (ability + proficiency + weapon bonus)
    attack_bonus = calculate_attack_bonus(attacker, weapon_data)

    # Roll d20 + bonuses vs target AC
    attack_roll = roll_d20() + attack_bonus

    if attack_roll >= target.ac:
        # Hit - roll damage
        damage = roll_damage(weapon_data) + modifiers
        apply_damage(target, damage)
    else:
        # Miss
        log_miss(attacker, target)
```

### Monster System

**Implementation:** Comprehensive monster database with standardized attack parsing

**Files:**
- `data/monsters/` - Monster JSON data (451 monsters)
- `src/talekeeper/services/monster_attack_parser.py` - Attack text parsing
- `src/talekeeper/services/monster_attack_processor.py` - Attack execution
- `src/talekeeper/services/standardized_attack_processor.py` - Standardized format
- `docs/monster_attack_standardization.md` - Standardization plan

**Database Schema:**
```sql
CREATE TABLE monsters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,                  -- humanoid, beast, monstrosity, etc.
    subtype TEXT,
    size TEXT,                  -- tiny, small, medium, large, huge, gargantuan
    alignment TEXT,
    armor_class INTEGER,
    hit_points INTEGER,
    speed TEXT,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    challenge_rating TEXT,
    experience_points INTEGER,
    proficiency_bonus INTEGER,
    saving_throws TEXT,
    skills TEXT,
    damage_resistances TEXT,
    damage_immunities TEXT,
    condition_immunities TEXT,
    senses TEXT,
    languages TEXT,
    special_abilities TEXT,     -- JSON
    actions TEXT,               -- JSON
    legendary_actions TEXT,     -- JSON
    reactions TEXT,             -- JSON
    environment TEXT
);
```

**Attack Parsing:**
- Complex regex patterns for D&D Beyond format
- Handles attack bonus, damage dice, save DCs
- Condition application (grappled, poisoned, etc.)
- Special effects (poison damage on failed save, etc.)

**Standardization (Planned):**
- Move from text parsing to structured JSON format
- Explicit mechanics definition
- Type safety
- Extensibility
- Multilingual support

### Monster Knowledge System

**Implementation:** Skill-based monster information reveal system

**File:** `src/talekeeper/services/monster_knowledge.py`

**Skills:**
- **Nature:** Beasts, Plants
- **Arcana:** Aberrations, Constructs, Dragons, Elementals, Monstrosities
- **Religion:** Celestials, Fiends, Undead
- **History:** Giants, Humanoids

**Information Tiers:**
- **DC 10-15:** Basic type and CR
- **DC 12-18:** Abilities and resistances
- **DC 15+:** Immunities and special abilities
- **DC 18+:** Specific attack patterns

**UI Integration:**
- Hover tooltips on monster portraits
- Color-coded knowledge levels
- Skill check results visible in log

---

## Campaign & Exploration

### Campaign Frame System

**Implementation:** Flexible encounter generation parameters and campaign-specific rules

**Files:**
- `src/talekeeper/ui/encounter_pane/campaign_frame.py` - Campaign settings data structure
- `src/talekeeper/ui/encounter_pane/encounter_generator.py` - Encounter generation engine
- `docs/CAMPAIGN_FRAME_SYSTEM.md` - Complete documentation

**Campaign Parameters:**
```python
{
    "name": "Campaign Name",
    "monster_type_weights": {
        "humanoid": 0.3,
        "beast": 0.2,
        "monstrosity": 0.2,
        "undead": 0.15,
        "fiend": 0.15
    },
    "difficulty_distribution": {
        "low": 0.4,
        "moderate": 0.5,
        "high": 0.1
    },
    "monster_alignment_rules": {
        "allow_evil": true,
        "allow_humanoid_not_good": true
    },
    "rest_rules": {
        "short_rest_frequency": 0.3,
        "long_rest_required": 8
    }
}
```

**XP Budget System:**
- D&D-standard XP budgets for levels 1-20
- Three difficulty tiers (Low, Moderate, High)
- CR scaling based on party level
- Encounter structure patterns (single boss vs multiple enemies)

**RandomBag Mechanics:**
- Ensures encounter variety
- Prevents immediate monster repetition
- All qualified monsters appear eventually

### Hex Map System

**Implementation:** Standalone hex-based wilderness exploration system

**Files:**
- `src/talekeeper/services/hex_coordinate_system.py` - Hex math & neighbors
- `src/talekeeper/services/hex_map_service.py` - Core generation & state
- `src/talekeeper/services/hex_event_logger.py` - Event tracking
- `src/talekeeper/services/hex_scouting_service.py` - Skill-based hex scouting
- `src/talekeeper/ui/hex_map/hex_map_widget.py` - Main map UI
- `docs/HEX_MAP_SYSTEM.md` - Complete documentation

**Core Features:**
- Axial coordinate system (industry-standard)
- Just-in-time generation (hexes only generate when adjacent)
- Per-character maps (unique exploration for each character)
- Event logging (combat, loot, narrative)
- Skill-based scouting (Nature, Survival, Perception, etc.)

**Terrain Types:**
- Plains (30% encounter rate)
- Forest (50% encounter rate)
- Mountain (40% encounter rate)
- Hills (35% encounter rate)
- Swamp (60% encounter rate)
- Desert (20% encounter rate)

**Visibility States:**
1. **Ungenerated** (dark gray) - Doesn't exist yet
2. **Generated but Hidden** (dimmed) - Exists but not revealed
3. **Revealed** (normal) - Player can see terrain
4. **Visited** (bright) - Player has been there

**Skill-Based Scouting:**
- Same DC calculations as monster knowledge (DC = 10 + CR)
- Reveals encounter details before entering hex
- Nature/Survival for terrain, Perception for encounters
- Integration with character proficiencies

**Database Schema:**
```sql
-- Migration 010_hex_map_system.sql
character_hex_map (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    q INTEGER NOT NULL,         -- Axial Q coordinate
    r INTEGER NOT NULL,         -- Axial R coordinate
    biome TEXT,                 -- terrain type
    difficulty TEXT,
    encounter_type TEXT,
    encounter_data TEXT,        -- JSON
    visited BOOLEAN DEFAULT 0,
    settlement_name TEXT,       -- NEW in migration 038
    accommodation_name TEXT,    -- NEW in migration 038
    created_at TEXT,
    UNIQUE(character_id, q, r)
);

hex_events (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    q INTEGER,
    r INTEGER,
    event_type TEXT,            -- 'travel', 'combat', 'resource', 'narrative'
    event_data TEXT,            -- JSON
    timestamp TEXT
);
```

### Long Rest & Lifestyle System

**Implementation:** Long rest with settlement-based accommodations and hazards

**Files:**
- `src/talekeeper/services/settlement_name_service.py` - Name generation (280 lines)
- `src/talekeeper/services/long_rest_service.py` - Rest logic (390 lines)
- `src/talekeeper/ui/rest_pane/long_rest_widget.py` - Main rest UI (440 lines)
- `src/talekeeper/ui/rest_pane/event_resolution_widget.py` - Hazard UI (330 lines)
- `docs/LONG_REST_IMPLEMENTATION_COMPLETE.md` - Complete documentation

**Lifestyle Options:**
- **Wretched** - Free (50% hazard chance)
- **Squalid** - 1 sp (25% hazard chance)
- **Poor** - 2 sp (safe)
- **Modest** - 1 gp (safe)
- **Comfortable** - 2 gp (safe)
- **Wealthy** - 4 gp (safe)

**Settlement Types:**
- **Empty Hex** - Wretched only (wilderness camping)
- **Hamlet** - Wretched, Squalid, Poor (inns/homes)
- **Village** - Wretched to Comfortable (inns, manor)
- **Town** - All lifestyles (inns, noble estates)

**Settlement Name Generation:**
- 60 historic UK inn names (The Red Lion, The Golden Dragon, etc.)
- 80 worthy names (Aelric, Harold, Matilda, Eleanor, etc.)
- Deterministic seed-based (same hex = same names forever)
- Database persistence

**Rest Flow:**
1. Player selects lifestyle
2. DEDUCT GOLD (payment happens first)
3. Check for hazard trigger (Wretched 50%, Squalid 25%)
4. If encounter: Combat (REST INTERRUPTED, must pay again)
5. If hazard: Resolve effects (damage/conditions) → GRANT REST
6. If safe: GRANT REST immediately

**Encounter Types (6):**
1. **Bandits** - Combat (CR = character level)
2. **Wild Animals** - Combat (CR = level -1)
3. **Cutpurses** - DC 15 Dex save or lose 2d10 gp
4. **Corrupt Guards** - Pay 1d10 gp or fight
5. **Desperate Beggar** - DC 12 Cha save or lose 1d6 gp + 1d4 rations
6. **Thugs Shakedown** - DC 13 Intimidation or pay 3d6 gp or fight

**Hazard Types (6):**
1. **Disease** - DC 12 Con save or disadvantage on checks for 1d4 days
2. **Theft** - DC 14 Perception or lose 2d10 gp + 1 item
3. **Exposure** - DC 13 Con save or 1d6 cold damage + 1 exhaustion
4. **Food Poisoning** - DC 13 Con save or poisoned for 8 hours
5. **Structural Collapse** - DC 14 Dex save or 2d6 bludgeoning damage
6. **Fire** - DC 15 Dex save or 2d8 fire damage + lose 1d4 items

**Database Schema:**
```sql
-- Migration 038_long_rest_lifestyle.sql
character_long_rests (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    hex_q INTEGER,
    hex_r INTEGER,
    lifestyle_type TEXT,        -- 'wretched', 'squalid', etc.
    cost_gp REAL,
    hazard_triggered BOOLEAN DEFAULT 0,
    hazard_type TEXT,           -- 'encounter' or 'hazard'
    hazard_details TEXT,        -- JSON
    rest_completed BOOLEAN DEFAULT 0,
    timestamp TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

### Skill Challenge System

**Implementation:** D&D 2024 skill challenge mechanics

**File:** `src/talekeeper/services/skill_challenge_manager.py`

**Features:**
- Multiple skill checks with success/failure tracking
- Success threshold (e.g., 3 successes before 3 failures)
- DC scaling based on difficulty
- Rewards on success (XP, items, story progression)
- Consequences on failure

**Usage:**
```python
from talekeeper.services.skill_challenge_manager import SkillChallengeManager

manager = SkillChallengeManager()

# Create skill challenge
challenge_id = manager.create_challenge(
    character_id=character_id,
    name="Escape the Collapsing Temple",
    description="The ancient temple is crumbling around you!",
    required_successes=3,
    max_failures=3,
    dc=15,
    skills=['Athletics', 'Acrobatics', 'Perception']
)

# Make skill check
result = manager.make_skill_check(
    challenge_id=challenge_id,
    skill='Athletics',
    roll=18,
    modifier=5
)

# Check if complete
if result['challenge_complete']:
    if result['success']:
        # Award XP/items
        pass
    else:
        # Apply consequences
        pass
```

---

## UI Components

### Main Window

**File:** `src/talekeeper/ui/main_window.py`

**Layout:** Fixed positions at 1920x1080 with 5% margins
- **Game Menu:** (96, 54)
- **Character Sheet:** (96, 144)
- **Encounter Pane:** (744, 54) - center
- **Log Panel:** (1392, 54) - top right
- **Equipment Panel:** (1392, 540) - bottom right
- **Action Panel:** (96, 726) - bottom left

**Signals:**
- `create_character_requested` - Start character creation
- `item_equipped` - Equipment changes
- `action_triggered` - Action card clicked
- `encounter_completed` - Combat finished
- `rest_completed` - Rest finished

**Keyboard Shortcuts:**
- `M` - Toggle hex map
- `R` - Long rest
- `Ctrl+T` - Toggle theme
- `ESC` - Close dialogs

### Action Panel

**File:** `src/talekeeper/ui/action_cards/action_panel.py`

**Implementation Guide:** `docs/ACTION_CARD_IMPLEMENTATION_GUIDE.md`

**Card Types:**
1. **Static Cards** - Universal actions (Dodge, Dash, Hide)
2. **Weapon Cards** - Main/off-hand weapon attacks
3. **Feature Cards** - Class-specific abilities

**Adding New Action Cards:**

**Step 1: Add ActionType Enum**
```python
class ActionType(str, Enum):
    CHANNEL_DIVINITY = "channel_divinity"  # Add your new type
```

**Step 2: Add Card Generation Logic**
```python
def _create_feature_cards(self):
    if (self.character_context.get('class_id', '').lower() == 'paladin'
        and self.character_context.get('level', 1) >= 3):

        card = ActionCard(
            ActionType.CHANNEL_DIVINITY,  # Type
            "⚡",                          # Icon
            "Channel Divinity",            # Name
            "Channel divine energy"        # Description
        )
        card.action_triggered.connect(self._trigger_action)
        self.action_cards[ActionType.CHANNEL_DIVINITY] = card
```

**Step 3: Add Action Handler**
```python
def _trigger_action(self, action: ActionCard):
    if action.action_type == ActionType.CHANNEL_DIVINITY:
        self._use_channel_divinity()
```

**Step 4: Implement Action Method**
```python
def _use_channel_divinity(self):
    if not self._has_channel_divinity_uses():
        return

    dialog = ChannelDivinityDialog(...)
    dialog.exec()
```

### Character Sheet

**File:** `src/talekeeper/ui/character_sheet/character_panel.py`

**Sections:**
- **Header:** Name, race, class, level
- **Ability Scores:** STR, DEX, CON, INT, WIS, CHA with modifiers
- **Combat Stats:** AC, HP, initiative, speed
- **Saving Throws:** Proficiency + ability modifier
- **Skills:** Proficiency + ability modifier
- **Proficiencies:** Armor, weapons, tools, languages
- **Features:** Class and subclass features
- **Spells:** Spell slots, prepared spells, known spells
- **Equipment:** Worn armor, weapons, items

**Proficiency Display:**
```python
# Skills
skill_proficiencies = proficiency_system.get_character_proficiencies(character_id)['skill']
is_proficient = skill_name in skill_proficiencies
skill_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)

# Saving Throws
save_proficiencies = proficiency_system.get_character_proficiencies(character_id)['saving_throw']
is_proficient = ability_name in save_proficiencies
save_bonus = ability_mod + (proficiency_bonus if is_proficient else 0)
```

### Condition Display

**File:** `src/talekeeper/ui/condition_display.py`

**Features:**
- **Condition Badges:** Color-coded, compact display
- **Spell Effect Badges:** 3-letter abbreviations (SoF, DiF, Aid, Ble)
- **Concentration Indicator:** Asterisk on badge
- **Rich Tooltips:** Condition/spell name, effect, duration
- **Up to 8 badges:** Conditions + spells

**Badge Colors:**
- **Blue:** AC bonus (Shield of Faith)
- **Pink:** Damage bonus (Divine Favor)
- **Orange:** HP/temp HP (Aid, Heroism)
- **Green:** Attack/save bonus (Bless)
- **Purple:** Other buffs

**Implementation:**
```python
class SpellEffectBadge(QWidget):
    def __init__(self, spell_name, effect_type, concentration, duration):
        # Create 3-letter abbreviation
        abbrev = self._create_abbreviation(spell_name)

        # Add concentration indicator
        if concentration:
            abbrev += "*"

        # Color-code by effect type
        color = self._get_effect_color(effect_type)

        # Create tooltip
        tooltip = f"{spell_name}\n{effect}\nDuration: {duration}"
```

### Theme System

**File:** `src/talekeeper/ui/themes.py`

**Themes:**
- **Light:** Default light theme
- **Dark:** Dark mode (Ctrl+T to toggle)

**Theme Application:**
```python
def apply_theme(theme_name):
    if theme_name == 'dark':
        app.setStyleSheet(DARK_THEME_STYLESHEET)
    else:
        app.setStyleSheet(LIGHT_THEME_STYLESHEET)
```

**Panel Updates:**
Each UI panel has `update_theme()` method that refreshes styling when theme changes.

---

## Database Schema

### Core Tables

**characters**
```sql
CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    race_id TEXT,
    class_id TEXT,
    level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 0,
    max_hp INTEGER,
    current_hp INTEGER,
    temp_hp INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 10,
    dexterity INTEGER DEFAULT 10,
    constitution INTEGER DEFAULT 10,
    intelligence INTEGER DEFAULT 10,
    wisdom INTEGER DEFAULT 10,
    charisma INTEGER DEFAULT 10,
    gold REAL DEFAULT 0,
    background_id TEXT,
    subclass_id TEXT,
    FOREIGN KEY (race_id) REFERENCES races(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (background_id) REFERENCES backgrounds(id)
);
```

**character_proficiencies**
```sql
CREATE TABLE character_proficiencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    proficiency_type TEXT NOT NULL, -- 'skill', 'weapon', 'armor', 'saving_throw', 'tool', 'language'
    proficiency_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'unknown', -- 'class', 'background', 'race', 'feat', 'manual'
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, proficiency_name)
);
```

**character_resources**
```sql
CREATE TABLE character_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    resource_name TEXT NOT NULL,    -- 'Second Wind', 'Action Surge', etc.
    current_uses INTEGER,
    max_uses INTEGER,
    recharge_type TEXT,             -- 'short_rest', 'long_rest', 'none'
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    UNIQUE(character_id, resource_name)
);
```

**feature_states**
```sql
CREATE TABLE feature_states (
    character_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    feature_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    uses_current INTEGER,
    uses_max INTEGER,
    configuration TEXT,              -- JSON config
    last_used TEXT,
    PRIMARY KEY (character_id, feature_name)
);
```

### Class Abilities

**class_abilities** (93 abilities across 5 classes)
```sql
CREATE TABLE class_abilities (
    ability_id TEXT PRIMARY KEY,
    class_name TEXT NOT NULL,
    ability_name TEXT NOT NULL,
    description TEXT,
    level_gained INTEGER NOT NULL,
    ability_type TEXT,              -- 'passive', 'action', 'bonus_action', 'reaction'
    action_cost TEXT,               -- 'action', 'bonus_action', 'reaction', 'none'
    uses_max INTEGER DEFAULT 0,     -- 0 = unlimited
    recharge_type TEXT,             -- 'short_rest', 'long_rest', 'none'
    scaling_formula TEXT,           -- References ability_scaling_formulas
    mechanics TEXT,                 -- JSON
    UNIQUE(class_name, ability_name)
);
```

**character_ability_usage**
```sql
CREATE TABLE character_ability_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    ability_id TEXT NOT NULL,
    current_uses INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT FALSE,
    turns_remaining INTEGER DEFAULT 0,
    last_used TEXT,
    last_reset TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (ability_id) REFERENCES class_abilities(ability_id),
    UNIQUE(character_id, ability_id)
);
```

**ability_scaling_formulas**
```sql
CREATE TABLE ability_scaling_formulas (
    formula_name TEXT PRIMARY KEY,
    formula_type TEXT,              -- 'level_based', 'proficiency_based', etc.
    formula_data TEXT               -- JSON with level→value mapping
);
```

### Spell System

**spells**
```sql
CREATE TABLE spells (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER,                  -- 0=cantrip, 1-9=spell level
    school TEXT,
    casting_time TEXT,
    range TEXT,
    components TEXT,
    duration TEXT,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    description TEXT,
    higher_levels TEXT,
    classes TEXT,                   -- JSON array
    is_buff BOOLEAN DEFAULT FALSE
);
```

**character_spells**
```sql
CREATE TABLE character_spells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id INTEGER NOT NULL,
    source TEXT,                    -- 'class', 'oath', 'patron', 'learned'
    is_prepared BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    UNIQUE(character_id, spell_id)
);
```

**active_spell_effects**
```sql
CREATE TABLE active_spell_effects (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    spell_id INTEGER,
    spell_name TEXT,
    effect_type TEXT,               -- 'ac_bonus', 'damage_bonus', 'temp_hp', etc.
    effect_data TEXT,               -- JSON
    rounds_remaining INTEGER,
    concentration BOOLEAN,
    caster_id TEXT,
    created_at TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

### Subclass System

**subclass_features**
```sql
CREATE TABLE subclass_features (
    feature_id INTEGER PRIMARY KEY,
    subclass_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    level INTEGER NOT NULL,
    feature_type TEXT,              -- 'passive', 'action', 'reaction', 'channel_divinity'
    action_cost TEXT,
    uses_max INTEGER DEFAULT 0,
    recharge_type TEXT,
    mechanics TEXT,                 -- JSON
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);
```

**subclass_spells**
```sql
CREATE TABLE subclass_spells (
    id INTEGER PRIMARY KEY,
    subclass_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,  -- 1st, 2nd, 3rd, 4th, 5th level tier
    spell_name TEXT NOT NULL,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id)
);
```

**character_features**
```sql
CREATE TABLE character_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    feature_id INTEGER,
    feature_name TEXT,
    level_gained INTEGER,
    is_active BOOLEAN DEFAULT FALSE,
    uses_current INTEGER DEFAULT 0,
    uses_max INTEGER DEFAULT 0,
    last_used TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (feature_id) REFERENCES subclass_features(feature_id)
);
```

### Exploration System

**character_hex_map**
```sql
CREATE TABLE character_hex_map (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    q INTEGER NOT NULL,             -- Axial Q coordinate
    r INTEGER NOT NULL,             -- Axial R coordinate
    biome TEXT,
    difficulty TEXT,
    encounter_type TEXT,
    encounter_data TEXT,            -- JSON
    visited BOOLEAN DEFAULT 0,
    settlement_name TEXT,
    accommodation_name TEXT,
    created_at TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id),
    UNIQUE(character_id, q, r)
);
```

**hex_events**
```sql
CREATE TABLE hex_events (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    q INTEGER,
    r INTEGER,
    event_type TEXT,                -- 'travel', 'combat', 'resource', 'narrative'
    event_data TEXT,                -- JSON
    timestamp TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

**character_long_rests**
```sql
CREATE TABLE character_long_rests (
    id INTEGER PRIMARY KEY,
    character_id TEXT NOT NULL,
    hex_q INTEGER,
    hex_r INTEGER,
    lifestyle_type TEXT,
    cost_gp REAL,
    hazard_triggered BOOLEAN DEFAULT 0,
    hazard_type TEXT,
    hazard_details TEXT,            -- JSON
    rest_completed BOOLEAN DEFAULT 0,
    timestamp TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

### Monster System

**monsters**
```sql
CREATE TABLE monsters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT,
    subtype TEXT,
    size TEXT,
    alignment TEXT,
    armor_class INTEGER,
    hit_points INTEGER,
    speed TEXT,
    strength INTEGER,
    dexterity INTEGER,
    constitution INTEGER,
    intelligence INTEGER,
    wisdom INTEGER,
    charisma INTEGER,
    challenge_rating TEXT,
    experience_points INTEGER,
    proficiency_bonus INTEGER,
    saving_throws TEXT,
    skills TEXT,
    damage_resistances TEXT,
    damage_immunities TEXT,
    condition_immunities TEXT,
    senses TEXT,
    languages TEXT,
    special_abilities TEXT,         -- JSON
    actions TEXT,                   -- JSON
    legendary_actions TEXT,         -- JSON
    reactions TEXT,                 -- JSON
    environment TEXT
);
```

---

## Testing

### Regression Test Suite

**File:** `tests/run_regression_tests.py`

**Test Modes:**
```bash
# Quick tests - 30 seconds (Always run after changes)
python tests/run_regression_tests.py --quick
run_tests.bat quick

# Full tests - 2-3 minutes (Before commits)
python tests/run_regression_tests.py --full
run_tests.bat full

# Detailed tests - 4-5 minutes (Feature validation)
python tests/run_regression_tests.py --detailed
run_tests.bat detailed
```

**Test Breakdown:**
- **Quick (6 tests):** Core systems (character, combat, database, action economy)
- **Full (11 tests):** Quick + comprehensive (subclass, progression, conditions)
- **Detailed (12+ tests):** Full + feature tests (Hero Mode, future features)

### Unit Tests

**Structure:**
```
tests/
├── unit/
│   ├── test_spell_effects_service.py
│   ├── test_spell_handler_registry.py
│   ├── test_spell_effect_display.py
│   └── ...
├── services/
│   ├── test_fighter_champion.py
│   ├── test_weapon_attack_service.py
│   ├── test_condition_manager.py
│   └── ...
└── spells/
    ├── test_healing_spells.py
    ├── test_buff_spells.py
    └── ...
```

**Running Unit Tests:**
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_spell_effects_service.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=src/talekeeper/services -v
```

### Integration Tests

**Structure:**
```
tests/integration/
├── test_spell_effects_integration.py
├── test_fighter_combat_flow.py
├── test_morale_and_beast_loot.py
└── ...
```

**Running Integration Tests:**
```bash
python -m pytest tests/integration/ -v
```

### Qt6 UI Tests

**Framework:** pytest-qt

**Structure:**
```
tests/ui/
├── test_action_panel_integration.py
├── test_rest_restrictions.py
└── ...
```

**Running UI Tests:**
```bash
python -m pytest tests/ui/ -v
```

### Test Coverage Areas

**Core Systems:**
- Character creation flow
- Equipment effects on stats
- Fighting styles
- Action card availability
- Combat calculations
- Level progression
- Spell effects
- Condition application
- Subclass features

**Class-Specific:**
- Fighter (Second Wind, Action Surge, Indomitable, Weapon Mastery)
- Barbarian (Rage, Reckless Attack, Brutal Strike)
- Rogue (Sneak Attack, Cunning Action, Uncanny Dodge)
- Paladin (Divine Smite, Lay on Hands, Channel Divinity, Oath spells)
- Warlock (Pact Magic, Invocations, Patron features)

**Spell System:**
- Spell effects (AC, attack, damage bonuses)
- Concentration tracking
- Duration management
- Buff/debuff application
- Healing calculations

---

## Development Commands

### Running the Application
```bash
python main.py
```

### Database Operations
```bash
# Apply migration
sqlite3 talekeeper.db < database/migrations/XXX_migration_name.sql

# Check monster count
sqlite3 talekeeper.db "SELECT COUNT(*) FROM monsters;"

# View character data
sqlite3 talekeeper.db "SELECT * FROM characters;"

# Check proficiencies
sqlite3 talekeeper.db "SELECT * FROM character_proficiencies WHERE character_id = 'char_id';"
```

### Linting & Type Checking
```bash
# Lint Python code
python -m pylint main.py src/talekeeper/ui/ src/talekeeper/core/ src/talekeeper/services/

# Type check (if mypy is configured)
python -m mypy main.py
```

### Debug Commands (In-Application)
```
/debug performance          # Show timing metrics
/debug conditions <char>    # Show active conditions
/debug test_rage <char>     # Test rage mechanics
/debug config              # Show current configuration
/debug help                # Full command list
```

---

## Code Style & Standards

### Code Standards Met
- No Unicode characters (ASCII only)
- No inline comments (unless specifically requested)
- Follows existing patterns
- Consistent service architecture
- PyQt6 best practices
- Error handling (graceful degradation)
- Type consistency
- SQL injection prevention

### Import Patterns
```python
# Always use full import paths (new structure)
from talekeeper.core.game_engine_sqlite import GameEngine
from talekeeper.services.proficiency_system import ProficiencySystem
from talekeeper.ui.main_window import MainWindow
```

### Database Patterns
```python
# Always use context managers for database connections
with sqlite3.connect('talekeeper.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
    result = cursor.fetchone()

# Use parameterized queries (prevent SQL injection)
cursor.execute("UPDATE characters SET current_hp = ? WHERE id = ?", (new_hp, character_id))
```

### Signal/Slot Patterns
```python
# Connect signals in __init__ or setup methods
self.menu.create_character_requested.connect(self._start_character_creation)
self.equipment_panel.item_equipped.connect(self._on_item_equipped)
self.action_panel.action_triggered.connect(lambda action, context: ...)
```

---

## Known Issues & Workarounds

### HP Tracking During Combat (CRITICAL)
Combat HP is tracked in `parent.character_sheet.character_data`, NOT in the database or character_context during active combat:
- **Damage Application:** Reads from character_sheet → applies damage → updates character_sheet
- **Healing MUST:** Read from character_sheet → apply healing → update character_sheet
- **NEVER:** Read HP from database or character_context for healing during combat (will be stale)
- **Pattern Location:** See `_apply_damage_to_player()` and Second Wind implementation in `src/talekeeper/ui/action_cards/action_panel.py`

### Ollama LLM Integration (Optional)
The campaign description service can use Ollama for narrative generation:
- **Warning:** `[LLM] Ollama request failed: HTTPConnectionPool` is EXPECTED when Ollama isn't running
- **Fallback:** Service automatically uses deterministic text when Ollama unavailable
- **Not Critical:** Application works fine without Ollama
- **To Enable:** Install and run Ollama separately (`ollama serve`)

### Fighting Styles
Multiple implementation approaches exist in the codebase:
- Some in `feat_effects.py`
- Some in `weapon_attack_service.py`
- Some in UI components
- Test with: `python testing/run_tests.py --mode specific`

### Character Features
- Features may not initialize properly for new characters
- `feature_integration.py` handles the feature system
- Check `character_features` table in database

---

## File Locations Reference

### Core Engine
- `src/talekeeper/core/game_engine_sqlite.py` - Main game coordinator
- `src/talekeeper/core/combat_manager.py` - Combat system
- `src/talekeeper/core/feature_integration.py` - Feature system
- `src/talekeeper/core/config.py` - Configuration management
- `src/talekeeper/core/debug_commands.py` - Debug utilities

### Services
- `src/talekeeper/services/proficiency_system.py` - Proficiency handling
- `src/talekeeper/services/condition_manager.py` - Condition tracking
- `src/talekeeper/services/action_economy_enforcer.py` - Action economy
- `src/talekeeper/services/class_abilities_service.py` - Unified class abilities
- `src/talekeeper/services/spell_effects_service.py` - Spell effects
- `src/talekeeper/services/weapon_attack_service.py` - Weapon attacks
- `src/talekeeper/services/enhanced_subclass_manager.py` - Subclass management

### Class-Specific Services
- `src/talekeeper/services/fighter_abilities.py` - Fighter
- `src/talekeeper/services/barbarian_abilities.py` - Barbarian
- `src/talekeeper/services/rogue_abilities.py` - Rogue
- `src/talekeeper/services/paladin_abilities.py` - Paladin
- `src/talekeeper/services/warlock_service.py` - Warlock

### UI Components
- `src/talekeeper/ui/main_window.py` - Main window coordinator
- `src/talekeeper/ui/action_cards/action_panel.py` - Action cards
- `src/talekeeper/ui/character_sheet/character_panel.py` - Character sheet
- `src/talekeeper/ui/encounter_pane/encounter_panel.py` - Encounters
- `src/talekeeper/ui/equipment_layout/equipment_panel.py` - Equipment
- `src/talekeeper/ui/log/log_panel.py` - Combat log
- `src/talekeeper/ui/hex_map/hex_map_widget.py` - Hex map
- `src/talekeeper/ui/rest_pane/long_rest_widget.py` - Long rest

### Database
- `talekeeper.db` - SQLite database (root directory)
- `database/migrations/` - Migration scripts
- `src/talekeeper/database/database_init.py` - Database initialization

### Documentation
- `docs/IMPLEMENTATION_GUIDE.md` - This file
- `docs/Fighter_Class.md` - Fighter implementation
- `docs/Barbarian_Class.md` - Barbarian implementation
- `docs/Rogue_Class.md` - Rogue implementation
- `docs/PALADIN_SUBCLASS_COMPLETE.md` - Paladin implementation
- `docs/SPELL_SYSTEM_COMPLETE_STATUS.md` - Spell system status
- `docs/UNIFIED_CLASS_ABILITIES_IMPLEMENTATION_COMPLETE.md` - Class abilities
- `docs/HEX_MAP_SYSTEM.md` - Hex map system
- `docs/LONG_REST_IMPLEMENTATION_COMPLETE.md` - Long rest system

---

## Quick Reference

### Character Creation Flow
1. Select race → class → background
2. Roll/assign ability scores
3. Select skills (based on class choices)
4. Initialize proficiencies (class + background + race)
5. Initialize starting equipment
6. Initialize class features
7. Initialize spell slots (if spellcaster)
8. Save to database

### Combat Flow
1. Roll initiative
2. Create combat session
3. Add combatants (player + monsters)
4. Start first turn → Reset action economy
5. Player/monster takes actions
6. End turn → Next combatant in initiative order
7. Round transition → Reset reactions
8. Combat end → Award XP/loot

### Level Up Flow
1. Check XP threshold
2. Increment level
3. Roll/assign HP increase
4. Update proficiency bonus
5. Grant new class features
6. Grant subclass features (at appropriate levels)
7. Update spell slots (if spellcaster)
8. Grant oath/patron spells (if applicable)
9. ASI/feat selection (at ASI levels)
10. Update character resources

### Spell Casting Flow
1. Select spell from action cards
2. Auto-target self (if buff/healing in solo play) OR select target
3. Expend spell slot
4. Roll attack/save (if applicable)
5. Apply damage/healing/effects
6. Create active spell effect record (if buff/debuff)
7. Track concentration (if applicable)
8. Update character sheet display

### Rest Flow
1. Short Rest:
   - Restore hit dice
   - Restore short rest abilities (Second Wind, Action Surge, Rage)
   - Restore Warlock Pact Magic slots
2. Long Rest:
   - Restore all HP
   - Restore all hit dice
   - Restore long rest abilities (Indomitable, Lay on Hands)
   - Restore spell slots
   - Clear exhaustion (1 level)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-19
**Maintainer:** TaleKeeper Development Team
**Status:** Comprehensive reference for current implementation
