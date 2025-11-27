# Warlock Improvement Log

## Character Blueprint (Level 1)

- **Template & Patron**: Base build on `templates/warlock_fiend.json` (Fiend patron) so automation stays aligned with the class matrix (`tests/fixtures/class_feature_matrix.yaml:374`).
- **Level & XP**: Level 1 shell loaded with **355,000 XP**, the total needed to reach level 20 using the Character Advancement table (`docs/SRD_CC_v5.2.1.md:2235-2254`).
- **Wealth on Hand**: Use Starting Equipment Option **B** (100 GP) plus the level 17-20 reserve of **20,000 GP + 1d10 * 250 GP** so the character can afford every level-up purchase allowed by the SRD (`docs/SRD_CC_v5.2.1.md:2367-2399`, `docs/SRD_CC_v5.2.1.md:6198-6203`). Record 22,500 GP to cover the maximum die roll and keep fixtures deterministic.
- **Ability Scores**: `STR 8 (-1), DEX 14 (+2), CON 13 (+1), INT 12 (+1), WIS 10 (+0), CHA 15 (+2)` based on the Warlock row in the Standard Array by Class table (`docs/SRD_CC_v5.2.1.md:2040-2050`).
- **Hit Points & Dice**: 9 HP (d8 + CON +1) and a 1d8 Hit Die from the Core Warlock Traits table (`docs/SRD_CC_v5.2.1.md:6188-6196`).
- **Saving Throws & Training**: Wisdom and Charisma saving throws; light armor, simple weapons, and arcane focus proficiency (`docs/SRD_CC_v5.2.1.md:6188-6196`).
- **Skills**: Arcana and Deception (both listed among the class options at `docs/SRD_CC_v5.2.1.md:6188-6194`).
- **Equipment**: Leather armor, sickle, two daggers, arcane focus (orb), occult lore book, and scholar's pack from Option A, while the Option B gold sits in the ledger for later automation checks (`docs/SRD_CC_v5.2.1.md:6198-6203`).

### Spellcasting & Feature Picks

- **Cantrips**: Eldritch Blast and Prestidigitation as recommended for Pact Magic (`docs/SRD_CC_v5.2.1.md:6251-6258`).
- **Prepared Spells**: Charm Person and Hex to match the SRD guidance (`docs/SRD_CC_v5.2.1.md:6265-6286`).
- **Spell Slots**: One Pact Magic slot at level 1 (`docs/SRD_CC_v5.2.1.md:6294-6306`).
- **Invocation**: Armor of Shadows has no prerequisite, keeps AC stable, and is defined at `docs/SRD_CC_v5.2.1.md:6386-6390`.
- **Subclass Hooks**: Stay on Fiend features once level 3 unlocks per the matrix and the Fiend patron section (`docs/SRD_CC_v5.2.1.md:6701-6724`).

## XP & Wealth Buffer for Level 20

- **Experience Roadmap**: Preload XP milestones at every level break (300 through 305,000 XP) so QA can march the character through TaleKeeper without editing fixtures mid-run; 355,000 XP guarantees Eldritch Master is unlockable when services exist (`docs/SRD_CC_v5.2.1.md:2235-2254`).
- **Gold Reserve**: The "Starting Equipment at Higher Levels" table gives level 17-20 characters 20,000 GP plus 1d10 * 250 GP along with their normal starting gear. Keeping the entire 22,500 GP worst-case fund on the character ensures we never block a level-up that expects downtime purchases (`docs/SRD_CC_v5.2.1.md:2367-2399`).
- **Ledger Suggestion**: Store three fields in the DB/template fixture: `starting_equipment_gp` (100), `progression_fund_gp` (20,000), and `swing_fund_gp` (2,500). Tests can then assert exact gold totals even if the UI introduces the die roll later.

## Implementation Updates

- **Template Sync**: `templates/warlock_fiend.json` now mirrors the blueprint--standard array ability scores, Arcana/Deception skills, Charm Person + Hex prep, and a `wealth_ledger` stocked with 355,000 XP and 22,500 GP so backend/UI tests can jump from level 1 to 20 without editing fixtures (`templates/warlock_fiend.json:1-49`).
- **Matrix Coverage**: `tests/fixtures/class_feature_matrix.yaml` includes new feature rows for Magical Cunning, Contact Patron, Mystic Arcanum tiers (6th/7th/8th/9th), Epic Boon, and Eldritch Master, each pointing at the backend tests that already exercise those mechanics (`tests/fixtures/class_feature_matrix.yaml:374-470`).

## Immediate Ability Coverage Check

- Backend traceability now exists for every SRD feature the Warlock gains from level 1-20, but each `verification.ui` stanza is still marked `planned`, so nothing in the Qt automation suite ensures Pact slots, Invocations, Pacts, Patrons, Magical Cunning, Mystic Arcanum, Contact Patron, Epic Boon, or Eldritch Master controls render and behave correctly.
- `tests/README_PROGRESSION_TESTING.md:226-236` still reports Fighter as the only class under progression testing; Warlock fixtures remain "planned," so no automated level-ups cover the new matrix data yet.
- `docs/latest_work.md` continues to call out the need to generalize the fighter progression harness and populate class fixtures, which is where the Warlock ASI/invocation/spell scripts will come from.

## Issues Needing Fixes

1. **UI Automation Blind Spots** - Populate the Warlock `verification.ui.tests` entries once `tests/testing_framework_ui_automation.py` is parameterized; today there is no UI validation for Pact Magic, Invocations, Pact Boons, Fiend features, Magical Cunning, Mystic Arcanum, Contact Patron, Epic Boon, or Eldritch Master.
2. **Progression Fixture Missing** - Author a Warlock choice fixture (mirroring `fighter_champion_choices.yaml`) so the generalized progression harness knows which ASIs, invocations, spells, and Mystic Arcanum picks to take when leveling.
3. **Service/Creator Support** - Implement the `WarlockService.update_*` handlers referenced by the matrix (Magical Cunning, Contact Patron, Mystic Arcanum tiers, Eldritch Master) and teach `ProgrammaticCharacterCreator`/`UnifiedLevelUpService` to respect the new `wealth_ledger` fields so the template's XP/GP data flows end-to-end.
