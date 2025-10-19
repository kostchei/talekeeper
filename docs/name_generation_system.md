# Name Generation System - TaleKeeper

## Overview
Based on the pleb repository's NPC name generation system and historic UK tavern naming conventions, this document defines the name generation system for settlements, inns/taverns, and local worthies (nobles/leaders).

## Existing System Analysis

### From pleb Repository
**Location**: d:\Code\pleb\nameGenerators\aquilonianNames.js

**Pattern**: Syllable-based + historic name lists
- 50% syllable combination (generated)
- 50% historic name list (curated)

**Syllable Structure**:
```
Male:   [Start] + [Mid?] + [End]  (2-3 syllables)
Female: [Start] + [Mid?] + [End]  (2-3 syllables)
```

**Example Names**:
- Arthurian: Lancelot, Gawain, Percival, Guinevere, Morgan, Isolde
- Generated: Arbelgon, Calgallon, Morgaldin, Anwen, Moralin

## Inn/Tavern Name System

### Historic UK Patterns (Pre-1700)

#### Pattern 1: The [Adjective] + [Noun]
Most common historic pattern for British pubs and inns.

**Adjectives** (20 entries):
- Red, White, Black, Golden, Silver, Blue, Green
- Royal, King's, Queen's, Crown
- Old, Ancient, New
- Jolly, Merry, Dancing, Singing
- Wise, Drunken

**Nouns - Animals** (30 entries):
- Lion, Hart, Stag, Boar, Bear, Bull, Eagle, Swan, Horse
- Dragon, Wyvern, Griffin, Unicorn (heraldic)
- Rat, Eel, Pig, Snake, Camel, Frog, Crow
- Hound, Fox, Hare, Badger, Otter

**Nouns - Objects** (30 entries):
- Crown, Bell, Anvil, Wheel, Axe, Hammer, Anchor
- Rose, Oak, Bush, Tree, Vine
- Tankard, Goblet, Barrel, Keg, Flagon
- Shield, Sword, Dagger, Blade, Lance
- Key, Lock, Gate, Door, Lantern
- Plough, Sickle, Mill

**Example Combinations**:
- The Red Lion
- The Golden Dragon
- The Silver Tankard
- The Jolly Boar
- The Dancing Wench (from tavern_generator.csv)
- The Wise Camel (from tavern_generator.csv)

#### Pattern 2: [Noun] & [Noun]
Two-part names with ampersand, common in medieval England.

**Examples**:
- Dog & Lantern (from tavern_generator.csv)
- Boar & Candle (from tavern_generator.csv)
- Cloak & Dragon (from tavern_generator.csv)
- Blade & Tankard (from tavern_generator.csv)
- Cup & Blade (from tavern_generator.csv)
- Frog & Bard (from tavern_generator.csv)
- Bell & Dragon
- Rose & Crown
- Harp & Crown
- Fox & Hounds

#### Pattern 3: The [Occupational/Location Name]
Named after profession or place feature.

**Examples**:
- The Smith's Arms
- The Miller's Rest
- The Shepherd's Crook
- The Sailor's Return
- The Traveler's Rest
- The Merchant's Hall
- The Cooper's Arms (cooper = barrel maker)
- The Fletcher's Lodge (fletcher = arrow maker)

#### Pattern 4: Possessive Names
Owner or saint's name.

**Examples**:
- St. George's Inn
- The Bishop's Rest
- The Friar's Lodge
- The Knight's Hall
- The Abbot's Table

### Complete Inn Name Lists

#### Expanded from tavern_generator.csv (40 entries)

**From CSV**:
1. The Crimson Rat
2. The Dancing Wench
3. The Dog & Lantern
4. The Rusty Eel
5. The Demon's Goblet
6. The Singing Trident
7. The Boar & Candle
8. The Silver Dagger
9. The Filthy Wheel
10. The Captain's Pig
11. The Jolly Snake
12. The Wise Camel
13. Cloak & Dragon
14. The Royal Axe
15. The Gilded Bell
16. The Blade & Tankard
17. The Drunken Shield
18. Cup & Blade
19. The Jeweled Anvil
20. The Frog & Bard

**Additional 40 Historic Names** (researched from UK pub history):

21. The Red Lion
22. The White Hart
23. The Royal Oak
24. The King's Head
25. The Queen's Arms
26. The Crown & Anchor
27. The George & Dragon
28. The Rose & Crown
29. The Golden Eagle
30. The Black Bull
31. The Green Man
32. The Swan & Cygnet
33. The Old Bell
34. The Angel & Crown
35. The Lamb & Flag
36. The Ship & Anchor
37. The Plough & Stars
38. The Three Barrels
39. The Copper Kettle
40. The Blue Door
41. The Hop Pole
42. The Barley Mow
43. The White Horse
44. The Saracen's Head
45. The Turk's Head
46. The Holly Bush
47. The Bull & Bush
48. The Crossed Keys
49. The Bell & Dragon
50. The Harp & Crown
51. The Fox & Hounds
52. The Stag & Hounds
53. The Coach & Horses
54. The Wheatsheaf
55. The Miller's Arms
56. The Smith's Forge
57. The Traveler's Rest
58. The Sailor's Return
59. The Merchant's Hall
60. The Cooper's Arms

**Total**: 60 unique inn names

### Generation Method for Inns

```python
def generate_inn_name(seed: int) -> str:
    """Generate inn/tavern name using seed-based randomization."""
    rng = random.Random(seed)

    # Choose pattern (60% curated list, 40% generated)
    if rng.random() < 0.6:
        # Use curated historic names
        return rng.choice(HISTORIC_INN_NAMES)
    else:
        # Generate new name
        pattern = rng.choice(["adjective_noun", "noun_and_noun", "possessive"])

        if pattern == "adjective_noun":
            adj = rng.choice(ADJECTIVES)
            noun = rng.choice(NOUNS_ALL)
            return f"The {adj} {noun}"

        elif pattern == "noun_and_noun":
            noun1 = rng.choice(NOUNS_ALL)
            noun2 = rng.choice(NOUNS_ALL)
            # Avoid same noun twice
            while noun2 == noun1:
                noun2 = rng.choice(NOUNS_ALL)
            return f"{noun1} & {noun2}"

        else:  # possessive
            owner = rng.choice(OCCUPATIONS)
            noun = rng.choice(["Arms", "Rest", "Lodge", "Hall", "Table"])
            return f"The {owner}'s {noun}"
```

## Worthy (Noble/Leader) Name System

### Purpose
Generate names for local lords, burghers, chiefs, headmen, and other settlement leaders.

### Medieval English Titles by Settlement Type

**Hamlet (1-200 people)**:
- Headman [Name]
- Goodman [Name]
- Yeoman [Name]
- Elder [Name]

**Village (200-2,000 people)**:
- Reeve [Name]
- Bailiff [Name]
- Alderman [Name]
- Burgher [Name]
- Squire [Name]
- Dame [Name] (female)

**Town (2,000+ people)**:
- Lord [Name]
- Lady [Name]
- Baron [Name]
- Baroness [Name]
- Chief [Name]
- Thane [Name]
- Master [Name]

### Name Generation Pattern

Based on pleb's Arthurian/syllable hybrid system:

**Male Names** (50 curated + syllable generation):

**Curated Anglo-Saxon/Norman Names**:
1. Aelric, Aldric, Alwin, Athelstan, Beorn
2. Brand, Cedric, Cynric, Dunstan, Eadric
3. Edgar, Edmund, Edwin, Godwin, Harold
4. Leofric, Osric, Oswald, Randulf, Roderic
5. Siward, Thorfinn, Thurstan, Ulfric, Wulfric
6. Geoffrey, Gilbert, Hugh, Ralph, Roger
7. Walter, William, Robert, Richard, Henry
8. Thomas, John, Peter, Simon, Matthew
9. Baldwin, Bertram, Conrad, Godfrey, Humphrey
10. Reynard, Theobald, Warin, Warner, Wymond

**Curated Celtic/Welsh Names**:
11. Cadoc, Caradoc, Cormac, Dafydd, Dylan
12. Gareth, Griffith, Gwion, Llywelyn, Morgan
13. Owen, Rhys, Taliesin, Tristan, Urien

**Female Names** (30 curated + syllable generation):

**Curated Anglo-Saxon/Norman Names**:
1. Aelgifu, Aldith, Edith, Elfleda, Godgifu
2. Gunnhild, Matilda, Maud, Sybil, Eadgyth
3. Eleanor, Isabella, Joanna, Katherine, Margaret
4. Alice, Beatrice, Cecily, Emma, Hawise
5. Joan, Juliana, Lucy, Mary, Philippa
6. Agnes, Avice, Constance, Dionisia, Ela

**Curated Celtic/Welsh Names**:
7. Angharad, Branwen, Ceridwen, Dwynwen, Elen
8. Gwendolyn, Gwenllian, Isolde, Morwenna, Rhiannon

**Syllable Generation** (when not using curated):
- Male Start: ["Ael", "Al", "Ed", "God", "Os", "Wulf", "Thur", "Ran", "Leof"]
- Male Mid: ["ric", "win", "stan", "mund", "wald", "bert", "fred"]
- Male End: ["son", "ton", "ham", "ford", "ley", "bury", "field"]
- Female Start: ["Ae", "Ed", "El", "Gunn", "Gwen", "Mor", "Ceri", "Bran"]
- Female Mid: ["gi", "flae", "hild", "wen", "wyn", "dwen"]
- Female End: ["da", "lyn", "wen", "eth", "ith", "lian"]

### Generation Method for Worthies

```python
def generate_worthy_name(settlement_type: str, seed: int) -> str:
    """Generate worthy (noble/leader) name with title."""
    rng = random.Random(seed)

    # Determine gender (70% male, 30% female for medieval accuracy)
    is_male = rng.random() < 0.7

    # Choose name (60% curated, 40% syllable-generated)
    if rng.random() < 0.6:
        if is_male:
            name = rng.choice(MALE_WORTHY_NAMES)
        else:
            name = rng.choice(FEMALE_WORTHY_NAMES)
    else:
        # Generate from syllables
        name = generate_syllable_name(is_male, rng)

    # Add title based on settlement type
    if settlement_type == 'hamlet':
        if is_male:
            title = rng.choice(["Headman", "Goodman", "Yeoman", "Elder"])
        else:
            title = rng.choice(["Goodwife", "Wise Woman", "Elder"])
        return f"{title} {name}"

    elif settlement_type == 'village':
        if is_male:
            title = rng.choice(["Reeve", "Bailiff", "Alderman", "Squire"])
        else:
            title = rng.choice(["Dame", "Goodwife", "Mistress"])
        return f"{title} {name}"

    else:  # town
        if is_male:
            title = rng.choice(["Lord", "Baron", "Chief", "Thane", "Master"])
        else:
            title = rng.choice(["Lady", "Baroness", "Mistress", "Dame"])
        return f"{title} {name}"
```

## Settlement Name System

### Naming Patterns by Settlement Type

#### Hamlet Names (1-200 people)
**Pattern**: [Owner/Feature]'s + [Geographic/Building]

**Owner Names**:
- Use worthy names without title (e.g., "Aelric", "Godwin", "Edith")

**Geographic/Building Terms**:
- Crossing, Ford, Bridge, Mill, Farm, Stead
- Hollow, Glen, Vale, Dell
- Croft, Garth, Thorp, Wick

**Examples**:
- Aelric's Crossing
- Godwin's Mill
- Edith's Ford
- Wulfric's Farm
- Matilda's Stead
- Harold's Hollow

#### Village Names (200-2,000 people)
**Pattern**: [Geographic Feature] + [Suffix]

**Geographic Prefixes**:
- High, Low, Deep, Broad, Long, Wide
- North, South, East, West
- Wood, Stone, Iron, Silver, Gold
- River, Brook, Lake, Mere, Marsh
- Hill, Ridge, Down, Peak, Tor
- Oak, Ash, Elm, Willow, Thorn

**Suffixes**:
- -ton (town), -ham (homestead), -bury (fortified place)
- -ford (river crossing), -bridge
- -ley/-leigh (clearing), -field
- -mere (lake), -marsh, -wood
- -ridge, -hill, -vale, -dale

**Examples**:
- Highridge, Deepwood, Stonebridge
- Oakton, Ashbury, Elmfield
- Riverford, Brookham, Lakemere
- Ironhill, Silvervale, Thornley
- Northmarsh, Eastdale, Westwood

#### Town Names (2,000+ people)
**Pattern**: [Major Feature] + [Suffix] OR [Historic Name]

**Major Features**:
- Castle, Fort, Keep, Tower, Wall
- Market, Gate, Port, Haven
- King, Queen, Prince, Duke
- Saint names (St. Cuthbert, St. Albans, etc.)

**Examples**:
- Castleton, Kingsgate, Queensport
- Fortbridge, Keephaven, Wallham
- Marketshire, Portfield, Gatebury
- St. Michael's Rest, St. Aelred's Keep

### Settlement Name Generation Method

```python
def generate_settlement_name(settlement_type: str, biome: str, seed: int) -> str:
    """Generate settlement name based on type and biome."""
    rng = random.Random(seed)

    if settlement_type == 'hamlet':
        # Owner's + Feature
        owner = rng.choice(PERSONAL_NAMES_SHORT)
        feature = rng.choice(HAMLET_FEATURES)
        return f"{owner}'s {feature}"

    elif settlement_type == 'village':
        # Geographic + Suffix
        prefix = rng.choice(VILLAGE_PREFIXES)
        suffix = rng.choice(VILLAGE_SUFFIXES)
        return f"{prefix}{suffix}"

    else:  # town
        # 50% historic pattern, 50% major feature
        if rng.random() < 0.5:
            feature = rng.choice(TOWN_FEATURES)
            suffix = rng.choice(TOWN_SUFFIXES)
            return f"{feature}{suffix}"
        else:
            # Use curated town names
            return rng.choice(HISTORIC_TOWN_NAMES)
```

## Integration with Long Rest System

### Settlement >= 500 Population
When settlement population >= 500, assign permanent name to hex:

```python
# In settlement_name_service.py
def get_or_create_settlement_name(character_id: str, q: int, r: int) -> Dict:
    """Get existing name or generate new one."""
    # Check database for existing name
    existing = db.get_settlement_name(character_id, q, r)
    if existing:
        return existing

    # Generate new names
    settlement_type = db.get_settlement_type(character_id, q, r)
    biome = db.get_biome(character_id, q, r)
    seed = db.get_encounter_seed(character_id, q, r)

    settlement_name = generate_settlement_name(settlement_type, biome, seed)

    # Only generate inn if Modest+ lifestyle available
    lifestyle = determine_highest_lifestyle(settlement_type)
    if lifestyle in ['modest', 'comfortable', 'wealthy']:
        inn_name = generate_inn_name(seed + 1)
    else:
        inn_name = None

    # Generate worthy if village or larger
    if settlement_type in ['village', 'town_small', 'town_medium', 'town_large']:
        worthy_name = generate_worthy_name(settlement_type, seed + 2)
    else:
        worthy_name = None

    # Store in database
    db.save_settlement_names(character_id, q, r, settlement_name, inn_name, worthy_name)

    return {
        'settlement_name': settlement_name,
        'inn_name': inn_name,
        'worthy_name': worthy_name
    }
```

### Display in Long Rest UI

**Example - Hamlet with Poor lifestyle**:
```
Long Rest - Aelric's Crossing (Hamlet)
Population: ~150

Available Accommodations:
  ( ) Wretched - Free
  (*) Poor - 2 sp
      Goodwife Matilda's barn
```

**Example - Village with Modest lifestyle**:
```
Long Rest - Highridge (Village)
Population: ~750

Available Accommodations:
  ( ) Squalid - 1 sp
  (*) Modest - 1 gp
      The Silver Dagger (inn)
  ( ) Comfortable - 2 gp
      Reeve Oswald's manor
```

**Example - Town with all lifestyles**:
```
Long Rest - Kingsgate (Town)
Population: ~3,200

Available Accommodations:
  ( ) Wretched - Free
  ( ) Squalid - 1 sp
      The Rusty Eel (flophouse)
  ( ) Poor - 2 sp
      The Traveler's Rest (common room)
  (*) Modest - 1 gp
      The Royal Oak (private room)
  ( ) Comfortable - 2 gp
      The Golden Dragon (well-appointed)
  ( ) Wealthy - 4 gp
      Lord Randulf's manor (private suite)
```

## Implementation File Structure

### settlement_name_service.py

```python
# Location: src/talekeeper/services/settlement_name_service.py

class SettlementNameService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.inn_names = HISTORIC_INN_NAMES  # 60 curated names
        self.adjectives = ADJECTIVES
        self.nouns = NOUNS_ALL
        self.occupations = OCCUPATIONS
        self.male_names = MALE_WORTHY_NAMES
        self.female_names = FEMALE_WORTHY_NAMES
        # ... etc

    def generate_inn_name(self, seed: int) -> str:
        """Generate inn/tavern name."""
        pass

    def generate_worthy_name(self, settlement_type: str, seed: int) -> str:
        """Generate noble/leader name with title."""
        pass

    def generate_settlement_name(self, settlement_type: str, biome: str, seed: int) -> str:
        """Generate settlement name."""
        pass

    def get_or_create_settlement_names(self, character_id: str, q: int, r: int) -> Dict:
        """Get existing or generate new names for hex settlement."""
        pass
```

## Data Tables Summary

### Required Lists

1. **HISTORIC_INN_NAMES**: 60 curated historic UK pub names
2. **ADJECTIVES**: 20 inn adjectives (Red, Golden, Jolly, etc.)
3. **NOUNS_ANIMALS**: 30 animal nouns (Lion, Dragon, Boar, etc.)
4. **NOUNS_OBJECTS**: 30 object nouns (Crown, Anvil, Tankard, etc.)
5. **OCCUPATIONS**: 20 medieval occupations (Smith, Miller, Merchant, etc.)
6. **MALE_WORTHY_NAMES**: 50 curated male names (Aelric, Harold, Geoffrey, etc.)
7. **FEMALE_WORTHY_NAMES**: 30 curated female names (Matilda, Eleanor, Gwendolyn, etc.)
8. **HAMLET_FEATURES**: 20 hamlet geographic/building terms
9. **VILLAGE_PREFIXES**: 40 village name prefixes
10. **VILLAGE_SUFFIXES**: 15 village name suffixes
11. **TOWN_FEATURES**: 20 town major features
12. **TOWN_SUFFIXES**: 10 town suffixes
13. **HISTORIC_TOWN_NAMES**: 20 curated historic town names

**Total Data Points**: ~400 curated entries + syllable generation fallback

## Testing Strategy

### Unit Tests
```python
def test_inn_name_generation():
    service = SettlementNameService('test.db')

    # Test deterministic with seed
    name1 = service.generate_inn_name(12345)
    name2 = service.generate_inn_name(12345)
    assert name1 == name2  # Same seed = same name

    # Test variety
    names = set()
    for i in range(100):
        names.add(service.generate_inn_name(i))
    assert len(names) > 50  # At least 50 unique names from 100 seeds

def test_worthy_name_by_settlement():
    service = SettlementNameService('test.db')

    hamlet_worthy = service.generate_worthy_name('hamlet', 100)
    assert hamlet_worthy.startswith(('Headman', 'Goodman', 'Yeoman', 'Elder'))

    village_worthy = service.generate_worthy_name('village', 100)
    assert village_worthy.startswith(('Reeve', 'Bailiff', 'Squire', 'Dame'))

    town_worthy = service.generate_worthy_name('town_small', 100)
    assert town_worthy.startswith(('Lord', 'Baron', 'Thane', 'Lady'))

def test_settlement_persistence():
    service = SettlementNameService('test.db')

    # First call generates
    result1 = service.get_or_create_settlement_names('char1', 5, 10)

    # Second call retrieves
    result2 = service.get_or_create_settlement_names('char1', 5, 10)

    assert result1 == result2  # Names persist
```

## Future Enhancements

### Regional Name Variations
- **Forest biomes**: Use tree/nature names (Oakvale, Pinewood, Ferndale)
- **Mountain biomes**: Use stone/height names (Highpeak, Stoneridge, Ironhold)
- **Coastal biomes**: Use sea/port names (Seaport, Wavehaven, Saltmarsh)
- **Desert biomes**: Use dune/oasis names (Sandford, Dunewatch, Oasisrest)

### Cultural Variations
- **Celtic settlements**: Use Welsh/Gaelic patterns (Caer-, Llan-, -wyn)
- **Nordic settlements**: Use Norse patterns (-heim, -borg, -vik)
- **Roman settlements**: Use Latin patterns (-chester, -caster, -castra)

### NPC Integration
- Generate full NPCs for innkeepers (using pleb's NPC generator)
- Generate backstories for worthies
- Create family trees for noble houses
- Track reputation with settlements

## References

- **pleb repository**: d:\Code\pleb\nameGenerators\aquilonianNames.js
- **TaleKeeper tavern CSV**: docs\tavern_generator.csv
- **Historic UK pub names**: Web research on pre-1700 British inns
- **Medieval naming conventions**: Anglo-Saxon, Norman, Celtic patterns
- **D&D settlement sizes**: PHB 2024 lifestyle rules
