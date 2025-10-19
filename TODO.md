# TaleKeeper TODO List

Record all actions taken to a file for future reference 
Create a “ all monsters randomly “ dnd baseline
List all fighter abilities for each level in a doc.
Plan out how to create those mechanically in a doc.
Implement that plan.
Record the issues.
List all barbarian abilities for each level in a doc.
Look at the fighter doc
 Learn from what broke and why
Plan out how to create the barbarian abilities based on the prior knowledge 
Implement that plan.
Record the issues….

## 🚨 Critical Issues
- [ ] **Check Two-Weapon Fighting** - Verify off-hand attacks and damage modifiers
- [ ] **Check Nick weapon mastery** - Light weapon extra attacks
- [ ] **Level progression** - Fighter, Barbarian, Rogue to level 20

## ⚔️ Combat & Mechanics
- [ ] Range attacks and movement system
- [ ] Weapon mastery implementations (Nick, Cleave, Graze, etc.)
- [ ] Stealth mechanics
- [ ] Encounter parlay/negotiation
- [ ] Encounter avoidance options
- [ ] Pickpocket mechanics
- [ ] Poisons system
- [ ] **Monster Non-Attack Abilities** (See [CONAN_NON_ATTACK_ABILITIES.md](docs/CONAN_NON_ATTACK_ABILITIES.md))
  - [ ] Phase 1: Recharge abilities (dragon breath weapons)
  - [ ] Phase 2: Limited use abilities (X/Day)
  - [ ] Phase 3: Charm/Domination effects
  - [ ] Phase 4: Fear & Frightened conditions
  - [ ] Phase 5: Paralysis & Petrification
  - [ ] Phase 6: Legendary Actions
  - [ ] Phase 7: Lair Actions

## 🏛️ Towns & Economy
- [ ] Towns for selling equipment
- [ ] Training costs for skills/abilities
- [ ] Item drops from defeated monsters
- [ ] Economic system for adventuring

## 🎭 Character Development
### Classes & Subclasses
- [ ] **Barbarian subclasses**
  - [ ] Berserker (Path of the Berserker)
  - [ ] Slayer (custom OSR-style subclass)
- [ ] **Rogue subclasses**
  - [ ] Thief (classic)
  - [ ] Trader (custom OSR-style subclass)
- [ ] **Fighter subclasses**
  - [ ] Champion (simple, effective)
  - [ ] Gladiator (custom OSR-style subclass)
- [ ] **Warlock** - Full spellcaster class
  - [ ] Fiend patron (SRD)
  - [ ] Old One patron (OSR feel)
- [ ] **Paladin** - Half-caster class
  - [ ] Devotion oath (SRD)
  - [ ] Vengeance oath (OSR feel)

### Multiclassing
- [ ] Multiclass prerequisites
- [ ] Multiclass progression rules
- [ ] Spell slot progression for multiclass

## 🎲 Skills & Exploration
- [ ] Full skill system implementation
- [ ] Skill-based encounters
- [ ] Trap detection and disarmament
- [ ] Environmental hazards
- [ ] City adventures
- [ ] Dungeon exploration mechanics

## 🖼️ Visual & Narrative
- [ ] Character portrait images
- [ ] Monster artwork
- [ ] Item icons/images
- [ ] Combat-to-story parser
- [ ] Ollama connectivity for local AI storytelling

## 🌍 Campaign System
- [ ] Campaign frame interface
- [ ] Module system for adventures
- [ ] Save/load campaign states
- [ ] Adventure progression tracking

## 🔧 Technical Improvements
- [ ] Performance optimization for large encounters
- [ ] Memory leak detection and fixes
- [ ] UI responsiveness improvements
- [ ] Database query optimization

## ✅ Testing Coverage Needed
- [ ] Two-weapon fighting automated tests
- [ ] Nick mastery validation
- [ ] Level 1-20 progression tests for all classes
- [ ] Multiclass combination tests
- [ ] Skill check mechanics
- [ ] Economic system tests

## 📋 Release Planning

### Pre-Release 1 (Core Mechanics)
- [ ] Fix critical two-weapon fighting
- [ ] Complete Nick weapon mastery
- [ ] Validate level progression to 20
- [ ] Basic town/economy system

### Release 1 (Playable Game)
- [ ] All fighter/barbarian/rogue subclasses
- [ ] Complete skill system
- [ ] Basic adventure modules
- [ ] Campaign interface

### Release 2 (Enhanced Features)
- [ ] Warlock and Paladin classes
- [ ] Multiclassing system
- [ ] AI storytelling integration
- [ ] Advanced visual features

## 🏷️ Priority Labels

**P0 - Critical**: Game-breaking issues that prevent core gameplay
**P1 - High**: Important features for Release 1
**P2 - Medium**: Nice-to-have features for Release 2
**P3 - Low**: Future enhancements

## 📝 Notes

### Testing Priority
Use the new Qt6 testing framework to validate:
```bash
# Test current fighting styles
python testing/run_tests.py --mode specific

# Test two-weapon fighting specifically
python testing/test_specific_features.py
```

### Database Considerations
- Character progression requires `character_features` table updates
- New classes need entries in `classes` table
- Subclass features need `class_features` definitions

### UI Panel Updates Required
- Action cards for new class abilities
- Character sheet for multiclass display
- Equipment panel for economy features
- Encounter panel for new mechanics

---
*Last updated: 2024-12-05*
*Use automated testing to validate implementations*