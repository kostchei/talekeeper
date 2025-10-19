# Central Naming Service - Campaign Frame Integration Plan

**Date**: 2025-10-19
**Status**: Planning - Implementation on Hold

## Problem Statement

Currently, `SettlementNameService` has hardcoded name lists that assume a specific fantasy style (medieval Anglo-Saxon/Norman). However, TaleKeeper supports multiple campaign frames with different thematic settings:

- **Conan**: Barbaric, ancient world (Hyborian Age)
- **Golden Age**: Classic high fantasy (D&D traditional)
- **Dark Sun** (future): Harsh desert survival
- **Planescape** (future): Planar cosmopolitan
- **Gothic Horror** (future): Dark, Victorian-inspired

Each campaign frame should have culturally-appropriate names for:
- **Settlements** (towns, villages, hamlets)
- **Inns/Taverns** (The Red Lion vs The Blood Pit vs The Obsidian Oasis)
- **Worthies** (Lord Randulf vs Warlord Thulsa vs Sand Chief Tarak)
- **NPCs** (general character names)

## Current Architecture Issues

### Issue 1: Hardcoded Name Lists
**File**: `src/talekeeper/services/settlement_name_service.py`

```python
# Current approach - not campaign-aware
HISTORIC_INN_NAMES = [
    "The Red Lion", "The White Hart", "The Royal Oak"  # Medieval English only
]

MALE_WORTHY_NAMES = [
    "Aelric", "Harold", "Geoffrey"  # Anglo-Saxon/Norman only
]
```

**Problem**: These names don't fit Conan (Cimmerian/Aquilonian) or Dark Sun (Athasian) settings.

### Issue 2: No Campaign Frame Integration
**File**: `src/talekeeper/services/settlement_name_service.py`

```python
def generate_inn_name(self, seed: int) -> str:
    # No campaign_frame parameter!
    rng = random.Random(seed)
    return rng.choice(HISTORIC_INN_NAMES)
```

**Problem**: No way to switch name lists based on active campaign.

### Issue 3: Existing Campaign Frame Has Narrative Prompts
**File**: `src/talekeeper/ui/encounter_pane/campaign_frame.py`

```python
class CampaignFrame:
    def __init__(self, data=None, ...):
        self.narrative_prompt = data.get('narrative_prompt')
        self.narrative_combat_prompt = data.get('narrative_combat_prompt')
        # But NO naming configuration!
```

**File**: `campaign/conan.json`
```json
{
  "name": "Conan (Core)",
  "style": "conan",
  "narrative_prompt": "...Conan-style sword-and-sorcery...",
  "narrative_combat_prompt": "...brutal, visceral prose..."
}
```

**Problem**: Campaign frames have narrative style but not naming style.

## Proposed Solution: Central Naming Service

### Architecture Overview

```
CentralNamingService
├── Loads campaign frame configuration
├── Selects name lists based on campaign style
├── Falls back to default (medieval) if campaign has no custom names
├── Used by:
│   ├── SettlementNameService (settlements, inns, worthies)
│   ├── NPCGenerator (character names)
│   ├── MonsterNameService (unique monster names)
│   └── Future: Item names, ship names, guild names
```

### New Campaign Frame Schema

**Add to CampaignFrame class**:
```python
class CampaignFrame:
    def __init__(self, data=None, ...):
        # Existing fields...
        self.narrative_prompt = data.get('narrative_prompt')

        # NEW: Naming configuration
        self.naming_style = data.get('naming_style')  # 'medieval', 'conan', 'darksun', etc.
        self.custom_name_sets = data.get('custom_name_sets', {})
```

**Example: conan.json (extended)**:
```json
{
  "name": "Conan (Core)",
  "style": "conan",
  "naming_style": "hyborian",
  "custom_name_sets": {
    "inn_names": [
      "The Serpent's Den", "The Blood & Iron", "The Savage Blade",
      "The Scarlet Citadel", "The Black Lotus", "The Crimson Hawk",
      "The Demon's Cup", "The Shadizar Crossing", "The Cimmerian's Rest"
    ],
    "male_worthy_names": [
      "Conan", "Thulsa", "Constantius", "Taurus", "Valeria", "Zenobia",
      "Thoth-Amon", "Stygius", "Xaltotun", "Nabonidus", "Ascalante"
    ],
    "female_worthy_names": [
      "Belit", "Red Sonja", "Yasmela", "Taramis", "Valerius", "Atali"
    ],
    "settlement_prefixes": [
      "Shadizar", "Tarantia", "Khorshemish", "Argos", "Koth", "Shem"
    ],
    "settlement_suffixes": [],
    "worthy_titles": {
      "hamlet": ["Headman", "Chieftain", "Elder"],
      "village": ["Reeve", "Warlord", "Hetman"],
      "town": ["Lord", "High Priest", "Tyrant", "Satrap"]
    }
  }
}
```

**Example: darksun.json (future)**:
```json
{
  "name": "Dark Sun",
  "style": "darksun",
  "naming_style": "athasian",
  "custom_name_sets": {
    "inn_names": [
      "The Obsidian Oasis", "The Dusty Kank", "The Sand Viper",
      "The Red Sun Rest", "The Slave's Respite", "The Ceramic Cup"
    ],
    "male_worthy_names": [
      "Rikus", "Agis", "Tithian", "Kalak", "Hamanu", "Dregoth", "Abalach-Re"
    ],
    "female_worthy_names": [
      "Sadira", "Neeva", "Lalali-Puy", "Sielba"
    ],
    "worthy_titles": {
      "hamlet": ["Elder", "Water Keeper", "Tribe Leader"],
      "village": ["Templar", "Merchant Prince", "Defiler"],
      "town": ["Sorcerer-King", "High Templar", "Patrician"]
    }
  }
}
```

### Central Naming Service Implementation Plan

**File**: `src/talekeeper/services/central_naming_service.py`

```python
from typing import Dict, List, Optional
import random
from talekeeper.ui.encounter_pane.campaign_frame import CampaignFrame


class CentralNamingService:
    """
    Centralized naming service that adapts to campaign frame settings.
    Provides culturally-appropriate names for settlements, NPCs, inns, etc.
    """

    def __init__(self, campaign_frame: Optional[CampaignFrame] = None):
        self.campaign_frame = campaign_frame
        self.naming_style = self._determine_naming_style()
        self.name_sets = self._load_name_sets()

    def _determine_naming_style(self) -> str:
        """Determine which naming style to use."""
        if not self.campaign_frame:
            return 'default'  # Medieval/Golden Age

        # Check for explicit naming_style in campaign
        if hasattr(self.campaign_frame, 'naming_style') and self.campaign_frame.naming_style:
            return self.campaign_frame.naming_style

        # Fall back to campaign style
        style_map = {
            'conan': 'hyborian',
            'golden': 'default',
            'darksun': 'athasian',
            'planescape': 'planar',
            'gothic': 'victorian'
        }

        return style_map.get(self.campaign_frame.style, 'default')

    def _load_name_sets(self) -> Dict:
        """Load name sets from campaign or defaults."""
        # If campaign has custom_name_sets, use those
        if (self.campaign_frame and
            hasattr(self.campaign_frame, 'custom_name_sets') and
            self.campaign_frame.custom_name_sets):
            return self._merge_with_defaults(self.campaign_frame.custom_name_sets)

        # Otherwise load from built-in name sets
        return self._load_builtin_name_set(self.naming_style)

    def _load_builtin_name_set(self, style: str) -> Dict:
        """Load built-in name sets by style."""
        if style == 'hyborian':
            return HYBORIAN_NAME_SET
        elif style == 'athasian':
            return ATHASIAN_NAME_SET
        elif style == 'planar':
            return PLANAR_NAME_SET
        elif style == 'victorian':
            return VICTORIAN_NAME_SET
        else:
            return DEFAULT_NAME_SET  # Medieval/Golden Age

    def _merge_with_defaults(self, custom_sets: Dict) -> Dict:
        """Merge custom name sets with defaults for missing fields."""
        defaults = DEFAULT_NAME_SET
        merged = defaults.copy()

        for key, value in custom_sets.items():
            if isinstance(value, list) and value:
                merged[key] = value
            elif isinstance(value, dict) and value:
                merged[key] = value

        return merged

    # Public API

    def generate_inn_name(self, seed: int) -> str:
        """Generate inn/tavern name appropriate for campaign."""
        rng = random.Random(seed)
        inn_names = self.name_sets.get('inn_names', [])

        if not inn_names:
            inn_names = DEFAULT_NAME_SET['inn_names']

        if rng.random() < 0.6:
            return rng.choice(inn_names)
        else:
            return self._generate_compound_inn_name(rng)

    def _generate_compound_inn_name(self, rng: random.Random) -> str:
        """Generate procedural inn name from parts."""
        adjectives = self.name_sets.get('inn_adjectives', DEFAULT_NAME_SET['inn_adjectives'])
        nouns = self.name_sets.get('inn_nouns', DEFAULT_NAME_SET['inn_nouns'])

        adj = rng.choice(adjectives)
        noun = rng.choice(nouns)

        return f"The {adj} {noun}"

    def generate_worthy_name(self, settlement_type: str, seed: int) -> str:
        """Generate worthy (leader) name with culture-appropriate title."""
        rng = random.Random(seed)
        is_male = rng.random() < 0.7

        # Get names
        if is_male:
            names = self.name_sets.get('male_worthy_names', [])
        else:
            names = self.name_sets.get('female_worthy_names', [])

        if not names:
            names = DEFAULT_NAME_SET['male_worthy_names' if is_male else 'female_worthy_names']

        name = rng.choice(names)

        # Get title
        titles = self.name_sets.get('worthy_titles', {})
        title_list = titles.get(settlement_type, [])

        if not title_list:
            title_list = DEFAULT_NAME_SET['worthy_titles'][settlement_type]

        title = rng.choice(title_list)

        return f"{title} {name}"

    def generate_settlement_name(self, settlement_type: str, biome: str, seed: int) -> str:
        """Generate settlement name appropriate for campaign."""
        rng = random.Random(seed)

        if settlement_type == 'hamlet':
            return self._generate_hamlet_name(rng)
        elif settlement_type == 'village':
            return self._generate_village_name(rng)
        else:
            return self._generate_town_name(rng)

    def _generate_hamlet_name(self, rng: random.Random) -> str:
        """Generate hamlet name (Owner's Feature pattern)."""
        names = self.name_sets.get('personal_names', [])
        features = self.name_sets.get('hamlet_features', DEFAULT_NAME_SET['hamlet_features'])

        if not names:
            names = (self.name_sets.get('male_worthy_names', []) +
                    self.name_sets.get('female_worthy_names', []))

        owner = rng.choice(names)
        feature = rng.choice(features)

        return f"{owner}'s {feature}"

    def _generate_village_name(self, rng: random.Random) -> str:
        """Generate village name (Geographic prefix + suffix)."""
        prefixes = self.name_sets.get('settlement_prefixes', DEFAULT_NAME_SET['settlement_prefixes'])
        suffixes = self.name_sets.get('settlement_suffixes', DEFAULT_NAME_SET['settlement_suffixes'])

        prefix = rng.choice(prefixes)
        suffix = rng.choice(suffixes)

        return f"{prefix}{suffix}"

    def _generate_town_name(self, rng: random.Random) -> str:
        """Generate town name (curated or procedural)."""
        town_names = self.name_sets.get('town_names', [])

        if town_names and rng.random() < 0.5:
            return rng.choice(town_names)
        else:
            features = self.name_sets.get('town_features', DEFAULT_NAME_SET['town_features'])
            suffixes = self.name_sets.get('town_suffixes', DEFAULT_NAME_SET['town_suffixes'])

            feature = rng.choice(features)
            suffix = rng.choice(suffixes)

            return f"{feature}{suffix}"

    def generate_npc_name(self, gender: str, seed: int) -> str:
        """Generate NPC name for random encounters."""
        rng = random.Random(seed)

        if gender == 'male':
            names = self.name_sets.get('male_npc_names', self.name_sets.get('male_worthy_names', []))
        else:
            names = self.name_sets.get('female_npc_names', self.name_sets.get('female_worthy_names', []))

        if not names:
            names = DEFAULT_NAME_SET['male_npc_names' if gender == 'male' else 'female_npc_names']

        return rng.choice(names)


# Built-in Name Sets

DEFAULT_NAME_SET = {
    # Medieval/Golden Age (current implementation)
    'inn_names': [
        "The Red Lion", "The White Hart", "The Royal Oak", "The King's Head",
        # ... (60 historic UK names from settlement_name_service.py)
    ],
    'inn_adjectives': ["Red", "Golden", "Silver", "Royal", "Jolly", "Merry"],
    'inn_nouns': ["Lion", "Dragon", "Eagle", "Stag", "Crown", "Bell"],
    'male_worthy_names': ["Aelric", "Harold", "Geoffrey", "Randulf", "William"],
    'female_worthy_names': ["Matilda", "Eleanor", "Gwendolyn", "Isabella"],
    'worthy_titles': {
        'hamlet': ["Headman", "Goodman", "Yeoman", "Elder"],
        'village': ["Reeve", "Bailiff", "Squire", "Dame"],
        'town': ["Lord", "Baron", "Thane", "Lady"]
    },
    'hamlet_features': ["Crossing", "Ford", "Mill", "Farm", "Hollow"],
    'settlement_prefixes': ["High", "Deep", "Stone", "Oak", "River"],
    'settlement_suffixes': ["ton", "ham", "bury", "ford", "wood"],
    'town_features': ["Castle", "Market", "King", "Fort"],
    'town_suffixes': ["ton", "bury", "gate", "port"],
    'town_names': ["Kingsgate", "Silverkeep", "Irongate"],
    'male_npc_names': ["Aelric", "Harold", "Geoffrey", "Randulf"],
    'female_npc_names': ["Matilda", "Eleanor", "Gwendolyn"]
}

HYBORIAN_NAME_SET = {
    # Conan the Barbarian (Robert E. Howard)
    'inn_names': [
        "The Serpent's Den", "The Blood & Iron", "The Savage Blade",
        "The Scarlet Citadel", "The Black Lotus", "The Crimson Hawk",
        "The Demon's Cup", "The Shadizar Crossing", "The Cimmerian's Rest",
        "The Pit & Pyre", "The Red Priest", "The Stygian Shadow",
        "The Hyrkanian Horse", "The Kushite Spear", "The Aquilonian Crown"
    ],
    'inn_adjectives': ["Bloody", "Savage", "Crimson", "Black", "Iron", "Scarlet"],
    'inn_nouns': ["Blade", "Serpent", "Hawk", "Wolf", "Skull", "Demon"],
    'male_worthy_names': [
        "Conan", "Thulsa", "Constantius", "Taurus", "Stygius", "Xaltotun",
        "Nabonidus", "Ascalante", "Thoth-Amon", "Valka", "Tothmekri"
    ],
    'female_worthy_names': [
        "Belit", "Valeria", "Yasmela", "Taramis", "Atali", "Zenobia", "Red Sonja"
    ],
    'worthy_titles': {
        'hamlet': ["Chieftain", "Headman", "Elder", "Hetman"],
        'village': ["Warlord", "Reeve", "Hetman", "Priest"],
        'town': ["Lord", "High Priest", "Tyrant", "Satrap", "Khan"]
    },
    'hamlet_features': ["Cairn", "Outpost", "Waystation", "Ford", "Camp"],
    'settlement_prefixes': ["Shadizar", "Khorshemish", "Argos", "Koth", "Zamora"],
    'settlement_suffixes': ["", "-ia", "-um", "-ar"],
    'town_features': ["Citadel", "Throne", "Pyramid", "Sanctum"],
    'town_suffixes': ["", "-ia", "-um"],
    'town_names': [
        "Tarantia", "Shadizar", "Khorshemish", "Argos", "Khemi",
        "Messantia", "Aghrapur", "Sultanapur"
    ],
    'male_npc_names': ["Conan", "Thulsa", "Constantius", "Stygius"],
    'female_npc_names': ["Belit", "Valeria", "Yasmela"]
}

ATHASIAN_NAME_SET = {
    # Dark Sun (TSR/Wizards of the Coast)
    'inn_names': [
        "The Obsidian Oasis", "The Dusty Kank", "The Sand Viper",
        "The Red Sun Rest", "The Slave's Respite", "The Ceramic Cup",
        "The Elven Market", "The Dune Trader", "The Salt View",
        "The Tembo's Den", "The Arena's Shadow", "The Water Hoard"
    ],
    'inn_adjectives': ["Dusty", "Obsidian", "Crimson", "Scorched", "Parched"],
    'inn_nouns': ["Kank", "Viper", "Sun", "Dune", "Arena", "Slave"],
    'male_worthy_names': [
        "Rikus", "Agis", "Tithian", "Kalak", "Hamanu", "Dregoth",
        "Borys", "Tectuktitlay", "Daskinor", "Andropinis"
    ],
    'female_worthy_names': [
        "Sadira", "Neeva", "Lalali-Puy", "Abalach-Re", "Sielba"
    ],
    'worthy_titles': {
        'hamlet': ["Elder", "Water Keeper", "Tribe Leader", "Sand Shaper"],
        'village': ["Templar", "Merchant Prince", "Defiler", "Preserver"],
        'town': ["Sorcerer-King", "High Templar", "Patrician", "Veiled One"]
    },
    'hamlet_features': ["Oasis", "Dune", "Salt Flat", "Outpost", "Spring"],
    'settlement_prefixes': ["Tyr", "Balic", "Draj", "Gulg", "Nibenay"],
    'settlement_suffixes': ["", "-al", "-ak"],
    'town_features': ["Arena", "Ziggurat", "Obsidian", "Templar"],
    'town_suffixes': ["", "-ay", "-ak"],
    'town_names': [
        "Tyr", "Balic", "Draj", "Gulg", "Nibenay", "Raam", "Urik"
    ],
    'male_npc_names': ["Rikus", "Agis", "Tithian"],
    'female_npc_names': ["Sadira", "Neeva"]
}

# PLANAR_NAME_SET and VICTORIAN_NAME_SET would be defined similarly
```

### Updated SettlementNameService

**File**: `src/talekeeper/services/settlement_name_service.py` (refactored)

```python
from typing import Dict, Optional
from talekeeper.services.central_naming_service import CentralNamingService
from talekeeper.ui.encounter_pane.campaign_frame import CampaignFrame


class SettlementNameService:
    """
    Settlement-specific naming service.
    Delegates to CentralNamingService for campaign-aware name generation.
    """

    def __init__(self, db_path: str, campaign_frame: Optional[CampaignFrame] = None):
        self.db_path = db_path
        self.central_naming = CentralNamingService(campaign_frame)

    def generate_inn_name(self, seed: int) -> str:
        """Generate inn name using campaign-aware central service."""
        return self.central_naming.generate_inn_name(seed)

    def generate_worthy_name(self, settlement_type: str, seed: int) -> str:
        """Generate worthy name using campaign-aware central service."""
        return self.central_naming.generate_worthy_name(settlement_type, seed)

    def generate_settlement_name(self, settlement_type: str, biome: str, seed: int) -> str:
        """Generate settlement name using campaign-aware central service."""
        return self.central_naming.generate_settlement_name(settlement_type, biome, seed)

    # get_or_create_settlement_names() stays the same
    # Database methods stay the same
```

## Integration Points

### 1. Campaign Frame Selection
**Where**: User selects campaign at character creation or campaign start

```python
# main_window.py or campaign_selector.py
selected_campaign = CampaignFrame.load_from_file('campaign/conan.json')

# Store in game engine or global state
self.game_engine.campaign_frame = selected_campaign
```

### 2. Long Rest Widget
**File**: `src/talekeeper/ui/rest_pane/long_rest_widget.py`

```python
# Current (no campaign awareness)
self.name_service = SettlementNameService(db_path)

# Updated (campaign-aware)
campaign_frame = self.parent.game_engine.campaign_frame  # Get from game state
self.name_service = SettlementNameService(db_path, campaign_frame)
```

### 3. Hex Map Generation
**File**: `src/talekeeper/services/hex_map_service.py`

```python
# When generating new hex with settlement
def _generate_hex(self, character_id: str, q: int, r: int):
    # ... existing code ...

    # Get campaign frame from character or global state
    campaign_frame = self._get_campaign_frame(character_id)

    # Use campaign-aware naming
    name_service = SettlementNameService(self.db_path, campaign_frame)
    settlement_data = name_service.get_or_create_settlement_names(character_id, q, r)
```

### 4. NPC Generation
**File**: Future `src/talekeeper/services/npc_generator.py`

```python
def generate_npc(self, character_id: str, seed: int):
    campaign_frame = self._get_campaign_frame(character_id)
    central_naming = CentralNamingService(campaign_frame)

    npc_name = central_naming.generate_npc_name('male', seed)
    # "Aelric" in Golden Age, "Conan" in Hyborian, "Rikus" in Athasian
```

## Data Storage Strategy

### Option 1: Embed in Campaign JSON
**Pros**: Self-contained, version-controlled with campaigns
**Cons**: Large JSON files, redundant data

**Example**: conan.json with full name sets (shown above)

### Option 2: Separate Name Set Files
**Pros**: Reusable, smaller campaign files
**Cons**: More files to manage

**Structure**:
```
campaign/
├── conan.json               # References "hyborian" name set
├── golden.json              # References "default" name set
├── darksun.json             # References "athasian" name set
└── name_sets/
    ├── default.json         # Medieval/Golden Age names
    ├── hyborian.json        # Conan names
    ├── athasian.json        # Dark Sun names
    ├── planar.json          # Planescape names
    └── victorian.json       # Gothic Horror names
```

**conan.json (slim)**:
```json
{
  "name": "Conan (Core)",
  "style": "conan",
  "naming_style": "hyborian",
  "narrative_prompt": "..."
}
```

**name_sets/hyborian.json**:
```json
{
  "inn_names": ["The Serpent's Den", "The Blood & Iron", ...],
  "male_worthy_names": ["Conan", "Thulsa", ...],
  "worthy_titles": {...}
}
```

### Recommended: Option 2 (Separate Files)
- Cleaner campaign definitions
- Easier to add new name sets without touching campaigns
- Name sets can be shared across similar campaigns
- Easier to contribute community name sets

## Backwards Compatibility

### For Existing Characters
If a character was created before campaign frames existed:

```python
def _get_campaign_frame(self, character_id: str) -> Optional[CampaignFrame]:
    """Get campaign frame for character, or None for legacy."""
    # Check character's campaign_frame_id in database
    # If None, return None (uses default/medieval names)
    # CentralNamingService handles None gracefully
```

### For Existing Settlements
Settlement names already generated with old service:

```python
# settlement_name_service.py
def get_or_create_settlement_names(self, character_id: str, q: int, r: int):
    existing = self._get_existing_names(character_id, q, r)

    if existing:
        return existing  # Don't regenerate! Preserve existing names

    # Only new settlements use campaign-aware generation
    return self._generate_new_settlement_names(...)
```

## Implementation Checklist

**Phase 1: Core Service** (3-4 hours):
- [ ] Create `central_naming_service.py`
- [ ] Implement `CentralNamingService` class
- [ ] Define DEFAULT_NAME_SET (copy from settlement_name_service.py)
- [ ] Define HYBORIAN_NAME_SET (Conan names)
- [ ] Add unit tests for name generation

**Phase 2: Campaign Integration** (2-3 hours):
- [ ] Update `CampaignFrame` class with naming fields
- [ ] Create `campaign/name_sets/` directory structure
- [ ] Create `name_sets/default.json`
- [ ] Create `name_sets/hyborian.json`
- [ ] Update `conan.json` to reference hyborian naming style

**Phase 3: Service Refactoring** (2-3 hours):
- [ ] Refactor `SettlementNameService` to use `CentralNamingService`
- [ ] Update `LongRestWidget` to pass campaign_frame
- [ ] Update `HexMapService` to use campaign-aware naming
- [ ] Add campaign_frame parameter to all naming calls

**Phase 4: Testing** (2-3 hours):
- [ ] Unit tests for CentralNamingService
- [ ] Integration tests with campaign frames
- [ ] Manual testing: Conan campaign vs Golden Age campaign
- [ ] Verify backwards compatibility with existing settlements

**Total Estimated Time**: 9-13 hours

## Future Extensions

### Community Name Sets
Allow users to create custom name sets:

```
user_data/
└── custom_name_sets/
    ├── my_homebrew.json
    ├── tolkien_inspired.json
    └── cyberpunk.json
```

### Procedural Generation Modes
Some campaigns might want full procedural names:

```json
{
  "naming_style": "procedural",
  "name_generation": {
    "mode": "syllable",
    "syllable_patterns": {
      "male": ["start", "middle?", "end"],
      "female": ["start", "middle", "end"]
    },
    "syllable_lists": {
      "male_start": ["Ar", "Cal", "Mor"],
      "male_middle": ["bel", "gal"],
      "male_end": ["gon", "din"]
    }
  }
}
```

This would use the pleb-style syllable generation instead of curated lists.

### LLM-Generated Names
For campaigns using Ollama:

```json
{
  "naming_style": "llm",
  "name_generation_prompt": "Generate a Hyborian-age barbarian name in the style of Robert E. Howard. Output only the name, no explanation."
}
```

## Risks & Mitigations

### Risk 1: Performance (Name Set Loading)
**Mitigation**: Load name sets once on service initialization, cache in memory

### Risk 2: Breaking Existing Names
**Mitigation**: Only apply to NEW settlements/NPCs, preserve existing names in database

### Risk 3: Inconsistent Theming
**Mitigation**: Require all campaigns to define naming_style, fall back to 'default'

### Risk 4: Large Name Sets
**Mitigation**: Use separate JSON files, lazy load only when needed

## Success Criteria

1. **Campaign-Appropriate Names**: Conan campaign generates Hyborian names, Golden Age generates medieval names
2. **Backwards Compatible**: Existing characters/settlements keep their names
3. **Extensible**: Easy to add new name sets (Dark Sun, Planescape, etc.)
4. **Consistent**: Same seed + same campaign = same name (deterministic)
5. **Fallback Graceful**: Missing name sets fall back to default without errors

---

**Planning Complete**: 2025-10-19
**Implementation**: On Hold (per user request)
**Dependencies**: Campaign Frame system, Settlement Name Service
**Priority**: Medium (enhances immersion but not critical for v1.0)
