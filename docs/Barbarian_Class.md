# 🪓 Barbarian

## Core Barbarian Traits

- **Primary Ability:** Strength  
- **Hit Die:** 1d12 per Barbarian level  
- **Saving Throw Proficiencies:** Strength, Constitution  
- **Skill Proficiencies (Choose 2):**  
  Animal Handling, Athletics, Intimidation, Nature, Perception, Survival  
- **Weapon Proficiencies:** Simple and Martial weapons  
- **Armor Training:** Light armor, Medium armor, Shields  
- **Starting Equipment (Choose A or B):**  
  - **A:** Greataxe, 4 Handaxes, Explorer’s Pack, 15 GP  
  - **B:** 75 GP

## Multiclassing

- Gain the Barbarian's **Hit Die**, **Martial Weapon Proficiency**, and **Shield Training**
- Gain the **Level 1 Features** of the Barbarian

## Class Features by Level

| Level | Proficiency Bonus | Class Features                                                                 | Rages | Rage Damage | Weapon Mastery |
|-------|-------------------|--------------------------------------------------------------------------------|--------|--------------|----------------|
| 1     | +2                | Rage, Unarmored Defense, Weapon Mastery                                        | 2      | +2           | 2              |
| 2     | +2                | Danger Sense, Reckless Attack                                                  | 2      | +2           | 2              |
| 3     | +2                | Subclass, Primal Knowledge                                                     | 3      | +2           | 2              |
| 4     | +2                | Ability Score Improvement                                                      | 3      | +2           | 3              |
| 5     | +3                | Extra Attack, Fast Movement                                                    | 3      | +2           | 3              |
| 6     | +3                | Subclass Feature                                                               | 4      | +2           | 3              |
| 7     | +3                | Feral Instinct, Instinctive Pounce                                             | 4      | +2           | 3              |
| 8     | +3                | Ability Score Improvement                                                      | 4      | +2           | 3              |
| 9     | +4                | Brutal Strike                                                                  | 4      | +3           | 3              |
| 10    | +4                | Subclass Feature                                                               | 4      | +3           | 4              |
| 11    | +4                | Relentless Rage                                                                | 4      | +3           | 4              |
| 12    | +4                | Ability Score Improvement                                                      | 5      | +3           | 4              |
| 13    | +5                | Improved Brutal Strike                                                         | 5      | +3           | 4              |
| 14    | +5                | Subclass Feature                                                               | 5      | +3           | 4              |
| 15    | +5                | Persistent Rage                                                                | 5      | +3           | 4              |
| 16    | +5                | Ability Score Improvement                                                      | 5      | +4           | 4              |
| 17    | +6                | Improved Brutal Strike                                                         | 6      | +4           | 4              |
| 18    | +6                | Indomitable Might                                                              | 6      | +4           | 4              |
| 19    | +6                | Epic Boon                                                                       | 6      | +4           | 4              |
| 20    | +6                | Primal Champion                                                                | 6      | +4           | 4              |

## Level Features

### Level 1: Rage
- Bonus Action to enter Rage (if not wearing Heavy armor)
- While raging:
  - Resistance to Bludgeoning, Piercing, Slashing damage
  - Rage Damage Bonus to Strength-based attacks
  - Advantage on Strength checks and saves
  - No Spellcasting or Concentration
  - Ends early if you don Heavy armor or become Incapacitated
- Extend rage by:
  - Making an attack roll
  - Forcing a saving throw
  - Taking a Bonus Action to extend
- Max duration: 10 minutes

#### TaleKeeper Implementation Notes
- Rage is tracked through the action card resource system. Activating the [RAGE] action card consumes a use, marks the character as raging, and refreshes melee weapon cards so the bonus is visible immediately.
- Damage bonuses now come directly from the active combat context instead of a database lookup. This guarantees the correct +2 / +3 / +4 scaling based on barbarian level and ensures Cleave follow-up attacks inherit the Rage state.
- If an attack is ineligible (ranged or thrown), combat logs include a debug message explaining why the Rage bonus was skipped, which helps QA and table rulings.

### Level 1: Unarmored Defense
- AC = 10 + Dex + Con (can use a shield)

### Level 1: Weapon Mastery
- Gain 2 weapon mastery choices (simple/martial melee)
- Can change 1 weapon choice on Long Rest
- More slots gained as you level up

### Level 2: Danger Sense
- Advantage on Dex saves (unless Incapacitated)

### Level 2: Reckless Attack
- On your first attack of the turn:
  - Advantage on Strength attack rolls
  - Enemies have Advantage to hit you until your next turn

### Level 3: Primal Knowledge
- Gain one more skill from your class list
- While Raging, you can use Strength for:
  - Acrobatics, Intimidation, Perception, Stealth, Survival

### Level 4, 8, 12, 16: Ability Score Improvement
- Take ASI or feat of your choice

### Level 5: Extra Attack
- Make two attacks on Attack action

### Level 5: Fast Movement
- +10 ft movement (if not wearing Heavy armor)

### Level 7: Feral Instinct
- Advantage on Initiative rolls

### Level 7: Instinctive Pounce
- When entering Rage, move up to half your speed

### Level 9: Brutal Strike
- If you use Reckless Attack, you can forgo Advantage:
  - On hit, deal +1d10 and apply one:
    - Forceful Blow: Push 15 ft & move toward target
    - Hamstring Blow: -15 ft Speed until next turn

### Level 11: Relentless Rage
- Drop to 0 HP → make DC 10 Con save
  - On success, drop to HP = 2 × Barbarian level instead
  - DC increases by 5 each time (resets after rest)

### Level 13: Improved Brutal Strike
- Add 2 new effects to Brutal Strike:
  - Staggering Blow: Target has Disadvantage on next save & can’t make Opportunity Attacks
  - Sundering Blow: Next attack roll vs target gains +5

### Level 15: Persistent Rage
- Regain all Rage uses when rolling Initiative (once per Long Rest)
- Rage now lasts 10 minutes without extension actions
- Ends only if you fall Unconscious or don Heavy armor

### Level 17: Brutal Strike Upgrade
- Brutal Strike damage increases to 2d10
- You can apply two different effects per use

### Level 18: Indomitable Might
- If your Strength check/save is lower than your Strength score, use your score instead

### Level 19: Epic Boon
- Gain an Epic Boon feat or any other qualified feat  
  Recommended: Boon of Irresistible Offense

### Level 20: Primal Champion
- Strength and Constitution increase by +4 (max 25)

## Barbarian Subclass: Path of the Berserker

### Level 3: Frenzy
- When you Reckless Attack while Raging:
  - Add d6s equal to Rage Damage Bonus to first hit

### Level 6: Mindless Rage
- While Raging:  
  - Immune to Charmed and Frightened  
  - If already affected, it ends on entering Rage

### Level 10: Retaliation
- When damaged by a creature within 5 ft:
  - Use Reaction to make 1 melee weapon/unarmed attack

### Level 14: Intimidating Presence
- As Bonus Action:
  - 30 ft emanation → Wis Save DC (8 + Str mod + Prof)
  - On fail: Frightened for 1 minute (repeat save each turn)
  - Use again after Long Rest or by expending a Rage use