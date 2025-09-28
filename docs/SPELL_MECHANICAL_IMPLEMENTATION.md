# Spell Mechanical Implementation Guide
*Technical documentation for implementing D&D 2024 spells in TaleKeeper*

## Overview

This document provides detailed technical implementation approaches for the priority spells identified in the Solo Play Spell Analysis. Each spell category includes code patterns, database schemas, and integration points with the existing TaleKeeper system.

## Core Architecture Components

### 1. BaseSpell Class Structure

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import random
import sqlite3

@dataclass
class SpellResult:
    success: bool
    damage_dealt: Optional[int] = None
    healing_done: Optional[int] = None
    targets_affected: List[str] = None
    concentration_started: bool = False
    concentration_ended: Optional[str] = None
    conditions_applied: List[Dict] = None
    log_messages: List[str] = None
    blocked_attack: bool = False
    requires_save: bool = False
    save_dc: Optional[int] = None

class BaseSpell(ABC):
    def __init__(self, db_path: str):
        self.db_path = db_path

    @abstractmethod
    def cast(self, caster_id: str, **kwargs) -> SpellResult:
        """Cast the spell with given parameters"""
        pass

    def get_spell_attack_bonus(self, caster_id: str) -> int:
        """Calculate spell attack bonus for caster"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT level, spellcasting_ability, proficiency_bonus
                FROM characters WHERE id = ?
            """, (caster_id,))

            level, ability, prof = cursor.fetchone()
            ability_mod = self.get_ability_modifier(caster_id, ability)
            return prof + ability_mod

    def get_spell_save_dc(self, caster_id: str) -> int:
        """Calculate spell save DC for caster"""
        return 8 + self.get_spell_attack_bonus(caster_id)

    def roll_damage(self, damage_formula: str) -> int:
        """Roll damage dice from formula like '3d6+2'"""
        # Implementation of dice rolling logic
        pass

    def apply_damage(self, target_id: str, damage: int, damage_type: str):
        """Apply damage to target, considering resistances"""
        # Integration with existing damage system
        pass

    def apply_condition(self, target_id: str, condition_data: Dict):
        """Apply a condition effect to target"""
        # Integration with condition system
        pass
```

### 2. Spell Registry System

```python
class SpellRegistry:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.spells = {}
        self._register_spells()

    def _register_spells(self):
        """Register all implemented spells"""
        self.spells.update({
            'magic_missile': MagicMissileSpell(self.db_path),
            'fireball': FireballSpell(self.db_path),
            'shield': ShieldSpell(self.db_path),
            'cure_wounds': CureWoundsSpell(self.db_path),
            'bless': BlessSpell(self.db_path),
            # Add more spells as implemented
        })

    def cast_spell(self, spell_id: str, caster_id: str, **kwargs) -> SpellResult:
        """Cast a spell by ID with parameters"""
        if spell_id not in self.spells:
            raise ValueError(f"Spell {spell_id} not implemented")

        spell = self.spells[spell_id]
        return spell.cast(caster_id, **kwargs)

    def get_available_spells(self, character_id: str) -> List[Dict]:
        """Get all spells a character can currently cast"""
        # Query character's known spells, available spell slots, etc.
        pass
```

## Spell Implementation Patterns

### Pattern 1: Direct Damage Spells

#### Magic Missile Implementation
```python
class MagicMissileSpell(BaseSpell):
    def cast(self, caster_id: str, targets: List[str], spell_level: int = 1) -> SpellResult:
        # Magic Missile: 3 missiles at 1st level, +1 per level above 1st
        num_missiles = 3 + (spell_level - 1)
        total_damage = 0
        messages = []

        # Distribute missiles among targets
        for i in range(num_missiles):
            target = targets[i % len(targets)]
            damage = self.roll_damage("1d4+1")  # Each missile does 1d4+1

            self.apply_damage(target, damage, "force")
            total_damage += damage
            messages.append(f"Missile {i+1} hits {target} for {damage} force damage")

        return SpellResult(
            success=True,
            damage_dealt=total_damage,
            targets_affected=targets,
            log_messages=messages
        )
```

#### Fireball Implementation
```python
class FireballSpell(BaseSpell):
    def cast(self, caster_id: str, target_point: Tuple[int, int],
             spell_level: int = 3) -> SpellResult:
        # Fireball: 8d6 base damage, +1d6 per level above 3rd
        damage_dice = 8 + (spell_level - 3)
        base_damage = self.roll_damage(f"{damage_dice}d6")
        save_dc = self.get_spell_save_dc(caster_id)

        # Find all targets in 20-foot radius
        targets_in_area = self.get_targets_in_radius(target_point, 20)
        affected_targets = []
        total_damage = 0
        messages = []

        for target_id in targets_in_area:
            dex_save = self.roll_saving_throw(target_id, "dexterity")

            if dex_save >= save_dc:
                actual_damage = base_damage // 2  # Half damage on save
                messages.append(f"{target_id} saves for half damage ({actual_damage})")
            else:
                actual_damage = base_damage
                messages.append(f"{target_id} fails save, takes full damage ({actual_damage})")

            self.apply_damage(target_id, actual_damage, "fire")
            affected_targets.append(target_id)
            total_damage += actual_damage

        return SpellResult(
            success=True,
            damage_dealt=total_damage,
            targets_affected=affected_targets,
            requires_save=True,
            save_dc=save_dc,
            log_messages=messages
        )
```

### Pattern 2: Healing Spells

#### Cure Wounds Implementation
```python
class CureWoundsSpell(BaseSpell):
    def cast(self, caster_id: str, target_id: str, spell_level: int = 1) -> SpellResult:
        # Cure Wounds: 1d8 + spell mod, +1d8 per level above 1st
        healing_dice = 1 + (spell_level - 1)
        spell_mod = self.get_ability_modifier(caster_id, "wisdom")  # Assume cleric

        healing = self.roll_damage(f"{healing_dice}d8") + spell_mod

        # Apply healing (integration with existing healing system)
        actual_healing = self.apply_healing(target_id, healing)

        return SpellResult(
            success=True,
            healing_done=actual_healing,
            targets_affected=[target_id],
            log_messages=[f"Heals {target_id} for {actual_healing} hit points"]
        )
```

### Pattern 3: Buff/Debuff Spells

#### Bless Implementation
```python
class BlessSpell(BaseSpell):
    def cast(self, caster_id: str, targets: List[str], spell_level: int = 1) -> SpellResult:
        # Bless affects up to 3 creatures, +1 per spell level above 1st
        max_targets = min(3 + (spell_level - 1), len(targets))
        selected_targets = targets[:max_targets]

        # Apply blessed condition to each target
        for target_id in selected_targets:
            self.apply_condition(target_id, {
                'condition_name': 'blessed',
                'duration_rounds': 600,  # 10 minutes
                'effects': {
                    'attack_bonus': '1d4',
                    'saving_throw_bonus': '1d4'
                },
                'concentration': True,
                'caster_id': caster_id,
                'spell_id': 'bless'
            })

        # Start concentration for caster
        self.start_concentration(caster_id, 'bless', spell_level)

        return SpellResult(
            success=True,
            targets_affected=selected_targets,
            concentration_started=True,
            conditions_applied=[{'name': 'blessed', 'targets': selected_targets}],
            log_messages=[f"Blesses {len(selected_targets)} targets"]
        )
```

### Pattern 4: Reaction Spells

#### Shield Implementation
```python
class ShieldSpell(BaseSpell):
    def cast(self, caster_id: str, triggering_attack: Optional[Dict] = None) -> SpellResult:
        # Shield: +5 AC until start of next turn, blocks Magic Missile

        # Apply temporary AC bonus
        self.apply_temporary_effect(caster_id, {
            'effect_type': 'ac_bonus',
            'bonus': 5,
            'duration': 'until_next_turn',
            'source': 'shield_spell'
        })

        messages = [f"{caster_id} gains +5 AC until their next turn"]
        blocked_attack = False

        # Check if this blocks the triggering attack
        if triggering_attack:
            old_ac = triggering_attack.get('target_ac', 0)
            new_ac = old_ac + 5
            attack_roll = triggering_attack.get('attack_roll', 0)

            if attack_roll < new_ac and attack_roll >= old_ac:
                blocked_attack = True
                messages.append("Shield deflects the incoming attack!")

        return SpellResult(
            success=True,
            targets_affected=[caster_id],
            blocked_attack=blocked_attack,
            log_messages=messages
        )
```

### Pattern 5: Utility Spells

#### Invisibility Implementation
```python
class InvisibilitySpell(BaseSpell):
    def cast(self, caster_id: str, target_id: str, spell_level: int = 2) -> SpellResult:
        # Invisibility: Target becomes invisible until attacking or casting

        # Apply invisible condition
        self.apply_condition(target_id, {
            'condition_name': 'invisible',
            'duration_rounds': 600,  # Up to 1 hour
            'effects': {
                'attacks_against': 'disadvantage',
                'attacks_by': 'advantage',
                'cannot_be_seen': True
            },
            'concentration': True,
            'caster_id': caster_id,
            'spell_id': 'invisibility',
            'break_on_attack': True,
            'break_on_spell': True
        })

        # Start concentration for caster
        self.start_concentration(caster_id, 'invisibility', spell_level)

        return SpellResult(
            success=True,
            targets_affected=[target_id],
            concentration_started=True,
            log_messages=[f"{target_id} becomes invisible"]
        )
```

## Database Schema Extensions

### Spell Mechanical Data Table
```sql
CREATE TABLE spell_mechanics (
    spell_id TEXT PRIMARY KEY,
    spell_name TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    school TEXT NOT NULL,
    casting_time TEXT NOT NULL,
    range_text TEXT NOT NULL,
    components TEXT NOT NULL,
    duration TEXT NOT NULL,
    concentration BOOLEAN DEFAULT FALSE,
    ritual BOOLEAN DEFAULT FALSE,

    -- Damage mechanics
    damage_dice TEXT,           -- "3d6", "1d4+1", etc.
    damage_type TEXT,          -- "fire", "cold", "force", etc.
    damage_scaling TEXT,       -- "1d6_per_level", "1d4_per_2_levels", etc.

    -- Attack mechanics
    spell_attack BOOLEAN DEFAULT FALSE,
    ranged_attack BOOLEAN DEFAULT FALSE,

    -- Save mechanics
    saving_throw TEXT,         -- "dexterity", "wisdom", etc.
    save_effect TEXT,          -- "half", "negates", "special"

    -- Area mechanics
    area_type TEXT,            -- "sphere", "cone", "line", "cube"
    area_size INTEGER,         -- radius/length in feet
    area_scaling TEXT,         -- how area changes with spell level

    -- Healing mechanics
    healing_dice TEXT,         -- "1d8", "2d4+2", etc.
    healing_scaling TEXT,      -- "1d8_per_level", etc.

    -- Condition mechanics
    condition_applied TEXT,    -- condition name if applies one
    condition_duration TEXT,   -- "1_round", "10_minutes", "concentration"

    -- Implementation data
    implementation_class TEXT, -- Python class name
    implementation_priority INTEGER, -- 1=high, 2=medium, 3=low
    special_mechanics TEXT,    -- JSON for complex interactions

    FOREIGN KEY (spell_id) REFERENCES spells(id)
);
```

### Active Spell Effects Table
```sql
CREATE TABLE active_spell_effects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    spell_id TEXT NOT NULL,
    caster_id TEXT NOT NULL,
    effect_type TEXT NOT NULL,      -- "damage", "healing", "condition", "buff", "debuff"
    effect_subtype TEXT,            -- "ongoing_damage", "ac_bonus", "attack_penalty", etc.

    -- Duration tracking
    duration_type TEXT NOT NULL,    -- "rounds", "minutes", "hours", "permanent", "until_next_turn"
    duration_remaining INTEGER,     -- rounds/minutes remaining

    -- Effect data
    effect_value INTEGER,           -- numeric bonus/penalty
    effect_dice TEXT,              -- dice formula for variable effects
    effect_data TEXT,              -- JSON for complex effect data

    -- Concentration
    requires_concentration BOOLEAN DEFAULT FALSE,
    concentration_broken BOOLEAN DEFAULT FALSE,

    -- Timing
    trigger_timing TEXT,           -- "start_turn", "end_turn", "on_attack", "on_damage"
    created_round INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id),
    FOREIGN KEY (caster_id) REFERENCES characters(id)
);
```

### Concentration Tracking Table
```sql
CREATE TABLE character_concentration (
    character_id TEXT PRIMARY KEY,
    spell_id TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    start_round INTEGER NOT NULL,
    duration_remaining INTEGER,     -- rounds remaining
    concentration_dc INTEGER DEFAULT 10,

    -- Linked effects (for cleanup when concentration breaks)
    linked_effects TEXT,           -- JSON array of effect IDs

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (character_id) REFERENCES characters(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);
```

## Integration with Existing Systems

### Action Panel Integration

#### Enhanced Spell Action Cards
```python
def _create_spell_action_cards(self):
    """Create action cards for available spells"""
    if not self.character_context:
        return

    spells = self._get_character_castable_spells()

    for spell in spells:
        spell_id = spell['spell_id']

        # Determine action type based on spell mechanics
        action_type = self._determine_spell_action_type(spell)

        # Create card with spell data
        card = ActionCard(
            title=spell['name'],
            description=self._format_spell_description(spell),
            icon=self._get_spell_icon(spell),
            action_type=action_type,
            spell_data=spell,
            available=self._can_cast_spell(spell),
            tooltip=self._generate_spell_tooltip(spell)
        )

        # Add spell level selection if higher slots available
        if self._has_higher_spell_slots(spell['spell_level']):
            card.add_level_selector(spell['spell_level'])

        self.action_cards[f"spell_{spell_id}"] = card

def _determine_spell_action_type(self, spell: Dict) -> ActionType:
    """Determine action type based on spell mechanics"""
    if spell.get('spell_attack') or spell.get('damage_dice'):
        return ActionType.SPELL_ATTACK
    elif spell.get('casting_time') == 'Reaction':
        return ActionType.SPELL_REACTION
    else:
        return ActionType.SPELL_UTILITY
```

### Combat Log Integration

#### Spell Effect Logging
```python
def log_spell_cast(self, spell_result: SpellResult, caster_name: str, spell_name: str):
    """Log spell casting results to combat log"""

    # Main cast message
    self._log_to_combat_panel(f"{caster_name} casts {spell_name}")

    # Damage/healing messages
    if spell_result.damage_dealt:
        self._log_to_combat_panel(f"Deals {spell_result.damage_dealt} damage", "damage")

    if spell_result.healing_done:
        self._log_to_combat_panel(f"Heals {spell_result.healing_done} hit points", "healing")

    # Condition messages
    if spell_result.conditions_applied:
        for condition in spell_result.conditions_applied:
            self._log_to_combat_panel(f"Applies {condition['name']} condition", "condition")

    # Concentration messages
    if spell_result.concentration_started:
        self._log_to_combat_panel(f"{caster_name} begins concentrating on {spell_name}", "concentration")

    # Custom messages
    for message in spell_result.log_messages or []:
        self._log_to_combat_panel(message, "spell_effect")
```

### Character Sheet Integration

#### Active Effects Display
```python
def update_active_effects_display(self):
    """Update character sheet to show active spell effects"""

    effects = self.get_active_spell_effects(self.character_id)

    # Group effects by type
    buffs = [e for e in effects if e['effect_type'] == 'buff']
    debuffs = [e for e in effects if e['effect_type'] == 'debuff']
    conditions = [e for e in effects if e['effect_type'] == 'condition']

    # Update UI elements
    self.active_buffs_panel.clear()
    for buff in buffs:
        self.active_buffs_panel.add_effect_widget(buff)

    self.active_debuffs_panel.clear()
    for debuff in debuffs:
        self.active_debuffs_panel.add_effect_widget(debuff)

    # Update concentration indicator
    concentration = self.get_concentration_spell(self.character_id)
    if concentration:
        self.concentration_indicator.show()
        self.concentration_indicator.set_spell(concentration['spell_name'])
        self.concentration_indicator.set_duration(concentration['duration_remaining'])
    else:
        self.concentration_indicator.hide()
```

## Testing Framework

### Spell Test Base Class
```python
class SpellTestBase:
    def setUp(self):
        self.db_path = ":memory:"  # In-memory database for testing
        self.spell_registry = SpellRegistry(self.db_path)
        self.setup_test_data()

    def setup_test_data(self):
        """Create test characters and data"""
        with sqlite3.connect(self.db_path) as conn:
            # Create test wizard
            conn.execute("""
                INSERT INTO characters (id, name, level, intelligence, proficiency_bonus)
                VALUES ('test_wizard', 'Test Wizard', 5, 16, 3)
            """)

            # Give wizard spell slots
            conn.execute("""
                INSERT INTO character_spell_slots (character_id, level, total, used)
                VALUES ('test_wizard', 1, 4, 0),
                       ('test_wizard', 2, 3, 0),
                       ('test_wizard', 3, 2, 0)
            """)

    def test_magic_missile(self):
        """Test Magic Missile spell"""
        result = self.spell_registry.cast_spell(
            'magic_missile',
            caster_id='test_wizard',
            targets=['target1'],
            spell_level=1
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.damage_dealt)
        self.assertEqual(len(result.targets_affected), 1)
        self.assertGreaterEqual(result.damage_dealt, 3)  # Minimum damage
        self.assertLessEqual(result.damage_dealt, 15)    # Maximum damage at level 1
```

## Performance Considerations

### Caching Strategy
```python
class SpellPerformanceOptimizer:
    def __init__(self):
        self.spell_data_cache = {}
        self.character_spell_cache = {}

    def get_cached_spell_data(self, spell_id: str) -> Dict:
        """Cache spell mechanics to avoid repeated DB queries"""
        if spell_id not in self.spell_data_cache:
            self.spell_data_cache[spell_id] = self._load_spell_data(spell_id)
        return self.spell_data_cache[spell_id]

    def invalidate_character_cache(self, character_id: str):
        """Clear character spell cache when spells change"""
        if character_id in self.character_spell_cache:
            del self.character_spell_cache[character_id]
```

### Batch Operations
```python
def apply_aoe_spell_effects(self, targets: List[str], spell_effect: Dict):
    """Apply spell effects to multiple targets efficiently"""

    # Group operations by type
    damage_operations = []
    condition_operations = []

    for target_id in targets:
        if spell_effect.get('damage'):
            damage_operations.append((target_id, spell_effect['damage']))

        if spell_effect.get('condition'):
            condition_operations.append((target_id, spell_effect['condition']))

    # Execute in batches
    if damage_operations:
        self.batch_apply_damage(damage_operations)

    if condition_operations:
        self.batch_apply_conditions(condition_operations)
```

## Conclusion

This technical implementation guide provides the foundation for implementing a robust spell system in TaleKeeper. The modular architecture allows for easy extension, while the comprehensive database schema supports all D&D 2024 spell mechanics. The integration points ensure seamless operation with existing TaleKeeper systems, and the testing framework guarantees reliability.

The focus on performance optimization and clear code patterns will enable rapid implementation of the priority spells identified in the Solo Play Spell Analysis, creating an engaging and mechanically accurate spellcasting experience for solo D&D play.