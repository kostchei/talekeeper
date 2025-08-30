# TaleKeeper Resource Management & Rest System Design Document

## Overview

This document outlines the design and implementation plan for D&D 2024 resource management and rest mechanics in TaleKeeper. The system will handle short rests, long rests, resource recovery, and ability usage tracking according to official D&D rules.

## Current System Analysis

### Existing Architecture Strengths
- **Combat Flow**: Well-defined encounter states with clear end detection
- **Action Panel**: Established card-based ability system with cooldown infrastructure
- **Character Model**: Solid dataclass foundation with hit points and basic tracking
- **Signal System**: PyQt6 signals enable clean component communication

### Current Limitations
- **Time-based Cooldowns**: Second Wind uses 10-turn cooldown instead of short rest recovery
- **No Rest Mechanics**: No short/long rest implementation
- **Limited Resources**: Only HP and hit dice tracked, no spell slots or class resources
- **Missing Post-Combat Flow**: Combat ends abruptly without rest opportunities

## D&D 2024 Rest Mechanics Requirements

### Short Rest (1 Hour)
- **Triggers**: After combat completion, player choice during exploration
- **Recovery**: 
  - Hit dice can be spent to recover HP
  - Short rest abilities recover (Second Wind, Action Surge, Warlock spell slots)
  - Fighter: Change weapon mastery
- **Limitations**: No daily limit, but requires safety and time

### Long Rest (8 Hours)
- **Triggers**: Player choice in safe locations, requires rations
- **Recovery**:
  - All HP recovered to maximum
  - Half hit dice recovered (up to half total)
  - All spell slots recovered
  - All abilities recovered (short rest + long rest)
  - All class resources recovered (Ki, Bardic Inspiration, etc.)
- **Requirements**: 1 ration consumed, safe location
- **Limitations**: We are not tracking time as such

## System Architecture Design

### 1. Character Resource Model Extensions

```python
@dataclass
class Character:
    # Existing fields...
    
    # Resource Tracking
    spell_slots_current: Dict[int, int] = field(default_factory=dict)  # {level: current_slots}
    spell_slots_max: Dict[int, int] = field(default_factory=dict)      # {level: max_slots}
    class_resources: Dict[str, int] = field(default_factory=dict)      # {resource_name: current}
    class_resources_max: Dict[str, int] = field(default_factory=dict)  # {resource_name: max}
    
    # Rest Tracking
    last_short_rest: Optional[str] = None  # ISO timestamp
    last_long_rest: Optional[str] = None   # ISO timestamp
    
    # Ability Usage
    ability_uses: Dict[str, int] = field(default_factory=dict)  # {ability_name: uses_remaining}
    ability_uses_max: Dict[str, int] = field(default_factory=dict)  # {ability_name: max_uses}
```


### 3. Post-Combat Action Cards

When combat ends (`is_encounter_complete() == True`), display action cards **in the same encounter tab where monsters were defeated**:

#### Loot Card
- **Purpose**: Search defeated monsters for treasure and equipment
- **Action**: Opens loot dialog displaying pre-generated loot
- **Mechanics**: **Dummy loot pre-generated when monsters spawn** based on CR
- **Implementation**: Simple placeholder loot for now, full treasure generation system later

#### Short Rest Card  
- **Purpose**: Begin automatic short rest (assumed after every encounter)
- **Requirements**: None - player always takes short rest after combat
- **Action**: Instant rest with **optional** hit dice spending for HP recovery

### 4. Rest Dialog Components

#### Short Rest Dialog
- **Duration**: **Instant** - no countdown, immediate completion when clicked
- **Hit Dice Management**: 
  - Show available hit dice by class (d6, d8, d10, d12)
  - Click to spend → **roll dice manually** + CON modifier → recover HP
  - Cannot exceed max HP
  - **Optional** - player can choose to spend hit dice or not
- **Ability Recovery**: **Automatic** restoration of short rest abilities
- **Visual Feedback**: Abilities flash yellow when recovered, log announcement
- **Completion**: Close dialog, update character resources, return to exploration

#### Long Rest Dialog
- **Requirements Check**: 
  - Check inventory for 1+ rations (stacked item)
  - **Consume 1 ration automatically** (reduce stack count)
  - Check 24-hour limit since last long rest
- **Duration**: **Instant** - immediate completion when clicked
- **Full Recovery**: **All resources restored automatically** (HP, spell slots, abilities, hit dice)
- **Inventory Integration**: 1 ration consumed from existing inventory stack
- **Location Safety**: Simple safe/unsafe indicator

### 5. Action Panel Integration

#### Resource-Based Cooldowns
Replace time-based cooldowns with rest-based recovery:

```python
class RestRecovery(Enum):
    NONE = "none"           # No limit (cantrips, basic attacks)
    SHORT_REST = "short"    # Second Wind, Action Surge
    LONG_REST = "long"      # Spell slots, daily abilities
    
class ActionCard:
    recovery_type: RestRecovery = RestRecovery.NONE
    uses_remaining: int = 1
    uses_max: int = 1
```

#### Ability State Indicators
- **Available**: Normal appearance
- **Exhausted**: **Grayed out** completely, shows recovery requirement  
- **Recovery Animation**: **Yellow flash** around ability when restored after rest
- **Log Announcements**: "Second Wind recovered!" messages in combat log
- **Limited Uses**: Badge showing "2/3" remaining uses

### 6. Resource Display Integration

#### Character Panel Enhancements
- **Resource Section**: Show current/max for all tracked resources
- **Rest Status**: Time since last short/long rest
- **Inventory Integration**: Rations visible in inventory as stacked items ("Rations (5)", "Rations (11)", etc.)

#### Action Card Tooltips
- Show exact recovery requirements
- Display remaining uses if limited
- Indicate recovery type (short rest, long rest, etc.)

## Updated Technical Requirements

### Post-Combat Flow
1. **Combat Ends** → All monsters defeated
2. **Monster Cards Replaced** → Loot and Short Rest cards appear **in same encounter tab location**
3. **Default Assumption** → Player always takes short rest after every encounter
4. **Instant Actions** → No time delays, immediate results

### Resource Management Rules
- **Short Rest**: Always assumed after combat, instant ability recovery + optional hit dice spending
- **Long Rest**: Instant full recovery, consumes exactly 1 ration, 24-hour cooldown
- **Rations**: Tracked in inventory as stacked items, only consumed on long rest (1 per rest)
- **Starting Rations**: Player begins with 5 rations total
- **Hit Dice**: Manual rolling (dice + CON modifier) for HP recovery choice
- **Potion Consumption**: Potion of Healing → Empty Bottle (0.25 lb, 1 cp value)

### Visual Feedback System
- **Exhausted Abilities**: Completely grayed out
- **Recovery Animation**: Yellow flash effect when abilities return
- **Log Messages**: "Second Wind recovered!" announcements
- **Resource Display**: Always-visible ration counter in character panel

## Implementation Phases

### Phase 1: Core Infrastructure (Foundation)
**Priority: HIGH**

1. **Character Model Extensions**
   - Add resource tracking fields to `Character` dataclass
   - Update `CharacterDTO` and conversion methods
   - Modify database schema and migration

2. **Rest State Architecture**  
   - Create `RestSession` model
   - Add rest tracking to game state
   - Implement rest validation logic

3. **Post-Combat Detection**
   - Enhance `is_encounter_complete()` with callback system
   - Add encounter end signal emission
   - Create post-combat state in encounter panel

**Deliverables**: Extended character model, rest state tracking, combat end detection

### Phase 2: Combat Integration (User Experience)
**Priority: HIGH**

4. **Post-Combat Action Cards**
   - Create Loot and Short Rest cards
   - Add to encounter panel after combat completion
   - Implement card selection and state transitions

5. **Short Rest Implementation**
   - Create short rest dialog component
   - Implement hit dice spending mechanics
   - Add automatic ability recovery
   - Update character resources after rest

6. **Action Panel Rest Integration**
   - Replace time-based cooldowns with rest-based recovery
   - Update `ActionCard` to show resource states
   - Modify card availability based on usage limits

**Deliverables**: Playable short rest system, post-combat flow, resource-aware action cards

### Phase 3: Advanced Features (Polish)
**Priority: MEDIUM**

7. **Long Rest Implementation**
   - Create long rest dialog with ration requirements
   - Implement 24-hour limitation checking  
   - Add location safety considerations
   - Full resource recovery automation

8. **Spell Slot Management**
   - Add spell slot tracking to character model
   - Create spell slot display in character panel
   - Integrate with spellcasting abilities

9. **Class-Specific Resources**
   - Implement Ki points (Monk)
   - Add Bardic Inspiration (Bard)
   - Create Channel Divinity tracking (Cleric/Paladin)
   - Expand for all D&D classes

**Deliverables**: Complete rest system, spell management, class-specific resources

### Phase 4: Enhancement & Polish (Quality of Life)
**Priority: LOW**

10. **Advanced Rest Features**
    - Rest interruption mechanics
    - Group rest coordination
    - Environmental rest limitations

11. **Resource Optimization**
    - Automatic resource suggestions
    - Rest planning recommendations
    - Resource usage analytics

**Deliverables**: Polished rest experience, advanced resource management

## Technical Integration Points

### Encounter Panel (`encounter_pane/encounter_panel.py`)
- **Line 2464**: `is_encounter_complete()` - Add post-combat card display
- **Line 580**: `set_combat_mode()` - Add rest state handling  
- **Line 639**: `_start_combat()` - Initialize encounter resource tracking

### Action Panel (`action_cards/action_panel.py`)
- **Line 319**: Cooldown system - Replace with rest-based recovery
- **Line 1528**: `load_character_feats()` - Add resource state loading
- **ActionCard class**: Add resource tracking fields

### Character Model (`models/character_indexeddb.py`)
- **Line 30**: `Character` dataclass - Add resource fields
- **Line 117**: `to_dict()` - Include resource serialization
- **Line 122**: `from_dict()` - Handle resource deserialization

### Game Engine (`core/game_engine_indexeddb.py`)  
- **Line 331**: Character creation - Initialize resources
- **Line 378**: `_character_to_dto()` - Include resource conversion
- Add rest session management methods

## Success Criteria

### Functional Requirements
✅ **Combat Completion**: After defeating all monsters, Loot and Short Rest cards appear
✅ **Short Rest Recovery**: Hit dice spending recovers HP, abilities refresh
✅ **Long Rest Recovery**: Full resource restoration with ration consumption
✅ **Resource Tracking**: All abilities show correct usage states
✅ **Action Cards**: Display availability based on resource states

### User Experience Goals
✅ **Intuitive Flow**: Natural progression from combat → rest → exploration
✅ **Clear Feedback**: Visual indicators for resource states and recovery options
✅ **D&D Accuracy**: Rest mechanics match official 2024 rules
✅ **Performance**: No noticeable impact on combat or character loading

### Technical Quality
✅ **Data Integrity**: Character resources persist across sessions
✅ **Error Handling**: Graceful handling of edge cases and invalid states
✅ **Extensibility**: Easy addition of new resource types and recovery mechanics
✅ **Maintainability**: Clean separation of concerns and clear code structure

## Risk Mitigation

### Data Migration
- **Risk**: Existing characters lack resource fields
- **Mitigation**: Character model `from_dict()` handles missing fields gracefully

### Performance Impact
- **Risk**: Frequent resource updates slow the system
- **Mitigation**: Batch resource updates, efficient data structures

### Complexity Creep
- **Risk**: Over-engineering leads to development delays
- **Mitigation**: Phased implementation focusing on core functionality first

### User Confusion
- **Risk**: Complex rest mechanics overwhelm players
- **Mitigation**: Clear visual design, helpful tooltips, optional automation

---

**Document Status**: Draft v1.0
**Last Updated**: 2025-08-30
**Next Review**: After Phase 1 completion