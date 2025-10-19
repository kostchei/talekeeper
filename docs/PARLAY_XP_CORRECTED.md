# Parlay & Pickpocket XP - CORRECTED Formula

## Discovery: Encounter Generator Already Calculates XP

### Existing XP System

**File**: `encounter_generator.py` line 127
```python
"xp": CR_TO_XP.get(cr_str, 0)
```

Each monster in an encounter already has its XP calculated from CR.

**File**: `encounter_panel.py` line 249
```python
total_xp = sum(m.get('xp', 0) for m in encounter_data.get('monsters', []))
```

Total encounter XP = sum of all monster XP values.

---

## CORRECTED: Use Total Encounter XP (Not Just Strongest Monster)

### Current (Wrong) Approach
```python
# OLD - Only rewards for strongest monster
max_xp = max(m.get('experience_points', 0) for m in monsters)
parlay_xp = max_xp // 2
```

**Problem**:
- Only considers 1 monster in multi-monster encounters
- 4 Goblins (200 XP total) → 25 XP (only 1 goblin counted)
- Should be 100 XP (50% of 200 total)

### CORRECTED: Use Total Encounter XP
```python
# NEW - Rewards for entire encounter
total_xp = sum(m.get('xp', 0) for m in monsters)
parlay_xp = total_xp // 2
```

**Benefits**:
- Matches combat XP structure
- Fair for multi-monster encounters
- Simpler logic

---

## Revised XP Rewards

| Resolution | Formula | Example (4 Goblins = 200 XP) |
|------------|---------|------------------------------|
| **Combat Victory** | 100% total XP | 200 XP |
| **Parlay Success** | 50% total XP | 100 XP |
| **Pickpocket Success** | 75% total XP | 150 XP |
| **Stealth Avoid** | 33% total XP | 66 XP |

---

## Implementation Changes

### File: `src/talekeeper/services/parlay_system.py`

**REPLACE** `calculate_parlay_xp_reward()`:

```python
def calculate_parlay_xp_reward(self, monsters: List[Dict]) -> int:
    """
    Calculate XP reward for successful parlay.

    Award 50% of TOTAL encounter XP (not just strongest monster).

    Args:
        monsters: List of monster dicts with 'xp' field

    Returns:
        Half of total encounter XP
    """
    if not monsters:
        return 0

    # Sum all monster XP (already calculated from CR by encounter generator)
    total_xp = sum(m.get('xp', 0) for m in monsters)

    return total_xp // 2
```

**UPDATE** `execute_pickpocket_attempt()`:

```python
def execute_pickpocket_attempt(self, character_id: str, monsters: List[Dict], character_data: Dict) -> Dict:
    """
    Execute pickpocket with 75% of TOTAL encounter XP.
    """
    # ... existing dual skill check code ...

    if overall_success:
        # Calculate XP reward (75% of TOTAL encounter XP)
        total_xp = sum(m.get('xp', 0) for m in monsters)
        pickpocket_xp = int(total_xp * 0.75)

        # ... rest of success handling ...
```

---

## Comparison: Old vs New

### Scenario: 4 Goblins (CR 1/4 each = 50 XP each)

**Total Encounter XP**: 200 XP

| Method | OLD (Strongest Only) | NEW (Total) |
|--------|---------------------|-------------|
| **Combat** | 200 XP | 200 XP |
| **Parlay** | 25 XP (1 goblin) ❌ | 100 XP (all 4) ✅ |
| **Pickpocket** | 37 XP (75% of 50) ❌ | 150 XP (75% of 200) ✅ |

### Scenario: 1 Aboleth (CR 10 = 5,900 XP)

**Total Encounter XP**: 5,900 XP

| Method | OLD | NEW |
|--------|-----|-----|
| **Combat** | 5,900 XP | 5,900 XP |
| **Parlay** | 2,950 XP | 2,950 XP (same) ✅ |
| **Pickpocket** | 4,425 XP | 4,425 XP (same) ✅ |

**Key Insight**: Old approach only worked correctly for solo encounters. New approach works for both.

---

## Stealth Avoidance Also Uses Total XP

**File**: `src/talekeeper/services/encounter_avoidance.py`

Verify it already uses total:
```python
def _calculate_avoidance_xp(self, monsters: List[Dict]) -> int:
    """Calculate XP for avoiding encounter (33% of total)."""
    total_xp = sum(m.get('xp', 0) for m in monsters)
    return int(total_xp * 0.33)
```

This should already be correct if implemented.

---

## NO Need for CR-to-XP in Parlay System!

**Major Simplification**: The encounter generator ALREADY did the CR-to-XP conversion and stored it in each monster dict.

**Remove from parlay_system.py**:
```python
# DELETE THIS:
# from talekeeper.services.cr_to_xp import cr_to_xp, get_most_powerful_monster

# DELETE THIS:
# def _get_monster_xp(self, monster: Dict) -> int:
#     return cr_to_xp(monster.get('challenge_rating', '0'))
```

**Why**: Monsters passed to parlay_system ALREADY have 'xp' field calculated!

---

## Simplified Implementation

### Step 1: No CR Conversion Needed

Monsters from encounter generator already have:
```python
{
    'name': 'Goblin',
    'cr': 0.25,
    'cr_str': '1/4',
    'xp': 50,  # <-- ALREADY CALCULATED
    'alignment': 'Neutral Evil',
    'intelligence': 10,
    # ... other fields ...
}
```

### Step 2: Just Sum the XP

```python
def calculate_parlay_xp_reward(self, monsters: List[Dict]) -> int:
    """50% of total encounter XP."""
    return sum(m.get('xp', 0) for m in monsters) // 2
```

**That's it.** No CR conversion, no "most powerful" logic needed.

---

## Updated Documentation

### Parlay XP Calculation

**Old Documentation**:
> Award 50% XP from the **most powerful monster**

**NEW Documentation**:
> Award 50% of **total encounter XP**

### Pickpocket XP Calculation

**Old Documentation**:
> Award 75% XP from the **most powerful monster**

**NEW Documentation**:
> Award 75% of **total encounter XP**

---

## Testing with Real Data

### Test 1: Multi-Monster Encounter
```python
monsters = [
    {'name': 'Goblin', 'xp': 50, 'cr_str': '1/4'},
    {'name': 'Goblin', 'xp': 50, 'cr_str': '1/4'},
    {'name': 'Goblin', 'xp': 50, 'cr_str': '1/4'},
    {'name': 'Hobgoblin', 'xp': 100, 'cr_str': '1/2'}
]

total = sum(m['xp'] for m in monsters)  # 250 XP
parlay_reward = total // 2  # 125 XP
pickpocket_reward = int(total * 0.75)  # 187 XP
```

### Test 2: Solo Boss
```python
monsters = [
    {'name': 'Aboleth', 'xp': 5900, 'cr_str': '10'}
]

total = 5900
parlay_reward = 2950  # 50%
pickpocket_reward = 4425  # 75%
```

---

## Benefits of This Approach

1. ✅ **Simpler**: No CR conversion needed in parlay_system
2. ✅ **Accurate**: Matches combat XP exactly
3. ✅ **Fair**: Multi-monster encounters rewarded properly
4. ✅ **Consistent**: Uses same XP values as combat victory
5. ✅ **Less Code**: Remove entire CR conversion module from parlay

---

## Files to Update

### Delete (Not Needed)
- ❌ `src/talekeeper/services/cr_to_xp.py` - Encounter generator already does this

### Update
- ✅ `src/talekeeper/services/parlay_system.py` - Use sum of 'xp' field
- ✅ `src/talekeeper/services/encounter_avoidance.py` - Verify uses total
- ✅ Documentation - Update to "total encounter XP"

---

## Summary

**Key Discovery**: Monsters already have XP calculated. Just sum them up!

**Old Approach**:
```python
primary_monster = get_most_powerful_monster(monsters)
xp = cr_to_xp(primary_monster['challenge_rating'])
reward = xp // 2
```

**NEW Approach**:
```python
reward = sum(m.get('xp', 0) for m in monsters) // 2
```

**Result**:
- 90% less code
- Correct for all encounter types
- Matches how combat XP works
