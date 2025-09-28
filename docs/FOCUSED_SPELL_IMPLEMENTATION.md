# Focused Spell Implementation - 4 Classes
*Cleric, Paladin, Warlock, Wizard - Testing Leveling & Spell Selection*

## Scope

**4 Classes**: Cleric, Paladin, Warlock, Wizard
**Per Class**: 6 first level spells + 4 cantrips (Paladin: 6 first level only)
**Total**: 24 level 1 spells + 12 cantrips = 36 spells

**Focus**: Enable testing of:
- Leveling up and gaining new spell choices
- Spell selection at character creation
- Spell preparation mechanics
- Cantrip vs leveled spell distinction

## Spell Selection by Class

### Cleric

#### Cantrips (4)
1. **Sacred Flame** - Dex save, 1d8 radiant damage
2. **Guidance** - +1d4 to ability check (concentration)
3. **Resistance** - Reduce damage by 1d4 (concentration, 1 min)
4. **Light** - Create light on object for 1 hour

#### Level 1 Spells (6)
1. **Cure Wounds** - Touch, heal 1d8 + spell mod
2. **Healing Word** - Bonus action, ranged, heal 1d4 + spell mod
3. **Bless** - 3 targets, +1d4 to attacks/saves, concentration, 1 min
4. **Guiding Bolt** - Ranged spell attack, 4d6 radiant, next attack has advantage
5. **Shield of Faith** - +2 AC, concentration, 10 min
6. **Inflict Wounds** - Melee spell attack, 3d10 necrotic

### Paladin

#### Cantrips (0)
*Paladins do not receive cantrips in D&D 2024*

#### Level 1 Spells (6)
1. **Cure Wounds** - Touch, heal 1d8 + spell mod
2. **Bless** - 3 targets, +1d4 to attacks/saves, concentration, 1 min
3. **Shield of Faith** - +2 AC, concentration, 10 min
4. **Divine Smite** - Add 2d8 radiant to melee weapon hit (3d8 vs undead/fiend)
5. **Divine Favor** - +1d4 radiant to weapon attacks, concentration, 1 min
6. **Protection from Evil and Good** - Condition immunity + disadvantage on attacks

### Warlock

#### Cantrips (4)
1. **Eldritch Blast** - Ranged spell attack, 1d10 force damage
2. **Chill Touch** - Ranged spell attack, 1d8 necrotic, no healing next turn
3. **Poison Spray** - Con save, 1d12 poison damage, 10 ft range
4. **Prestidigitation** - Minor magical tricks and utility

#### Level 1 Spells (6)
1. **Hex** - 1d6 extra necrotic per hit, disadvantage on ability checks, concentration, 1 hr
2. **Hellish Rebuke** - Reaction when hit, 2d10 fire damage, Dex save half
3. **Bane** - 3 targets, -1d4 to attacks/saves, Cha save negates, concentration, 1 min
4. **Protection from Evil and Good** - Condition immunity + disadvantage on attacks
5. **Armor of Agathys** - 5 temp HP, melee attackers take 5 cold damage, 1 hour
6. **Hideous Laughter** - Wis save, Prone + Incapacitated, concentration, 1 min

### Wizard

#### Cantrips (4)
1. **Fire Bolt** - Ranged spell attack, 1d10 fire damage
2. **Ray of Frost** - Ranged spell attack, 1d8 cold damage, -10 ft speed
3. **Shocking Grasp** - Melee spell attack, 1d8 lightning, no reactions
4. **Mage Hand** - Invisible hand manipulates objects at 30 ft

#### Level 1 Spells (6)
1. **Magic Missile** - Auto-hit, 3 missiles, 1d4+1 force each
2. **Shield** - Reaction, +5 AC until start of next turn
3. **Mage Armor** - 13 + Dex AC, 8 hours
4. **Burning Hands** - 15 ft cone, 3d6 fire, Dex save half
5. **Grease** - 10 ft square, prone on Dex save fail, difficult terrain
6. **False Life** - 1d4+4 temporary HP, 1 hour

## Implementation Architecture

### Spell Type Categories

#### Cantrips
- No spell slot consumption
- Scale with character level (not implemented yet)
- Can be cast unlimited times
- Typically weaker than leveled spells

```python
class Cantrip(SpellImplementation):
    def __init__(self, spell_id: str, db_path: str):
        super().__init__(spell_id, db_path)
        self.requires_spell_slot = False

    def get_damage_dice_count(self, caster_level: int) -> int:
        if caster_level >= 17:
            return 4
        elif caster_level >= 11:
            return 3
        elif caster_level >= 5:
            return 2
        else:
            return 1
```

#### Attack Cantrips
```python
class FireBoltCantrip(Cantrip):
    def cast(self, caster_id: str, target_id: str, **kwargs) -> SpellResult:
        caster_level = self._get_character_level(caster_id)
        dice_count = self.get_damage_dice_count(caster_level)

        attack_bonus = self._get_spell_attack_bonus(caster_id)
        attack_roll = self._roll_d20() + attack_bonus
        target_ac = self._get_target_ac(target_id)

        if attack_roll >= target_ac:
            damage = self._roll_dice(f"{dice_count}d10")
            self._apply_damage(target_id, damage, "fire")

            return SpellResult(
                success=True,
                spell_id='fire_bolt',
                caster_id=caster_id,
                spell_level=0,
                damage_dealt=damage,
                damage_type='fire',
                targets_affected=[target_id],
                log_messages=[f"Fire Bolt hits for {damage} fire damage!"]
            )
        else:
            return SpellResult(
                success=True,
                spell_id='fire_bolt',
                caster_id=caster_id,
                spell_level=0,
                log_messages=["Fire Bolt misses!"]
            )
```

#### Save Cantrips
```python
class SacredFlameCantrip(Cantrip):
    def cast(self, caster_id: str, target_id: str, **kwargs) -> SpellResult:
        caster_level = self._get_character_level(caster_id)
        dice_count = self.get_damage_dice_count(caster_level)
        save_dc = self._get_spell_save_dc(caster_id)

        save_roll = self._make_saving_throw(target_id, "dexterity")

        if save_roll < save_dc:
            damage = self._roll_dice(f"{dice_count}d8")
            self._apply_damage(target_id, damage, "radiant")

            return SpellResult(
                success=True,
                spell_id='sacred_flame',
                caster_id=caster_id,
                spell_level=0,
                damage_dealt=damage,
                damage_type='radiant',
                targets_affected=[target_id],
                save_dc=save_dc,
                saving_throw_made=False,
                log_messages=[f"Sacred Flame hits for {damage} radiant damage!"]
            )
        else:
            return SpellResult(
                success=True,
                spell_id='sacred_flame',
                caster_id=caster_id,
                spell_level=0,
                save_dc=save_dc,
                saving_throw_made=True,
                log_messages=["Target saves against Sacred Flame!"]
            )
```

## Leveling & Spell Selection Mechanics

### Character Creation Spell Selection

#### Wizard (Learns from Spellbook)
- Starts with 6 level 1 spells in spellbook
- Can prepare [Intelligence modifier + Wizard level] spells
- Knows all selected cantrips immediately

```python
def initialize_wizard_spells(character_id: str, selected_spells: List[str],
                            selected_cantrips: List[str]):
    """Initialize wizard's starting spells"""
    # Add 6 level 1 spells to spellbook
    for spell_id in selected_spells[:6]:
        add_spell_to_spellbook(character_id, spell_id)

    # Add cantrips (always prepared)
    for cantrip_id in selected_cantrips[:3]:  # Level 1 wizard gets 3 cantrips
        add_known_cantrip(character_id, cantrip_id)
```

#### Cleric (Prepares from Full List)
- Can prepare [Wisdom modifier + Cleric level] spells
- Has access to entire Cleric spell list
- Knows all selected cantrips immediately

```python
def initialize_cleric_spells(character_id: str, prepared_spells: List[str],
                            selected_cantrips: List[str]):
    """Initialize cleric's starting spells"""
    wisdom_mod = get_ability_modifier(character_id, 'wisdom')
    max_prepared = wisdom_mod + 1  # Level 1

    # Set prepared spells
    for spell_id in prepared_spells[:max_prepared]:
        prepare_spell(character_id, spell_id)

    # Add cantrips (always prepared)
    for cantrip_id in selected_cantrips[:3]:  # Level 1 cleric gets 3 cantrips
        add_known_cantrip(character_id, cantrip_id)
```

#### Warlock (Knows Limited Spells)
- Knows 2 spells at level 1
- All known spells are always available (no preparation)
- Knows 2 cantrips at level 1

```python
def initialize_warlock_spells(character_id: str, selected_spells: List[str],
                             selected_cantrips: List[str]):
    """Initialize warlock's starting spells"""
    # Add 2 known spells
    for spell_id in selected_spells[:2]:
        add_known_spell(character_id, spell_id)

    # Add 2 cantrips
    for cantrip_id in selected_cantrips[:2]:
        add_known_cantrip(character_id, cantrip_id)
```

#### Paladin (Prepares from Paladin List)
- Can prepare [Charisma modifier + half Paladin level] spells
- At level 1, can only prepare if Cha mod > 0
- No cantrips

```python
def initialize_paladin_spells(character_id: str, prepared_spells: List[str]):
    """Initialize paladin's starting spells"""
    charisma_mod = get_ability_modifier(character_id, 'charisma')
    paladin_level = 1
    max_prepared = max(0, charisma_mod + (paladin_level // 2))

    # Set prepared spells (may be 0 if low Cha)
    for spell_id in prepared_spells[:max_prepared]:
        prepare_spell(character_id, spell_id)
```

### Leveling Up Spell Progression

#### Level 2 Progression
```python
def level_up_spellcaster(character_id: str, new_level: int, class_name: str):
    """Handle spell progression when leveling up"""

    if class_name == 'wizard':
        # Learn 2 new spells
        spell_choices = get_available_wizard_spells(new_level)
        return {
            'action': 'select_spells_to_learn',
            'choices': spell_choices,
            'count': 2
        }

    elif class_name == 'warlock':
        # Learn 1 new spell, can swap 1 existing
        spell_choices = get_available_warlock_spells(new_level)
        return {
            'action': 'select_spell_to_learn',
            'choices': spell_choices,
            'count': 1,
            'allow_swap': True
        }

    elif class_name == 'cleric':
        # No new spells learned, but can prepare more
        wisdom_mod = get_ability_modifier(character_id, 'wisdom')
        max_prepared = wisdom_mod + new_level
        return {
            'action': 'update_prepared_count',
            'max_prepared': max_prepared
        }

    elif class_name == 'paladin':
        # Can prepare more spells
        charisma_mod = get_ability_modifier(character_id, 'charisma')
        max_prepared = charisma_mod + (new_level // 2)
        return {
            'action': 'update_prepared_count',
            'max_prepared': max_prepared
        }
```

## Database Schema

### Spell Data Tables
```sql
CREATE TABLE spells (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    level INTEGER NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_text TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,
    components TEXT,
    description TEXT,

    damage_dice TEXT,
    damage_type TEXT,
    healing_dice TEXT,
    save_type TEXT,
    spell_attack BOOLEAN DEFAULT FALSE,
    aoe_type TEXT,
    aoe_size INTEGER
);

CREATE TABLE cantrips (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_text TEXT NOT NULL,
    damage_dice_base TEXT,
    damage_type TEXT,
    save_type TEXT,
    spell_attack BOOLEAN DEFAULT FALSE,
    scales_with_level BOOLEAN DEFAULT TRUE,
    description TEXT,

    FOREIGN KEY (id) REFERENCES spells(id)
);
```

### Character Spell Tracking
```sql
CREATE TABLE character_spellcasting (
    character_id TEXT PRIMARY KEY,
    spellcasting_class TEXT NOT NULL,
    spellcasting_ability TEXT NOT NULL,
    spell_save_dc INTEGER,
    spell_attack_bonus INTEGER,
    spells_prepared_max INTEGER,

    FOREIGN KEY (character_id) REFERENCES characters(id)
);

CREATE TABLE character_known_cantrips (
    character_id TEXT NOT NULL,
    cantrip_id TEXT NOT NULL,
    learned_at_level INTEGER,

    PRIMARY KEY (character_id, cantrip_id),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (cantrip_id) REFERENCES cantrips(id)
);

CREATE TABLE character_known_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    learned_at_level INTEGER,
    source TEXT DEFAULT 'class',

    PRIMARY KEY (character_id, spell_id),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

CREATE TABLE character_prepared_spells (
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    prepared_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (character_id, spell_id),
    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

CREATE TABLE character_spell_slots (
    character_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    total_slots INTEGER NOT NULL,
    used_slots INTEGER DEFAULT 0,

    PRIMARY KEY (character_id, spell_level),
    FOREIGN KEY (character_id) REFERENCES characters(id)
);
```

## Testing Framework

### Test 1: Cantrip Scaling
```python
def test_cantrip_damage_scaling():
    """Test that cantrips scale with character level"""
    wizard = create_test_character('wizard', level=1)
    target = create_test_character('fighter', level=1)

    # Level 1: 1d10
    result = cast_spell('fire_bolt', wizard, target)
    assert 1 <= result.damage_dealt <= 10

    # Level up to 5
    level_up_character(wizard, 5)

    # Level 5: 2d10
    result = cast_spell('fire_bolt', wizard, target)
    assert 2 <= result.damage_dealt <= 20
```

### Test 2: Spell Selection at Creation
```python
def test_wizard_spell_selection():
    """Test wizard starts with 6 spells in spellbook"""
    wizard = create_character('wizard', level=1,
        selected_spells=['magic_missile', 'shield', 'mage_armor',
                        'burning_hands', 'grease', 'false_life'],
        selected_cantrips=['fire_bolt', 'ray_of_frost', 'mage_hand']
    )

    spellbook = get_spellbook(wizard)
    assert len(spellbook) == 6

    cantrips = get_known_cantrips(wizard)
    assert len(cantrips) == 3
```

### Test 3: Leveling Up and Learning Spells
```python
def test_wizard_learns_spells_on_levelup():
    """Test wizard learns 2 new spells at level up"""
    wizard = create_test_character('wizard', level=1)

    initial_spells = len(get_spellbook(wizard))

    level_up_data = level_up_spellcaster(wizard, 2, 'wizard')

    assert level_up_data['action'] == 'select_spells_to_learn'
    assert level_up_data['count'] == 2

    # Select 2 new spells
    learn_spells(wizard, ['sleep', 'detect_magic'])

    final_spells = len(get_spellbook(wizard))
    assert final_spells == initial_spells + 2
```

### Test 4: Preparation System
```python
def test_cleric_preparation():
    """Test cleric can prepare spells from full list"""
    cleric = create_test_character('cleric', level=1, wisdom=16)  # +3 mod

    max_prepared = 1 + 3  # level + wis mod = 4

    prepare_spells(cleric, ['cure_wounds', 'bless', 'shield_of_faith', 'guiding_bolt'])

    prepared = get_prepared_spells(cleric)
    assert len(prepared) == 4

    # Try to prepare 5th spell (should fail)
    result = prepare_spell(cleric, 'inflict_wounds')
    assert not result.success
    assert "maximum" in result.error_message.lower()
```

## Implementation Timeline

### Week 1: Core Infrastructure
- Day 1-2: Cantrip base classes and scaling
- Day 3-4: Attack and save-based cantrips
- Day 5: Cantrip testing

### Week 2: Level 1 Spells
- Day 1-2: Healing, damage, and buff spells
- Day 3: Reaction spells (Shield, Hellish Rebuke)
- Day 4-5: Complex spells (Hex, Bless, Grease)

### Week 3: Spell Selection System
- Day 1-2: Character creation spell selection UI
- Day 3: Level up spell learning UI
- Day 4: Preparation system UI
- Day 5: Integration testing

## Success Criteria

- [ ] All 12 cantrips implemented and scaling correctly
- [ ] All 24 level 1 spells implemented and tested
- [ ] Character creation allows spell/cantrip selection
- [ ] Leveling up properly grants new spells/slots
- [ ] Wizard spellbook system working
- [ ] Cleric/Paladin preparation system working
- [ ] Warlock known spell system working
- [ ] Spell slot consumption and tracking accurate
- [ ] UI shows available vs prepared vs known spells correctly

## Summary

This focused implementation covers the 4 primary spellcasting classes with enough spells to:
- Test full spell selection at character creation
- Test leveling up and gaining new spell options
- Test different spellcasting systems (prepared, known, spellbook)
- Provide tactical variety in combat
- Enable comprehensive testing of spell mechanics

Total scope: 36 spells (12 cantrips + 24 level 1 spells) across 4 classes.