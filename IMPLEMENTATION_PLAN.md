# TaleKeeper Feature Implementation Plan

## Overview
This document outlines the implementation plan for new features marked with ** in the readme.md file. Each section includes the feature description, implementation approach, and relevant code locations.

## 1. Rest System Enhancements

### Feature: Prevent Rests During Active Combat/Hazards
**Description**: Don't allow rests while there are monsters or hazards active.

**Implementation Points**:
- Location: TBD (researching)
- Approach: Check combat state before allowing rest
- UI Changes: Disable rest buttons when monsters active

### Feature: Long Rest Consumes Rations
**Description**: A long rest uses (eats) a ration from inventory.

**Implementation Points**:
- Location: TBD (researching)
- Approach: Check for ration in inventory, consume on long rest
- Failure Case: Prevent long rest or apply exhaustion if no ration

## 2. Town/Shop Encounters

### Feature: Three-Tier Shop System
**Description**: Create shops in 3 sizes with gold limits and dynamic inventory:
- Small: 20gp limit, 10 base (under 20gp) + 1d10 items
- Medium: 200gp limit, 10 base (under 20gp) + 2d10 items (under 200gp)
- Large: 2000gp limit, 10 base (under 20gp) + 3d10 items (under 2000gp)


**Implementation Points**:
- Location: TBD (researching)
- Database: Add shop encounters to seeds
- Service: Create shop_service.py for inventory generation
- UI: Create shop interface panel

## 3. Skill Encounter Rewards

### Feature: Skill Encounters Grant Items
**Description**: Skill encounters should give out items that appear in inventory - potions, common items, rations.

**Implementation Points**:
- Location: TBD (researching)
- Approach: Add loot table to skill challenge rewards
- Items: Healing potions, rations, common adventuring gear

## 4. Encounter Parlay System

### Feature: Diplomatic Resolution for Non-Evil Monsters
**Description**: 75% of non-evil monsters can be parlayed with. Offer "Do you wish to attempt to Parlay" prompt.

**Skill Challenge**: Pick up to 3 CHA skills + 1 random INT or WIS skill
**Reward**: 1/2 XP from most powerful monster, no combat

**Implementation Points**:
- Location: TBD (researching)
- Database: Add can_parlay flag to monsters (75% of non-evil)
- UI: Pre-combat dialog prompt
- Service: Parlay skill challenge system

## 5. Stealth-Based Encounter Avoidance

### Feature: Avoid Encounters with Stealth
**Description**: Use Stealth skill to avoid encounters entirely.

**Implementation Points**:
- Location: TBD (researching)
- Approach: Stealth check vs monster Perception
- Reward: Partial XP, no combat

## 6. Pickpocket System

### Feature: Pickpocket Avoided Encounters and Shops
**Description**: For encounters you've avoided or in shops, attempt pickpocketing.

**Skill Challenge**: Stealth + Sleight of Hand + 1 other random skill
**Reward**: Medium XP for that level + treasure roll

**Implementation Points**:
- Location: TBD (researching)
- Trigger: Available after avoiding encounter or in shops
- UI: Pickpocket button/option
- Service: Pickpocket skill challenge

## 7. Multiclassing System

### Feature: D&D 2024 Multiclassing
**Description**: Allow characters to take levels in multiple classes.

**Implementation Points**:
- Location: TBD (researching)
- Database: Track class levels separately
- Requirements: Ability score prerequisites
- Mechanics: Hit dice, proficiencies, spell slots

## Implementation Priority

1. **Phase 1 - Rest System** (Quick wins)
   - Rest restrictions
   - Ration consumption

2. **Phase 2 - Shops** (New content)
   - Shop encounters
   - Inventory generation

3. **Phase 3 - Social Interactions** (New systems)
   - Skill encounter rewards
   - Parlay system
   - Stealth avoidance

4. **Phase 4 - Advanced Features** (Complex)
   - Pickpocket system
   - Multiclassing

## Code Research Status

### Files to Investigate
- [ ] core/game_engine_sqlite.py - Main game coordinator
- [ ] core/combat_engine.py - Combat state management
- [ ] encounter_pane/ - Encounter UI and logic
- [ ] services/ - Game services for new features
- [ ] database/seeds/ - Monster and item data
- [ ] character_sheet/ - Character data management
- [ ] action_cards/ - Action system

### Research Notes
(To be filled in during code investigation)