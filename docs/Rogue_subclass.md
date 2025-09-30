# Rogue Subclass Implementation

## Implementation Status

### Thief (Partially Implemented)
- **Registry**: Listed in [subclass_registry.py](services/subclass_registry.py:36)
- **Module Path**: `services.subclasses.rogue.thief.ThiefDefinition`
- **Directory**: `services/subclasses/rogue/` - **NOT YET CREATED**
- **Action Integration**: Handler stubs exist in [subclass_action_integration.py](services/subclass_action_integration.py)
  - `_handle_thiefs_reflexes` method defined but not implemented
- **Stealth Integration**: No specific Thief mechanics in [stealth_mechanics.py](services/stealth_mechanics.py)
- **Subclass Manager**: Basic Thief checks exist in [subclass_manager.py](services/subclass_manager.py)

**Status**: REGISTERED BUT NOT IMPLEMENTED - Files do not exist yet

### Assassin (Partially Implemented)
- **Registry**: Listed in [subclass_registry.py](services/subclass_registry.py:37)
- **Module Path**: `services.subclasses.rogue.assassin.AssassinDefinition`
- **Directory**: `services/subclasses/rogue/` - **NOT YET CREATED**
- **Action Integration**: Handler stubs exist in [subclass_action_integration.py](services/subclass_action_integration.py)
  - `_handle_assassinate` method defined
  - `_handle_assassins_tools` method defined
- **Stealth Integration**: Assassin mechanics implemented in [stealth_mechanics.py](services/stealth_mechanics.py)
  - Assassinate feature check for level 3+
  - Initiative advantage on first round
  - Auto-crit on surprised creatures (D&D 2024)
- **Subclass Manager**: Basic Assassin checks exist in [subclass_manager.py](services/subclass_manager.py)

**Status**: PARTIALLY IMPLEMENTED - Stealth mechanics exist, but class files do not

### Arcane Trickster (Not Implemented)
- **Registry**: Listed in [subclass_registry.py](services/subclass_registry.py:38)
- **Module Path**: `services.subclasses.rogue.arcane_trickster.ArcaneTricksterDefinition`
- **Status**: NOT IMPLEMENTED

### Swashbuckler (Not Implemented)
- **Registry**: Listed in [subclass_registry.py](services/subclass_registry.py:39)
- **Module Path**: `services.subclasses.rogue.swashbuckler.SwashbucklerDefinition`
- **Status**: NOT IMPLEMENTED

### Athas Bard (Custom Subclass - Not Implemented)
- **Registry**: NOT LISTED
- **Module Path**: `services.subclasses.rogue.athas_bard.AthasBardDefinition`
- **Status**: NOT IMPLEMENTED - Custom Dark Sun themed infiltrator/poisoner subclass

---

## D&D 2024 Rogue Subclass: Thief

**Source**: SRD_CC_v5.2.1.md lines 5629-5679

### Level 3: Fast Hands
As a Bonus Action, you can do one of the following:
- **Sleight of Hand**: Make a Dexterity (Sleight of Hand) check to pick a lock or disarm a trap with Thieves' Tools or to pick a pocket
- **Use an Object**: Take the Utilize action, or take the Magic action to use a magic item that requires that action

**Implementation Notes**:
- Requires bonus action integration
- Need UI action card for Fast Hands
- Must track Thieves' Tools requirement
- Interacts with magic item system

### Level 3: Second-Story Work
You've trained to get into especially hard-to-reach places:
- **Climber**: You gain a Climb Speed equal to your Speed
- **Jumper**: You can determine your jump distance using your Dexterity rather than your Strength

**Implementation Notes**:
- Add climb speed to character stats
- Modify jump distance calculation to use DEX instead of STR
- Update movement system

### Level 9: Supreme Sneak
You gain the following Cunning Strike option:
- **Stealth Attack (Cost: 1d6)**: If you have the Hide action's Invisible condition, this attack doesn't end that condition on you if you end the turn behind Three-Quarters Cover or Total Cover

**Implementation Notes**:
- Extends Cunning Strike system (base Rogue feature at level 5)
- Requires cover detection system
- Integrates with stealth mechanics
- Must track Invisible condition from Hide action

### Level 13: Use Magic Device
You've learned how to maximize use of magic items:
- **Attunement**: You can attune to up to four magic items at once (instead of three)
- **Charges**: Whenever you use a magic item property that expends charges, roll 1d6. On a roll of 6, you use the property without expending the charges
- **Scrolls**: You can use any Spell Scroll, using Intelligence as your spellcasting ability for the spell. If the spell is a cantrip or a level 1 spell, you can cast it reliably. If the scroll contains a higher-level spell, you must first succeed on an Intelligence (Arcana) check (DC 10 + the spell's level). On a successful check, you cast the spell from the scroll. On a failed check, the scroll disintegrates

**Implementation Notes**:
- Increase attunement limit to 4
- Add charge conservation mechanic (1d6 roll)
- Enable scroll usage with INT-based check
- Requires spell scroll system implementation

### Level 17: Thief's Reflexes
You are adept at laying ambushes and quickly escaping danger. You can take two turns during the first round of any combat. You take your first turn at your normal Initiative and your second turn at your Initiative minus 10.

**Implementation Notes**:
- Major combat system modification
- Requires initiative tracking for two separate turns
- Must handle action economy for both turns
- Similar to Alert feat but with two full turns

---

## Implementation Plan: Thief Subclass

### Phase 1: Core Thief Definition
1. Create directory structure: `services/subclasses/rogue/`
2. Create `services/subclasses/rogue/__init__.py`
3. Create `services/subclasses/rogue/thief.py` with `ThiefDefinition` class
   - Inherit from `SubclassDefinition` (see `services/enhanced_subclass_manager.py`)
   - Define all 4 features with level gates
   - Use pattern from Champion/Berserker implementations

### Phase 2: Fast Hands (Level 3)
1. Create action card for Fast Hands bonus action
2. Implement Sleight of Hand check trigger
3. Implement Use Object/Magic Item trigger
4. Add to `services/subclass_action_integration.py`
5. UI integration in `action_cards/action_panel.py`

### Phase 3: Second-Story Work (Level 3)
1. Add climb speed to character stats calculation
2. Modify jump distance calculation in movement system
3. Add passive indicators to character sheet
4. Test with movement validation

### Phase 4: Supreme Sneak (Level 9)
1. Extend Cunning Strike system
2. Implement cover detection (Three-Quarters/Total)
3. Add Stealth Attack option to Cunning Strike UI
4. Integrate with existing stealth mechanics
5. Test with Hide action and Invisible condition

### Phase 5: Use Magic Device (Level 13)
1. Increase attunement limit in equipment system
2. Implement charge conservation (1d6 roll on use)
3. Implement scroll usage with INT check
4. Add spell scroll casting system
5. Handle scroll destruction on failed check

### Phase 6: Thief's Reflexes (Level 17)
1. Modify initiative system to support dual turns
2. Create second turn at Initiative - 10
3. Handle action economy reset between turns
4. Add combat log entries for both turns
5. Extensive combat system testing

### Phase 7: Testing
1. Create `test/test_thief_subclass.py`
2. Test each feature at appropriate levels
3. Test integration with Cunning Strike
4. Test integration with stealth system
5. Test Thief's Reflexes in combat encounters
6. Add to regression test suite

---

## D&D 2024 Assassin Subclass

**Note**: Assassin subclass is NOT in the SRD CC v5.2.1. The SRD only includes one subclass per class (Thief for Rogue). Assassin implementation would need to reference D&D 2024 Player's Handbook or use D&D 5e SRD Assassin as baseline.

### Existing Assassin Mechanics (services/stealth_mechanics.py)

Current implementation includes:
- **Assassinate Feature Check**: Detects Assassin subclass at level 3+
- **Initiative Advantage**: Grants advantage on first round attacks
- **Auto-Crit Surprised**: Automatic critical hits on surprised creatures
- **Stealth Attack Context**: Sets `assassin_init_advantage` flag

**Implementation Status**: Combat mechanics exist but class definition does not

### Implementation Needs
1. Create `services/subclasses/rogue/assassin.py`
2. Define Assassin features based on D&D 2024 rules
3. Integrate existing stealth mechanics with class definition
4. Add Assassin-specific action cards
5. Tool proficiency handling (Poisoner's Kit, Disguise Kit)
6. Infiltration expertise features

---

## Custom Subclass: Athas Bard (Rogue)

**Theme**: Dark Sun inspired infiltrator/poisoner who uses disguise, poison, and social manipulation to survive in a harsh world.

### Level 3: Master of Many Faces

You gain proficiency in Disguise Kit, Poisoner's Kit, and one musical instrument or artisan's tool of your choice.

You also gain two additional skill proficiencies from the Rogue list (Athletics, Acrobatics, Sleight of Hand, Stealth, Arcana, Deception, Insight, Intimidation, Investigation, Perception, Performance, Persuasion).

If you already have proficiency in one of these, you can instead gain Expertise in it.

**Implementation Notes**:
- Add tool proficiencies: Disguise Kit, Poisoner's Kit, choice of instrument/artisan tool
- Add 2 skill proficiencies from Rogue list
- If proficiency exists, grant Expertise instead
- Needs proficiency/expertise tracking system

### Level 3: Poisoncraft

You know how to concoct basic poisons using mundane ingredients (bugs, bile, plants, and bone splinters).

**Quick Mix**: You can create one dose of basic poison over a short rest without cost, or 2 during a long rest. These poisons expire after 24 hours.

**Apply Poison**: You can apply a poison as a bonus action.

**Poison Save**: DC = 8 + Proficiency + Dexterity or Intelligence modifier (choose when you gain this subclass)

**Available Poisons** (choose one at each long rest):

| Name | Effect |
|------|--------|
| Bloodsap Venom | Target must make a Con save or take 1d4 poison damage per turn for 1 minute (save ends at end of each turn) |
| Mindspike Toxin | Target must make an Int save or suffer disadvantage on Wisdom and Intelligence checks for 1 hour |
| Paralytic Resin | Target makes a Con save or becomes restrained until the end of its next turn |
| Agony Dust | Target takes no damage but has disadvantage on attack rolls for 1 round |

**Implementation Notes**:
- Poison crafting system during rest
- Poison expiration timer (24 hours)
- Bonus action to apply poison
- Choose DEX or INT for DC calculation at subclass selection
- 4 poison types with different effects
- Needs condition application system
- Requires resource tracking for poison doses

### Level 9: Living Guise

You gain expert use of disguise, dialect, and tradecraft.

You gain Expertise in Deception. If you already have Expertise in Deception, you gain Expertise in one other skill of your choice from the Rogue list.

You become a master of mundane disguise. With access to appropriate materials (clothing, makeup, props), you can create a convincing disguise of a specific person or role over the course of 10 minutes. The disguise holds up to casual inspection and grants advantage on Deception and Performance checks to maintain the role.

When attempting to avoid combat through Deception (such as talking your way out of a fight, bluffing your identity, or creating a diversion), you have advantage on the Deception check.

You may change disguise or role over the course of a short rest if you have access to materials.

**Implementation Notes**:
- Grant Expertise in Deception (or alternative skill if already have Expertise)
- Mundane disguise system (10 minutes to create)
- Disguise grants advantage on Deception and Performance checks
- Advantage on Deception checks when avoiding combat
- Short rest to change disguise
- Needs advantage tracking for combat avoidance context
- Integration with encounter avoidance system (services/encounter_avoidance.py)
- No spellcasting required

### Level 13: Toxic Arsenal

You've perfected your use of poisons, even the rare ones found in the wastes.

**Toxic Immunity**: You are immune to being poisoned and have resistance to poison damage.

**Enhanced Poisons**: Your crafted poisons deal +2 damage per die and last for 1 hour.

**Rare Poison Recipe**: You learn one rare poison recipe (DM's discretion or roll on loot table).

**Multiple Poisons**: You can now have 3 poisons active at a time.

**Implementation Notes**:
- Add poison immunity condition
- Add poison damage resistance
- Increase poison damage by +2 per die
- Extend poison duration to 1 hour
- Rare poison integration (custom recipes)
- Track 3 active poisons simultaneously

### Level 17: Apex Infiltrator

You move between roles, lives, and faces as easily as others change clothes.

**False Identity**: You can create a false identity during a long rest, complete with backstory, mannerisms, and believable history. Once created, you can assume it perfectly, gaining advantage on all Charisma checks related to that identity. You can maintain up to 3 false identities at a time.

**Perfect Disguise**: Your disguises are flawless. You can change your voice, gait, posture, and even apparent age or health. Investigation checks to see through your disguise are made with disadvantage.

**Instant Poison Mix**: You may craft and apply one poison as part of the same bonus action, once per turn.

**Implementation Notes**:
- False identity creation system (during long rest)
- Advantage on all Charisma checks for identity
- Track up to 3 false identities
- Investigation checks against disguise have disadvantage
- Instant poison craft + apply in single bonus action
- UI integration for identity management
- No spellcasting required

---

## Implementation Plan: Athas Bard Subclass

### Phase 1: Core Definition
1. Create `services/subclasses/rogue/athas_bard.py` with `AthasBardDefinition`
2. Define all 4 feature tiers (3, 9, 13, 17)
3. Register in `subclass_registry.py` as optional/custom subclass
4. Add feature flag for custom subclasses in config

### Phase 2: Master of Many Faces & Poisoncraft (Level 3)
1. Implement tool proficiency grants
2. Implement skill proficiency/expertise grants
3. Create poison crafting system
4. Add poison resource tracking
5. Create poison application action card
6. Implement 4 poison types with effects
7. Add poison expiration timer
8. DC calculation (DEX or INT choice)

### Phase 3: Living Guise (Level 9)
1. Grant Expertise in Deception (or alternative skill)
2. Implement mundane disguise system (10 minutes to create)
3. Advantage on Deception and Performance while in disguise
4. Advantage on Deception checks when avoiding combat
5. Short rest disguise change mechanic
6. Integration with encounter avoidance system

### Phase 4: Toxic Arsenal (Level 13)
1. Add poison immunity
2. Add poison damage resistance
3. Enhance poison damage (+2 per die)
4. Extend poison duration (1 hour)
5. Rare poison recipe system
6. Support 3 simultaneous active poisons

### Phase 5: Apex Infiltrator (Level 17)
1. False identity creation system
2. Identity-based Charisma advantage
3. Multiple identity tracking
4. Instant poison craft + apply (single bonus action)
5. UI for identity management

### Phase 6: Testing
1. Create `test/test_athas_bard_subclass.py`
2. Test tool/skill proficiency grants
3. Test poison crafting and application
4. Test poison effects and conditions
5. Test disguise and identity mechanics
6. Test toxic immunity and resistance
7. Add to regression suite (optional/custom)

---

## Architecture Notes

### Following Established Patterns
Use the same architecture as Barbarian/Fighter/Paladin subclasses:
- `SubclassDefinition` base class from `enhanced_subclass_manager.py`
- Feature definitions with level gates
- Action integration via `subclass_action_integration.py`
- Registry pattern via `subclass_registry.py`
- Bonus action/reaction UI via `action_cards/action_panel.py`

### Key Systems to Integrate
1. **Cunning Strike System**: Base Rogue feature that Thief extends
2. **Stealth Mechanics**: Already has Assassin hooks
3. **Magic Item System**: For Use Magic Device (Thief)
4. **Initiative System**: For Thief's Reflexes
5. **Cover System**: For Supreme Sneak (Thief)
6. **Action Economy**: For Fast Hands and Thief's Reflexes
7. **Poison System**: For Athas Bard Poisoncraft
8. **Identity/Disguise System**: For Athas Bard Living Guise and Apex Infiltrator
9. **Tool Proficiency System**: For Athas Bard Master of Many Faces
10. **Condition System**: For poison effects (Restrained, Poisoned, disadvantage)

### Dependencies
- Base Rogue class features (Sneak Attack, Cunning Strike, etc.)
- Condition system (Invisible condition from Hide)
- Cover detection system (may need implementation)
- Magic item/scroll system (may need expansion)
- Initiative tracking system (needs dual-turn support)

---

## Testing Strategy

### Unit Tests
- Feature availability at correct levels
- Fast Hands action availability
- Climb speed calculation
- Jump distance using DEX
- Attunement limit increase
- Charge conservation rolls
- Scroll usage with INT checks

### Integration Tests
- Fast Hands with Thieves' Tools
- Supreme Sneak with Hide action and cover
- Use Magic Device with magic items
- Thief's Reflexes in combat rounds
- Cunning Strike integration
- Stealth mechanics integration

### Regression Tests
Add Thief tests to `tests/run_regression_tests.py`:
- Quick suite: Basic feature validation
- Full suite: Complete level 1-20 progression
- Detailed suite: Combat scenarios with Thief's Reflexes

---

## Next Steps

### Priority Order
1. **Immediate**: Create `services/subclasses/rogue/` directory structure
2. **Phase 1**: Implement Thief subclass definition with all features (standard D&D 2024)
3. **Phase 2**: Implement Fast Hands and Second-Story Work (level 3 features)
4. **Phase 3**: Test basic Thief functionality
5. **Phase 4**: Implement advanced features (Supreme Sneak, Use Magic Device)
6. **Phase 5**: Implement Thief's Reflexes (complex combat system change)
7. **Phase 6**: Full testing and integration
8. **Phase 7**: Implement Assassin subclass with proper D&D 2024 rules
9. **Phase 8**: Implement Athas Bard as custom/optional subclass (feature flag required)

### Custom Subclass Considerations
The Athas Bard subclass should be:
- Marked as custom/optional in registry
- Gated behind a feature flag in config
- Clearly documented as homebrew content
- Tested separately from core D&D 2024 subclasses
- Not included in default release builds unless explicitly enabled

---

## Reference Files

- [subclass_registry.py](services/subclass_registry.py) - Subclass registration
- [enhanced_subclass_manager.py](services/enhanced_subclass_manager.py) - Base class
- [subclass_action_integration.py](services/subclass_action_integration.py) - Action handlers
- [stealth_mechanics.py](services/stealth_mechanics.py) - Assassin mechanics
- [subclass_manager.py](services/subclass_manager.py) - Legacy subclass handling
- [rogue_abilities.py](services/rogue_abilities.py) - Base Rogue features
- [Barbarian_subclass.md](docs/Barbarian_subclass.md) - Architecture reference
- [Paladin_subclass.md](docs/Paladin_subclass.md) - Architecture reference