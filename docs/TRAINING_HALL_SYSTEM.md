# Training Hall Level Progression System

## Overview
The Training Hall system provides a D&D-style level progression mechanic where players must spend gold and time to level up when they have sufficient XP. This system integrates with TaleKeeper's existing encounter system as a special town encounter.

## Current State Analysis

### Existing Components
- **Level Up Service** (`services/level_up.py`): Backend leveling logic with multi-class support
- **XP System**: Characters track `experience_points` in database
- **Encounter System**: Tab-based encounters with action cards
- **Feature Integration**: Automatic feature granting on level up
- **Database Schema**: Full support for character levels and class progression

### Missing Components
- Training Hall encounter tab/interface
- Gold cost calculation and deduction
- Player choice UI for class selection (multi-classing)
- Level-up confirmation workflow
- Training hall as town encounter trigger

## Training Hall Design

### Trigger Conditions
The Training Hall encounter tab appears when:
1. Character has sufficient XP for next level (milestone: 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000)
2. Character is in a safe location (town/settlement)
3. Character has sufficient gold for training

### Training Costs
**Official D&D Training Costs** (from PHB):

| Level Attained | Training Time | Training Cost |
|----------------|---------------|---------------|
| 2–4            | 10 days       | 20 GP         |
| 5–10           | 20 days       | 40 GP         |
| 11–16          | 30 days       | 60 GP         |
| 17–20          | 40 days       | 80 GP         |

### Training Hall Interface

#### Layout
New encounter tab: **"Training Hall"** (similar to Short Rest card)

#### Content Sections
1. **Training Available Banner**
   ```
   🏛️ TRAINING AVAILABLE
   You have enough experience to advance to level X
   Cost: XXX gold pieces (includes food and lodging)
   ```

2. **Class Selection** (if multi-classing available)
   - Radio buttons for available classes
   - Current class levels display
   - New features preview for selected class

3. **Level Up Confirmation**
   - Summary of gained features
   - HP increase options (if applicable)
   - Gold cost confirmation
   - "Begin Training" button

#### Training Process
1. **Payment**: Deduct gold from character
2. **Long Rest Effect**: Full HP/resource restoration (included in training cost)
3. **Level Advancement**: 
   - Increase character level
   - Increase selected class level
   - Grant new class features
   - Update database
4. **Time Passage**: 1-7 days of downtime (narrative only)

### Technical Implementation

#### Database Changes
No schema changes needed - existing tables support this system:
- `levelup_costs` table: Contains official training costs by level range (needs population)
- `characters` table: Tracks XP and gold amounts
- `character_class_levels` table: Multi-class progression tracking

**Required Data Population**:
```sql
INSERT INTO levelup_costs (level_range_start, level_range_end, training_days, training_cost_gp) VALUES
(2, 4, 10, 20),
(5, 10, 20, 40),
(11, 16, 30, 60),
(17, 20, 40, 80);
```

#### New Files Needed
- `encounters/training_hall.py`: Training hall encounter logic
- `ui/training_interface.py`: Training hall UI components

#### Integration Points
- **Encounter Panel**: Add training hall tab when conditions met
- **Game Engine**: Check XP thresholds and gold availability
- **Character Panel**: Update display after training
- **Action Panel**: Handle training hall actions

### User Experience Flow

1. **XP Milestone Reached**: Player gains enough XP during exploration/combat
2. **Town Visit**: Player travels to town/settlement location
3. **Training Hall Appears**: New encounter tab automatically appears
4. **Training Decision**: Player reviews costs and potential gains
5. **Class Selection**: If multi-classing, choose which class to advance
6. **Training Begins**: Payment processed, character advances level
7. **Results**: New features granted, full rest completed, time passes
8. **Tab Removal**: Training hall tab disappears until next level threshold

### Advanced Features (Future)

#### Trainer NPCs
- Different trainers for different classes
- Special trainers unlock unique abilities
- Trainer availability affects costs

#### Training Variants
- **Intensive Training**: Double cost, half time
- **Self-Study**: Half cost, double time  
- **Group Training**: Discount for party members

#### Location-Based Training
- **Major Cities**: All classes available, standard costs
- **Small Towns**: Limited classes, +50% cost
- **Wilderness**: Self-training only, longer time

## Implementation Priority

### Phase 1 (Core System)
- [x] XP tracking system (already exists)
- [ ] Training hall encounter tab
- [ ] Gold cost calculation and deduction
- [ ] Basic level-up interface
- [ ] Integration with existing level_up_service

### Phase 2 (Polish)
- [ ] Multi-class selection UI
- [ ] Feature preview system
- [ ] Training time/narrative elements
- [ ] Visual improvements

### Phase 3 (Advanced)
- [ ] Trainer NPCs and location variants
- [ ] Special training options
- [ ] Training hall lore and flavor text

## Code Integration Notes

### Key Files to Modify
- `encounter_pane/encounter_panel.py`: Add training hall tab logic
- `core/game_engine_sqlite.py`: Add training availability checks
- `action_cards/action_panel.py`: Add training actions

### Existing Services to Use
- `services/level_up.py`: Backend leveling logic
- Character database operations
- Feature system integration

### UI Consistency
- Follow existing encounter tab patterns
- Use action card style for training options  
- Match current theme and styling
- Integrate with log panel for training messages

## Testing Scenarios

1. **Standard Level Up**: Character reaches level 2, has gold, trains successfully
2. **Insufficient Gold**: Character has XP but lacks training funds
3. **Multi-class Choice**: Character chooses different class for advancement
4. **Feature Integration**: Verify new class features are properly granted
5. **Long Rest Effects**: Confirm full recovery after training
6. **Edge Cases**: Level 20 cap, invalid states, database errors

This system transforms leveling from an automatic process into an engaging player decision that requires resource management and strategic planning, perfectly fitting D&D's progression philosophy.