"""
File: backend/routers/items.py
Path: /backend/routers/items.py

Pseudo Code:
1. Get equipment: return all available items filtered by type/rarity
2. Equip/unequip: manage character equipment slots, calculate AC/stats
3. Shop system: list vendor items, handle buy/sell transactions
4. Loot generation: create random loot from monster tables
5. Inventory management: track weight, identify items, organize storage
6. Item crafting: combine materials, upgrade equipment (future)

Items and Equipment Router
Handles inventory, equipment slots, shopping, and loot management.

AI Agents: Key endpoints:
- GET /equipment - Get all available equipment/items
- POST /equip - Equip/unequip items on character
- GET /shop - Get shop inventory with pricing
- POST /purchase - Buy items from vendors
- POST /sell - Sell items to vendors
- POST /loot - Generate loot from defeated monsters
- GET /inventory/{character_id} - Get character inventory
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc, func
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
import json
from loguru import logger
from datetime import datetime
from enum import Enum

from database import get_db, GameQueries
from models.character import Character
from models.items import (
    Item, CharacterInventory, ShopInventory, LootTable,
    ItemType, ItemRarity, EquipmentSlot,
    EquipItemRequest, PurchaseItemRequest, SellItemRequest,
    LootGenerationRequest, ItemResponse, InventoryResponse
)
from models.game import GameState
from models.monsters import Monster
from services.dice import DiceRoller
from services.item_service import ItemService

router = APIRouter()
dice = DiceRoller()

class ShopType(str, Enum):
    GENERAL_STORE = "general_store"
    WEAPON_SMITH = "weapon_smith"
    ARMOR_SMITH = "armor_smith"
    MAGIC_SHOP = "magic_shop"
    TAVERN = "tavern"

@router.get("/equipment", response_model=List[ItemResponse])
async def get_equipment(
    item_type: Optional[ItemType] = None,
    rarity: Optional[ItemRarity] = None,
    max_cost: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all available equipment and items.
    
    Filter by type, rarity, or cost for specific needs.
    
    AI Agents: Use for:
    - Character creation equipment selection
    - Shop inventory filtering
    - Loot table generation
    """
    try:
        query = select(Item)
        
        # Apply filters
        if item_type:
            query = query.where(Item.type == item_type)
        if rarity:
            query = query.where(Item.rarity == rarity)
        if max_cost:
            query = query.where(Item.cost_gp <= max_cost)
        
        items = db.execute(query.order_by(Item.type, Item.cost_gp)).scalars().all()
        
        return [
            ItemResponse(
                id=item.id,
                name=item.name,
                type=item.type,
                subtype=item.subtype,
                rarity=item.rarity,
                cost_gp=float(item.cost_gp) if item.cost_gp else 0,
                weight=float(item.weight) if item.weight else 0,
                description=item.description,
                properties=item.properties or {},
                requirements=item.requirements or {},
                effects=item.effects or {},
                armor_class=item.armor_class,
                damage_dice=item.damage_dice,
                damage_type=item.damage_type,
                range_normal=item.range_normal,
                range_long=item.range_long,
                is_magical=item.is_magical or False,
                attunement_required=item.attunement_required or False
            )
            for item in items
        ]
        
    except Exception as e:
        logger.error(f"Error getting equipment: {e}")
        raise HTTPException(status_code=500, detail="Failed to get equipment")

@router.post("/equip", response_model=Dict[str, Any])
async def equip_item(
    equip_data: EquipItemRequest,
    db: Session = Depends(get_db)
):
    """
    Equip or unequip an item on a character.
    
    Handles equipment slots, stat calculations, and restrictions.
    
    AI Agents: Extend for:
    - Attunement requirements
    - Class/race restrictions
    - Set bonuses for matching equipment
    """
    try:
        character = db.get(Character, equip_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get character's inventory item
        inventory_item = db.execute(
            select(CharacterInventory).where(
                and_(
                    CharacterInventory.character_id == equip_data.character_id,
                    CharacterInventory.item_id == equip_data.item_id
                )
            )
        ).scalar_one_or_none()
        
        if not inventory_item:
            raise HTTPException(status_code=404, detail="Item not found in character inventory")
        
        item = db.get(Item, equip_data.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        service = ItemService(db)
        
        if equip_data.equip:
            # Equipping item
            result = service.equip_item(character, inventory_item, item, equip_data.slot)
            
            if result["success"]:
                # Update character stats
                service.recalculate_character_stats(character)
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Equipped {item.name}",
                    "equipped_slot": result["slot"],
                    "unequipped_items": result.get("unequipped_items", []),
                    "new_armor_class": character.armor_class,
                    "stat_changes": result.get("stat_changes", {})
                }
            else:
                raise HTTPException(status_code=400, detail=result["message"])
        
        else:
            # Unequipping item
            if not inventory_item.equipped:
                raise HTTPException(status_code=400, detail="Item is not equipped")
            
            old_slot = inventory_item.equipped_slot
            inventory_item.equipped = False
            inventory_item.equipped_slot = None
            
            # Recalculate stats without this item
            service.recalculate_character_stats(character)
            db.commit()
            
            return {
                "success": True,
                "message": f"Unequipped {item.name}",
                "unequipped_slot": old_slot,
                "new_armor_class": character.armor_class
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error equipping item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to equip/unequip item")

@router.get("/shop/{shop_type}", response_model=Dict[str, Any])
async def get_shop_inventory(
    shop_type: ShopType,
    character_level: int = 1,
    db: Session = Depends(get_db)
):
    """
    Get shop inventory based on shop type and character level.
    
    Different shops stock different items appropriate to character level.
    
    AI Agents: Extend for:
    - Dynamic pricing based on character reputation
    - Limited stock that replenishes over time
    - Seasonal or event-based special items
    """
    try:
        # Base shop inventories
        shop_items = []
        
        if shop_type == ShopType.GENERAL_STORE:
            # Basic adventuring gear
            basic_items = db.execute(
                select(Item).where(
                    and_(
                        Item.type.in_([ItemType.GEAR, ItemType.CONSUMABLE]),
                        Item.rarity == ItemRarity.COMMON,
                        Item.cost_gp <= 100
                    )
                )
            ).scalars().all()
            shop_items.extend(basic_items)
            
        elif shop_type == ShopType.WEAPON_SMITH:
            # Weapons appropriate to character level
            max_cost = 50 + (character_level * 100)
            weapons = db.execute(
                select(Item).where(
                    and_(
                        Item.type == ItemType.WEAPON,
                        Item.cost_gp <= max_cost
                    )
                )
            ).scalars().all()
            shop_items.extend(weapons)
            
        elif shop_type == ShopType.ARMOR_SMITH:
            # Armor appropriate to character level
            max_cost = 100 + (character_level * 150)
            armor = db.execute(
                select(Item).where(
                    and_(
                        Item.type == ItemType.ARMOR,
                        Item.cost_gp <= max_cost
                    )
                )
            ).scalars().all()
            shop_items.extend(armor)
            
        elif shop_type == ShopType.MAGIC_SHOP:
            # Magic items (higher level characters only)
            if character_level >= 3:
                magic_items = db.execute(
                    select(Item).where(
                        and_(
                            Item.is_magical == True,
                            Item.rarity.in_([ItemRarity.COMMON, ItemRarity.UNCOMMON])
                        )
                    )
                ).scalars().all()
                shop_items.extend(magic_items[:5])  # Limited selection
            
        elif shop_type == ShopType.TAVERN:
            # Food, drink, lodging
            tavern_items = [
                {"name": "Ale", "cost": 4, "type": "consumable", "description": "A mug of ale"},
                {"name": "Meal", "cost": 10, "type": "consumable", "description": "A hearty meal"},
                {"name": "Room for the night", "cost": 20, "type": "service", "description": "Rest at the inn"},
                {"name": "Rations (1 day)", "cost": 2, "type": "gear", "description": "Trail rations"}
            ]
            
            return {
                "shop_type": shop_type,
                "shop_name": _get_shop_name(shop_type),
                "items": tavern_items,
                "character_level": character_level,
                "special_offers": []
            }
        
        # Convert items to shop format
        shop_inventory = []
        for item in shop_items:
            # Apply level-based pricing adjustments
            price_modifier = 1.0
            if character_level <= 1:
                price_modifier = 0.8  # Discount for new characters
            elif character_level >= 5:
                price_modifier = 1.2  # Premium pricing for high-level characters
            
            final_price = int(float(item.cost_gp or 0) * price_modifier)
            
            shop_inventory.append({
                "id": str(item.id),
                "name": item.name,
                "type": item.type,
                "subtype": item.subtype,
                "rarity": item.rarity,
                "cost": final_price,
                "original_cost": float(item.cost_gp) if item.cost_gp else 0,
                "description": item.description,
                "properties": item.properties or {},
                "in_stock": True,  # AI Agents: Implement stock tracking
                "quantity_available": 99  # AI Agents: Implement limited quantities
            })
        
        # Add special offers based on character level
        special_offers = []
        if character_level == 1:
            special_offers.append({
                "name": "Starter Kit Discount",
                "description": "20% off basic gear for new adventurers",
                "discount": 0.2
            })
        
        return {
            "shop_type": shop_type,
            "shop_name": _get_shop_name(shop_type),
            "items": shop_inventory,
            "character_level": character_level,
            "special_offers": special_offers,
            "shop_keeper_greeting": _get_shop_greeting(shop_type, character_level)
        }
        
    except Exception as e:
        logger.error(f"Error getting shop inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get shop inventory")

@router.post("/purchase", response_model=Dict[str, Any])
async def purchase_item(
    purchase_data: PurchaseItemRequest,
    db: Session = Depends(get_db)
):
    """
    Purchase an item from a shop.
    
    Handles gold transactions and adds item to character inventory.
    
    AI Agents: Extend for:
    - Bulk purchasing discounts
    - Trade-in values for old equipment
    - Reputation-based pricing
    """
    try:
        character = db.get(Character, purchase_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        item = db.get(Item, purchase_data.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Get character's game state for gold
        game_state = db.execute(
            select(GameState).where(GameState.character_id == purchase_data.character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")
        
        # Calculate final price (with any modifiers)
        base_cost = float(item.cost_gp) if item.cost_gp else 0
        quantity = purchase_data.quantity or 1
        total_cost = int(base_cost * quantity)
        
        # Apply level-based pricing
        if character.level <= 1:
            total_cost = int(total_cost * 0.8)  # New character discount
        elif character.level >= 5:
            total_cost = int(total_cost * 1.2)  # High-level pricing
        
        # Check if character has enough gold
        if game_state.inventory_gold < total_cost:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient gold. Need {total_cost}, have {game_state.inventory_gold}"
            )
        
        # Deduct gold
        game_state.inventory_gold -= total_cost
        
        # Add item to inventory or increase quantity
        existing_item = db.execute(
            select(CharacterInventory).where(
                and_(
                    CharacterInventory.character_id == purchase_data.character_id,
                    CharacterInventory.item_id == purchase_data.item_id
                )
            )
        ).scalar_one_or_none()
        
        if existing_item:
            existing_item.quantity += quantity
            inventory_item = existing_item
        else:
            inventory_item = CharacterInventory(
                character_id=purchase_data.character_id,
                item_id=purchase_data.item_id,
                quantity=quantity,
                equipped=False,
                identified=True,  # Shop items are identified
                acquired_at=datetime.utcnow(),
                notes=f"Purchased from {purchase_data.shop_type or 'shop'}"
            )
            db.add(inventory_item)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Purchased {quantity}x {item.name} for {total_cost} gold",
            "item": {
                "id": str(item.id),
                "name": item.name,
                "quantity": quantity
            },
            "cost": total_cost,
            "remaining_gold": game_state.inventory_gold,
            "inventory_updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to purchase item")

@router.post("/sell", response_model=Dict[str, Any])
async def sell_item(
    sell_data: SellItemRequest,
    db: Session = Depends(get_db)
):
    """
    Sell an item from character inventory.
    
    Items sell for 50% of their original value (D&D standard).
    
    AI Agents: Extend for:
    - Different sell rates by shop type
    - Condition-based pricing
    - Rare item negotiations
    """
    try:
        character = db.get(Character, sell_data.character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get inventory item
        inventory_item = db.execute(
            select(CharacterInventory).where(
                and_(
                    CharacterInventory.character_id == sell_data.character_id,
                    CharacterInventory.item_id == sell_data.item_id
                )
            )
        ).scalar_one_or_none()
        
        if not inventory_item:
            raise HTTPException(status_code=404, detail="Item not found in inventory")
        
        quantity_to_sell = sell_data.quantity or 1
        if inventory_item.quantity < quantity_to_sell:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough items. Have {inventory_item.quantity}, trying to sell {quantity_to_sell}"
            )
        
        item = db.get(Item, sell_data.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Calculate sell price (50% of original value)
        base_value = float(item.cost_gp) if item.cost_gp else 0
        sell_price = int(base_value * 0.5 * quantity_to_sell)
        
        # Can't sell equipped items
        if inventory_item.equipped and quantity_to_sell >= inventory_item.quantity:
            raise HTTPException(status_code=400, detail="Cannot sell equipped item. Unequip first.")
        
        # Get game state for gold
        game_state = db.execute(
            select(GameState).where(GameState.character_id == sell_data.character_id)
        ).scalar_one_or_none()
        
        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")
        
        # Update inventory
        inventory_item.quantity -= quantity_to_sell
        
        # Remove item if quantity reaches 0
        if inventory_item.quantity <= 0:
            db.delete(inventory_item)
        
        # Add gold
        game_state.inventory_gold += sell_price
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Sold {quantity_to_sell}x {item.name} for {sell_price} gold",
            "item": {
                "id": str(item.id),
                "name": item.name,
                "quantity_sold": quantity_to_sell
            },
            "gold_received": sell_price,
            "total_gold": game_state.inventory_gold,
            "item_removed": inventory_item.quantity <= 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selling item: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to sell item")

@router.post("/loot", response_model=Dict[str, Any])
async def generate_loot(
    loot_data: LootGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate loot from defeated monsters or treasure chests.
    
    Uses loot tables based on monster CR and character level.
    
    AI Agents: Extend for:
    - Themed loot based on monster type
    - Magic item identification mechanics
    - Cursed items with hidden effects
    """
    try:
        # Get monster for loot table (if specified)
        monster = None
        if loot_data.monster_id:
            monster = db.get(Monster, loot_data.monster_id)
            if not monster:
                raise HTTPException(status_code=404, detail="Monster not found")
        
        character_level = loot_data.character_level or 1
        loot_generated = []
        total_gold = 0
        
        # Generate gold based on source
        if monster:
            # Gold based on monster CR
            cr = monster.challenge_rating
            gold_dice = max(1, int(cr * 2))
            total_gold = dice.roll(f"{gold_dice}d6") * 5
        else:
            # Generic treasure
            total_gold = dice.roll(f"{character_level}d10") * 10
        
        if total_gold > 0:
            loot_generated.append({
                "type": "currency",
                "name": "Gold Pieces",
                "quantity": total_gold,
                "value": total_gold,
                "rarity": "common"
            })
        
        # Generate items based on character level and source
        item_chance = 30  # Base 30% chance for items
        if monster and monster.challenge_rating >= 1:
            item_chance += int(monster.challenge_rating * 15)  # Higher CR = better loot
        
        item_roll = dice.roll("1d100")
        if item_roll <= item_chance:
            # Determine item rarity based on character level
            rarity_roll = dice.roll("1d100")
            
            if character_level <= 2:
                # Low level: mostly common items
                if rarity_roll <= 80:
                    target_rarity = ItemRarity.COMMON
                else:
                    target_rarity = ItemRarity.UNCOMMON
            elif character_level <= 5:
                # Mid level: common and uncommon
                if rarity_roll <= 60:
                    target_rarity = ItemRarity.COMMON
                elif rarity_roll <= 95:
                    target_rarity = ItemRarity.UNCOMMON
                else:
                    target_rarity = ItemRarity.RARE
            else:
                # High level: all rarities possible
                if rarity_roll <= 40:
                    target_rarity = ItemRarity.COMMON
                elif rarity_roll <= 70:
                    target_rarity = ItemRarity.UNCOMMON
                elif rarity_roll <= 90:
                    target_rarity = ItemRarity.RARE
                else:
                    target_rarity = ItemRarity.VERY_RARE
            
            # Find items of target rarity
            suitable_items = db.execute(
                select(Item).where(
                    and_(
                        Item.rarity == target_rarity,
                        Item.cost_gp <= character_level * 200  # Level-appropriate cost
                    )
                )
            ).scalars().all()
            
            if suitable_items:
                selected_item = dice.choice(suitable_items)
                loot_generated.append({
                    "type": "item",
                    "id": str(selected_item.id),
                    "name": selected_item.name,
                    "item_type": selected_item.type,
                    "rarity": selected_item.rarity,
                    "quantity": 1,
                    "value": float(selected_item.cost_gp) if selected_item.cost_gp else 0,
                    "identified": not selected_item.is_magical,  # Magic items need identification
                    "description": selected_item.description
                })
        
        # Consumable items (potions, scrolls) have separate chance
        consumable_roll = dice.roll("1d100")
        if consumable_roll <= 25:  # 25% chance for consumables
            consumables = db.execute(
                select(Item).where(
                    and_(
                        Item.type == ItemType.CONSUMABLE,
                        Item.rarity.in_([ItemRarity.COMMON, ItemRarity.UNCOMMON])
                    )
                )
            ).scalars().all()
            
            if consumables:
                selected_consumable = dice.choice(consumables)
                quantity = dice.roll("1d3")  # 1-3 consumables
                loot_generated.append({
                    "type": "item",
                    "id": str(selected_consumable.id),
                    "name": selected_consumable.name,
                    "item_type": selected_consumable.type,
                    "rarity": selected_consumable.rarity,
                    "quantity": quantity,
                    "value": float(selected_consumable.cost_gp) if selected_consumable.cost_gp else 0,
                    "identified": True,
                    "description": selected_consumable.description
                })
        
        # Calculate total loot value
        total_value = sum(item["value"] * item["quantity"] for item in loot_generated)
        
        return {
            "success": True,
            "loot_source": f"Monster: {monster.name}" if monster else "Treasure",
            "character_level": character_level,
            "items_generated": loot_generated,
            "total_items": len(loot_generated),
            "total_value": total_value,
            "generation_method": "random_tables"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating loot: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate loot")

@router.get("/inventory/{character_id}", response_model=InventoryResponse)
async def get_character_inventory(
    character_id: UUID,
    include_equipped: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get character's complete inventory with equipment status.
    
    AI Agents: Use for inventory management UI and encumbrance calculations.
    """
    try:
        character = db.get(Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get all inventory items
        inventory_query = select(CharacterInventory, Item).join(
            Item, CharacterInventory.item_id == Item.id
        ).where(CharacterInventory.character_id == character_id)
        
        if not include_equipped:
            inventory_query = inventory_query.where(CharacterInventory.equipped == False)
        
        inventory_data = db.execute(inventory_query).all()
        
        # Organize items by category
        equipped_items = {}
        unequipped_items = []
        total_weight = 0
        total_value = 0
        
        for inv_item, item in inventory_data:
            item_data = {
                "inventory_id": str(inv_item.id),
                "item_id": str(item.id),
                "name": item.name,
                "type": item.type,
                "subtype": item.subtype,
                "rarity": item.rarity,
                "quantity": inv_item.quantity,
                "weight_each": float(item.weight) if item.weight else 0,
                "weight_total": (float(item.weight) if item.weight else 0) * inv_item.quantity,
                "value_each": float(item.cost_gp) if item.cost_gp else 0,
                "value_total": (float(item.cost_gp) if item.cost_gp else 0) * inv_item.quantity,
                "equipped": inv_item.equipped,
                "equipped_slot": inv_item.equipped_slot,
                "identified": inv_item.identified,
                "description": item.description,
                "properties": item.properties or {},
                "is_magical": item.is_magical or False,
                "notes": inv_item.notes,
                "acquired_at": inv_item.acquired_at
            }
            
            total_weight += item_data["weight_total"]
            total_value += item_data["value_total"]
            
            if inv_item.equipped:
                slot = inv_item.equipped_slot or "unknown"
                equipped_items[slot] = item_data
            else:
                unequipped_items.append(item_data)
        
        # Calculate carrying capacity (STR score * 15 lbs in D&D 5e)
        carrying_capacity = character.strength * 15
        encumbrance_status = "normal"
        
        if total_weight > carrying_capacity:
            encumbrance_status = "overloaded"
        elif total_weight > carrying_capacity * 0.75:
            encumbrance_status = "heavy"
        elif total_weight > carrying_capacity * 0.5:
            encumbrance_status = "medium"
        
        # Get character's gold
        game_state = db.execute(
            select(GameState).where(GameState.character_id == character_id)
        ).scalar_one_or_none()
        
        current_gold = game_state.inventory_gold if game_state else 0
        
        return InventoryResponse(
            character_id=character_id,
            equipped_items=equipped_items,
            unequipped_items=unequipped_items,
            total_items=len(inventory_data),
            total_weight=total_weight,
            total_value=total_value,
            carrying_capacity=carrying_capacity,
            encumbrance_status=encumbrance_status,
            current_gold=current_gold,
            equipment_slots_used=len(equipped_items),
            equipment_slots_available=_get_available_equipment_slots()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inventory")

def _get_shop_name(shop_type: ShopType) -> str:
    """Get friendly name for shop type."""
    names = {
        ShopType.GENERAL_STORE: "General Store",
        ShopType.WEAPON_SMITH: "The Forge & Blade",
        ShopType.ARMOR_SMITH: "Ironguard Armory",
        ShopType.MAGIC_SHOP: "Mystic Emporium",
        ShopType.TAVERN: "The Prancing Pony"
    }
    return names.get(shop_type, "Shop")

def _get_shop_greeting(shop_type: ShopType, character_level: int) -> str:
    """Get shop keeper greeting based on type and character level."""
    if character_level <= 1:
        greetings = {
            ShopType.GENERAL_STORE: "Welcome, young adventurer! First time out? I've got everything you need to get started.",
            ShopType.WEAPON_SMITH: "Ah, a new face! Looking for your first real weapon? I've got some fine starter blades.",
            ShopType.ARMOR_SMITH: "New to the adventuring life? You'll want some proper protection before heading out.",
            ShopType.MAGIC_SHOP: "Welcome to my humble shop. Perhaps a healing potion for your journeys?",
            ShopType.TAVERN: "Welcome, traveler! Pull up a chair and try our famous stew."
        }
    else:
        greetings = {
            ShopType.GENERAL_STORE: "Welcome back! I see you've gained some experience. Need supplies for your next adventure?",
            ShopType.WEAPON_SMITH: "Ah, a seasoned warrior! I have some fine weapons that might interest you.",
            ShopType.ARMOR_SMITH: "Welcome! I can see you've seen some battles. Perhaps it's time to upgrade your armor?",
            ShopType.MAGIC_SHOP: "Greetings, accomplished adventurer. I have some rare items that might catch your eye.",
            ShopType.TAVERN: "Welcome back, hero! Your usual table is waiting."
        }
    
    return greetings.get(shop_type, "Welcome to my shop!")

def _get_available_equipment_slots() -> List[str]:
    """Get list of all possible equipment slots."""
    return [
        "head", "neck", "chest", "back", "arms", "hands", "waist", "legs", "feet",
        "main_hand", "off_hand", "ring_1", "ring_2", "trinket_1", "trinket_2"
    ]