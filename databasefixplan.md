# Database Fix Plan for Character Creation

## Character Creation Process Analysis

The character creation process should follow these steps:

### 1. API Call Flow
1. **Frontend**: User fills out character creation form
2. **Frontend**: Calls `POST /api/character/create` with character data
3. **Backend**: Character router receives request
4. **Backend**: CharacterService.create_character() processes the request
5. **Backend**: Returns created character data to frontend

### 2. Database Operations Required

#### Step 1: Validate Input Data
- Verify race_id exists in races table
- Verify class_id exists in classes table  
- Verify background_id exists in backgrounds table

#### Step 2: Create Character Record
- Insert into characters table with:
  - Basic info (name, race_id, class_id, background_id)
  - Ability scores (strength, dexterity, constitution, intelligence, wisdom, charisma)
  - Calculated stats (HP, AC, proficiency bonus, etc.)
  - Default values for other fields

#### Step 3: Create Game State Record
- Insert into game_states table with:
  - character_id reference
  - Default game state values
  - Initial location, gold, etc.

#### Step 4: Add Starting Equipment
- Query starting equipment from class and background
- Parse equipment lists
- Insert items into character_inventory table
- Mark appropriate items as equipped

### 3. Current Issues Identified

#### Issue 1: Missing Database Columns
The SQLAlchemy models expect columns that don't exist in the database schema:

**Items table missing columns:**
- range_normal (for ranged weapons)
- range_long (for ranged weapons)
- attunement_required (different from just attunement boolean)
- Other weapon/armor specific fields

#### Issue 2: Schema Mismatch
The database schema in init.sql doesn't match the SQLAlchemy models exactly.

#### Issue 3: Equipment Processing
The starting equipment processing is failing due to missing item attributes.

### 4. Fix Strategy

#### Phase 1: Complete Schema Alignment
1. Review all SQLAlchemy models
2. Ensure database schema matches exactly
3. Add all missing columns

#### Phase 2: Simplify Equipment Processing
1. Make equipment addition more robust
2. Handle missing item attributes gracefully
3. Add proper error handling

#### Phase 3: Test Complete Flow
1. Test character creation end-to-end
2. Verify all database insertions work
3. Test with different race/class/background combinations

### 5. Required Schema Updates

#### Items Table Additions Needed:
```sql
-- Weapon range properties
range_normal INTEGER,
range_long INTEGER,

-- Attunement properties  
attunement_required BOOLEAN DEFAULT FALSE,

-- Additional weapon properties
versatile_damage VARCHAR(20),
thrown_range_normal INTEGER,
thrown_range_long INTEGER,

-- Additional armor properties
don_time VARCHAR(20),
doff_time VARCHAR(20)
```

#### Character Table Additions Needed:
```sql
-- Spell casting (if missing)
spell_attack_bonus INTEGER,
spell_save_dc INTEGER,
prepared_spells_count INTEGER,

-- Additional proficiencies (if missing)
languages_known VARCHAR[],
expertise_skills VARCHAR[]
```

### 6. Testing Checklist

After implementing fixes:

- [ ] Create Human Fighter with Farmer background
- [ ] Create Human Rogue with Soldier background  
- [ ] Create Dwarf Fighter with Farmer background
- [ ] Create Dwarf Rogue with Soldier background
- [ ] Verify character appears in database
- [ ] Verify game_state created
- [ ] Verify starting equipment added
- [ ] Verify all calculated stats correct
- [ ] Test character update operations
- [ ] Test character deletion

### 7. Rollback Plan

If fixes cause issues:
1. Revert to minimal schema
2. Remove equipment processing temporarily
3. Focus on core character creation only
4. Add equipment system incrementally

## Next Steps

1. Implement schema updates
2. Test each change incrementally
3. Document any remaining issues
4. Provide working character creation system