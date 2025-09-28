# First Level Spell Implementation Plan
*TaleKeeper - 4 Spells Per Class Implementation & Testing*

## Executive Summary

This document outlines the implementation and testing process for 4 first level spells per spellcasting class. These spells are selected based on:
- Combat relevance for solo play
- Clear mechanical implementation
- No movement system dependencies
- Tactical variety and class identity

## Selected Spells by Class

### Bard (4 Spells)
1. **Cure Wounds** - Direct healing (1d8 + spell mod)
2. **Healing Word** - Bonus action ranged healing (1d4 + spell mod)
3. **Faerie Fire** - AoE advantage on attacks (Dex save)
4. **Thunderwave** - AoE damage + pushback (Con save, 2d8 thunder)

### Cleric (4 Spells)
1. **Cure Wounds** - Direct healing (1d8 + spell mod)
2. **Healing Word** - Bonus action ranged healing (1d4 + spell mod)
3. **Bless** - +1d4 to attacks and saves (up to 3 targets)
4. **Guiding Bolt** - Ranged spell attack (4d6 radiant, advantage on next attack)

### Druid (4 Spells)
1. **Cure Wounds** - Direct healing (1d8 + spell mod)
2. **Healing Word** - Bonus action ranged healing (1d4 + spell mod)
3. **Entangle** - AoE restrained condition (Str save)
4. **Thunderwave** - AoE damage (Con save, 2d8 thunder)

### Paladin (4 Spells)
1. **Cure Wounds** - Direct healing (1d8 + spell mod)
2. **Bless** - +1d4 to attacks and saves (up to 3 targets)
3. **Shield of Faith** - +2 AC bonus (concentration)
4. **Divine Smite** - Extra radiant damage on melee hit (2d8 + 1d8 per slot level)

### Ranger (4 Spells)
1. **Cure Wounds** - Direct healing (1d8 + spell mod)
2. **Hunter's Mark** - Extra damage on target (1d6 per hit, concentration)
3. **Entangle** - AoE restrained condition (Str save)
4. **Goodberry** - 10 berries, each heals 1 HP

### Sorcerer (4 Spells)
1. **Magic Missile** - Auto-hit force damage (3 missiles, 1d4+1 each)
2. **Shield** - Reaction +5 AC (until start of next turn)
3. **Mage Armor** - 13 + Dex AC (8 hours)
4. **Burning Hands** - AoE fire damage (Dex save, 3d6 fire)

### Warlock (4 Spells)
1. **Hex** - Extra damage on target (1d6 necrotic per hit, concentration)
2. **Hellish Rebuke** - Reaction damage when hit (2d10 fire, Dex save half)
3. **Bane** - Penalty to attacks and saves (-1d4, up to 3 targets, Cha save)
4. **Protection from Evil and Good** - Condition immunity + disadvantage on attacks

### Wizard (4 Spells)
1. **Magic Missile** - Auto-hit force damage (3 missiles, 1d4+1 each)
2. **Shield** - Reaction +5 AC (until start of next turn)
3. **Mage Armor** - 13 + Dex AC (8 hours)
4. **Burning Hands** - AoE fire damage (Dex save, 3d6 fire)

## Implementation Process

### Phase 1: Core Spell Infrastructure (Week 1)

#### 1.1 Base Spell Classes
```python
# Location: services/spells/base_spell.py

class SpellType(Enum):
    DAMAGE = "damage"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    CONTROL = "control"
    UTILITY = "utility"

class CastingTime(Enum):
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"

class SpellImplementation:
    def __init__(self, spell_id: str, db_path: str):
        self.spell_id = spell_id
        self.db_path = db_path
        self.spell_data = self._load_spell_data()

    def cast(self, caster_id: str, spell_level: int, **kwargs) -> SpellResult:
        raise NotImplementedError

    def _load_spell_data(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM spells WHERE id = ?
            """, (self.spell_id,))
            return dict(cursor.fetchone())
```

#### 1.2 Spell Result Object
```python
@dataclass
class SpellResult:
    success: bool
    spell_id: str
    caster_id: str
    spell_level: int

    damage_dealt: Optional[int] = None
    damage_type: Optional[str] = None
    healing_done: Optional[int] = None
    targets_affected: List[str] = field(default_factory=list)

    concentration_started: bool = False
    concentration_ended: Optional[str] = None

    conditions_applied: List[Dict] = field(default_factory=list)
    conditions_removed: List[str] = field(default_factory=list)

    saving_throw_made: Optional[bool] = None
    save_dc: Optional[int] = None

    log_messages: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
```

### Phase 2: Spell Type Implementations (Week 1-2)

#### 2.1 Healing Spells
```python
# Location: services/spells/healing_spells.py

class CureWoundsSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, target_id: str) -> SpellResult:
        spell_mod = self._get_spellcasting_modifier(caster_id)
        healing_dice = spell_level

        healing = self._roll_dice(f"{healing_dice}d8") + spell_mod
        actual_healing = self._apply_healing(target_id, healing)

        return SpellResult(
            success=True,
            spell_id='cure_wounds',
            caster_id=caster_id,
            spell_level=spell_level,
            healing_done=actual_healing,
            targets_affected=[target_id],
            log_messages=[f"Cure Wounds heals {actual_healing} HP"]
        )

class HealingWordSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, target_id: str) -> SpellResult:
        spell_mod = self._get_spellcasting_modifier(caster_id)
        healing_dice = spell_level

        healing = self._roll_dice(f"{healing_dice}d4") + spell_mod
        actual_healing = self._apply_healing(target_id, healing)

        return SpellResult(
            success=True,
            spell_id='healing_word',
            caster_id=caster_id,
            spell_level=spell_level,
            healing_done=actual_healing,
            targets_affected=[target_id],
            log_messages=[f"Healing Word heals {actual_healing} HP (bonus action)"]
        )
```

#### 2.2 Direct Damage Spells
```python
# Location: services/spells/damage_spells.py

class MagicMissileSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, targets: List[str]) -> SpellResult:
        num_missiles = 3 + (spell_level - 1)
        total_damage = 0
        messages = []

        for i in range(num_missiles):
            target = targets[i % len(targets)]
            damage = self._roll_dice("1d4") + 1

            self._apply_damage(target, damage, "force")
            total_damage += damage
            messages.append(f"Missile {i+1} hits {target} for {damage} force damage")

        return SpellResult(
            success=True,
            spell_id='magic_missile',
            caster_id=caster_id,
            spell_level=spell_level,
            damage_dealt=total_damage,
            damage_type='force',
            targets_affected=targets,
            log_messages=messages
        )

class BurningHandsSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, targets: List[str]) -> SpellResult:
        damage_dice = 3 + (spell_level - 1)
        base_damage = self._roll_dice(f"{damage_dice}d6")
        save_dc = self._get_spell_save_dc(caster_id)

        affected = []
        total_damage = 0
        messages = []

        for target_id in targets:
            save_roll = self._make_saving_throw(target_id, "dexterity")

            if save_roll >= save_dc:
                actual_damage = base_damage // 2
                messages.append(f"{target_id} saves, takes {actual_damage} fire damage")
            else:
                actual_damage = base_damage
                messages.append(f"{target_id} fails save, takes {actual_damage} fire damage")

            self._apply_damage(target_id, actual_damage, "fire")
            affected.append(target_id)
            total_damage += actual_damage

        return SpellResult(
            success=True,
            spell_id='burning_hands',
            caster_id=caster_id,
            spell_level=spell_level,
            damage_dealt=total_damage,
            damage_type='fire',
            targets_affected=affected,
            save_dc=save_dc,
            log_messages=messages
        )
```

#### 2.3 Buff Spells
```python
# Location: services/spells/buff_spells.py

class BlessSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, targets: List[str]) -> SpellResult:
        max_targets = min(3, len(targets))
        selected = targets[:max_targets]

        for target_id in selected:
            self._apply_condition(target_id, {
                'condition_name': 'blessed',
                'duration_rounds': 600,
                'effects': {
                    'attack_roll_bonus': '1d4',
                    'saving_throw_bonus': '1d4'
                },
                'concentration': True,
                'caster_id': caster_id,
                'spell_id': 'bless'
            })

        self._start_concentration(caster_id, 'bless', spell_level)

        return SpellResult(
            success=True,
            spell_id='bless',
            caster_id=caster_id,
            spell_level=spell_level,
            targets_affected=selected,
            concentration_started=True,
            conditions_applied=[{'name': 'blessed', 'targets': selected}],
            log_messages=[f"Blesses {len(selected)} targets with +1d4 to attacks and saves"]
        )

class ShieldOfFaithSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, target_id: str) -> SpellResult:
        self._apply_condition(target_id, {
            'condition_name': 'shield_of_faith',
            'duration_rounds': 600,
            'effects': {
                'ac_bonus': 2
            },
            'concentration': True,
            'caster_id': caster_id,
            'spell_id': 'shield_of_faith'
        })

        self._start_concentration(caster_id, 'shield_of_faith', spell_level)

        return SpellResult(
            success=True,
            spell_id='shield_of_faith',
            caster_id=caster_id,
            spell_level=spell_level,
            targets_affected=[target_id],
            concentration_started=True,
            conditions_applied=[{'name': 'shield_of_faith', 'targets': [target_id]}],
            log_messages=[f"{target_id} gains +2 AC from Shield of Faith"]
        )
```

#### 2.4 Reaction Spells
```python
# Location: services/spells/reaction_spells.py

class ShieldSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int,
             triggering_attack: Optional[Dict] = None) -> SpellResult:
        self._apply_temporary_effect(caster_id, {
            'effect_type': 'ac_bonus',
            'bonus': 5,
            'duration': 'until_next_turn'
        })

        blocked = False
        if triggering_attack:
            old_ac = triggering_attack['target_ac']
            new_ac = old_ac + 5
            attack_roll = triggering_attack['attack_roll']

            if old_ac <= attack_roll < new_ac:
                blocked = True

        return SpellResult(
            success=True,
            spell_id='shield',
            caster_id=caster_id,
            spell_level=spell_level,
            targets_affected=[caster_id],
            log_messages=[
                f"{caster_id} gains +5 AC",
                "Shield deflects the attack!" if blocked else ""
            ]
        )

class HellishRebukeSpell(SpellImplementation):
    def cast(self, caster_id: str, spell_level: int, attacker_id: str) -> SpellResult:
        damage_dice = 2 + (spell_level - 1)
        base_damage = self._roll_dice(f"{damage_dice}d10")
        save_dc = self._get_spell_save_dc(caster_id)

        save_roll = self._make_saving_throw(attacker_id, "dexterity")

        if save_roll >= save_dc:
            actual_damage = base_damage // 2
            message = f"{attacker_id} saves, takes {actual_damage} fire damage"
        else:
            actual_damage = base_damage
            message = f"{attacker_id} fails save, takes {actual_damage} fire damage"

        self._apply_damage(attacker_id, actual_damage, "fire")

        return SpellResult(
            success=True,
            spell_id='hellish_rebuke',
            caster_id=caster_id,
            spell_level=spell_level,
            damage_dealt=actual_damage,
            damage_type='fire',
            targets_affected=[attacker_id],
            save_dc=save_dc,
            log_messages=[message]
        )
```

### Phase 3: Spell Registry & Integration (Week 2)

#### 3.1 Spell Registry
```python
# Location: services/spell_registry.py

class FirstLevelSpellRegistry:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.spells = self._register_spells()

    def _register_spells(self) -> Dict[str, SpellImplementation]:
        return {
            'cure_wounds': CureWoundsSpell('cure_wounds', self.db_path),
            'healing_word': HealingWordSpell('healing_word', self.db_path),
            'bless': BlessSpell('bless', self.db_path),
            'shield_of_faith': ShieldOfFaithSpell('shield_of_faith', self.db_path),
            'magic_missile': MagicMissileSpell('magic_missile', self.db_path),
            'shield': ShieldSpell('shield', self.db_path),
            'mage_armor': MageArmorSpell('mage_armor', self.db_path),
            'burning_hands': BurningHandsSpell('burning_hands', self.db_path),
            'thunderwave': ThunderwaveSpell('thunderwave', self.db_path),
            'faerie_fire': FaerieFireSpell('faerie_fire', self.db_path),
            'entangle': EntangleSpell('entangle', self.db_path),
            'guiding_bolt': GuidingBoltSpell('guiding_bolt', self.db_path),
            'divine_smite': DivineSmiteSpell('divine_smite', self.db_path),
            'hunters_mark': HuntersMarkSpell('hunters_mark', self.db_path),
            'goodberry': GoodberrySpell('goodberry', self.db_path),
            'hex': HexSpell('hex', self.db_path),
            'hellish_rebuke': HellishRebukeSpell('hellish_rebuke', self.db_path),
            'bane': BaneSpell('bane', self.db_path),
            'protection_from_evil_and_good': ProtectionFromEvilAndGoodSpell(
                'protection_from_evil_and_good', self.db_path
            ),
        }

    def cast_spell(self, spell_id: str, caster_id: str,
                   spell_level: int, **kwargs) -> SpellResult:
        if spell_id not in self.spells:
            return SpellResult(
                success=False,
                spell_id=spell_id,
                caster_id=caster_id,
                spell_level=spell_level,
                error_message=f"Spell {spell_id} not implemented"
            )

        spell = self.spells[spell_id]
        return spell.cast(caster_id, spell_level, **kwargs)
```

## Testing Framework

### Test Structure

#### Test 1: Basic Spell Casting
```python
# Location: test/test_first_level_spells.py

class TestFirstLevelSpells:
    def setUp(self):
        self.db_path = ":memory:"
        self.setup_test_database()
        self.spell_registry = FirstLevelSpellRegistry(self.db_path)
        self.test_wizard = self.create_test_character('wizard', level=1)
        self.test_cleric = self.create_test_character('cleric', level=1)
        self.test_target = self.create_test_character('fighter', level=1)

    def test_cure_wounds(self):
        """Test Cure Wounds healing"""
        initial_hp = 5
        self.set_character_hp(self.test_target, initial_hp)

        result = self.spell_registry.cast_spell(
            'cure_wounds',
            caster_id=self.test_cleric,
            spell_level=1,
            target_id=self.test_target
        )

        assert result.success
        assert result.healing_done > 0
        assert result.healing_done >= 1  # Minimum 1d8 roll
        assert result.healing_done <= 8 + self.get_spell_mod(self.test_cleric)

        final_hp = self.get_character_hp(self.test_target)
        assert final_hp == initial_hp + result.healing_done

    def test_magic_missile(self):
        """Test Magic Missile auto-hit damage"""
        result = self.spell_registry.cast_spell(
            'magic_missile',
            caster_id=self.test_wizard,
            spell_level=1,
            targets=[self.test_target]
        )

        assert result.success
        assert result.damage_dealt >= 6  # Minimum 3 missiles * (1+1)
        assert result.damage_dealt <= 15  # Maximum 3 missiles * (4+1)
        assert result.damage_type == 'force'
        assert len(result.targets_affected) == 1

    def test_bless_concentration(self):
        """Test Bless buff and concentration"""
        result = self.spell_registry.cast_spell(
            'bless',
            caster_id=self.test_cleric,
            spell_level=1,
            targets=[self.test_wizard, self.test_target]
        )

        assert result.success
        assert result.concentration_started
        assert len(result.targets_affected) == 2

        concentration = self.get_concentration(self.test_cleric)
        assert concentration['spell_id'] == 'bless'

        blessed_condition = self.get_condition(self.test_wizard, 'blessed')
        assert blessed_condition is not None
        assert blessed_condition['effects']['attack_roll_bonus'] == '1d4'
```

#### Test 2: Spell Slot Consumption
```python
class TestSpellSlotConsumption:
    def test_slot_usage(self):
        """Test that casting consumes spell slots"""
        slots_before = self.get_spell_slots(self.test_wizard, level=1)

        self.spell_registry.cast_spell(
            'magic_missile',
            caster_id=self.test_wizard,
            spell_level=1,
            targets=[self.test_target]
        )

        slots_after = self.get_spell_slots(self.test_wizard, level=1)
        assert slots_after['used'] == slots_before['used'] + 1

    def test_no_slots_available(self):
        """Test casting with no slots fails"""
        self.use_all_spell_slots(self.test_wizard, level=1)

        result = self.spell_registry.cast_spell(
            'magic_missile',
            caster_id=self.test_wizard,
            spell_level=1,
            targets=[self.test_target]
        )

        assert not result.success
        assert "no spell slots" in result.error_message.lower()
```

#### Test 3: Saving Throws
```python
class TestSavingThrows:
    def test_burning_hands_save(self):
        """Test Burning Hands with saving throw"""
        result = self.spell_registry.cast_spell(
            'burning_hands',
            caster_id=self.test_wizard,
            spell_level=1,
            targets=[self.test_target]
        )

        assert result.success
        assert result.save_dc is not None
        assert result.damage_dealt > 0

        base_damage = 3 * 3.5  # Average of 3d6
        assert result.damage_dealt <= base_damage  # Could be full or half
```

#### Test 4: Concentration Breaking
```python
class TestConcentration:
    def test_concentration_breaks_on_damage(self):
        """Test concentration breaks when taking damage"""
        self.spell_registry.cast_spell(
            'bless',
            caster_id=self.test_cleric,
            spell_level=1,
            targets=[self.test_wizard]
        )

        assert self.get_concentration(self.test_cleric) is not None

        self.apply_damage(self.test_cleric, 10)

        concentration_broken = self.check_concentration_save(
            self.test_cleric, damage=10
        )

        if concentration_broken:
            assert self.get_concentration(self.test_cleric) is None
            assert self.get_condition(self.test_wizard, 'blessed') is None
```

### Integration Testing

#### Test 5: Action Card Integration
```python
class TestActionCardIntegration:
    def test_spell_cards_appear(self):
        """Test that spell action cards are created"""
        action_panel = ActionPanel()
        action_panel.character_context = self.test_wizard_data

        action_panel._create_spell_action_cards()

        spell_cards = [k for k in action_panel.action_cards.keys()
                      if isinstance(k, str) and k.startswith('spell_')]

        assert 'spell_magic_missile' in action_panel.action_cards
        assert 'spell_shield' in action_panel.action_cards
        assert 'spell_mage_armor' in action_panel.action_cards
        assert 'spell_burning_hands' in action_panel.action_cards
```

## Implementation Timeline

### Week 1: Core Infrastructure
- Day 1-2: Base spell classes and SpellResult object
- Day 3-4: Healing and direct damage spell implementations
- Day 5: Testing framework setup

### Week 2: Spell Implementations
- Day 1-2: Buff/debuff and control spells
- Day 3: Reaction spells
- Day 4-5: Integration with action panel and combat log

### Week 3: Testing & Polish
- Day 1-2: Comprehensive testing of all 32 spells
- Day 3: Bug fixes and edge cases
- Day 4-5: Documentation and cleanup

## Success Criteria

- [ ] All 32 first level spells (4 per class) implemented
- [ ] All spells have passing unit tests
- [ ] Spell slots consumed correctly
- [ ] Concentration tracked and broken appropriately
- [ ] Action cards display available spells
- [ ] Combat log shows spell effects clearly
- [ ] No performance degradation with multiple active effects
- [ ] Saving throws calculated correctly
- [ ] Healing integrates with existing HP system
- [ ] Damage applies with type resistance/immunity checks

## Summary

This implementation focuses on 4 carefully selected first level spells per class that provide:
- **Immediate combat utility** (damage, healing, buffs)
- **Class identity** (unique spells per class where possible)
- **Tactical depth** (concentration choices, reaction timing)
- **Clear mechanics** (no ambiguous edge cases)

The phased approach ensures a solid foundation before expanding to higher level spells.