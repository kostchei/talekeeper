# Parlay System Implementation - Pre-Implementation Audit

## Critical Issues to Address Before Coding

### 1. Monster Data Validation

**Issue**: `max()` on `experience_points` will fail if any monster lacks that field.

**Location**: All helpers that select "most powerful monster"

**Fix Required**:
```python
# BEFORE (unsafe):
primary_monster = max(monsters, key=lambda m: m.get('experience_points', 0))

# AFTER (safe with fallback):
primary_monster = max(
    monsters,
    key=lambda m: m.get('experience_points', 0) if m.get('experience_points') else 0
)

# OR better - explicit handling:
def _get_most_powerful_monster(monsters: List[Dict]) -> Dict:
    """Get most powerful monster by XP, with fallback to first if no XP data."""
    if not monsters:
        return None

    monsters_with_xp = [m for m in monsters if m.get('experience_points')]

    if monsters_with_xp:
        return max(monsters_with_xp, key=lambda m: m['experience_points'])

    # Fallback: use first monster if none have XP
    return monsters[0]
```

**Files Affected**:
- `parlay_system.py`: `get_parlay_skills_for_encounter()`
- `parlay_system.py`: `calculate_parlay_xp_reward()`
- `parlay_system.py`: `execute_pickpocket_attempt()`

---

### 2. Disadvantage Mode String Handling

**Issue**: Current skill challenge system may expect boolean `has_disadvantage`, not string mode.

**Current Code** (skill_challenge_manager.py line 262-264):
```python
# Roll d20
roll_result = random.randint(1, 20)
total_result = roll_result + ability_modifier + proficiency_bonus
```

**Needs to Support**:
- `'none'` - no disadvantage
- `'first'` - first skill check only
- `'all'` - all skill checks

**Validation Required**:
1. Check if `SkillChallengeManager.attempt_skill()` can handle string modes
2. Verify skill usage tracking to determine "first check"
3. Test that metadata table stores/retrieves mode correctly

**Integration Point**:
```python
# Need to track which skills have been attempted
# "first" mode should apply to the FIRST skill used, not first attempt of each skill

# Current tracking in session.skill_usage:
# {"Persuasion": 1, "Deception": 0, "Insight": 2}

# For "first" mode, need to check:
# sum(session.skill_usage.values()) == 0  # Is this the first attempt overall?
```

---

### 3. Missing Attributes & Methods

**Issue**: Implementation assumes several attributes/methods exist without verification.

**Encounter Panel Assumptions**:
- `_parlay_monsters` attribute (created dynamically)
- `_stealth_monsters` attribute (created dynamically)
- `_restore_parlay_monsters_for_combat()` method (needs creation)
- `player_hidden` attribute (check if exists)

**Action Panel Assumptions**:
- `_refresh_action_cards()` method (verify exists)
- `_log_action()` method (verify exists)
- Access to parent `encounter_panel` (verify structure)

**Audit Required**:
```bash
# Check for existing methods/attributes
grep -n "_parlay_monsters" src/talekeeper/ui/encounter_pane/encounter_panel.py
grep -n "_refresh_action_cards" src/talekeeper/ui/action_cards/action_panel.py
grep -n "player_hidden" src/talekeeper/ui/encounter_pane/encounter_panel.py
```

---

### 4. Random Skill Selection Repeatability

**Issue**: Random skill selection makes debugging/testing harder.

**Current Design**:
```python
selected_cha = random.sample(cha_skills, 2)
```

**Considerations**:
- Should parlay skills be deterministic per monster type?
- Should we seed random for reproducible testing?
- Should we log selected skills for debugging?

**Recommendation**:
Add logging to track skill selection:
```python
def _get_intelligent_non_evil_skills(self) -> List[str]:
    """2 random CHA skills + 1 random INT/WIS skill."""
    cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
    int_wis_skills = [...]

    selected_cha = random.sample(cha_skills, 2)
    selected_int_wis = random.choice(int_wis_skills)

    skills = selected_cha + [selected_int_wis]

    # Log for debugging
    print(f"[PARLAY] Selected skills (Intelligent Non-Evil): {skills}")

    return skills
```

---

### 5. Database Migration Dependencies

**Issue**: Code assumes metadata table exists before first use.

**Migration Required**:
```sql
-- Must run BEFORE first parlay attempt
CREATE TABLE IF NOT EXISTS skill_challenge_metadata (
    template_id TEXT NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    PRIMARY KEY (template_id, metadata_key),
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_challenge_metadata_template
ON skill_challenge_metadata(template_id);
```

**Validation Required**:
- Check if table creation is automatic or requires manual migration
- Verify foreign key constraints work correctly
- Test that metadata persists across sessions

---

### 6. Stealth Integration Point

**Issue**: Documentation shows `_on_stealth_success()` but this method may not exist.

**Current Stealth Flow** (encounter_panel.py around line 4750):
```python
# Likely looks like this:
if stealth_total >= stealth_dc:
    stealth_text = f"\n\n[HIDDEN] You remain undetected..."
    # ... set player_hidden flag
    # ... create flee button
```

**Need to Find**:
1. Where stealth success is handled
2. Where to insert pickpocket opportunity check
3. How monsters are stored during stealth

**Search Required**:
```bash
grep -n "HIDDEN\|stealth.*success\|player_hidden.*True" src/talekeeper/ui/encounter_pane/encounter_panel.py
```

---

### 7. Alignment Parsing Edge Cases

**Issue**: Alignment field may have unexpected formats.

**Known Formats**:
- `"Neutral Good"`
- `"Lawful Evil"`
- `"any"`
- `"unaligned"`
- `""`
- `None`

**Edge Cases to Handle**:
```python
def _determine_if_evil(self, alignment: str) -> bool:
    """Determine if creature is evil."""
    if not alignment:
        return False  # null/empty = not evil

    alignment_lower = alignment.strip().lower()

    # Handle "any" - 1/3 chance evil
    if alignment_lower == "any":
        return random.random() < 0.33

    # Handle "unaligned" - not evil
    if alignment_lower == "unaligned":
        return False

    # Handle "neutral" without good/evil qualifier
    if alignment_lower == "neutral":
        return False  # True neutral = not evil

    # Check for evil keyword
    return 'evil' in alignment_lower
```

**Test Cases Needed**:
- "any" alignment (multiple rolls to verify 1/3 chance)
- "unaligned" (should be non-evil)
- "neutral" vs "Neutral Evil"
- Empty/null alignment

---

### 8. Gold Column Existence

**Issue**: Code assumes `characters` table has `gold` column.

**Check Required**:
```bash
sqlite3 talekeeper.db ".schema characters" | grep gold
```

**If Missing**:
```sql
ALTER TABLE characters ADD COLUMN gold INTEGER DEFAULT 0;
```

**Alternative**: Check if gold is tracked differently (e.g., in inventory)

---

### 9. Pickpocket Action Card Refresh Timing

**Issue**: When should pickpocket card appear/disappear?

**Questions**:
1. Does action panel auto-refresh when `_parlay_monsters` is set?
2. Do we need to trigger a signal/event?
3. What happens if player changes zones with pickpocket available?

**Recommended Flow**:
```python
# After successful parlay:
self._parlay_monsters = monsters
self._check_pickpocket_opportunity()

# Inside _check_pickpocket_opportunity:
if can_pickpocket:
    # Signal to action panel to refresh
    self.pickpocket_available.emit(True)  # Add this signal if needed

# Or simpler - action panel polls in _create_action_cards:
def _create_action_cards(self):
    cards = []
    # ... existing cards ...

    # Check for pickpocket
    pickpocket_card = self._check_for_pickpocket_card()
    if pickpocket_card:
        cards.append(pickpocket_card)

    return cards
```

---

## Pre-Implementation Checklist

### Database Audit
- [ ] Verify all monsters have `experience_points` field (or add fallback)
- [ ] Check if `gold` column exists in `characters` table
- [ ] Verify `character_proficiencies` table structure
- [ ] Check `skills` field in monsters (JSON format consistency)

### Code Audit
- [ ] Find actual stealth success handler location
- [ ] Verify `_refresh_action_cards()` method exists in action panel
- [ ] Check if `player_hidden` attribute exists in encounter panel
- [ ] Verify signal/slot connections for action card refresh

### Integration Points
- [ ] Test AdvantageSystem can handle 'first' and 'all' modes
- [ ] Verify skill usage tracking in SkillChallengeManager
- [ ] Check metadata table read/write in skill challenge
- [ ] Test monster data parsing (alignment, intelligence, skills)

### Testing Infrastructure
- [ ] Create test monsters with various alignment values
- [ ] Create test character with/without proficiencies
- [ ] Set up test scenario for "first" disadvantage mode
- [ ] Set up test scenario for "all" disadvantage mode

---

## Recommended Implementation Order

### Phase 0: Validation (Before Coding)
1. Run database checks
2. Audit existing code for assumed methods
3. Create database migration script
4. Write unit tests for new helper methods

### Phase 1: Core Parlay (Safe Changes)
1. Add `_determine_if_evil()` helper (isolated)
2. Add 4 skill selection helpers (isolated)
3. Add monster stat helpers (isolated)
4. Test each helper independently

### Phase 2: Integration (Risky Changes)
1. Update `create_parlay_challenge()` to use new helpers
2. Add metadata storage for disadvantage mode
3. Update `SkillChallengeManager.attempt_skill()` for disadvantage
4. Test parlay flow end-to-end

### Phase 3: UI Wiring
1. Connect Influence button
2. Add parlay handlers to encounter panel
3. Update skill widget display
4. Test UI integration

### Phase 4: Pickpocket
1. Add pickpocket eligibility check
2. Add dual skill check logic
3. Create action card
4. Integrate with stealth
5. Test pickpocket flows

---

## Risk Assessment

### High Risk
1. **Disadvantage Mode Integration** - Requires changes to core skill challenge system
2. **Stealth Integration** - Unclear where to hook in
3. **Action Card Refresh** - May need new signal/slot connections

### Medium Risk
1. **Monster Data Quality** - Some monsters may lack required fields
2. **Random Skill Selection** - Makes debugging harder
3. **Database Migration** - Must run before any parlay attempts

### Low Risk
1. **Helper Methods** - Isolated, easy to test
2. **Alignment Parsing** - Simple logic
3. **Logging** - Non-critical enhancement

---

## Blockers & Unknowns

### Must Resolve Before Coding
1. **Stealth Integration Point**: Where exactly does stealth success happen?
2. **Action Card Refresh**: How to trigger card list update?
3. **Disadvantage Tracking**: How to track "first check" for 'first' mode?

### Can Resolve During Coding
1. Monster XP fallbacks
2. Gold column existence
3. Skill selection logging

---

## Success Criteria

### Minimal Viable Implementation
- [ ] Parlay works for all 4 categories
- [ ] Disadvantage applies correctly
- [ ] XP awards work
- [ ] Combat triggers on failure
- [ ] Basic pickpocket works (parlay only, skip stealth for MVP)

### Full Implementation
- [ ] All above, plus:
- [ ] Pickpocket from stealth
- [ ] Monster stat parsing handles all edge cases
- [ ] Comprehensive error handling
- [ ] Full test coverage

---

## Next Steps

1. **Run Validation Scripts**:
```bash
# Check monster XP coverage
sqlite3 talekeeper.db "SELECT COUNT(*) FROM monsters WHERE experience_points IS NULL"

# Check for gold column
sqlite3 talekeeper.db ".schema characters" | grep gold

# Find stealth success handler
grep -n "HIDDEN\|player_hidden.*=.*True" src/talekeeper/ui/encounter_pane/encounter_panel.py
```

2. **Create Test Monster Set**:
```sql
-- Create test monsters covering all 4 parlay categories
SELECT name, intelligence, alignment, experience_points
FROM monsters
WHERE
  (intelligence >= 4 AND alignment NOT LIKE '%evil%') OR  -- Intelligent non-evil
  (intelligence >= 4 AND alignment LIKE '%evil%') OR      -- Intelligent evil
  (intelligence <= 3 AND alignment NOT LIKE '%evil%') OR  -- Simple non-evil
  (intelligence <= 3 AND alignment LIKE '%evil%')         -- Simple evil
LIMIT 10;
```

3. **Audit Encounter Panel**:
```bash
# Find all methods we're assuming exist
grep -n "def _.*parlay\|def _.*stealth\|player_hidden" src/talekeeper/ui/encounter_pane/encounter_panel.py
```

4. **Create Implementation Branch**:
```bash
git checkout -b feature/parlay-system-enhanced
```

---

## Documentation Corrections Needed

### Minor Text Issues
- Character encoding is clean (≤ renders correctly)
- No mojibake detected in current version

### Technical Clarifications Needed
1. Specify exact line numbers for code insertion (may have drifted)
2. Add error handling examples for all database operations
3. Include rollback strategy if implementation fails mid-way

---

## Open Questions for User

1. **Gold Column**: Is gold tracked in `characters` table or somewhere else?
2. **Stealth Flow**: Can you confirm where stealth success is handled in encounter_panel.py?
3. **Action Card Refresh**: How should action panel know to refresh cards?
4. **MVP Scope**: Should first implementation include stealth pickpocket, or just parlay?
