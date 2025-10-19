# Vendors Planning Document

## Settlement Generation Table

| d100 Roll | Settlement Type | Population Range | Sub-roll |
|-----------|----------------|------------------|----------|
| 01-06 | Empty/Wild | 0 | - |
| 07-31 | Hamlet | 1-200 | - |
| 32-99 | Village | 200-2,000 | - |
| 100 | Town+ | 2,000+ | Roll d6: 1-3 Small Town, 4-5 Medium Town, 6 Large Town |

## Settlement Economy Tiers

| Population | Base Pool (gp) | Base Cap (gp) | Description |
|------------|----------------|---------------|-------------|
| 25 | 10 | 10 | A few tools, torches, or rations; maybe one simple weapon. |
| 75 | 25 | 25 | Basic gear and a few weapons; no armor heavier than leather. |
| 150 | 50 | 50 | Small hamlet with a smith or trader; some martial arms. |
| 200 | 75 | 75 | Large hamlet or small village; chain shirts and longbows appear. |
| 500 | 200 | 100 | Modest village market; horses, mail shirts, bulk supplies. |
| 1,000 | 400 | 150 | Large village or small town; wide range of mundane goods. |
| 1,500 | 700 | 200 | Market town; can commission splint or multiple armors. |
| 2,000 | 1,000 | 250 | Small rural town; supports full adventuring outfitting. |

## Vendor Purchasing Rules

### Settlement Purchasing Caps
Each vendor's actual purchasing pool and price cap varies:
- **Purchasing Pool**: Base Pool x (1% to 200%, avg 100%)
- **Price Cap**: Base Cap x (1% to 200%, avg 100%)

### Inventory Generation
- **Premium Items** (50% of cap): 1-8 items
- **High-Value Items** (50-100% of cap): 1-8 items

### Town Tiers

| Settlement | Purchasing Pool | Special Inventory |
|------------|----------------|-------------------|
| Small Town | 5,000 gp | All Player's Handbook items |
| Medium Town | 10,000 gp | All PHB items + 1d8 Uncommon magic items |
| Large Town/City | 100,000 gp | All PHB items + 1d8 Uncommon + 1d4 Rare magic items |

## Lifestyle Expenses

### Availability by Settlement

| Settlement Type | Available Lifestyles | Roll |
|----------------|---------------------|------|
| Hamlet | Squalid, Poor, or Modest | Roll d3 |
| Village | Squalid, Poor, Modest, or Comfortable | Roll d4 |
| Town+ | All lifestyles (player choice) | - |

### Lifestyle Costs & Effects

| Lifestyle | Cost per Day | Description | Special |
|-----------|-------------|-------------|---------|
| Wretched | Free | Survive via chance and charity. Often exposed to natural dangers from sleeping outside. | 50% chance of encounter or hazard |
| Squalid | 1 sp | Bare minimum for necessities. Exposed to unhealthy conditions and opportunistic criminals. | 25% chance of encounter or hazard |
| Poor | 2 sp | Frugal spending for necessities. | - |
| Modest | 1 gp | Average standard of living. | - |
| Comfortable | 2 gp | Modest spending with a few luxuries. | - |
| Wealthy | 4 gp | Finer things in life, might have servants. | - |

## Hex-Based Vendor System Implementation

### Settlement Generation per Hex

**When a hex is first explored, roll d100:**

| d100 Roll | Result | Settlement Type | Notes |
|-----------|--------|----------------|-------|
| 01-06 | Empty/Wild | None | No vendors, no settlement (6% chance) |
| 07-31 | Hamlet | hamlet | Population 1-200 (25% chance) |
| 32-99 | Village | village | Population 200-2,000 (68% chance) |
| 100 | Town+ | Roll d6 for size | 1% chance |

**If d100 = 100, roll d6 for town size:**
- 1-3: Small Town (population ~2,000)
- 4-5: Medium Town (population ~5,000)
- 6: Large Town (population ~10,000+)

**Settlement type is PERMANENT for that hex** (doesn't change on revisit)

If settlement type is "Empty/Wild" (01-06), there is no vendor button in the hex.

### Shop Visit Flow

**When player clicks "Vendor" in hex:**
1. Check settlement type (from hex data)
   - If "Empty/Wild": No vendor button exists
   - Otherwise: Show vendor button
2. Display message based on settlement type:
   - Hamlet: "In this hamlet, you find a small shop"
   - Village: "In this village, you find a general store"
   - Town: "In this town, you find a well-stocked merchant"
3. **Generate fresh shop inventory** (happens every time you visit):
   - Roll variance (1-200%) for purchasing pool
   - Roll variance (1-200%) for price cap
   - Generate inventory based on settlement type and variances
   - Roll character's charisma skills for buy prices
   - Display shop with pre-haggled buy prices

**Shop inventory refreshes:**
- Every time you leave the hex and come back
- Day-to-day changes (new stock, different prices)
- Variance rolls are NEW each visit (not cached)

### Dynamic Pricing System

#### Buy Price Calculation (Player Buying from Vendor)
```
Base Markup: 25%
Charisma Discount: Highest of (Persuasion, Deception, Intimidation) skill roll
Crafter Discount: 20% if character has Crafter feat

Final Markup = 25% - Charisma_Roll% - (20% if Crafter)
Minimum Markup = 0%

Buy Price = Base Cost × (1 + Final Markup / 100)
```

**Example:**
- Longsword base cost: 15 gp
- Persuasion roll: 13
- Has Crafter feat
- Final markup: 25% - 13% - 20% = -8% → 0% (minimum)
- Buy price: 15 gp × 1.00 = 15 gp

#### Sell Price Calculation (Player Selling to Vendor)
```
Base Sell Rate: 40% of item value
Charisma Bonus: Highest charisma skill ROLL (d20 + bonus) as %
Roll per item: Each item gets its own roll

Final Sell Rate = 40% + Charisma_Skill_Roll%
Maximum Sell Rate = 100% (can't sell for more than base value)

Sell Price = Base Cost × (Final Sell Rate / 100)
```

**Example:**
- Longsword base cost: 15 gp
- Character has Persuasion +7, Deception +3, Intimidation +5
- Roll Persuasion: d20(12) + 7 = 19
- Roll Deception: d20(8) + 3 = 11
- Roll Intimidation: d20(15) + 5 = 20 (highest)
- Sell rate: 40% + 20% = 60%
- Sell price: 15 gp × 0.60 = 9 gp

### Pre-Haggled Pricing

**On shop generation (for buying):**
1. Generate inventory based on settlement type
2. Roll once for all buy prices:
   - Roll Persuasion/Deception/Intimidation (use highest)
   - Apply to all items player can buy
   - Calculate buy price with discounts
3. Store pre-calculated buy prices with inventory

**Per item (for selling):**
1. When player sells an item:
   - Roll Persuasion/Deception/Intimidation three times (use highest)
   - Calculate sell price with bonus
   - Each item sold gets a new roll

### Charisma Skill Roll
For both buying and selling, use the **highest** of:
- Persuasion: d20 + Persuasion bonus
- Deception: d20 + Deception bonus
- Intimidation: d20 + Intimidation bonus

**Buy prices**: One roll per shop visit, applies to all items
**Sell prices**: One roll per item sold

## Current TaleKeeper Implementation

### Existing Shop System
- **Location**: src/talekeeper/services/shop_service.py
- **Shop Sizes**:
  - SMALL: 20gp max, 10+1d10 items
  - MEDIUM: 200gp max, 10+2d10 items
  - LARGE: 2000gp max, 10+3d10 items
- **Features**:
  - Fixed 25% markup on items
  - Buy/sell interface
  - Sells back at 50% value
  - Common and uncommon items only
  - Category filtering (Weapons, Armor, Gear)

## Integration with TaleKeeper Hex Map System

### Current Hex Map Architecture
- **Location**: src/talekeeper/services/hex_map_service.py
- **Database**: character_hex_map table (per-character hex tiles)
- **Coordinates**: Axial system (q, r) with deterministic seeds
- **Generation**: Just-in-time when hexes are revealed
- **UI**: hex_map_widget.py (Press 'M' to open)

### Existing Hex Map Schema
```sql
character_hex_map (
    character_id, q, r,
    terrain_type, biome, encounter_seed,
    revealed, visited, cleared
)
```

### Settlement Integration Strategy

#### Phase 1: Add Settlement to Hex Generation
Modify `_generate_hex()` in hex_map_service.py:
1. Use existing `encounter_seed` to determine settlement
2. Roll d100 using seed: 01-06=empty, 07-31=hamlet, 32-99=village, 100=town
3. Store settlement type in new column
4. Settlement generated once per hex, never changes

#### Phase 2: Vendor Button in Hex UI
Modify hex_map_widget.py info panel:
1. Check settlement_type when hex is selected
2. Show "Vendor" button if not empty
3. Button opens shop with hex-specific data
4. Each visit regenerates shop inventory

#### Phase 3: Shop Integration
Modify shop_service.py and town_encounter.py:
1. Accept hex coordinates (q, r) as parameter
2. Use hex seed for variance rolls (consistent per visit)
3. Generate fresh inventory on each shop open
4. Apply charisma-based pricing

### Implementation Changes Needed

#### 1. Database Migration (New File: 011_hex_settlements.sql)
```sql
ALTER TABLE character_hex_map ADD COLUMN settlement_type TEXT;

CREATE INDEX IF NOT EXISTS idx_hex_settlement
ON character_hex_map(character_id, settlement_type);
```

**Settlement values:**
- NULL or 'empty': No settlement (01-06 roll)
- 'hamlet': Small settlement (07-31 roll)
- 'village': Medium settlement (32-99 roll)
- 'town_small': Small town (100 roll, d6=1-3)
- 'town_medium': Medium town (100 roll, d6=4-5)
- 'town_large': Large town (100 roll, d6=6)

#### 2. HexMapService Changes (hex_map_service.py)

**Modify `_generate_hex()` method:**
```python
def _generate_hex(self, character_id: str, q: int, r: int) -> Dict:
    # ... existing code ...

    # Generate settlement type
    random.seed(seed)  # Use same seed for deterministic results
    settlement_roll = random.randint(1, 100)

    if settlement_roll <= 6:
        settlement_type = 'empty'
    elif settlement_roll <= 31:
        settlement_type = 'hamlet'
    elif settlement_roll <= 99:
        settlement_type = 'village'
    else:  # 100
        town_roll = random.randint(1, 6)
        if town_roll <= 3:
            settlement_type = 'town_small'
        elif town_roll <= 5:
            settlement_type = 'town_medium'
        else:
            settlement_type = 'town_large'

    # Add settlement_type to INSERT statement
    cursor.execute('''
        INSERT INTO character_hex_map
        (character_id, q, r, terrain_type, biome, encounter_seed,
         revealed, visited, settlement_type)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
    ''', (character_id, q, r, terrain, biome, seed, settlement_type))
```

**Add new method:**
```python
def get_hex_settlement(self, character_id: str, q: int, r: int) -> Optional[str]:
    conn = self._get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT settlement_type FROM character_hex_map WHERE character_id = ? AND q = ? AND r = ?',
        (character_id, q, r)
    )
    row = cursor.fetchone()
    conn.close()
    return row['settlement_type'] if row else None
```

#### 3. ShopService Changes (shop_service.py)

**Add new methods:**
```python
def get_charisma_skill_roll(self, character_data: Dict) -> int:
    """Roll highest of Persuasion, Deception, Intimidation"""
    skills = ['Persuasion', 'Deception', 'Intimidation']
    rolls = []

    for skill in skills:
        bonus = character_data.get(f'{skill.lower()}_bonus', 0)
        roll = random.randint(1, 20) + bonus
        rolls.append(roll)

    return max(rolls)

def has_crafter_feat(self, character_data: Dict) -> bool:
    """Check if character has Crafter feat"""
    # Query character_feats table
    character_id = character_data.get('id')
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM character_feats WHERE character_id = ? AND feat_name = 'Crafter'",
        (character_id,)
    )
    has_feat = cursor.fetchone()[0] > 0
    conn.close()
    return has_feat

def generate_hex_shop_inventory(
    self,
    settlement_type: str,
    character_data: Dict,
    hex_seed: int
) -> Dict:
    """Generate shop inventory for a hex with character-based pricing"""

    # Roll charisma discount once for all buy prices
    charisma_roll = self.get_charisma_skill_roll(character_data)
    has_crafter = self.has_crafter_feat(character_data)

    # Calculate buy discount
    buy_discount = charisma_roll
    if has_crafter:
        buy_discount += 20

    # Determine shop size from settlement
    shop_size_map = {
        'hamlet': ShopSize.SMALL,
        'village': ShopSize.MEDIUM,
        'town_small': ShopSize.LARGE,
        'town_medium': ShopSize.LARGE,
        'town_large': ShopSize.LARGE
    }
    shop_size = shop_size_map.get(settlement_type, ShopSize.MEDIUM)

    # Use hex seed for variance
    random.seed(hex_seed)
    pool_variance = random.randint(1, 200) / 100.0
    cap_variance = random.randint(1, 200) / 100.0

    # Generate base inventory
    inventory = self.generate_shop_inventory(shop_size)

    # Apply character-specific pricing
    for item in inventory:
        base_cost = item.get('cost_gp', 0)

        # Buy price: 25% markup - discounts
        markup = max(0, 25 - buy_discount)
        buy_price = base_cost * (1 + markup / 100.0)
        item['buy_price_gp'] = buy_price
        item['buy_price_display'], _ = format_currency(buy_price)
        item['buy_discount_applied'] = buy_discount

    return {
        'inventory': inventory,
        'charisma_roll': charisma_roll,
        'has_crafter': has_crafter,
        'pool_variance': pool_variance,
        'cap_variance': cap_variance
    }

def calculate_sell_price(self, item_cost: float, character_data: Dict) -> Tuple[float, str]:
    """Calculate sell price with per-item charisma roll"""
    charisma_roll = self.get_charisma_skill_roll(character_data)
    sell_rate = min(100, 40 + charisma_roll)
    sell_price = item_cost * (sell_rate / 100.0)
    display, _ = format_currency(sell_price)
    return (sell_price, display, charisma_roll)
```

#### 4. Hex Map UI Changes (hex_map_widget.py)

**Add vendor button to info panel:**
```python
def _update_info_panel(self, hex_data: Dict):
    # ... existing code ...

    # Add vendor button if settlement exists
    settlement_type = hex_data.get('settlement_type')
    if settlement_type and settlement_type != 'empty':
        vendor_button = QPushButton("Visit Vendor")
        vendor_button.clicked.connect(
            lambda: self._open_hex_shop(hex_data['q'], hex_data['r'], settlement_type)
        )
        self.info_layout.addWidget(vendor_button)

def _open_hex_shop(self, q: int, r: int, settlement_type: str):
    """Open shop interface for this hex"""
    self.hex_shop_requested.emit(q, r, settlement_type)
```

**Add signal to class definition:**
```python
class HexMapWidget(QWidget):
    hex_shop_requested = pyqtSignal(int, int, str)  # q, r, settlement_type
```

#### 5. Main Window Integration (main_window.py)

**Connect hex shop signal:**
```python
def _setup_hex_map(self):
    # ... existing code ...
    self.hex_map_widget.hex_shop_requested.connect(self._open_hex_shop)

def _open_hex_shop(self, q: int, r: int, settlement_type: str):
    """Open shop for a specific hex"""
    if not self.game_engine.current_character:
        return

    # Get hex seed for this location
    hex_service = HexMapService('talekeeper.db')
    hex_data = hex_service.get_hex_data(self.game_engine.current_character['id'], q, r)

    # Create shop interface
    from talekeeper.ui.encounter_pane.hex_shop_interface import HexShopInterface
    shop = HexShopInterface(
        character_data=self.game_engine.current_character,
        settlement_type=settlement_type,
        hex_seed=hex_data['encounter_seed'],
        hex_coords=(q, r),
        parent=self
    )

    shop.shopping_completed.connect(lambda: self._close_hex_shop(shop))

    # Show shop (overlay or replace encounter pane)
    self._show_hex_shop_overlay(shop)
```

#### 6. New File: hex_shop_interface.py

Create new shop interface specifically for hex-based vendors:
```python
class HexShopInterface(ShopInterface):
    def __init__(self, character_data, settlement_type, hex_seed, hex_coords, parent=None):
        self.hex_seed = hex_seed
        self.hex_coords = hex_coords

        # Generate hex-specific shop data
        shop_service = ShopService()
        shop_data = shop_service.generate_hex_shop_inventory(
            settlement_type, character_data, hex_seed
        )

        # Call parent with modified shop size
        super().__init__(character_data, self._get_shop_size(settlement_type), parent)

        # Override inventory with hex-specific data
        self.shop_inventory = shop_data['inventory']
        self.charisma_roll = shop_data['charisma_roll']
```

## Integration with Base Encounter Panel (Non-Hex System)

### Current Vendor System in Encounter Panel
- **Location**: src/talekeeper/ui/encounter_pane/encounter_panel.py:4463
- **Trigger**: "Vendors" option in encounter type dropdown (line 683)
- **Current behavior**: Randomly picks Small/Medium/Large shop size
- **Issue**: No charisma-based pricing, no settlement variation

### Changes to Encounter Panel Vendor Generation

#### Modify `_generate_vendor_encounter()` method:
```python
def _generate_vendor_encounter(self):
    """Generate a vendor encounter with charisma-based pricing."""
    character_data = self._get_current_character_data()
    if not character_data:
        self.encounter_details_text.setPlainText("No active character found.")
        return

    from talekeeper.services.shop_service import ShopSize, ShopService
    import random

    # Roll for settlement type (same as hex generation)
    settlement_roll = random.randint(1, 100)
    if settlement_roll <= 6:
        # No vendor encounter - empty wilderness
        self.encounter_details_text.setPlainText(
            "You search for signs of civilization but find nothing. "
            "This area is too remote for any traveling merchants."
        )
        self.monsters_frame.setVisible(False)
        self.encounters_list.setVisible(False)
        return
    elif settlement_roll <= 31:
        settlement_type = 'hamlet'
        shop_size = ShopSize.SMALL
        description_prefix = "You encounter a humble peddler from a nearby hamlet"
    elif settlement_roll <= 99:
        settlement_type = 'village'
        shop_size = ShopSize.MEDIUM
        description_prefix = "A traveling merchant from a village has set up camp"
    else:  # 100
        town_roll = random.randint(1, 6)
        if town_roll <= 3:
            settlement_type = 'town_small'
            shop_size = ShopSize.LARGE
            description_prefix = "A well-stocked caravan from a nearby town offers goods"
        elif town_roll <= 5:
            settlement_type = 'town_medium'
            shop_size = ShopSize.LARGE
            description_prefix = "A prosperous merchant caravan has traveled from a medium town"
        else:
            settlement_type = 'town_large'
            shop_size = ShopSize.LARGE
            description_prefix = "An impressive merchant guild from a large city has goods for sale"

    # Generate shop with charisma-based pricing
    shop_service = ShopService()

    # Use random seed for this encounter (changes each generation)
    encounter_seed = random.randint(1, 1000000)

    shop_data = shop_service.generate_hex_shop_inventory(
        settlement_type, character_data, encounter_seed
    )

    # Create shop interface with pre-haggled prices
    self.vendor_widget = ShopInterface(character_data, shop_size, self)

    # Override inventory with character-specific pricing
    self.vendor_widget.shop_inventory = shop_data['inventory']

    self.encounters_layout.addWidget(self.vendor_widget)

    # Update description with charisma roll info
    charisma_roll = shop_data['charisma_roll']
    has_crafter = shop_data['has_crafter']

    description_text = f"{description_prefix}.\n\n"
    description_text += f"Your negotiation skills (roll: {charisma_roll}"
    if has_crafter:
        description_text += ", Crafter feat"
    description_text += f") have secured favorable prices.\n\n"
    description_text += f"Buy prices: {max(0, 25 - charisma_roll - (20 if has_crafter else 0))}% markup\n"
    description_text += f"Sell prices: {min(100, 40 + charisma_roll)}% of value"

    # Use narrative service if available
    if self.description_service and self.campaign_frame:
        inventory = shop_data['inventory']
        vendor_context = {
            "name": "Travelling Vendor",
            "settlement_type": settlement_type,
            "shop_size": shop_size.size_name,
            "inventory_count": len(inventory),
            "charisma_roll": charisma_roll,
            "has_crafter": has_crafter,
            "character_level": character_data.get('level'),
        }
        narrative = self.description_service.generate_description(
            "vendor", vendor_context, self.campaign_frame
        )
        if narrative:
            description_text = narrative + "\n\n" + description_text

    self.encounter_details_text.setPlainText(description_text)
    self.encounters_list.setVisible(False)
    self.monsters_frame.setVisible(False)
```

### Summary of Base UI Changes
1. **6% chance no vendor** - Roll 01-06 = empty wilderness, no shop
2. **Settlement-based shops** - Roll determines shop size (hamlet/village/town)
3. **Charisma pricing** - Each vendor generation rolls character skills
4. **Fresh inventory** - New stock/prices each time you click "Generate Encounter"
5. **Descriptive text** - Shows negotiation results to player

This makes the non-hex vendor system consistent with the hex-based system!

## IMPLEMENTATION COMPLETE SUMMARY (Oct 19, 2025)

### ✅ All Core Features Implemented

The vendor system has been **fully implemented** with all planned features:

**Phase 1: Database & Core Service** - COMPLETE
- ✅ Created migration 037_hex_settlements.sql (for existing databases)
- ✅ Updated migration 010_hex_map_system.sql (for new databases)
- ✅ **Migration applied** - settlement_type column added to character_hex_map
- ✅ Implemented settlement generation in HexMapService._generate_hex()
- ✅ Added get_hex_settlement() helper method
- ✅ Implemented ShopService.generate_hex_shop_inventory()
- ✅ Added get_charisma_skill_roll() with Persuasion/Deception/Intimidation
- ✅ Added has_crafter_feat() method
- ✅ Added calculate_sell_price_with_character() with per-item rolls
- ✅ Implemented settlement-to-shop-size mapping
- ✅ Added variance system (1-200% pool/cap)

**Phase 2: UI Components** - COMPLETE
- ✅ Created HexShopInterface extending ShopInterface
- ✅ Added negotiation info panel to hex shops
- ✅ Added vendor button to HexMapWidget
- ✅ Implemented hex_shop_requested signal
- ✅ Updated encounter panel vendor generation

**Phase 3: Integration** - COMPLETE
- ✅ Wired _on_hex_shop_requested handler in main_window
- ✅ Dialog-based hex shop display
- ✅ Updated _generate_vendor_encounter() with settlement rolls
- ✅ Added 6% "no vendor" wilderness result
- ✅ Pre-haggled pricing display with negotiation results

**Phase 4: Testing** - COMPLETE
- ✅ Created comprehensive test suite (tests/test_vendor_system.py)
- ✅ 14 unit tests covering all systems
- ✅ All tests passing (settlement generation, pricing, skills, feats)

### Implementation Files Created/Modified

**New Files:**
- database/migrations/037_hex_settlements.sql (ALTER TABLE migration for existing databases)
- tests/test_vendor_system.py
- src/talekeeper/ui/encounter_pane/hex_shop_interface.py

**Modified Files:**
- database/migrations/010_hex_map_system.sql (added settlement_type column for new databases)
- src/talekeeper/services/hex_map_service.py
- src/talekeeper/services/shop_service.py
- src/talekeeper/ui/hex_map/hex_map_widget.py
- src/talekeeper/ui/main_window.py
- src/talekeeper/ui/encounter_pane/encounter_panel.py

### Database Migration Strategy

**For Existing Databases:**
- Run migration 037_hex_settlements.sql to ALTER TABLE and add settlement_type column
- Command: `sqlite3 talekeeper.db < database/migrations/037_hex_settlements.sql`

**For New Databases:**
- Migration 010_hex_map_system.sql now includes settlement_type in CREATE TABLE
- New databases created from scratch will have the column automatically

**Verification:**
```bash
# Check if column exists
sqlite3 talekeeper.db "PRAGMA table_info(character_hex_map);" | grep settlement_type

# Expected output line 14:
# 14|settlement_type|TEXT|0||0
```

### Feature Completion Status: 100%

All features from the planning document have been implemented:
- ✅ Settlement generation (d100 table with town sub-rolls)
- ✅ Charisma-based dynamic pricing
- ✅ Crafter feat integration (+20% discount)
- ✅ Hex-specific shop variance (1-200%)
- ✅ Settlement-to-shop-size mapping
- ✅ Skill roll negotiation mechanics
- ✅ Database schema for settlements
- ✅ Hex map vendor UI integration
- ✅ HexShopInterface component
- ✅ Pre-haggled pricing display
- ✅ Variance system (pool/cap modifiers)
- ✅ Per-item sell price rolling

## IMPLEMENTATION STATUS & ISSUES (As of Oct 2025)

**NOTE: This section reflects the ORIGINAL status before implementation. See above summary for current status.**

### Critical Implementation Gaps

#### [CRITICAL] Missing Database Schema
**Status**: ✅ COMPLETED
**File**: database/migrations/037_hex_settlements.sql
**Issue**: The `character_hex_map` table does NOT have a `settlement_type` column
- Current schema only includes: `terrain_type`, `biome`, `encounter_seed`
- Documentation expects: `settlement_type` column storing 'empty', 'hamlet', 'village', 'town_small', 'town_medium', 'town_large'
- Missing migration: `011_hex_settlements.sql` (referenced in documentation but does not exist)
**Impact**: Hex-based vendor system cannot function without this column. Settlement data has nowhere to persist.
**Resolution**: Created migration 037_hex_settlements.sql with:
  - ALTER TABLE character_hex_map ADD COLUMN settlement_type TEXT
  - CREATE INDEX idx_hex_settlement ON character_hex_map(character_id, settlement_type)

#### [CRITICAL] No Settlement Generation Logic
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/hex_map_service.py:75-111
**Issue**: `_generate_hex()` method only generates terrain and biome, no settlement logic
- Current: `random.choice(TERRAIN_TYPES)` for terrain only
- Expected: d100 roll for settlement type (01-06=empty, 07-31=hamlet, 32-99=village, 100=town)
- Expected: Sub-roll d6 for town size when d100=100
- Expected: Deterministic using hex seed for consistent settlements per hex
**Impact**: Hexes never generate settlement data. Vendor availability cannot be determined.
**Resolution Required**: Add settlement generation to `_generate_hex()` matching documented d100 table

#### [HIGH] Missing Charisma-Based Pricing System
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py:57-99
**Issue**: Service uses fixed 25% markup and 50% sell-back with no character interaction
- Current `generate_shop_inventory()`: Accepts `markup_percent` parameter (defaults to 25.0)
- Current `calculate_sell_price()`: Hardcoded `item_cost * 0.5` return
- Documentation expects (vendors_planning.md:329-381):
  - `generate_hex_shop_inventory(settlement_type, character_data, hex_seed)`
  - Buy formula: 25% - Charisma_Roll% - (20% if Crafter)
  - Sell formula: 40% + Charisma_Roll% (capped at 100%)
  - Variance system: pool_variance and cap_variance (1-200%)
**Impact**: No negotiation mechanics. Player skills irrelevant to shop prices. Hex-specific variance impossible.
**Resolution Required**:
- Add `generate_hex_shop_inventory()` method
- Add `get_charisma_skill_roll(character_data)` method
- Add `has_crafter_feat(character_data)` method
- Rewrite `calculate_sell_price()` to accept character_data and roll per item

#### [HIGH] calculate_sell_price Ignores Character Context
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py:96
**Issue**: Method signature is `calculate_sell_price(item_cost: float)` with no character data
- Current: Returns hardcoded 50% (`item_cost * 0.5`)
- Documentation expects (vendors_planning.md:383-389):
  - Signature: `calculate_sell_price(item_cost, character_data)`
  - Roll charisma skills (Persuasion, Deception, Intimidation) - use highest
  - Formula: 40% + skill_roll% (max 100%)
  - Each item sold gets its own roll
**Impact**: UI cannot display negotiation results. Selling is always 50% regardless of character build.
**Resolution Required**: Change method signature, add skill rolling logic, implement per-item rolls

#### [HIGH] ShopInterface Not Adapted for Hex System
**Status**: PARTIAL IMPLEMENTATION
**File**: src/talekeeper/ui/encounter_pane/town_encounter.py:1258, 1616
**Issue**: `ShopInterface` still uses old shop_price_gp/shop_price_display pattern
- Current line 1258: `self.shop_inventory = self.shop_service.generate_shop_inventory(self.shop_size)`
- Current line 1616: `price_gp = item_data['shop_price_gp']`
- Documentation expects:
  - Work with hex-aware payload: `buy_price_gp`, `charisma_roll`, `has_crafter`, variance values
  - Display negotiation results to player
  - Show markup/discount percentages
**Impact**: Even if service is updated, UI has no way to display new pricing data or negotiation info.
**Resolution Required**:
- Update `ShopInterface.__init__()` to accept shop_data dict
- Modify item display to show `buy_price_gp` instead of `shop_price_gp`
- Add negotiation info display (charisma roll, discounts applied)

#### [HIGH] Encounter Panel Vendor Uses Old Logic
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/ui/encounter_pane/encounter_panel.py:4463
**Issue**: `_generate_vendor_encounter()` does not implement documented settlement system
- Current: Randomly picks SMALL/MEDIUM/LARGE shop size
- Documentation expects (vendors_planning.md:485-538):
  - Roll d100 for settlement type
  - 01-06: No vendor, display wilderness message
  - 07-31: Hamlet (SMALL shop)
  - 32-99: Village (MEDIUM shop)
  - 100: Town (roll d6 for size, LARGE shop)
  - Generate with `generate_hex_shop_inventory()`
  - Display charisma negotiation results
  - Use narrative service for vendor description
**Impact**: Non-hex vendor encounters inconsistent with design. No "empty wilderness" result. No settlement flavor.
**Resolution Required**: Replace method implementation to match documented flow

#### [HIGH] No Hex Map Vendor Integration
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/ui/hex_map/hex_map_widget.py
**Issue**: No vendor UI or signals in hex map widget
- Documentation expects (vendors_planning.md:394-472):
  - Vendor button when `settlement_type != 'empty'`
  - Signal: `hex_shop_requested = pyqtSignal(int, int, str)` for (q, r, settlement_type)
  - Method: `_open_hex_shop(q, r, settlement_type)`
  - Settlement-specific messaging in info panel
- Current: No vendor-related code exists in file
**Impact**: Players cannot access vendors from hex map. Hex exploration and vendor system completely disconnected.
**Resolution Required**:
- Add `hex_shop_requested` signal
- Add vendor button to `_update_info_panel()` when settlement exists
- Implement `_open_hex_shop()` method
- Wire signal to main_window

#### [HIGH] Missing HexShopInterface Class
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/ui/encounter_pane/hex_shop_interface.py (DOES NOT EXIST)
**Issue**: Documentation describes full class but file does not exist
- Documentation expects (vendors_planning.md:452-473):
  - Class: `HexShopInterface(ShopInterface)`
  - Constructor accepts: character_data, settlement_type, hex_seed, hex_coords
  - Generates hex-specific inventory on initialization
  - Overrides inventory with charisma-priced items
- Current: No file, no class, no implementation
**Impact**: Even with hex map button, there's no component to open. Hex-vendor flow broken.
**Resolution Required**: Create new file and implement HexShopInterface class extending ShopInterface

#### [HIGH] Main Window Missing Hex Shop Handler
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/ui/main_window.py
**Issue**: No signal connection or handler for hex shop requests
- Documentation expects (vendors_planning.md:419-449):
  - Method: `_open_hex_shop(q, r, settlement_type)`
  - Get hex seed from HexMapService
  - Create HexShopInterface instance
  - Display as overlay or replace encounter pane
  - Connect `shopping_completed` signal
- Current: No hex shop code exists in main_window
**Impact**: Signal chain broken. No pathway from hex map click to shop display.
**Resolution Required**: Add signal connection in hex map setup, implement handler method

### Medium Priority Issues

#### [MEDIUM] No Skill Proficiency Query System
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py
**Issue**: Cannot retrieve character skill bonuses for Persuasion/Deception/Intimidation
- Expected: Query `character_proficiencies` table and calculate skill modifiers
- Expected: d20 + skill_bonus for each charisma skill
- Expected: Return highest of three rolls
- Current: No database query, no skill calculation, no roll logic
**Impact**: Cannot implement charisma-based pricing formula
**Resolution Required**:
- Add database query to get skill proficiencies
- Calculate ability modifier + proficiency bonus
- Implement d20 roll + modifiers for each skill
- Return max(Persuasion_roll, Deception_roll, Intimidation_roll)

#### [MEDIUM] No Crafter Feat Check
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py
**Issue**: Cannot determine if character has Crafter feat for 20% discount
- Expected: Query `character_feats` table WHERE feat_name = 'Crafter'
- Expected: Return boolean for feat ownership
- Current: No implementation
**Impact**: Crafter feat bonus (+20% discount) not applied to buy prices
**Resolution Required**: Add `has_crafter_feat(character_data)` method querying character_feats

#### [MEDIUM] Town Encounter Shop Selection Manual
**Status**: INCORRECT IMPLEMENTATION
**File**: src/talekeeper/ui/encounter_pane/town_encounter.py:1967-2026
**Issue**: `_show_shop()` presents manual shop size dialog to player
- Current: Radio buttons for Small/Medium/Large shop selection
- Expected: Town context should automatically determine shop tier
- Impact: Breaks immersion. Player chooses shop wealth instead of discovering it.
**Resolution Required**: Remove shop size dialog, auto-determine size from town/settlement context

#### [MEDIUM] No Settlement-to-ShopSize Mapping
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py
**Issue**: No automatic mapping from settlement type to ShopSize enum
- Documentation defines (vendors_planning.md:347-354):
  - hamlet -> ShopSize.SMALL (20 GP max)
  - village -> ShopSize.MEDIUM (200 GP max)
  - town_small/medium/large -> ShopSize.LARGE (2000 GP max)
- Current: Manual ShopSize selection only
**Impact**: Settlement economic tiers not enforced. Hamlets could have expensive items.
**Resolution Required**: Add mapping dict in `generate_hex_shop_inventory()`

#### [MEDIUM] No Pool/Cap Variance System
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/services/shop_service.py
**Issue**: Shop limits are fixed per size, no variance between visits
- Documentation expects (vendors_planning.md:28-34):
  - Purchasing Pool: Base Pool × (1-200%)
  - Price Cap: Base Cap × (1-200%)
  - Premium items: 50% of cap, 1-8 items
  - High-value items: 50-100% of cap, 1-8 items
- Current: Fixed limits from ShopSize enum (20/200/2000)
**Impact**: All shops of same size feel identical. No variety between visits to same hex.
**Resolution Required**: Add variance rolling to `generate_hex_shop_inventory()` using hex_seed

#### [MEDIUM] Incomplete Vendor Narrative Integration
**Status**: PARTIAL IMPLEMENTATION
**File**: src/talekeeper/ui/encounter_pane/encounter_panel.py:4479-4500
**Issue**: Vendor encounter has narrative stub but missing context
- Current: Basic vendor_context dict with shop_size and inventory_count
- Documentation expects (vendors_planning.md:563-578):
  - settlement_type in context
  - charisma_roll value
  - has_crafter boolean
  - character_level
  - Negotiation results in description text
  - Pre-haggled price summary
**Impact**: Less immersive vendor encounters, missing skill feedback
**Resolution Required**: Expand vendor_context and add negotiation text to narrative

### Architectural Issues

#### [LOW] Duplicate shop_service.py Outside Package
**Status**: TECHNICAL DEBT
**File**: services/shop_service.py (root) vs src/talekeeper/services/shop_service.py
**Issue**: Two copies of ShopService exist, tests import the root copy
- Root path: services/shop_service.py
- Package path: src/talekeeper/services/shop_service.py
- Test imports: test/test_shop_system.py and test/test_shop_integration.py import root copy
**Impact**: Code maintenance burden. Fixes to package version not tested. Sync issues.
**Resolution Required**:
- Consolidate to single location (package path)
- Update test imports to use talekeeper.services.shop_service
- Delete root copy after migration

#### [LOW] No Pre-Haggled UI Display
**Status**: NOT IMPLEMENTED
**File**: src/talekeeper/ui/encounter_pane/town_encounter.py:1236-1436
**Issue**: ShopInterface doesn't show negotiation results
- Documentation expects (vendors_planning.md:151-166):
  - Show one-time charisma roll used for all buy prices
  - Display final markup percentage
  - Show Crafter feat bonus if applicable
  - Display "Pre-haggled prices" message
- Current: No negotiation info displayed, prices appear without context
**Impact**: Player doesn't understand why prices vary or how their skills affected prices
**Resolution Required**: Add negotiation info section to shop UI

### Documentation vs Implementation Drift

#### Overall Implementation Status: ~15%

**Implemented Features (15%)**:
- Basic shop inventory generation (ShopService.generate_shop_inventory)
- Buy/sell interface (ShopInterface widget)
- Hex map coordinate system (HexMapService, HexCoordinateSystem)
- Equipment database (EquipmentDatabase)
- Fixed-price transactions

**NOT Implemented Features (85%)**:
- Settlement generation system (0%)
- Charisma-based dynamic pricing (0%)
- Crafter feat integration (0%)
- Hex-specific shop variance (0%)
- Settlement-to-shop-size mapping (0%)
- Skill roll negotiation mechanics (0%)
- Database schema for settlements (0%)
- Hex map vendor UI integration (0%)
- HexShopInterface component (0%)
- Pre-haggled pricing display (0%)
- Variance system (pool/cap modifiers) (0%)
- Per-item sell price rolling (0%)

### Estimated Implementation Effort

**Phase 1: Database & Core Service (12-16 hours)**
- Create 011_hex_settlements.sql migration
- Update HexMapService._generate_hex() with settlement logic
- Implement ShopService.generate_hex_shop_inventory()
- Add skill rolling and Crafter feat checks
- Rewrite calculate_sell_price() with character context

**Phase 2: UI Components (16-20 hours)**
- Create HexShopInterface class
- Update ShopInterface for negotiation display
- Add vendor button to HexMapWidget
- Implement hex_shop_requested signal chain
- Update encounter panel vendor generation

**Phase 3: Integration & Polish (8-12 hours)**
- Wire main_window hex shop handler
- Update town encounter auto-sizing
- Add pre-haggled pricing UI
- Implement variance system display
- Narrative service integration

**Phase 4: Testing & Consolidation (4-8 hours)**
- Consolidate duplicate shop_service.py files
- Update test suite for new pricing
- Test hex-to-vendor flow end-to-end
- Verify settlement persistence across hex revisits

**Total Estimated Effort**: 40-56 hours

### Critical Path to MVP

To get a minimally functional hex vendor system:
1. Add settlement_type column (1 hour)
2. Implement settlement generation in _generate_hex() (2 hours)
3. Create basic generate_hex_shop_inventory() without variance (3 hours)
4. Add hex vendor button to hex map widget (2 hours)
5. Create minimal HexShopInterface (3 hours)
6. Wire signal to main_window (1 hour)
**MVP Estimate**: 12 hours

This would provide hex-based vendors with settlement types but NO charisma pricing or variance.

### Recommendations

**Immediate Actions**:
1. Update documentation to reflect current implementation status (mark features as PLANNED vs IMPLEMENTED)
2. Create database migration for settlement_type column
3. Decide: Full implementation or scale back design to match resources

**Decision Point**:
The current documentation represents an aspirational design, not implemented reality. Team should decide whether to:
- **Option A**: Commit 40-60 hours to full implementation
- **Option B**: Scale back design to match current ~15% implementation and update docs accordingly
- **Option C**: Implement MVP (12 hours) and iterate based on player feedback

**Technical Debt**:
- Consolidate duplicate shop_service.py files before any major work
- Add integration tests for vendor flow before implementing charisma pricing
- Consider feature flag system to enable hex vendors incrementally
