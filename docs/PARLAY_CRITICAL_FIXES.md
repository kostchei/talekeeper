# Parlay System - Critical Fixes Required

## BLOCKERS FOUND - Must Fix Before Implementation

### ⚠️ BLOCKER #1: Monster XP Values are ALL ZERO

**Discovery**: 446 out of 476 monsters (93.7%) have `experience_points = 0`

**Impact**: All code using `max(monsters, key=lambda m: m.get('experience_points', 0))` will fail to select correct monster

**Root Cause**: Database doesn't store XP values, only Challenge Rating

**Solution**: Create CR-to-XP conversion function

```python
# File: src/talekeeper/services/parlay_system.py

CR_TO_XP = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000
}

def _get_monster_xp(self, monster: Dict) -> int:
    """
    Get monster XP from CR since experience_points is always 0.

    Args:
        monster: Monster dict

    Returns:
        XP value based on CR
    """
    cr = monster.get('challenge_rating', '0')

    # Handle string CR
    if isinstance(cr, str):
        cr_str = cr.strip()
    else:
        cr_str = str(cr)

    # Look up XP
    xp = CR_TO_XP.get(cr_str, 0)

    # Fallback for unknown CRs
    if xp == 0 and cr_str not in ["0", ""]:
        print(f"[PARLAY] Warning: Unknown CR '{cr_str}' for monster {monster.get('name')}")
        # Try converting to float and estimating
        try:
            if '/' in cr_str:
                num, denom = cr_str.split('/')
                cr_float = float(num) / float(denom)
            else:
                cr_float = float(cr_str)

            # Estimate XP if not in table
            if cr_float < 1:
                xp = int(25 * cr_float)
            else:
                xp = int(200 * (cr_float ** 1.5))
        except:
            xp = 10  # Minimum fallback

    return xp

def _get_most_powerful_monster(self, monsters: List[Dict]) -> Dict:
    """
    Get most powerful monster by CR-based XP.

    Args:
        monsters: List of monster dicts

    Returns:
        Most powerful monster, or first if all have CR 0
    """
    if not monsters:
        return None

    # Calculate XP for each monster
    monsters_with_xp = [(m, self._get_monster_xp(m)) for m in monsters]

    # Return monster with highest XP
    return max(monsters_with_xp, key=lambda t: t[1])[0]
```

**Files to Update**:
1. `get_parlay_skills_for_encounter()` - use `_get_most_powerful_monster()`
2. `calculate_parlay_xp_reward()` - use `_get_monster_xp()`
3. `execute_pickpocket_attempt()` - use `_get_most_powerful_monster()`

---

### ⚠️ BLOCKER #2: No Gold Column in Characters Table

**Discovery**: `characters` table has no `gold` column

**Impact**: Pickpocket gold award will fail

**Solution Options**:

**Option A: Add Gold Column** (Recommended)
```sql
-- Migration: XXX_add_gold_to_characters.sql
ALTER TABLE characters ADD COLUMN gold INTEGER DEFAULT 0;
```

**Option B: Use Existing System**
Check if gold is tracked differently - search for currency/wealth tables:
```bash
sqlite3 talekeeper.db ".schema" | grep -i "gold\|currency\|wealth"
```

**Recommendation**: Since pickpocket now awards **treasure items** instead of gold, this is less critical. Can defer gold column until later.

---

### ⚠️ BLOCKER #3: No _refresh_action_cards Method

**Discovery**: `action_panel.py` only has `_refresh_spell_action_cards()`, not generic refresh

**Impact**: Pickpocket card won't appear automatically

**Solution**: Action panel likely rebuilds cards periodically. Find the main card generation method:

```python
# Search for where action cards are initially created
# Likely something like:
def _create_action_cards(self):
    """Create all available action cards."""
    cards = []

    # ... existing cards ...

    # Add pickpocket card if available
    pickpocket_card = self._check_for_pickpocket_card()
    if pickpocket_card:
        cards.append(pickpocket_card)

    return cards
```

**Workaround**: Instead of calling `_refresh_action_cards()`, trigger card rebuild via parent signal:
```python
# In encounter_panel.py after setting _parlay_monsters:
if hasattr(self.parent(), 'action_panel'):
    self.parent().action_panel._create_action_cards()  # Force rebuild
```

---

### ✅ FOUND: Stealth Success Handler Location

**Location**: `encounter_panel.py` lines 4739-4753

**Code**:
```python
self.player_hidden = stealth_result['hidden']
if self.player_hidden:
    # Log detailed stealth success
    stealth_text = f"\n\n[HIDDEN] You remain undetected. You can make a surprise attack or flee."
```

**Integration Point**:
```python
# ADD after line 4753:
if self.player_hidden and self.encounter_instances:
    # Store monsters for pickpocket opportunity
    self._stealth_monsters = [inst.to_dict() for inst in self.encounter_instances.values()]

    # Check if character can pickpocket
    self._check_pickpocket_opportunity()
```

---

## Updated Implementation with Fixes

### File: `src/talekeeper/services/parlay_system.py`

**ADD** at top of class (after `__init__`):

```python
# CR to XP conversion table (D&D 2024)
CR_TO_XP = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100,
    "5": 1800, "6": 2300, "7": 2900, "8": 3900,
    "9": 5000, "10": 5900, "11": 7200, "12": 8400,
    "13": 10000, "14": 11500, "15": 13000, "16": 15000,
    "17": 18000, "18": 20000, "19": 22000, "20": 25000,
    "21": 33000, "22": 41000, "23": 50000, "24": 62000,
    "25": 75000, "26": 90000, "27": 105000, "28": 120000,
    "29": 135000, "30": 155000
}

def _get_monster_xp(self, monster: Dict) -> int:
    """Get monster XP from CR (experience_points field is always 0)."""
    cr = monster.get('challenge_rating', '0')
    cr_str = str(cr).strip() if cr else '0'

    xp = self.CR_TO_XP.get(cr_str, 0)

    if xp == 0 and cr_str not in ["0", "", None]:
        # Estimate for unknown CRs
        try:
            if '/' in cr_str:
                num, denom = cr_str.split('/')
                cr_float = float(num) / float(denom)
            else:
                cr_float = float(cr_str)

            xp = int(200 * (cr_float ** 1.5)) if cr_float >= 1 else int(25 * cr_float)
        except:
            xp = 10

    return max(10, xp)  # Minimum 10 XP

def _get_most_powerful_monster(self, monsters: List[Dict]) -> Dict:
    """Get most powerful monster by CR-based XP."""
    if not monsters:
        return None

    monsters_with_xp = [(m, self._get_monster_xp(m)) for m in monsters]
    return max(monsters_with_xp, key=lambda t: t[1])[0]
```

**UPDATE** `get_parlay_skills_for_encounter()`:

```python
def get_parlay_skills_for_encounter(self, monsters: List[Dict]) -> Tuple[List[str], str]:
    if not monsters:
        return [], 'none'

    # Use CR-based selection (NOT experience_points which is always 0)
    primary_monster = self._get_most_powerful_monster(monsters)
    if not primary_monster:
        return [], 'none'

    # ... rest of method unchanged ...
```

**UPDATE** `calculate_parlay_xp_reward()`:

```python
def calculate_parlay_xp_reward(self, monsters: List[Dict]) -> int:
    """Calculate XP reward for successful parlay (50% of strongest monster)."""
    if not monsters:
        return 0

    # Use CR-based XP
    primary_monster = self._get_most_powerful_monster(monsters)
    if not primary_monster:
        return 0

    max_xp = self._get_monster_xp(primary_monster)
    return max_xp // 2
```

---

## Revised Testing Strategy

### Test Data Setup

**Create test monsters with known CRs**:
```python
test_monsters = [
    {
        'name': 'Goblin',
        'challenge_rating': '1/4',
        'experience_points': 0,  # This is reality
        'intelligence': 10,
        'wisdom': 8,
        'alignment': 'Neutral Evil'
    },
    {
        'name': 'Aboleth',
        'challenge_rating': '10',
        'experience_points': 0,  # This is reality
        'intelligence': 18,
        'wisdom': 15,
        'alignment': 'Lawful Evil',
        'skills': '{"history": "+12", "perception": "+10"}'
    }
]

# Expected XP calculations:
# Goblin CR 1/4 = 50 XP -> Parlay reward = 25 XP
# Aboleth CR 10 = 5900 XP -> Parlay reward = 2950 XP
```

### Unit Tests

```python
def test_monster_xp_from_cr():
    """Test CR to XP conversion."""
    parlay = ParlaySystem()

    goblin = {'challenge_rating': '1/4'}
    assert parlay._get_monster_xp(goblin) == 50

    aboleth = {'challenge_rating': '10'}
    assert parlay._get_monster_xp(aboleth) == 5900

    # Test fractional CRs
    assert parlay._get_monster_xp({'challenge_rating': '1/8'}) == 25
    assert parlay._get_monster_xp({'challenge_rating': '1/2'}) == 100

    # Test edge cases
    assert parlay._get_monster_xp({'challenge_rating': '0'}) == 10
    assert parlay._get_monster_xp({'challenge_rating': None}) == 10
    assert parlay._get_monster_xp({}) == 10

def test_most_powerful_monster_selection():
    """Test selection uses CR, not broken experience_points."""
    parlay = ParlaySystem()

    monsters = [
        {'name': 'Goblin', 'challenge_rating': '1/4', 'experience_points': 0},
        {'name': 'Aboleth', 'challenge_rating': '10', 'experience_points': 0},
        {'name': 'Kobold', 'challenge_rating': '1/8', 'experience_points': 0}
    ]

    powerful = parlay._get_most_powerful_monster(monsters)
    assert powerful['name'] == 'Aboleth'
```

---

## Revised Implementation Checklist

### Pre-Implementation
- [x] Discovered XP values are all 0
- [x] Located stealth success handler (line 4739)
- [x] Confirmed no `_refresh_action_cards` method
- [x] Confirmed no gold column (but not needed for treasure system)
- [ ] Create CR-to-XP conversion function
- [ ] Test XP calculation with real monster data

### Phase 1: Core Parlay (WITH FIXES)
- [ ] Add `_get_monster_xp()` helper
- [ ] Add `_get_most_powerful_monster()` helper
- [ ] Add `_determine_if_evil()` helper
- [ ] Add 4 skill selection helpers
- [ ] Update `calculate_parlay_xp_reward()` to use CR
- [ ] Test XP calculations

### Phase 2: Integration
- [ ] Update `get_parlay_skills_for_encounter()` to use CR
- [ ] Add metadata storage for disadvantage mode
- [ ] Update `create_parlay_challenge()`
- [ ] Add disadvantage mode to SkillChallengeManager
- [ ] Test parlay flow

### Phase 3: UI Integration
- [ ] Wire Influence button
- [ ] Add parlay handlers
- [ ] Add pickpocket check to stealth (line 4753)
- [ ] Find action card refresh mechanism
- [ ] Test end-to-end

---

## Summary of Critical Changes

| Original Design | Reality | Fix Required |
|----------------|---------|--------------|
| Use `experience_points` field | Field is always 0 | Use CR-to-XP conversion |
| Call `_refresh_action_cards()` | Method doesn't exist | Find actual refresh mechanism |
| Award gold to `characters.gold` | Column doesn't exist | Use treasure system instead |
| Assume stealth handler | Unknown location | Found at line 4739 ✅ |

**Bottom Line**: Original implementation would have **completely failed** due to XP values being 0. This audit saved significant debugging time.
