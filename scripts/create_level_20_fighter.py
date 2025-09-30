#!/usr/bin/env python3
"""
Create a Level 20 Fighter (Champion) with full progression

This script creates "Sir Maximillian", a level 20 Champion Fighter with:
- All ASI improvements applied
- All Fighter features unlocked
- All Champion features active
- Epic Boon selected
- Full equipment and stats

The character will be inserted into the database with proper progression tracking.
"""

import sys
import sqlite3
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


class Level20FighterCreator:
    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path
        self.character_id = "sir_maximillian_l20"
        self.character_name = "Sir Maximillian"

    def create_character(self):
        """Create the level 20 Fighter in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print(f"Creating {self.character_name}, Level 20 Champion Fighter...")

        base_stats = {
            'strength': 20,
            'dexterity': 14,
            'constitution': 18,
            'intelligence': 10,
            'wisdom': 12,
            'charisma': 8
        }

        print(f"  Base Stats: STR {base_stats['strength']}, DEX {base_stats['dexterity']}, "
              f"CON {base_stats['constitution']}, INT {base_stats['intelligence']}, "
              f"WIS {base_stats['wisdom']}, CHA {base_stats['charisma']}")

        max_hp = 10 + (19 * (6 + 4))
        print(f"  Max HP: {max_hp} (10 base + 19 levels * (d10 avg 6 + CON +4))")

        cursor.execute("DELETE FROM characters WHERE id = ?", (self.character_id,))
        cursor.execute("DELETE FROM character_combat_state WHERE character_id = ?", (self.character_id,))
        cursor.execute("DELETE FROM character_subclasses WHERE character_id = ?", (self.character_id,))
        cursor.execute("DELETE FROM character_weapon_masteries WHERE character_id = ?", (self.character_id,))
        cursor.execute("DELETE FROM character_feats WHERE character_id = ?", (self.character_id,))

        cursor.execute("""
            INSERT INTO characters (
                id, name, race_id, class_id, subclass_id, background_id, level,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                hit_points_max, hit_points_current, max_hit_points,
                armor_class,
                experience_points,
                second_wind_uses_current, second_wind_uses_max,
                action_surge_uses_current, action_surge_uses_max,
                indomitable_uses_current, indomitable_uses_max,
                weapon_mastery_count
            ) VALUES (
                ?, ?, 'human', 'fighter', 'champion', 'soldier', 20,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                18,
                355000,
                4, 4,
                2, 2,
                3, 3,
                -1
            )
        """, (
            self.character_id, self.character_name,
            base_stats['strength'], base_stats['dexterity'], base_stats['constitution'],
            base_stats['intelligence'], base_stats['wisdom'], base_stats['charisma'],
            max_hp, max_hp, max_hp
        ))

        print("  Fighter Resources:")
        print("    - Second Wind: 4/4 uses (1d10+20 healing)")
        print("    - Action Surge: 2/2 uses")
        print("    - Indomitable: 3/3 uses (+20 to reroll)")

        cursor.execute("""
            INSERT OR REPLACE INTO character_combat_state (
                character_id,
                critical_range_min,
                studied_target_id,
                last_attack_missed,
                last_miss_turn,
                heroic_warrior_active,
                survivor_active,
                tactical_shift_movement
            ) VALUES (?, 18, NULL, 0, 0, 1, 1, 10)
        """, (self.character_id,))

        print("  Champion Features:")
        print("    - Improved Critical: 19-20 crit range")
        print("    - Superior Critical: 18-20 crit range (ACTIVE)")
        print("    - Remarkable Athlete: +10 on non-prof STR/DEX/CON checks")
        print("    - Heroic Warrior: Gain Heroic Inspiration at turn start")
        print("    - Survivor: Heal 9 HP (5 + CON +4) at turn start when bloodied")

        cursor.execute("""
            INSERT INTO character_subclasses (character_id, class_id, subclass_id)
            VALUES (?, 'fighter', 'champion')
        """, (self.character_id,))

        masteries = ['Longsword', 'Greatsword', 'Longbow', 'Handaxe']
        for weapon in masteries:
            cursor.execute("""
                INSERT OR REPLACE INTO character_weapon_masteries (
                    character_id, weapon_name, mastery_type
                ) VALUES (?, ?, 'push')
            """, (self.character_id, weapon))

        print(f"  Weapon Masteries: {', '.join(masteries)} (unlimited swaps)")

        cursor.execute("""
            INSERT INTO character_feats (character_id, feat_name, feat_source, level_acquired)
            VALUES (?, 'Boon of Combat Prowess', 'level_19_epic_boon', 19)
        """, (self.character_id,))

        print("  Epic Boon: Boon of Combat Prowess (+1 attack/damage)")

        conn.commit()

        print(f"\nCharacter created successfully: {self.character_name}")
        print(f"Character ID: {self.character_id}")

        self._generate_stats_document(cursor, base_stats, max_hp)

        conn.close()

    def _generate_stats_document(self, cursor, base_stats, max_hp):
        """Generate detailed stats document"""
        doc_path = project_root / "docs" / f"{self.character_id}_stats.md"

        str_mod = (base_stats['strength'] - 10) // 2
        dex_mod = (base_stats['dexterity'] - 10) // 2
        con_mod = (base_stats['constitution'] - 10) // 2
        int_mod = (base_stats['intelligence'] - 10) // 2
        wis_mod = (base_stats['wisdom'] - 10) // 2
        cha_mod = (base_stats['charisma'] - 10) // 2

        prof_bonus = 6

        attack_bonus = prof_bonus + str_mod + 1
        damage_bonus = str_mod + 1

        ac = 18

        content = f"""# {self.character_name} - Level 20 Champion Fighter

## Character Overview

**Name:** {self.character_name}
**Race:** Human (assumed)
**Class:** Fighter (Champion)
**Level:** 20
**Experience:** 355,000 XP
**Proficiency Bonus:** +{prof_bonus}

---

## Ability Scores

| Ability | Score | Modifier | Notes |
|---------|-------|----------|-------|
| **Strength** | {base_stats['strength']} | +{str_mod} | Primary attack stat |
| **Dexterity** | {base_stats['dexterity']} | +{dex_mod} | Initiative, AC |
| **Constitution** | {base_stats['constitution']} | +{con_mod} | HP, concentration saves |
| **Intelligence** | {base_stats['intelligence']} | +{int_mod} | - |
| **Wisdom** | {base_stats['wisdom']} | +{wis_mod} | Perception |
| **Charisma** | {base_stats['charisma']} | +{cha_mod} | - |

### ASI Progression (5 total)
1. **Level 4:** STR 16 → 18
2. **Level 6:** STR 18 → 20
3. **Level 8:** CON 16 → 18
4. **Level 12:** Feat - Great Weapon Master (assumed)
5. **Level 14:** DEX 12 → 14
6. **Level 16:** Feat - Alert (assumed)

---

## Combat Statistics

### Hit Points
- **Maximum HP:** {max_hp}
- **Current HP:** {max_hp}
- **Calculation:** 10 (1st level) + 190 (19 levels × 10 avg) = 200

### Armor Class
- **AC:** {ac}
- **Source:** Plate Armor (18 base)

### Attack Statistics
- **Attack Bonus:** +{attack_bonus} (Prof +{prof_bonus} + STR +{str_mod} + Boon +1)
- **Damage Bonus:** +{damage_bonus} (STR +{str_mod} + Boon +1)
- **Critical Hit Range:** 18-20 (Superior Critical)
- **Attacks per Round:** 4 (Three Extra Attacks feature)

### Example Attack (Greatsword)
- **Attack Roll:** 1d20 + {attack_bonus}
- **Damage:** 2d6 + {damage_bonus} slashing
- **Critical:** 4d6 + {damage_bonus} slashing (on 18-20)
- **Full Round:** 4 attacks = 4d20+{attack_bonus} attack / 8d6+{damage_bonus*4} damage

---

## Class Features

### Fighter Base Features

#### Level 1
- **Fighting Style:** Great Weapon Fighting (reroll 1-2 on damage dice)
- **Second Wind:** Bonus action, heal 1d10 + 20 HP, 4 uses per rest
- **Weapon Mastery:** 3+ weapons mastered (unlimited for Fighter)

#### Level 2
- **Action Surge:** Extra action in combat, 2 uses per rest
- **Tactical Mind:** Expend Second Wind use for +1d10 on failed ability check

#### Level 5
- **Extra Attack:** 2 attacks per Attack action
- **Tactical Shift:** Move 10 feet after Second Wind without provoking opportunity attacks

#### Level 9
- **Indomitable:** Reroll failed save + 20 bonus, 3 uses per long rest
- **Tactical Master:** Swap weapon mastery to Push/Sap/Slow mid-combat
- **Weapon Mastery Increase:** Now mastery applies to ALL weapons (unlimited)

#### Level 11
- **Two Extra Attacks:** 3 attacks per Attack action

#### Level 13
- **Indomitable (2 uses):** Upgraded to 2 uses per long rest
- **Studied Attacks:** Advantage on next attack after a miss

#### Level 17
- **Action Surge (2 uses):** Upgraded to 2 uses per rest
- **Indomitable (3 uses):** Upgraded to 3 uses per long rest

#### Level 19
- **Epic Boon:** Boon of Combat Prowess (+1 attack rolls and damage rolls)

#### Level 20
- **Three Extra Attacks:** 4 attacks per Attack action

---

## Champion Subclass Features

### Level 3: Improved Critical
- **Critical Range:** 19-20 (instead of natural 20)
- **Effect:** Double all damage dice on critical hit

### Level 3: Remarkable Athlete
- **Bonus:** +10 to non-proficient STR/DEX/CON checks (half prof, rounded up)
- **Examples:** Athletics +15 if not proficient, Acrobatics +12 if not proficient
- **Jump Distance:** Standing long jump = STR score (20 feet)

### Level 7: Additional Fighting Style
- **Second Style:** Dueling (assumed - +2 damage with one-handed weapon)
- **Notes:** Can switch between Great Weapon Fighting and Dueling based on weapon

### Level 10: Heroic Warrior
- **Effect:** Gain 1 Heroic Inspiration at the start of each turn in combat
- **Heroic Inspiration:** Add 1d6 to any d20 roll or save

### Level 15: Superior Critical
- **Critical Range:** 18-20 (expanded from 19-20)
- **Effect:** 15% crit chance on every attack

### Level 18: Survivor
- **Effect:** At start of turn, if HP ≤ 100 (bloodied), regain 9 HP (5 + CON mod +4)
- **Regeneration:** 9 HP per turn while bloodied

---

## Combat Capabilities

### Standard Combat Round (4 Attacks)
```
Attack 1: 1d20+{attack_bonus} | 2d6+{damage_bonus} damage
Attack 2: 1d20+{attack_bonus} | 2d6+{damage_bonus} damage
Attack 3: 1d20+{attack_bonus} | 2d6+{damage_bonus} damage
Attack 4: 1d20+{attack_bonus} | 2d6+{damage_bonus} damage

Average Damage per Round: 52 (4 × (7 avg + {damage_bonus}))
Critical Damage (18-20): 4d6+{damage_bonus} = 20 avg per crit
```

### Action Surge Round (8 Attacks)
```
Use Action Surge for second Attack action
Total Attacks: 8
Average Damage: 104 (8 × 13)
```

### Nova Round (Maximum Burst)
```
Action Surge + Great Weapon Master (assumed -5 attack/+10 damage)
8 attacks at +{attack_bonus-5} for 2d6+{damage_bonus+10} each
Average Damage: ~144 (8 × 18)
```

---

## Resource Management

### Per Short Rest
- **Second Wind:** Regain 1 use (max 4)
- **Action Surge:** Regain all uses (2 uses available)

### Per Long Rest
- **All Resources:** Fully restored
  - Second Wind: 4 uses
  - Action Surge: 2 uses
  - Indomitable: 3 uses
  - Hit Points: Full {max_hp} HP

---

## Weapon Mastery

{self.character_name} has mastered the following weapons (unlimited swaps for Fighters):

### Current Masteries
1. **Longsword** (Sap - disadvantage on next attack)
2. **Greatsword** (Graze - ability mod damage on miss)
3. **Longbow** (Slow - reduce speed by 10 ft)
4. **Handaxe** (Vex - advantage on next attack vs target)

### Tactical Master (Level 9)
Can swap any weapon mastery to **Push**, **Sap**, or **Slow** on a per-attack basis during combat.

---

## Defensive Capabilities

### Armor Class: {ac}
- **Plate Armor:** 18 base AC
- **No DEX bonus** (plate armor limitation)

### Saving Throws
- **Strength:** +{prof_bonus + str_mod} = +{prof_bonus + str_mod} (proficient)
- **Dexterity:** +{dex_mod}
- **Constitution:** +{prof_bonus + con_mod} = +{prof_bonus + con_mod} (proficient)
- **Intelligence:** +{int_mod}
- **Wisdom:** +{wis_mod}
- **Charisma:** +{cha_mod}

### Indomitable (3/day)
- Reroll any failed saving throw and add +20 bonus
- Effective save bonus: +20 on demand

### Survivor (Passive)
- Regenerate 9 HP per turn when below 100 HP
- Effective HP buffer: +45 HP over 5 rounds

---

## Skill Proficiencies (Assumed)

- **Athletics:** +{prof_bonus + str_mod} = +{prof_bonus + str_mod}
- **Intimidation:** +{prof_bonus + cha_mod} = +{prof_bonus + cha_mod}
- **Perception:** +{prof_bonus + wis_mod} = +{prof_bonus + wis_mod}

**Remarkable Athlete** applies to non-proficient STR/DEX/CON checks:
- Any non-proficient Athletics: +15
- Any non-proficient Acrobatics: +12

---

## Epic Boon: Boon of Combat Prowess

**Source:** Level 19 Fighter feature

**Effect:**
- **Attack Rolls:** +1 bonus to all attack rolls
- **Damage Rolls:** +1 bonus to all damage rolls

**Already Included In:**
- Attack Bonus: +{attack_bonus} includes Boon +1
- Damage Bonus: +{damage_bonus} includes Boon +1

---

## Mechanical Breakdown Summary

### Offense
- **Attack Bonus:** +{attack_bonus} = +{prof_bonus} (prof) + {str_mod} (STR) + 1 (Boon)
- **Damage Bonus:** +{damage_bonus} = +{str_mod} (STR) + 1 (Boon)
- **Attacks per Round:** 4 (base) or 8 (Action Surge)
- **Critical Range:** 18-20 (15% chance per attack)
- **Average DPR:** 52 (standard) / 104 (Action Surge)

### Defense
- **AC:** {ac} (Plate Armor)
- **HP:** {max_hp}
- **Effective HP:** {max_hp + 45} (with Survivor regeneration)
- **Save Rerolls:** 3 per day with +20 bonus

### Utility
- **Healing:** 4d10 + 80 HP per rest (Second Wind × 4)
- **Movement:** 10 feet free movement after Second Wind (Tactical Shift)
- **Inspiration:** 1d6 per turn in combat (Heroic Warrior)

---

## Combat Tactics

### Standard Encounter
1. Open with full Attack action (4 attacks)
2. Use Heroic Inspiration for critical rolls
3. Activate Second Wind if below 150 HP
4. Save Action Surge for boss/key moment

### Boss Fight
1. Action Surge for 8 attacks in one round
2. Use Indomitable to guarantee critical save passes
3. Rely on Survivor for sustained HP regeneration
4. Use Tactical Master to control battlefield (Push/Slow)

### Sustained Combat
1. Conserve Action Surge (2 uses available)
2. Use Second Wind liberally (4 uses, 1d10+20 each)
3. Activate Survivor at 100 HP threshold
4. Use Studied Attacks after misses for advantage

---

## Character Database Entry

**Database:** `talekeeper.db`
**Character ID:** `{self.character_id}`

### Stored Tables
- `characters`: Core stats and resources
- `character_combat_state`: Critical range, Survivor, Heroic Warrior states
- `character_subclasses`: Champion subclass linkage
- `character_weapon_masteries`: 4 mastered weapons
- `character_feats`: Epic Boon of Combat Prowess

---

**Document Generated:** {doc_path.name}
**Character Status:** Active in database
**Build Optimization:** Combat-focused tank/DPS hybrid
"""

        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nDetailed stats document generated: {doc_path}")
        print(f"  Total pages: ~7 pages of mechanical breakdown")

        return doc_path


def main():
    """Create the level 20 Fighter character"""
    print("=" * 70)
    print("Level 20 Champion Fighter Character Creator")
    print("=" * 70)
    print()

    creator = Level20FighterCreator()

    try:
        creator.create_character()
        print()
        print("=" * 70)
        print("SUCCESS: Character created and documented")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. View character in database: sqlite3 talekeeper.db 'SELECT * FROM characters WHERE id=\"sir_maximillian_l20\"'")
        print("  2. Read full breakdown: docs/sir_maximillian_l20_stats.md")
        print("  3. Test in combat: python test/test_level_20_fighter_combat.py")

    except Exception as e:
        print(f"\nERROR: Failed to create character: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())