# Long Rest & Lifestyle System - Planning Document

## Overview
When characters take a long rest in TaleKeeper, they must pay lifestyle expenses based on available accommodations in their current hex. Wretched and Squalid lifestyles trigger potential encounters or hazards before rest benefits are granted.

## D&D 2024 Long Rest Rules
- **Duration**: 8 hours of rest (6 hours sleep, 2 hours light activity)
- **Benefits**:
  - Restore all hit points
  - Restore all hit dice (up to half character level)
  - Restore spell slots
  - Remove exhaustion levels (1 level per rest)
  - Reset daily abilities
- **Interruption**: More than 1 hour of combat, casting spells, or strenuous activity interrupts rest

## Lifestyle Expenses & Availability

### Lifestyle Tiers

| Lifestyle | Cost per Day | Description | Special Effect |
|-----------|-------------|-------------|----------------|
| Wretched | Free | Survive via chance and charity. Sleep outside exposed to elements. | 50% encounter/hazard before rest |
| Squalid | 1 sp | Bare minimum shelter. Unhealthy conditions, opportunistic criminals. | 25% encounter/hazard before rest |
| Poor | 2 sp | Frugal necessities. Basic inn or local hospitality. | None |
| Modest | 1 gp | Average standard. Clean room, basic amenities. | None |
| Comfortable | 2 gp | Modest spending with luxuries. Well-maintained inn. | None |
| Wealthy | 4 gp | Fine accommodations. Private rooms, servants. | None |

### Settlement Availability

| Settlement Type | Available Lifestyles | Selection Method | Population |
|----------------|---------------------|------------------|------------|
| Empty/Wild | Wretched only | Automatic | 0 |
| Hamlet | Squalid, Poor, or Modest | Roll d3 | 1-200 |
| Village | Squalid, Poor, Modest, or Comfortable | Roll d4 | 200-2,000 |
| Town+ | All lifestyles | Player choice | 2,000+ |

### Settlement Names & Flavor

**When settlement population >= 500:**
- Generate and store settlement name on hex
- Display name on hex map
- Use name in rest UI ("Rest at [Settlement Name]")

**When Modest+ lifestyle available:**
- **Towns**: Named inns ("The Prancing Pony", "The Silver Stag")
- **Villages**: Local worthy ("Lord Harwin's manor", "Chief Oona's hall")
- **Hamlets**: Simple descriptors ("The miller's loft", "Widow Mara's barn")

## Wretched/Squalid Hazard System

### When Rest is Wretched or Squalid
Before granting rest benefits, roll for encounter or hazard:

**Wretched (50% chance):**
1. Roll d100
2. If 01-50: Trigger event
3. Roll d2: 1=encounter, 2=hazard

**Squalid (25% chance):**
1. Roll d100
2. If 01-25: Trigger event
3. Roll d2: 1=encounter, 2=hazard

### Encounter Types (d6)

| d6 | Encounter | Effect |
|----|-----------|--------|
| 1 | Bandits | Combat encounter (CR = character level) |
| 2 | Wild Animals | Combat encounter (CR = character level -1) |
| 3 | Cutpurses | DC 15 Dex save or lose 2d10 gp |
| 4 | Corrupt Guards | Pay 1d10 gp or fight (CR = character level) |
| 5 | Desperate Beggar | Charisma DC 12 or lose 1d6 gp, 1d4 rations |
| 6 | Thugs Shakedown | Intimidation DC 13 or pay 3d6 gp or fight |

### Hazard Types (d6)

| d6 | Hazard | Effect |
|----|--------|--------|
| 1 | Disease | DC 12 Con save or contract disease (disadvantage on ability checks for 1d4 days) |
| 2 | Theft | Lose 2d10 gp and 1 random item (DC 14 Perception to catch thief) |
| 3 | Exposure | Take 1d6 cold damage, DC 13 Con save or 1 exhaustion level |
| 4 | Food Poisoning | DC 13 Con save or poisoned condition for 8 hours |
| 5 | Structural Collapse | DC 14 Dex save or take 2d6 bludgeoning damage |
| 6 | Fire | DC 15 Dex save or take 2d8 fire damage, lose 1d4 items |

### Event Resolution - CRITICAL FLOW

### Payment Happens FIRST, Then Hazard Check

**Correct Flow**:
1. Player selects lifestyle option
2. **Deduct gold cost immediately**
3. Check for hazard trigger (Wretched 50%, Squalid 25%)
4. If hazard triggered:
   - Roll d2: 1=encounter, 2=hazard
   - Resolve event (combat or save)
   - If encounter: Combat happens, NO rest yet
   - If hazard: Apply effects (damage/conditions), THEN grant rest
5. If no hazard OR hazard resolved:
   - **Grant long rest benefits** (restore HP, resources, etc.)

### Key Points
- **Gold spent = commitment made** (no refunds even if interrupted)
- **Encounters interrupt rest** - must rest again after combat (pay again)
- **Hazards don't interrupt** - you suffer effects but still get rest
- **Safe lifestyles (Poor+)** - pay gold, get rest, no complications

## UI Implementation Plan

### Phase 1: Database Schema

#### New Table: character_long_rests
```sql
CREATE TABLE IF NOT EXISTS character_long_rests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id TEXT NOT NULL,
    hex_q INTEGER NOT NULL,
    hex_r INTEGER NOT NULL,
    rest_date TEXT NOT NULL,
    lifestyle_type TEXT NOT NULL,
    lifestyle_cost_gp REAL NOT NULL,
    settlement_name TEXT,
    accommodation_name TEXT,
    hazard_triggered INTEGER DEFAULT 0,
    hazard_type TEXT,
    hazard_result TEXT,
    rest_completed INTEGER DEFAULT 0,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

CREATE INDEX IF NOT EXISTS idx_character_rests
ON character_long_rests(character_id, rest_date);
```

#### Add to character_hex_map table
```sql
ALTER TABLE character_hex_map ADD COLUMN settlement_name TEXT;
ALTER TABLE character_hex_map ADD COLUMN accommodation_name TEXT;
```

### Phase 2: Settlement Name Generation Service

**Location**: `src/talekeeper/services/settlement_name_service.py`

```python
class SettlementNameService:
    def generate_settlement_name(self, settlement_type: str, biome: str, seed: int) -> str:
        """Generate settlement name based on type and biome"""
        pass

    def generate_accommodation_name(self, settlement_type: str, lifestyle: str, seed: int) -> str:
        """Generate inn/manor/hospitality name"""
        pass

    def get_or_create_settlement_name(self, character_id: str, q: int, r: int) -> str:
        """Get existing name or generate new one for hex"""
        pass
```

**Name Generation Tables:**
- **Town Names**: "[Prefix] + [Suffix]" (e.g., "Eastbrook", "Silvermere", "Irongate")
- **Village Names**: "[Geographic] + [Feature]" (e.g., "Highridge", "Deepwood", "Saltmarsh")
- **Hamlet Names**: "[Owner]'s + [Building]" (e.g., "Harwin's Crossing", "Mara's Mill")
- **Inn Names**: "The [Adjective] + [Noun]" (e.g., "The Prancing Pony", "The Golden Lion")

### Phase 3: Long Rest Service

**Location**: `src/talekeeper/services/long_rest_service.py`

```python
class LongRestService:
    def get_available_lifestyles(self, character_id: str, q: int, r: int) -> List[Dict]:
        """Return available lifestyles for current hex settlement"""
        # Check settlement_type from character_hex_map
        # Return lifestyle options with costs and names
        pass

    def check_hazard_trigger(self, lifestyle: str) -> Tuple[bool, str, str]:
        """Check if wretched/squalid triggers hazard
        Returns: (triggered, event_type, event_details)
        """
        pass

    def resolve_encounter(self, encounter_type: str, character_data: Dict) -> Dict:
        """Resolve encounter event, return combat or skill check results"""
        pass

    def resolve_hazard(self, hazard_type: str, character_data: Dict) -> Dict:
        """Resolve hazard event, return damage/condition/loss results"""
        pass

    def complete_long_rest(self, character_id: str, lifestyle_cost: float) -> bool:
        """Deduct gold, restore HP/resources, record rest"""
        pass
```

### Phase 4: Long Rest UI Widget

**Location**: `src/talekeeper/ui/rest_pane/long_rest_widget.py`

**UI Components:**
1. **Settlement Info Panel** (top)
   - Settlement name
   - Settlement type
   - Population estimate

2. **Lifestyle Selection Panel** (middle)
   - Radio buttons for available lifestyles
   - Display: Lifestyle name, cost, description
   - Warning text for Wretched/Squalid (hazard chance)
   - Accommodation name (if Modest+)

3. **Character Status Panel** (bottom left)
   - Current HP / Max HP
   - Current gold
   - Exhaustion level (if any)
   - Active conditions

4. **Action Buttons** (bottom right)
   - "Take Long Rest" (primary action)
   - "Cancel" (close widget)

5. **Event Resolution Panel** (overlay when hazard triggers)
   - Event description
   - Save/check prompt
   - Roll button
   - Result display
   - "Continue to Rest" button (after resolution)

### Phase 5: Integration Points

#### Main Window Integration
**Location**: `src/talekeeper/ui/main_window.py`

```python
def _show_long_rest_interface(self):
    """Show long rest widget as dialog or overlay"""
    # Get current hex position
    # Check settlement type
    # Create LongRestWidget
    # Connect signals
    pass

def _on_rest_completed(self, rest_data: Dict):
    """Handle rest completion, refresh character sheet"""
    pass
```

**Trigger Options:**
1. **Menu button**: "Rest" button in game menu
2. **Hex map**: "Rest Here" button in hex info panel
3. **Keyboard shortcut**: 'R' key

#### Hex Map Widget Integration
**Location**: `src/talekeeper/ui/hex_map/hex_map_widget.py`

```python
# Add to hex info panel
rest_button = QPushButton("Rest Here")
rest_button.clicked.connect(lambda: self.rest_requested.emit(q, r))

# Add signal
rest_requested = pyqtSignal(int, int)  # q, r
```

### Phase 6: Event Flow Diagrams

#### Flow 1: Safe Rest (Poor+ lifestyle)
```
Player clicks "Rest Here"
    |
    v
Display LongRestWidget
    |
    v
Show available lifestyles
    |
    v
Player selects lifestyle
    |
    v
Deduct gold cost
    |
    v
Grant rest benefits
    |
    v
Update character sheet
    |
    v
Close widget
```

#### Flow 2: Hazardous Rest (Wretched/Squalid)
```
Player clicks "Rest Here"
    |
    v
Display LongRestWidget with available lifestyles
    |
    v
Player selects Wretched or Squalid
    |
    v
DEDUCT GOLD COST (0 gp for Wretched, 1 sp for Squalid)
    |
    v
Roll for hazard trigger (d100: Wretched 01-50, Squalid 01-25)
    |
    +----> NO HAZARD (50%/75% safe)
    |        |
    |        v
    |     Display "You rest peacefully despite the conditions..."
    |        |
    |        v
    |     Grant rest benefits (HP, resources, spell slots)
    |        |
    |        v
    |     Close widget, return to game
    |
    +----> HAZARD TRIGGERED (50%/25% danger)
           |
           v
       Display "As you settle in, trouble finds you..."
           |
           v
       Roll d2: 1=Encounter, 2=Hazard
           |
           +----> ENCOUNTER (Combat/Confrontation)
           |        |
           |        v
           |     Display encounter description (Bandits, Cutpurses, etc.)
           |        |
           |        v
           |     Offer choice: Fight / Skill Check / Pay
           |        |
           |        v
           |     Resolve event
           |        |
           |        v
           |     If combat: Start combat encounter
           |        |
           |        v
           |     After combat ends: "Your rest was interrupted."
           |        |
           |        v
           |     NO REST GRANTED - return to rest menu
           |        |
           |        v
           |     Must select lifestyle again (and pay again)
           |
           +----> HAZARD (Environmental/Trap)
                  |
                  v
              Display hazard description (Exposure, Disease, Theft, etc.)
                  |
                  v
              Prompt saving throw (DC 12-15 Con/Dex/etc.)
                  |
                  v
              Player clicks "Roll Save"
                  |
                  v
              Roll d20 + modifier vs DC
                  |
                  +----> SUCCESS
                  |        |
                  |        v
                  |     Display "You avoid the worst of it..."
                  |        |
                  |        v
                  |     No damage/loss
                  |
                  +----> FAILURE
                           |
                           v
                       Apply hazard effects:
                       - Damage (1d6-2d8)
                       - Conditions (poisoned, exhaustion)
                       - Gold/item loss
                           |
                           v
                       Display "You suffer from [effect]..."
                           |
                           v
                       Update character HP/conditions/inventory
                  |
                  v
              "Despite the hardship, you manage to rest..."
                  |
                  v
              Grant rest benefits (HP, resources, spell slots)
                  |
                  v
              Close widget, return to game
```

**Key Difference**:
- **Encounters** = REST INTERRUPTED (no benefits, pay again)
- **Hazards** = REST COMPLETED (you suffer but still get rest)

## UI Mockup (Text-based)

```
+------------------------------------------------------------------+
|                    LONG REST - Irongate (Town)                   |
|                      Population: ~2,500                          |
+------------------------------------------------------------------+
| Available Accommodations:                                        |
|                                                                  |
|  ( ) Wretched - Free                                             |
|      Sleep in alley or abandoned building. DANGER: 50% hazard.   |
|                                                                  |
|  ( ) Squalid - 1 sp                                              |
|      The Rusty Nail (flophouse). CAUTION: 25% hazard.            |
|                                                                  |
|  ( ) Poor - 2 sp                                                 |
|      The Weary Traveler (common room with shared bunks).         |
|                                                                  |
|  (*) Modest - 1 gp                                               |
|      The Silver Stag (private room, basic amenities). [SELECTED] |
|                                                                  |
|  ( ) Comfortable - 2 gp                                          |
|      The Golden Lion (well-appointed room, hot bath).            |
|                                                                  |
|  ( ) Wealthy - 4 gp                                              |
|      Lord's Manor (private suite, servants, fine dining).        |
+------------------------------------------------------------------+
| Character Status:                        |  Current Gold: 47 gp  |
| HP: 28 / 42                              |  Cost: 1 gp           |
| Exhaustion: None                         |  After Rest: 46 gp    |
+------------------------------------------------------------------+
|                 [ Take Long Rest ]      [ Cancel ]               |
+------------------------------------------------------------------+
```

## Event Examples

### Example 1: Wretched Rest - Hazard (Exposure)
```
+------------------------------------------------------------------+
|                         HAZARD EVENT                             |
+------------------------------------------------------------------+
| You try to sleep in a sheltered alcove, but the cold night air   |
| seeps through your bedroll. Ice forms on your blanket.           |
|                                                                  |
| HAZARD: Exposure (Cold Weather)                                  |
| Make a DC 13 Constitution saving throw.                          |
|                                                                  |
|                      [ Roll Save (d20 + 2) ]                     |
+------------------------------------------------------------------+
```

**If failed:**
```
+------------------------------------------------------------------+
| You rolled: 8 + 2 = 10 (Failed!)                                 |
|                                                                  |
| The bitter cold saps your strength. You take 4 cold damage and   |
| gain 1 level of exhaustion.                                      |
|                                                                  |
| Current HP: 24 / 42     Exhaustion: 1                            |
|                                                                  |
| Despite the hardship, you manage to complete your rest.          |
|                                                                  |
|                      [ Continue to Rest ]                        |
+------------------------------------------------------------------+
```

### Example 2: Squalid Rest - Encounter (Cutpurses)
```
+------------------------------------------------------------------+
|                       ENCOUNTER EVENT                            |
+------------------------------------------------------------------+
| As you settle into the dingy flophouse, you notice a shadowy     |
| figure rifling through your pack!                                |
|                                                                  |
| ENCOUNTER: Cutpurses                                             |
| Make a DC 15 Dexterity saving throw to grab your belongings.     |
|                                                                  |
|                      [ Roll Save (d20 + 3) ]                     |
+------------------------------------------------------------------+
```

**If failed:**
```
+------------------------------------------------------------------+
| You rolled: 11 + 3 = 14 (Failed!)                                |
|                                                                  |
| The thief escapes into the night with 17 gold pieces!            |
|                                                                  |
| Current Gold: 30 gp (was 47 gp)                                  |
|                                                                  |
| Shaken but unharmed, you barricade the door and attempt to rest  |
| again.                                                           |
|                                                                  |
| YOUR REST WAS INTERRUPTED. You must select accommodations again. |
|                                                                  |
|                      [ Return to Rest Menu ]                     |
+------------------------------------------------------------------+
```

## Implementation Checklist

### Database (Migration 038_long_rest_lifestyle.sql)
- [ ] Create character_long_rests table
- [ ] Add settlement_name to character_hex_map
- [ ] Add accommodation_name to character_hex_map
- [ ] Add indexes

### Services
- [ ] Create SettlementNameService
  - [ ] Name generation tables
  - [ ] Seed-based deterministic names
  - [ ] Database storage/retrieval
- [ ] Create LongRestService
  - [ ] get_available_lifestyles()
  - [ ] check_hazard_trigger()
  - [ ] resolve_encounter()
  - [ ] resolve_hazard()
  - [ ] complete_long_rest()
  - [ ] deduct_gold()
  - [ ] restore_character_resources()

### UI Components
- [ ] Create LongRestWidget (PyQt6)
  - [ ] Settlement info panel
  - [ ] Lifestyle selection (radio buttons)
  - [ ] Character status display
  - [ ] Action buttons
  - [ ] Event resolution overlay
- [ ] Create EventResolutionWidget
  - [ ] Encounter display
  - [ ] Hazard display
  - [ ] Save/check rolling
  - [ ] Result display

### Integration
- [ ] Add "Rest" button to game menu
- [ ] Add "Rest Here" button to hex map info panel
- [ ] Add keyboard shortcut 'R'
- [ ] Connect signals in main_window
- [ ] Handle rest completion
- [ ] Refresh character sheet after rest

### Testing
- [ ] Test settlement name generation
- [ ] Test lifestyle availability by settlement type
- [ ] Test hazard trigger rates (50% wretched, 25% squalid)
- [ ] Test encounter resolution
- [ ] Test hazard resolution
- [ ] Test rest benefits application
- [ ] Test gold deduction
- [ ] Test edge cases (not enough gold, character at full HP)

## Edge Cases & Special Considerations

### Not Enough Gold
- If player cannot afford selected lifestyle, show warning
- Automatically select highest affordable lifestyle
- Always allow Wretched (free) as fallback

### Character at Full HP
- Still allow rest (restores spell slots, hit dice, conditions)
- Show "You are already at full health" message
- Confirm they still want to spend gold

### Multiple Characters
- Long rest applies to active character only
- If party system exists, rest all characters together
- All characters roll individual saves for hazards

### Combat Interruption
- If encounter occurs during rest, cancel rest
- Do NOT grant benefits
- Force return to rest selection menu
- Character must pay again for new rest attempt

### Death During Hazard
- If hazard reduces character to 0 HP
- Start death saves immediately
- If stabilized, allow rest to proceed (restores to 1 HP)
- If character dies, cancel rest, show death screen

### Settlement Name Persistence
- Once generated, settlement names NEVER change
- Stored in character_hex_map table
- Used for immersion ("You return to Irongate")
- Displayed on hex map when hex is revealed

### Accommodation Availability
- Hamlet: 1d3 determines highest available (1=squalid, 2=poor, 3=modest)
- Village: 1d4 determines highest available
- Town+: All lifestyles available
- Roll is PERMANENT for that hex (stored in character_hex_map)

## Future Enhancements

### Reputation System
- Repeated use of same accommodation builds reputation
- Discounts for loyal customers (5-10% after 3 visits)
- Better rooms offered ("Ah, our best customer!")

### Inn Quests
- Innkeepers offer side quests
- "Clear the rats from the cellar for free lodging"
- Rumors and plot hooks

### Random Events (Positive)
- Friendly travelers share stories (+1 inspiration)
- Local festival (free Comfortable lodging)
- Merchant caravan (shop available in morning)

### Lifestyle Bonuses (D&D 2024)
- **Comfortable+**: Advantage on next Charisma check (well-rested impression)
- **Wealthy**: Gain temporary contact (noble, merchant, guard captain)

### Weather Integration
- Wretched rest in rain: Higher exposure chance
- Wretched rest in snow: Automatic exposure hazard
- Modest+ protects from weather

## Reference: D&D 2024 Lifestyle Rules

**Player's Handbook 2024, Chapter 6: Equipment**

Lifestyle expenses provide a simple way to account for the cost of living in a fantasy world. They cover lodging, food, equipment maintenance, and other necessities.

**Downtime Activity**: Long rest counts as downtime, lifestyle expenses apply.

**Daily Cost**: Pay per day of rest (long rest = 1 day expense).

**Quality of Life**: Better lifestyles reduce danger but cost more gold.

## Implementation Timeline

### Phase 1: Database & Services (2-3 hours)
- Create migration
- Implement SettlementNameService
- Implement LongRestService (core logic)

### Phase 2: Basic UI (3-4 hours)
- Create LongRestWidget
- Implement lifestyle selection
- Implement safe rest flow

### Phase 3: Hazard System (4-5 hours)
- Implement hazard trigger logic
- Create EventResolutionWidget
- Implement encounter/hazard tables
- Implement save rolling UI

### Phase 4: Integration & Polish (2-3 hours)
- Wire main window signals
- Add hex map integration
- Add settlement names to hex display
- Add narration/flavor text

### Phase 5: Testing (2-3 hours)
- Write unit tests for services
- Test UI flows
- Test edge cases
- Balance encounter CR and hazard severity

**Total Estimated Time: 13-18 hours**

## Success Metrics

**System is complete when:**
1. Player can initiate long rest from hex map or menu
2. Available lifestyles correctly match settlement type
3. Wretched/Squalid trigger hazards at correct rates
4. Encounters and hazards resolve with proper D&D mechanics
5. Rest benefits apply correctly after hazard resolution
6. Settlement names generate and persist
7. Gold is deducted for lifestyle expenses
8. UI provides clear feedback for all events
9. Edge cases handled gracefully (no gold, death, etc.)
10. System integrates smoothly with existing TaleKeeper features
