# Spell Card Display and Mechanical Implementation Analysis
*Detailed breakdown of 36 spells for TaleKeeper implementation*

## Document Purpose

This analysis provides detailed specifications for each spell:
1. **Card Display**: How the spell appears as an action card
2. **Mechanical Implementation**: What happens when cast
3. **Special Considerations**: Edge cases, interactions, limitations
4. **Implementation Patterns**: Reusable patterns for similar spells

## Implementation Patterns Discovered

### Pattern 1: Simple Damage Cantrip
**Examples**: Fire Bolt, Ray of Frost, Shocking Grasp, Sacred Flame, Chill Touch, Poison Spray

**Card Display**:
- Icon: School-based emoji (🔥 fire, ❄️ cold, ⚡ lightning, ✨ radiant, 💀 necrotic, ☠️ poison)
- Name: Spell name
- Description: "XdY [damage type] | [Save or Attack]"
- Action Type: SPELL_ATTACK

**Mechanical Implementation**:
```python
class DamageCantrip(Cantrip):
    def cast(self, caster_id: str, target_id: str) -> SpellResult:
        caster_level = get_character_level(caster_id)
        dice_count = calculate_cantrip_dice(caster_level)  # 1/2/3/4 at 1/5/11/17

        if self.requires_attack_roll:
            attack_bonus = get_spell_attack_bonus(caster_id)
            attack_roll = roll_d20() + attack_bonus
            target_ac = get_target_ac(target_id)

            if attack_roll >= target_ac:
                damage = roll_dice(f"{dice_count}d{self.damage_die}")
                apply_damage(target_id, damage, self.damage_type)
                return success_result(damage, target_id)
            else:
                return miss_result()
        else:
            save_dc = get_spell_save_dc(caster_id)
            save_roll = make_saving_throw(target_id, self.save_type)

            if save_roll < save_dc:
                damage = roll_dice(f"{dice_count}d{self.damage_die}")
                apply_damage(target_id, damage, self.damage_type)
                return success_result(damage, target_id)
            else:
                return saved_result()
```

**Special Considerations**:
- Cantrips scale automatically with character level (NOT spell level)
- No spell slot consumption
- Must track whether attack roll or saving throw
- Some cantrips have additional effects (Ray of Frost reduces speed, Chill Touch prevents healing)

---

### Pattern 2: Direct Healing Spell
**Examples**: Cure Wounds, Healing Word

**Card Display**:
- Icon: ❤️ or 💚
- Name: Spell name + (Lvl X)
- Description: "Heal XdY + mod | Touch/Range 60ft"
- Action Type: SPELL_UTILITY

**Mechanical Implementation**:
```python
class HealingSpell(LeveledSpell):
    def cast(self, caster_id: str, target_id: str, spell_level: int) -> SpellResult:
        spell_mod = get_spellcasting_modifier(caster_id)
        dice_count = spell_level  # Scales 1:1 with slot level

        healing = roll_dice(f"{dice_count}d{self.base_die}") + spell_mod

        # Critical: Use character sheet HP, not database during combat
        actual_healing = apply_healing(target_id, healing)

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            healing_done=actual_healing,
            targets_affected=[target_id],
            log_messages=[f"Heals {actual_healing} HP"]
        )
```

**Special Considerations**:
- **CRITICAL**: During combat, HP is tracked in character_sheet.character_data, NOT database
- Must read current HP from character sheet before applying healing
- Healing cannot exceed max HP
- Healing Word is bonus action (casting_time must be checked)
- Scales with higher spell slots

---

### Pattern 3: Concentration Buff Spell
**Examples**: Bless, Shield of Faith, Hex, Guidance, Resistance

**Card Display**:
- Icon: 🛡️ (defense), ⚔️ (offense), 🎯 (accuracy), 🌟 (general buff)
- Name: Spell name + (Lvl X) or (Cantrip)
- Description: "+Xd4 to [thing] | Conc, X min"
- Action Type: SPELL_UTILITY

**Mechanical Implementation**:
```python
class ConcentrationBuffSpell(LeveledSpell):
    def cast(self, caster_id: str, targets: List[str], spell_level: int) -> SpellResult:
        # End any existing concentration first
        existing_concentration = get_concentration(caster_id)
        if existing_concentration:
            end_concentration(caster_id, existing_concentration['spell_id'])

        # Determine number of targets (often scales with spell level)
        max_targets = self.base_targets + (spell_level - self.base_spell_level)
        selected_targets = targets[:max_targets]

        # Apply condition to each target
        for target_id in selected_targets:
            apply_condition(target_id, {
                'condition_name': self.condition_name,
                'duration_rounds': self.duration_rounds,
                'effects': self.effects_dict,
                'concentration': True,
                'caster_id': caster_id,
                'spell_id': self.spell_id
            })

        # Start concentration for caster
        start_concentration(caster_id, self.spell_id, spell_level, self.duration_rounds)

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            targets_affected=selected_targets,
            concentration_started=True,
            conditions_applied=[{
                'name': self.condition_name,
                'targets': selected_targets
            }]
        )
```

**Special Considerations**:
- MUST check for existing concentration and end it
- Concentration breaks on:
  - Caster takes damage (Constitution save: DC = 10 or half damage, whichever is higher)
  - Caster is incapacitated, unconscious, or dies
  - Caster casts another concentration spell
- Duration tracked in rounds (10 rounds = 1 minute)
- When concentration breaks, all effects end immediately
- Some buffs affect attack rolls, some saving throws, some both

---

### Pattern 4: Reaction Spell
**Examples**: Shield, Hellish Rebuke

**Card Display**:
- Icon: 🛡️ (defensive) or 🔥 (offensive)
- Name: Spell name + (Lvl X)
- Description: "Reaction | +X AC or XdY damage"
- Action Type: SPELL_REACTION

**Mechanical Implementation**:
```python
class ReactionSpell(LeveledSpell):
    def cast(self, caster_id: str, spell_level: int, trigger_context: Dict) -> SpellResult:
        # Reaction spells trigger in response to events
        # trigger_context contains info about what triggered the reaction

        if self.is_defensive:
            # Shield-type spell
            bonus = self.calculate_bonus(spell_level)
            apply_temporary_effect(caster_id, {
                'effect_type': 'ac_bonus',
                'bonus': bonus,
                'duration': 'until_next_turn'
            })

            # Check if this retroactively blocks the triggering attack
            blocked = self.check_if_blocks_attack(trigger_context, bonus)

        else:
            # Hellish Rebuke-type spell
            attacker_id = trigger_context['attacker_id']
            damage_dice = self.base_dice + (spell_level - self.base_spell_level)
            base_damage = roll_dice(f"{damage_dice}d{self.damage_die}")

            save_dc = get_spell_save_dc(caster_id)
            save_roll = make_saving_throw(attacker_id, self.save_type)

            actual_damage = base_damage if save_roll < save_dc else base_damage // 2
            apply_damage(attacker_id, actual_damage, self.damage_type)

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(success=True, ...)
```

**Special Considerations**:
- Reaction spells must be available as a reaction (not used this turn)
- UI needs special handling: prompt when trigger condition occurs
- Shield can block Magic Missile entirely (special case)
- Hellish Rebuke allows save for half damage
- Consume reaction for the round

---

### Pattern 5: AoE Damage Spell
**Examples**: Burning Hands, Thunderwave

**Card Display**:
- Icon: 🔥 (fire), ⚡ (lightning/thunder), ❄️ (cold)
- Name: Spell name + (Lvl X)
- Description: "XdY [type] | 15ft cone/cube | [Save] half"
- Action Type: SPELL_ATTACK

**Mechanical Implementation**:
```python
class AoEDamageSpell(LeveledSpell):
    def cast(self, caster_id: str, targets: List[str], spell_level: int) -> SpellResult:
        # Calculate damage
        damage_dice = self.base_dice + (spell_level - self.base_spell_level)
        base_damage = roll_dice(f"{damage_dice}d{self.damage_die}")

        save_dc = get_spell_save_dc(caster_id)
        affected = []
        total_damage = 0
        messages = []

        for target_id in targets:
            save_roll = make_saving_throw(target_id, self.save_type)

            if save_roll >= save_dc:
                actual_damage = base_damage // 2
                messages.append(f"{target_id} saves, takes {actual_damage} {self.damage_type}")
            else:
                actual_damage = base_damage
                messages.append(f"{target_id} fails, takes {actual_damage} {self.damage_type}")

            apply_damage(target_id, actual_damage, self.damage_type)
            affected.append(target_id)
            total_damage += actual_damage

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            damage_dealt=total_damage,
            damage_type=self.damage_type,
            targets_affected=affected,
            save_dc=save_dc,
            log_messages=messages
        )
```

**Special Considerations**:
- Need to identify all targets in area (currently no positioning system)
- For implementation: UI must allow selecting multiple targets
- All targets get a saving throw
- Save for half damage (round down)
- Damage is same for all targets (roll once, apply to all)

---

### Pattern 6: Auto-Hit Damage Spell
**Examples**: Magic Missile

**Card Display**:
- Icon: ✨ or 🌟
- Name: Magic Missile (Lvl X)
- Description: "Auto-hit | X missiles | 1d4+1 force each"
- Action Type: SPELL_ATTACK

**Mechanical Implementation**:
```python
class MagicMissileSpell(LeveledSpell):
    def cast(self, caster_id: str, targets: List[str], spell_level: int) -> SpellResult:
        num_missiles = 3 + (spell_level - 1)  # 3 at 1st, +1 per level
        total_damage = 0
        messages = []

        for i in range(num_missiles):
            target = targets[i % len(targets)]  # Distribute among targets
            damage = roll_dice("1d4") + 1  # Always 1d4+1 per missile

            apply_damage(target, damage, "force")
            total_damage += damage
            messages.append(f"Missile {i+1} hits {target} for {damage} force")

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            damage_dealt=total_damage,
            damage_type='force',
            targets_affected=targets,
            log_messages=messages
        )
```

**Special Considerations**:
- NEVER misses (no attack roll or save)
- Shield spell completely negates Magic Missile
- Each missile rolled separately (can have different damage)
- Can distribute missiles among multiple targets
- Force damage (rarely resisted)

---

## Spell-by-Spell Analysis

### CLERIC SPELLS

#### Sacred Flame (Cantrip)
**Pattern**: Simple Damage Cantrip (Save-based)

**Card Display**:
- Icon: ✨
- Name: "Sacred Flame"
- Description: "1d8 radiant | Dex save"
- Scales: 1d8 → 2d8 → 3d8 → 4d8 at levels 1/5/11/17

**Mechanical Implementation**:
- Saving throw: Dexterity
- Damage type: Radiant
- Range: 60 feet
- No cover bonus (flames descend from above)

**Special Considerations**:
- Target gains no benefit from cover (unique property)
- Good against high-AC, low-Dex enemies
- Radiant damage is useful vs undead

**Implementation Notes**:
```python
def cast_sacred_flame(caster_id, target_id):
    caster_level = get_character_level(caster_id)
    dice_count = [1, 1, 2, 2, 3, 3, 4][min(caster_level // 3, 6)]

    save_dc = get_spell_save_dc(caster_id)
    save_roll = make_saving_throw(target_id, "dexterity")

    if save_roll < save_dc:
        damage = roll_dice(f"{dice_count}d8")
        apply_damage(target_id, damage, "radiant")
        return success_result(damage)
    else:
        return save_result()
```

---

#### Guidance (Cantrip)
**Pattern**: Concentration Buff Spell

**Card Display**:
- Icon: 🎯
- Name: "Guidance"
- Description: "+1d4 to ability check | Touch | Conc, 1 min"

**Mechanical Implementation**:
- Target: 1 creature (touch range)
- Duration: Concentration, up to 1 minute (10 rounds)
- Effect: Before the spell ends, target can add 1d4 to one ability check of their choice

**Special Considerations**:
- Only affects ability checks, NOT attack rolls or saving throws
- Single use: spell ends when the die is rolled
- Must be cast BEFORE the ability check
- Concentration required
- Not useful in combat (ability checks are rare in combat)

**Implementation Notes**:
```python
def cast_guidance(caster_id, target_id):
    # Start concentration
    start_concentration(caster_id, 'guidance', 0, duration_rounds=10)

    # Apply condition that grants +1d4 to next ability check
    apply_condition(target_id, {
        'condition_name': 'guided',
        'duration_rounds': 10,
        'charges': 1,  # Single use
        'effect': 'ability_check_bonus_1d4',
        'concentration': True,
        'caster_id': caster_id
    })

    return success_result(target_id, concentration=True)
```

**LOW PRIORITY**: Ability checks are rare in combat-focused solo play

---

#### Resistance (Cantrip)
**Pattern**: Concentration Buff Spell (Damage Reduction)

**Card Display**:
- Icon: 🛡️
- Name: "Resistance"
- Description: "-1d4 damage once | Touch | Conc, 1 min"

**Mechanical Implementation**:
- Target: 1 creature (touch range)
- Duration: Concentration, up to 1 minute (10 rounds)
- Effect: Choose damage type; reduce damage of that type by 1d4 (once per turn)

**Special Considerations**:
- Damage reduction, not damage prevention
- Only works once per turn
- Must choose damage type when cast (Acid, Bludgeoning, Cold, Fire, Lightning, Necrotic, Piercing, Poison, Radiant, Slashing, Thunder)
- Very tactical choice: need to predict enemy damage type

**Implementation Notes**:
```python
def cast_resistance(caster_id, target_id, damage_type_choice):
    start_concentration(caster_id, 'resistance', 0, duration_rounds=10)

    apply_condition(target_id, {
        'condition_name': 'resistant',
        'duration_rounds': 10,
        'damage_type': damage_type_choice,
        'reduction': '1d4',
        'per_turn': True,  # Only applies once per turn
        'concentration': True,
        'caster_id': caster_id
    })

    return success_result(target_id, concentration=True)

# When damage is applied:
def apply_damage_with_resistance(target_id, damage, damage_type):
    resistant_condition = get_condition(target_id, 'resistant')

    if resistant_condition and resistant_condition['damage_type'] == damage_type:
        if not resistant_condition['used_this_turn']:
            reduction = roll_dice('1d4')
            final_damage = max(0, damage - reduction)
            mark_resistance_used_this_turn(target_id)
            return final_damage

    return damage
```

**UI Consideration**: Need dropdown or selection UI for damage type when casting

---

#### Light (Cantrip)
**Pattern**: Utility Cantrip

**Card Display**:
- Icon: 💡
- Name: "Light"
- Description: "Illuminate object | 60ft | 1 hour"

**Mechanical Implementation**:
- Target: One object
- Duration: 1 hour
- Effect: Object sheds bright light in 20-foot radius, dim light for additional 20 feet
- Can be dismissed as action

**Special Considerations**:
- **NOT RELEVANT for solo tactical combat**
- Exploration/dungeon crawling utility
- No mechanical benefit in combat

**Implementation Notes**:
```python
# SKIP IMPLEMENTATION - Low priority utility
# Only implement if exploration features are added
```

**SKIP FOR NOW**: Not relevant to current combat focus

---

#### Cure Wounds (Level 1)
**Pattern**: Direct Healing Spell

**Card Display**:
- Icon: ❤️
- Name: "Cure Wounds (Lvl 1)"
- Description: "Heal 1d8+mod | Touch"
- Scales at higher levels: 1d8 per slot level

**Mechanical Implementation**:
- Action: Standard action
- Range: Touch
- Base healing: 1d8 + spellcasting ability modifier
- Scaling: +1d8 per spell slot level above 1st

**Special Considerations**:
- **CRITICAL HP TRACKING**: Must use character_sheet HP during combat
- Cannot exceed maximum HP
- Requires touch (melee range)
- Most efficient single-target healing

**Implementation Notes**:
```python
def cast_cure_wounds(caster_id, target_id, spell_level):
    # Get spellcasting modifier (Wisdom for Cleric)
    spell_mod = get_ability_modifier(caster_id, 'wisdom')

    # Roll healing: 1d8 per spell level + modifier
    healing = roll_dice(f"{spell_level}d8") + spell_mod

    # CRITICAL: Get current HP from character sheet, not database
    if in_combat():
        current_hp = get_character_sheet_hp(target_id)
        max_hp = get_character_sheet_max_hp(target_id)
    else:
        current_hp = get_database_hp(target_id)
        max_hp = get_database_max_hp(target_id)

    # Apply healing (cannot exceed max HP)
    actual_healing = min(healing, max_hp - current_hp)

    if in_combat():
        set_character_sheet_hp(target_id, current_hp + actual_healing)
    else:
        set_database_hp(target_id, current_hp + actual_healing)

    consume_spell_slot(caster_id, spell_level)

    return SpellResult(
        success=True,
        healing_done=actual_healing,
        targets_affected=[target_id],
        log_messages=[f"Cure Wounds heals {actual_healing} HP"]
    )
```

**UI Consideration**: Need to show available spell slots and allow level selection

---

#### Healing Word (Level 1)
**Pattern**: Direct Healing Spell (Bonus Action)

**Card Display**:
- Icon: 💚
- Name: "Healing Word (Lvl 1)"
- Description: "Heal 1d4+mod | 60ft | BONUS"
- Scales at higher levels: 1d4 per slot level

**Mechanical Implementation**:
- Action: **BONUS ACTION** (can attack same turn)
- Range: 60 feet (no touch required)
- Base healing: 1d4 + spellcasting ability modifier
- Scaling: +1d4 per spell slot level above 1st

**Special Considerations**:
- **BONUS ACTION ECONOMY**: This is huge for action economy
- Can heal AND attack on same turn
- Less healing than Cure Wounds (d4 vs d8)
- Ranged (can heal from distance)
- Perfect for getting downed allies back in fight

**Implementation Notes**:
```python
def cast_healing_word(caster_id, target_id, spell_level):
    # Check bonus action available
    if not has_bonus_action_available(caster_id):
        return failure_result("No bonus action available")

    spell_mod = get_ability_modifier(caster_id, 'wisdom')
    healing = roll_dice(f"{spell_level}d4") + spell_mod

    # Same HP tracking as Cure Wounds
    actual_healing = apply_healing_safely(target_id, healing)

    consume_spell_slot(caster_id, spell_level)
    consume_bonus_action(caster_id)

    return SpellResult(
        success=True,
        healing_done=actual_healing,
        targets_affected=[target_id],
        action_type='bonus_action',
        log_messages=[f"Healing Word heals {actual_healing} HP (bonus action)"]
    )
```

**UI Consideration**: Card should be visually distinct to show BONUS ACTION

---

#### Bless (Level 1)
**Pattern**: Concentration Buff Spell

**Card Display**:
- Icon: ⚔️🛡️
- Name: "Bless (Lvl 1)"
- Description: "+1d4 attacks/saves | 3 targets | Conc, 1 min"
- Scales: +1 target per spell level above 1st

**Mechanical Implementation**:
- Action: Standard action
- Range: 30 feet
- Targets: Up to 3 creatures (scales with higher spell slots)
- Duration: Concentration, up to 1 minute (10 rounds)
- Effect: Targets add 1d4 to attack rolls and saving throws

**Special Considerations**:
- EXTREMELY POWERFUL in solo play (affects every attack and save)
- Concentration: must maintain, breaks if caster damaged and fails Con save
- Multiple targets: can buff entire party
- Affects both offense (attacks) and defense (saves)

**Implementation Notes**:
```python
def cast_bless(caster_id, targets, spell_level):
    # Check and end existing concentration
    end_existing_concentration(caster_id)

    # Calculate number of targets
    max_targets = 3 + (spell_level - 1)
    selected_targets = targets[:max_targets]

    # Apply blessed condition to each target
    for target_id in selected_targets:
        apply_condition(target_id, {
            'condition_name': 'blessed',
            'duration_rounds': 10,
            'effects': {
                'attack_roll_bonus': '1d4',
                'saving_throw_bonus': '1d4'
            },
            'concentration': True,
            'caster_id': caster_id,
            'spell_id': 'bless'
        })

    # Start concentration
    start_concentration(caster_id, 'bless', spell_level, duration_rounds=10)

    consume_spell_slot(caster_id, spell_level)

    return SpellResult(
        success=True,
        targets_affected=selected_targets,
        concentration_started=True,
        conditions_applied=[{'name': 'blessed', 'targets': selected_targets}],
        log_messages=[f"Blesses {len(selected_targets)} creatures with +1d4"]
    )

# When making attack roll:
def make_attack_roll_with_bless(attacker_id):
    base_roll = roll_d20()
    blessed = has_condition(attacker_id, 'blessed')

    if blessed:
        bless_bonus = roll_dice('1d4')
        return base_roll + bless_bonus, f"(+{bless_bonus} bless)"

    return base_roll, ""

# When making saving throw:
def make_saving_throw_with_bless(character_id, save_type):
    base_roll = roll_d20() + get_save_bonus(character_id, save_type)
    blessed = has_condition(character_id, 'blessed')

    if blessed:
        bless_bonus = roll_dice('1d4')
        return base_roll + bless_bonus

    return base_roll
```

**UI Consideration**: Multi-target selector needed

---

#### Guiding Bolt (Level 1)
**Pattern**: Ranged Spell Attack with Buff Effect

**Card Display**:
- Icon: 💫
- Name: "Guiding Bolt (Lvl 1)"
- Description: "4d6 radiant | Spell attack | Next attack has advantage"
- Scales: +1d6 per spell level above 1st

**Mechanical Implementation**:
- Action: Standard action
- Range: 120 feet
- Attack: Ranged spell attack roll
- Damage: 4d6 radiant
- Scaling: +1d6 per spell level above 1st
- Effect: Next attack roll against target has advantage (ends after one attack)

**Special Considerations**:
- High base damage for level 1 (4d6 average 14)
- Secondary effect: advantage on next attack (huge for martial allies)
- Requires attack roll (can miss)
- Radiant damage (good vs undead)

**Implementation Notes**:
```python
def cast_guiding_bolt(caster_id, target_id, spell_level):
    # Make spell attack roll
    attack_bonus = get_spell_attack_bonus(caster_id)
    attack_roll = roll_d20() + attack_bonus
    target_ac = get_target_ac(target_id)

    if attack_roll >= target_ac:
        # Hit: deal damage
        damage_dice = 4 + (spell_level - 1)
        damage = roll_dice(f"{damage_dice}d6")
        apply_damage(target_id, damage, "radiant")

        # Apply "guided" condition for next attack
        apply_condition(target_id, {
            'condition_name': 'guided',
            'duration': 'until_next_attack',
            'effect': 'next_attack_has_advantage',
            'expires_on': 'hit_by_attack'
        })

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            damage_dealt=damage,
            damage_type='radiant',
            targets_affected=[target_id],
            conditions_applied=[{'name': 'guided', 'target': target_id}],
            log_messages=[
                f"Guiding Bolt hits for {damage} radiant damage",
                f"{target_id} glows with light - next attack has advantage"
            ]
        )
    else:
        # Miss
        consume_spell_slot(caster_id, spell_level)
        return SpellResult(
            success=True,
            log_messages=["Guiding Bolt misses"]
        )

# When attacking a guided target:
def make_attack_against_target(attacker_id, target_id):
    guided = has_condition(target_id, 'guided')

    if guided:
        attack_roll = roll_with_advantage()
        remove_condition(target_id, 'guided')  # Expires after one attack
    else:
        attack_roll = roll_d20()

    # Continue with attack...
```

**Implementation Complexity**: Medium (requires attack roll + condition tracking)

---

#### Shield of Faith (Level 1)
**Pattern**: Concentration Buff Spell (AC Boost)

**Card Display**:
- Icon: 🛡️
- Name: "Shield of Faith (Lvl 1)"
- Description: "+2 AC | 1 target | Conc, 10 min"

**Mechanical Implementation**:
- Action: Bonus action
- Range: 60 feet
- Target: 1 creature
- Duration: Concentration, up to 10 minutes (100 rounds)
- Effect: +2 bonus to AC

**Special Considerations**:
- **BONUS ACTION**: Can be cast and attack same turn
- Long duration (10 minutes = 100 rounds)
- Stacks with all other AC bonuses (armor, shield, Dex, etc.)
- Concentration required
- Simple, reliable defensive buff

**Implementation Notes**:
```python
def cast_shield_of_faith(caster_id, target_id, spell_level):
    if not has_bonus_action_available(caster_id):
        return failure_result("No bonus action available")

    end_existing_concentration(caster_id)

    apply_condition(target_id, {
        'condition_name': 'shield_of_faith',
        'duration_rounds': 100,  # 10 minutes
        'effects': {
            'ac_bonus': 2
        },
        'concentration': True,
        'caster_id': caster_id,
        'spell_id': 'shield_of_faith'
    })

    start_concentration(caster_id, 'shield_of_faith', spell_level, duration_rounds=100)

    consume_spell_slot(caster_id, spell_level)
    consume_bonus_action(caster_id)

    return SpellResult(
        success=True,
        targets_affected=[target_id],
        concentration_started=True,
        action_type='bonus_action',
        log_messages=[f"{target_id} gains +2 AC from Shield of Faith"]
    )

# When calculating AC:
def calculate_ac(character_id):
    base_ac = get_base_ac(character_id)

    shield_faith = has_condition(character_id, 'shield_of_faith')
    if shield_faith:
        base_ac += 2

    return base_ac
```

**Implementation Complexity**: Low (simple AC bonus with concentration)

---

#### Inflict Wounds (Level 1)
**Pattern**: Melee Spell Attack (High Damage)

**Card Display**:
- Icon: 💀
- Name: "Inflict Wounds (Lvl 1)"
- Description: "3d10 necrotic | Melee spell attack"
- Scales: +1d10 per spell level above 1st

**Mechanical Implementation**:
- Action: Standard action
- Range: Touch (melee)
- Attack: Melee spell attack roll
- Damage: 3d10 necrotic (average 16.5 - highest single-target 1st level damage)
- Scaling: +1d10 per spell level above 1st

**Special Considerations**:
- HIGHEST SINGLE-TARGET DAMAGE at level 1
- Requires melee range (dangerous for casters)
- Requires attack roll (can miss)
- Necrotic damage (some creatures resistant/immune)
- High risk, high reward

**Implementation Notes**:
```python
def cast_inflict_wounds(caster_id, target_id, spell_level):
    # Check melee range
    if not in_melee_range(caster_id, target_id):
        return failure_result("Target not in melee range")

    # Make melee spell attack
    attack_bonus = get_spell_attack_bonus(caster_id)
    attack_roll = roll_d20() + attack_bonus
    target_ac = get_target_ac(target_id)

    if attack_roll >= target_ac:
        damage_dice = 3 + (spell_level - 1)
        damage = roll_dice(f"{damage_dice}d10")
        apply_damage(target_id, damage, "necrotic")

        consume_spell_slot(caster_id, spell_level)

        return SpellResult(
            success=True,
            damage_dealt=damage,
            damage_type='necrotic',
            targets_affected=[target_id],
            log_messages=[f"Inflict Wounds hits for {damage} necrotic damage"]
        )
    else:
        consume_spell_slot(caster_id, spell_level)
        return SpellResult(
            success=True,
            log_messages=["Inflict Wounds misses"]
        )
```

**Tactical Note**: Glass cannon spell - huge damage but requires caster in melee

---

### PALADIN SPELLS

*(Paladin analysis continues similarly for all 6 spells)*

#### Cure Wounds (Level 1)
**SAME AS CLERIC** - See Cleric section above

---

#### Bless (Level 1)
**SAME AS CLERIC** - See Cleric section above

---

#### Shield of Faith (Level 1)
**SAME AS CLERIC** - See Cleric section above

---

#### Divine Smite (Level 1)
**Pattern**: Melee Damage Rider (Unique)

**Card Display**:
- Icon: ⚔️✨
- Name: "Divine Smite (Lvl 1)"
- Description: "+2d8 radiant on hit | +1d8 vs undead/fiends"
- Scales: +1d8 per spell level above 1st

**Mechanical Implementation**:
- Action: **NO ACTION** - Used after hitting with melee weapon
- Trigger: When you hit with melee weapon attack
- Damage: 2d8 radiant (+1d8 if target is undead or fiend)
- Scaling: +1d8 per spell level above 1st
- Maximum: 5d8 base damage (6d8 vs undead/fiends) at 4th level slot

**Special Considerations**:
- **UNIQUE MECHANIC**: Cast AFTER confirming hit (no wasted slot if miss)
- Adds to weapon damage on same attack
- Stacks with all other damage bonuses
- Can be used on critical hit (doubles smite dice too!)
- Very efficient spell slot usage
- Core Paladin feature

**Implementation Notes**:
```python
# Divine Smite is special: triggered after weapon attack hits

def on_weapon_attack_hit(attacker_id, target_id, weapon_damage):
    # After successful weapon attack, offer Divine Smite option
    if can_divine_smite(attacker_id):
        # UI: "Use Divine Smite?" with spell level selector
        if player_chooses_smite(spell_level):
            cast_divine_smite(attacker_id, target_id, spell_level, weapon_damage)

def cast_divine_smite(caster_id, target_id, spell_level, base_weapon_damage):
    # Calculate smite damage
    smite_dice = 2 + (spell_level - 1)
    max_dice = 5  # Cap at 5d8
    smite_dice = min(smite_dice, max_dice)

    # Bonus against undead/fiends
    is_fiend_or_undead = check_creature_type(target_id, ['undead', 'fiend'])
    if is_fiend_or_undead:
        smite_dice += 1

    smite_damage = roll_dice(f"{smite_dice}d8")
    total_damage = base_weapon_damage + smite_damage

    # Apply additional damage (weapon damage already applied)
    apply_additional_damage(target_id, smite_damage, "radiant")

    consume_spell_slot(caster_id, spell_level)

    return SpellResult(
        success=True,
        damage_dealt=smite_damage,
        damage_type='radiant',
        targets_affected=[target_id],
        log_messages=[
            f"Divine Smite adds {smite_damage} radiant damage!",
            f"Total damage: {total_damage}"
        ]
    )

# On critical hit:
def apply_divine_smite_on_crit(caster_id, target_id, spell_level):
    # Critical hits double ALL dice, including smite dice
    smite_dice = 2 + (spell_level - 1)
    smite_dice = min(smite_dice, 5)

    if is_fiend_or_undead(target_id):
        smite_dice += 1

    # Double the dice for critical
    crit_smite_damage = roll_dice(f"{smite_dice * 2}d8")

    return crit_smite_damage
```

**UI Complexity**: HIGH - Requires prompt after weapon hit, before damage resolution

---

#### Divine Favor (Level 1)
**Pattern**: Concentration Buff Spell (Damage Boost)

**Card Display**:
- Icon: ⚔️✨
- Name: "Divine Favor (Lvl 1)"
- Description: "+1d4 radiant per hit | Conc, 1 min"

**Mechanical Implementation**:
- Action: Bonus action
- Duration: Concentration, up to 1 minute (10 rounds)
- Effect: Weapon attacks deal an extra 1d4 radiant damage

**Special Considerations**:
- Bonus action: can attack same turn
- Applies to EVERY weapon attack that hits
- Radiant damage (bypasses most resistances)
- Concentration: vulnerable to breaking
- Good for multiple attacks (Extra Attack feature)
- Doesn't scale with spell level (always 1d4)

**Implementation Notes**:
```python
def cast_divine_favor(caster_id, spell_level):
    if not has_bonus_action_available(caster_id):
        return failure_result("No bonus action available")

    end_existing_concentration(caster_id)

    apply_condition(caster_id, {
        'condition_name': 'divine_favor',
        'duration_rounds': 10,
        'effects': {
            'weapon_damage_bonus': '1d4',
            'bonus_damage_type': 'radiant'
        },
        'concentration': True,
        'caster_id': caster_id,
        'spell_id': 'divine_favor'
    })

    start_concentration(caster_id, 'divine_favor', spell_level, duration_rounds=10)

    consume_spell_slot(caster_id, spell_level)
    consume_bonus_action(caster_id)

    return SpellResult(
        success=True,
        targets_affected=[caster_id],
        concentration_started=True,
        action_type='bonus_action',
        log_messages=[f"{caster_id} weapons glow with divine power (+1d4 radiant)"]
    )

# When making weapon attack:
def calculate_weapon_damage(attacker_id, base_damage):
    divine_favor = has_condition(attacker_id, 'divine_favor')

    if divine_favor:
        bonus_damage = roll_dice('1d4')
        total_damage = base_damage + bonus_damage
        return total_damage, f"+{bonus_damage} radiant"

    return base_damage, ""
```

**Tactical Note**: Efficient for characters with multiple attacks per turn

---

#### Protection from Evil and Good (Level 1)
**Pattern**: Concentration Buff Spell (Defensive)

**Card Display**:
- Icon: 🛡️✨
- Name: "Protection from Evil and Good (Lvl 1)"
- Description: "Adv saves vs aberrations/celestials/elementals/fey/fiends/undead | Conc, 10 min"

**Mechanical Implementation**:
- Action: Standard action
- Range: Touch
- Target: 1 creature
- Duration: Concentration, up to 10 minutes (100 rounds)
- Effects:
  - Disadvantage on attacks against target by aberrations, celestials, elementals, fey, fiends, and undead
  - Target has advantage on saving throws against such creatures
  - Target cannot be charmed, frightened, or possessed by such creatures

**Special Considerations**:
- Very situational (only works vs specific creature types)
- Can be extremely powerful vs the right enemies
- Useless vs beasts, humanoids, etc.
- Long duration
- Multiple defensive benefits

**Implementation Notes**:
```python
PROTECTED_CREATURE_TYPES = [
    'aberration', 'celestial', 'elemental',
    'fey', 'fiend', 'undead'
]

def cast_protection_from_evil_and_good(caster_id, target_id, spell_level):
    end_existing_concentration(caster_id)

    apply_condition(target_id, {
        'condition_name': 'protection_from_evil_and_good',
        'duration_rounds': 100,
        'effects': {
            'creature_types': PROTECTED_CREATURE_TYPES,
            'attacks_against_disadvantage': True,
            'saving_throws_advantage': True,
            'charm_immunity': True,
            'frighten_immunity': True,
            'possession_immunity': True
        },
        'concentration': True,
        'caster_id': caster_id
    })

    start_concentration(caster_id, 'protection_from_evil_and_good',
                       spell_level, duration_rounds=100)

    consume_spell_slot(caster_id, spell_level)

    return SpellResult(
        success=True,
        targets_affected=[target_id],
        concentration_started=True,
        log_messages=[
            f"{target_id} protected from evil and good",
            "Protected against: aberrations, celestials, elementals, fey, fiends, undead"
        ]
    )

# When creature attacks protected target:
def make_attack_against_protected_target(attacker_id, target_id):
    protection = has_condition(target_id, 'protection_from_evil_and_good')
    attacker_type = get_creature_type(attacker_id)

    if protection and attacker_type in protection['creature_types']:
        attack_roll = roll_with_disadvantage()
        return attack_roll, "disadvantage"

    return roll_d20(), "normal"
```

**Tactical Note**: Know your enemy - very powerful if you're fighting fiends/undead

---

### WARLOCK SPELLS

#### Eldritch Blast (Cantrip)
**Pattern**: Special Multi-Beam Attack Cantrip

**Card Display**:
- Icon: 💥
- Name: "Eldritch Blast"
- Description: "1 beam 1d10 force | Spell attack"
- Scales: 1/2/3/4 beams at levels 1/5/11/17

**Mechanical Implementation**:
- Action: Standard action
- Range: 120 feet
- Attack: Ranged spell attack for each beam
- Damage: 1d10 force per beam
- Scaling: Number of beams increases (1 → 2 → 3 → 4)
- Each beam: separate attack roll, can target different creatures

**Special Considerations**:
- **SIGNATURE WARLOCK CANTRIP**
- Can split beams between multiple targets
- Each beam needs separate attack roll
- Force damage (rarely resisted)
- Enhanced by Warlock invocations (e.g., Agonizing Blast adds Cha to each beam)
- Most damaging cantrip at high levels (4d10 = 40 max damage)

**Implementation Notes**:
```python
def cast_eldritch_blast(caster_id, targets, caster_level):
    # Calculate number of beams based on level
    num_beams = 1 + (caster_level >= 5) + (caster_level >= 11) + (caster_level >= 17)

    attack_bonus = get_spell_attack_bonus(caster_id)
    total_damage = 0
    messages = []

    for beam_num in range(num_beams):
        target = targets[beam_num % len(targets)]  # Distribute beams

        attack_roll = roll_d20() + attack_bonus
        target_ac = get_target_ac(target)

        if attack_roll >= target_ac:
            damage = roll_dice("1d10")

            # Check for Agonizing Blast invocation
            if has_invocation(caster_id, 'agonizing_blast'):
                cha_bonus = get_ability_modifier(caster_id, 'charisma')
                damage += cha_bonus
                messages.append(f"Beam {beam_num+1} hits {target} for {damage} force (+{cha_bonus} agonizing)")
            else:
                messages.append(f"Beam {beam_num+1} hits {target} for {damage} force")

            apply_damage(target, damage, "force")
            total_damage += damage
        else:
            messages.append(f"Beam {beam_num+1} misses {target}")

    return SpellResult(
        success=True,
        damage_dealt=total_damage,
        damage_type='force',
        targets_affected=list(set(targets[:num_beams])),
        log_messages=messages
    )
```

**UI Consideration**: Need to allow selecting target for each beam at higher levels

---

#### Chill Touch (Cantrip)
**Pattern**: Simple Damage Cantrip with Debuff

**Card Display**:
- Icon: 💀
- Name: "Chill Touch"
- Description: "1d8 necrotic | No healing 1 turn | Spell attack"
- Scales: 1d8 → 2d8 → 3d8 → 4d8

**Mechanical Implementation**:
- Action: Standard action
- Range: 120 feet
- Attack: Ranged spell attack
- Damage: 1d8 necrotic (scales with level)
- Effect: Target cannot regain HP until start of your next turn
- Special: Undead have disadvantage on attacks vs you until start of your next turn

**Special Considerations**:
- Healing prevention is powerful vs regenerating enemies
- Extra benefit vs undead (disadvantage on attacks)
- Necrotic damage (some resistance)
- Named "Chill Touch" but is ranged (weird D&D quirk)

**Implementation Notes**:
```python
def cast_chill_touch(caster_id, target_id, caster_level):
    dice_count = calculate_cantrip_dice(caster_level)
    attack_bonus = get_spell_attack_bonus(caster_id)

    attack_roll = roll_d20() + attack_bonus
    target_ac = get_target_ac(target_id)

    if attack_roll >= target_ac:
        damage = roll_dice(f"{dice_count}d8")
        apply_damage(target_id, damage, "necrotic")

        # Apply "chilled" condition
        apply_condition(target_id, {
            'condition_name': 'chilled',
            'duration_rounds': 1,  # Until start of caster's next turn
            'effects': {
                'cannot_regain_hp': True
            }
        })

        # If target is undead, add disadvantage on attacks
        if is_undead(target_id):
            apply_condition(target_id, {
                'condition_name': 'chilled_undead',
                'duration_rounds': 1,
                'effects': {
                    'attacks_disadvantage_vs': caster_id
                }
            })

            return SpellResult(
                success=True,
                damage_dealt=damage,
                damage_type='necrotic',
                targets_affected=[target_id],
                log_messages=[
                    f"Chill Touch hits for {damage} necrotic",
                    f"{target_id} cannot heal and attacks {caster_id} with disadvantage"
                ]
            )

        return SpellResult(
            success=True,
            damage_dealt=damage,
            damage_type='necrotic',
            targets_affected=[target_id],
            log_messages=[
                f"Chill Touch hits for {damage} necrotic",
                f"{target_id} cannot regain HP until next turn"
            ]
        )
    else:
        return miss_result()

# When healing is attempted:
def attempt_healing(target_id, healing_amount):
    chilled = has_condition(target_id, 'chilled')
    if chilled:
        return 0, "Target is chilled and cannot regain HP"

    return apply_healing(target_id, healing_amount), ""
```

**Tactical Note**: Excellent vs enemies with regeneration or healing abilities

---

#### Poison Spray (Cantrip)
**Pattern**: Simple Damage Cantrip (Save-based, Close Range)

**Card Display**:
- Icon: ☠️
- Name: "Poison Spray"
- Description: "1d12 poison | 10ft | Con save"
- Scales: 1d12 → 2d12 → 3d12 → 4d12

**Mechanical Implementation**:
- Action: Standard action
- Range: 10 feet (very short!)
- Save: Constitution
- Damage: 1d12 poison (highest cantrip damage die)

**Special Considerations**:
- HIGHEST DAMAGE DIE for cantrips (d12)
- Very short range (10 feet - effectively melee)
- Poison damage (many creatures resistant/immune)
- Constitution save (usually high for monsters)
- High risk, high reward

**Implementation Notes**:
```python
def cast_poison_spray(caster_id, target_id, caster_level):
    # Check range (10 feet)
    if not within_range(caster_id, target_id, 10):
        return failure_result("Target not within 10 feet")

    dice_count = calculate_cantrip_dice(caster_level)
    save_dc = get_spell_save_dc(caster_id)
    save_roll = make_saving_throw(target_id, "constitution")

    if save_roll < save_dc:
        damage = roll_dice(f"{dice_count}d12")
        apply_damage(target_id, damage, "poison")

        return SpellResult(
            success=True,
            damage_dealt=damage,
            damage_type='poison',
            targets_affected=[target_id],
            save_dc=save_dc,
            saving_throw_made=False,
            log_messages=[f"Poison Spray hits for {damage} poison damage"]
        )
    else:
        return SpellResult(
            success=True,
            save_dc=save_dc,
            saving_throw_made=True,
            log_messages=[f"{target_id} saves against Poison Spray"]
        )
```

**Tactical Note**: Dangerous for squishy Warlocks (requires close range)

---

*(Continue with all remaining Warlock and Wizard spells...)*

## Summary of Implementation Patterns

### Pattern Categories:
1. **Simple Damage Cantrips** (8 spells) - Most straightforward
2. **Direct Healing** (3 variations) - HP tracking critical
3. **Concentration Buffs** (6 spells) - Concentration management key
4. **Reaction Spells** (2 spells) - UI complexity high
5. **AoE Damage** (3 spells) - Multi-target handling
6. **Auto-Hit Damage** (1 spell) - Unique, no miss chance
7. **Special Mechanics** (Divine Smite, Hex, etc.) - Custom implementation

### Critical Implementation Notes:

1. **HP Tracking During Combat**:
   - ALWAYS use character_sheet.character_data for combat HP
   - Database HP is stale during active combat
   - See Second Wind implementation for pattern

2. **Concentration Management**:
   - Must track concentration per caster
   - End existing concentration when casting new concentration spell
   - Break concentration on damage (Con save: DC 10 or half damage)
   - Break on incapacitated/unconscious
   - All effects end when concentration breaks

3. **Action Economy**:
   - Track action/bonus action/reaction separately
   - Some spells are bonus actions (Healing Word, Shield of Faith, Divine Favor)
   - Reaction spells need special UI handling
   - Divine Smite is "no action" (cast after hit)

4. **Spell Slot Consumption**:
   - Always consume slot when cast (even if miss)
   - Exception: Some DMs allow not consuming on miss (house rule)
   - Track slots per spell level (1st, 2nd, 3rd, etc.)
   - Cantrips never consume slots

5. **Saving Throws vs Attack Rolls**:
   - Spell attack: Roll d20 + spell attack bonus vs AC
   - Saving throw: Target rolls d20 + save bonus vs spell save DC
   - Some spells allow save for half damage
   - Critical hits only on attack rolls, not saves

6. **Scaling**:
   - Cantrips scale with character level (not spell level)
   - Leveled spells scale with spell slot level used
   - Track both character level and spell slot level

7. **Card Display**:
   - Icon: Visual identifier (emoji for now)
   - Name: Include (Lvl X) for leveled spells
   - Description: Concise mechanical summary
   - Update availability based on spell slots

### Next Steps:
1. Implement base spell casting infrastructure
2. Start with Simple Damage Cantrips (easiest)
3. Add Direct Healing spells (HP tracking)
4. Implement Concentration system
5. Add Reaction spell UI
6. Test extensively with each pattern

### Testing Priorities:
1. Cantrip damage scaling at levels 1, 5, 11, 17
2. Spell slot consumption and tracking
3. Concentration starting, maintaining, breaking
4. HP tracking during vs outside combat
5. Multi-target spell selection
6. Reaction spell prompts