# Item Properties Plan

**Date:** 2025-09-15

This document outlines the plan for integrating magical item properties into TaleKeeper, enabling mechanical effects for D&D 2024 items.

## Goals
- Support static bonuses: attack, damage, armor class, and saving throws.
- Allow ability score modifications (e.g., Strength increase).
- Handle advantage on skill checks and saving throws provided by items.
- Implement consumable item effects (e.g., potions, scrolls).

## Core Concepts
1. **Item Effects Service**
   - Extend `ItemEffectsService` to parse item properties and persist bonuses in `character_magical_bonuses`.
   - Track ability score bonuses, attack/damage bonuses, saving throw bonuses, and advantages on skills/saves.
   - Provide retrieval of stored bonuses for other systems (combat, proficiency, etc.).

2. **Mechanical Integration**
   - Combat Manager adds attack and damage bonuses from magical items.
   - Proficiency system includes magical bonuses when calculating attack and saving throw modifiers.
   - Ability score bonuses modify the relevant ability before computing modifiers.

3. **Consumables**
   - Use existing item usage hooks to trigger consumable effects.
   - Example: Potion of Strength applies temporary Strength bonus and saves to database.
   - After use, item is removed from inventory.

## Next Steps
- Implement code changes in `services/item_effects.py` to recognize common magic item patterns (e.g., +1 Greatsword, +1 Studded Leather).
- Update `services/proficiency_system.py` and `core/combat_manager.py` to apply stored bonuses during play.
- Expand consumable handling for scrolls and potions using item usage signals.

