# Hybrid Database Pattern Documentation

**For Future Reference - TaleKeeper Desktop Database Architecture**

## The Problem We Solved

### DetachedInstanceError Hell 🔥
Previously, TaleKeeper suffered from frequent `DetachedInstanceError` exceptions when accessing SQLAlchemy objects outside their database sessions. This happened because:

1. **Session Management**: Objects were created in database sessions, then accessed later
2. **Lazy Loading**: Relationships like `character.race.name` were loaded on-demand
3. **UI Threading**: Tkinter UI accessed objects from different thread contexts
4. **Hacky Workarounds**: Used manual `_ = character.race.name` to force loading

### The Old Hacky Approach ❌
```python
# BAD: Forcing attribute loading with dummy assignments
_ = character.race.name if character.race else None  
_ = character.character_class.name if character.character_class else None
```

## The Solution: Hybrid DTO + Eager Loading Pattern ✅

### Architecture Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI/Business   │◄───│   Game Engine    │◄───│   Database      │
│   Logic (DTOs)  │    │   (Conversion)   │    │   (SQLAlchemy)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
    Plain Data              Hybrid Logic            ORM Objects
    No Sessions           DTOs + selectinload      Sessions Required
```

### Core Principles

#### 1. **Data Transfer Objects (DTOs)**
- **Location**: `core/dtos.py`
- **Purpose**: Plain Python dataclasses with no database dependencies
- **Usage**: All UI and business logic works with DTOs
- **Benefits**: No DetachedInstanceError possible, serializable, fast access

```python
@dataclass
class CharacterDTO:
    id: str
    name: str
    race_name: str  # Pre-resolved, no lazy loading
    class_name: str
    # ... all needed attributes
```

#### 2. **Eager Loading with selectinload()**
- **Purpose**: Load all needed relationships in single query
- **Method**: SQLAlchemy's `selectinload()` for separate SELECT queries
- **Alternative**: `joinedload()` for JOIN-based loading (use for 1:1 relationships)

```python
character = db.query(Character).options(
    selectinload(Character.race),
    selectinload(Character.character_class),
    selectinload(Character.subclass),
    selectinload(Character.background),
    selectinload(Character.save_slot)
).filter_by(id=character_id).first()
```

#### 3. **Immediate DTO Conversion**
- **Timing**: Convert to DTO within the database session
- **Location**: GameEngine conversion methods (`_character_to_dto()`, etc.)
- **Result**: Return DTOs from all public methods

```python
def load_character(self, save_slot: int) -> Optional[CharacterDTO]:
    with DatabaseSession() as db:
        # Eager load relationships
        character = db.query(Character).options(...).first()
        
        # Convert to DTO immediately (within session)
        character_dto = self._character_to_dto(character)
        
        # Return DTO - no session dependencies!
        return character_dto
```

## Implementation Details

### File Structure
```
core/
├── dtos.py              # All DTO definitions
├── game_engine.py       # Hybrid conversion logic
└── database.py          # Pure SQLAlchemy setup

models/
├── character.py         # SQLAlchemy models only
├── monsters.py          
└── ...
```

### Public API Changes
**All GameEngine methods now return DTOs:**

```python
# OLD: Returned SQLAlchemy objects (DetachedInstanceError prone)
def load_character(self, save_slot: int) -> Optional[Character]:

# NEW: Returns DTOs (safe for UI usage)
def load_character(self, save_slot: int) -> Optional[CharacterDTO]:

# Applied to all methods:
get_available_races() -> List[RaceDTO]
get_available_classes() -> List[ClassDTO] 
get_monsters_by_cr() -> List[MonsterDTO]
create_new_character() -> CharacterDTO
```

### Conversion Methods Pattern
**Every entity has a `_entity_to_dto()` method:**

```python
def _character_to_dto(self, character: Character) -> CharacterDTO:
    """
    Convert SQLAlchemy Character to CharacterDTO.
    Assumes relationships are eagerly loaded.
    """
    return CharacterDTO(
        id=character.id,
        name=character.name,
        race_name=character.race.name if character.race else "Unknown",
        # ... all attributes
    )
```

## When to Use Each Approach

### 1. selectinload() - DEFAULT CHOICE ✅
**Best for**: Most relationships, separate efficient queries
```python
selectinload(Character.race)  # Separate SELECT for races
```

### 2. joinedload() - Use Sparingly
**Best for**: Required 1:1 relationships, single query needed
```python
joinedload(Character.save_slot)  # JOIN with save_slots table
```

### 3. DTOs - ALWAYS for Public APIs ✅
**Best for**: All UI interactions, business logic, serialization
```python
# UI works with DTOs only
character_name = character_dto.name  # No session needed!
```

### 4. merge() - Use for Updates Only
**Best for**: Updating existing objects, on-demand operations
```python
def update_character_hp(self, character_id: str, new_hp: int):
    with DatabaseSession() as db:
        character = db.query(Character).get(character_id)
        character.current_hit_points = new_hp
        db.commit()
        return self._character_to_dto(character)
```

## Scalability Benefits

### Database Growth (2 races → 200 races)
- ✅ **DTOs**: Same performance, just more data objects
- ✅ **selectinload()**: SQLAlchemy optimizes queries automatically  
- ✅ **UI Performance**: No lazy loading delays in UI thread

### Code Complexity Growth
- ✅ **Maintainable**: Clear separation between data layer and business logic
- ✅ **Type Safety**: Full TypeScript-like type hints with dataclasses
- ✅ **Testing**: Easy to mock DTOs vs SQLAlchemy objects

### Memory Usage
- ✅ **Efficient**: DTOs are plain objects, lighter than SQLAlchemy objects
- ✅ **Predictable**: No hidden lazy loading memory spikes
- ✅ **Cacheable**: DTOs can be cached, pickled, JSON serialized

## Migration Guide for Future Changes

### Adding New Relationships
1. **Add to DTO** in `core/dtos.py`
2. **Add selectinload()** to GameEngine query
3. **Add to conversion method** (`_entity_to_dto()`)
4. **Update any UI code** to use new DTO attribute

### Adding New Entities
1. **Create EntityDTO** in `core/dtos.py`
2. **Add _entity_to_dto()** method in GameEngine  
3. **Add public get_entities()** method returning `List[EntityDTO]`
4. **Use selectinload()** for any relationships

### Performance Tuning
1. **Measure first**: Use SQL logging (`echo=True`) to see actual queries
2. **Optimize queries**: Switch `selectinload` to `joinedload` if needed
3. **Add indexing**: Database indexes for frequently queried fields
4. **Cache DTOs**: Add caching layer if needed (DTOs are perfect for this)

## Error Prevention Checklist ✅

### Code Review Checklist
- [ ] All public GameEngine methods return DTOs, not SQLAlchemy objects
- [ ] All database queries use `selectinload()` for relationships  
- [ ] DTO conversion happens within database session
- [ ] No `_ = object.relationship.attribute` hacks
- [ ] UI code only works with DTOs
- [ ] New relationships added to both DTO and selectinload()

### Testing Checklist  
- [ ] Test character creation returns CharacterDTO
- [ ] Test character loading returns CharacterDTO
- [ ] Test all DTO attributes accessible without database
- [ ] Test UI works with DTOs in isolation
- [ ] Test relationship data is pre-loaded (not None)

## Example Usage in UI Code

### BEFORE (Prone to DetachedInstanceError)
```python
def display_character(character: Character):
    name = character.name  # OK
    race = character.race.name  # ❌ DetachedInstanceError possible!
```

### AFTER (Safe with DTOs)
```python
def display_character(character: CharacterDTO):
    name = character.name       # ✅ Always works
    race = character.race_name  # ✅ Pre-loaded, always works
```

---

## Quick Reference Commands

### Adding a New Relationship
```bash
# 1. Add to DTO
# 2. Add selectinload to query
# 3. Add to _entity_to_dto() method
```

### Debugging Query Performance
```python
# Enable SQL logging in database.py
engine = create_engine(DATABASE_URL, echo=True)
```

### Testing DTO Conversion
```python
# Ensure all attributes work without session
character_dto = game_engine.load_character(1)
assert character_dto.race_name != None  # Should be pre-loaded
```

**Remember**: DTOs solve DetachedInstanceError permanently by eliminating the problem entirely! 🎉