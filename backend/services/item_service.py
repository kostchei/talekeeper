"""
File: backend/services/item_service.py
Path: /backend/services/item_service.py

Item and inventory management service.
AI Agents: Comprehensive item handling with equipment logic and stat calculations.

Pseudo Code:
1. Handle item equipping/unequipping with slot management
2. Calculate AC and stat bonuses from equipped items
3. Process item buying/selling with shop systems
4. Generate random loot from monster tables
5. Manage inventory weight and carrying capacity
6. Apply magical item effects and properties
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

from models.character import Character
from models.items import Item, CharacterInventory, ItemType, EquipmentSlot
from services.dice import DiceRoller

class ItemService:
    """
    Service for item and inventory management.
    AI Agents: Extend with enchantment, crafting, and item identification systems.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.dice = DiceRoller()
    
    def equip_item(self, character: Character, inventory_item: CharacterInventory, 
                   item: Item, slot: Optional[str] = None) -> Dict[str, Any]:
        """
        Equip an item on a character with full validation and stat updates.
        
        Returns:
            dict: Result with success status, slot used, and any unequipped items
        """
        try:
            # Validate item can be equipped
            if not self._can_equip_item(character, item):
                return {
                    "success": False,
                    "message": f"Cannot equip {item.name} - requirements not met"
                }
            
            # Determine equipment slot
            target_slot = slot or item.equipment_slot
            if not target_slot:
                return {
                    "success": False,
                    "message": f"{item.name} cannot be equipped - no valid slot"
                }
            
            # Check for conflicts and handle unequipping
            unequipped_items = []
            conflict_result = self._handle_equipment_conflicts(character, item, target_slot)
            if not conflict_result["success"]:
                return conflict_result
            unequipped_items = conflict_result.get("unequipped_items", [])
            
            # Equip the item
            inventory_item.equipped = True
            inventory_item.equipped_slot = target_slot
            
            # Handle attunement for magic items
            if item.attunement_required and not inventory_item.attuned:
                attunement_result = self._handle_attunement(character, inventory_item, item)
                if not attunement_result["success"]:
                    inventory_item.equipped = False
                    inventory_item.equipped_slot = None
                    return attunement_result
            
            # Calculate stat changes
            stat_changes = self._calculate_item_stat_effects(item, equipped=True)
            
            return {
                "success": True,
                "slot": target_slot,
                "unequipped_items": unequipped_items,
                "stat_changes": stat_changes,
                "message": f"Equipped {item.name} to {target_slot}"
            }
            
        except Exception as e:
            logger.error(f"Error equipping item: {e}")
            return {
                "success": False,
                "message": f"Failed to equip item: {str(e)}"
            }
    
    def _can_equip_item(self, character: Character, item: Item) -> bool:
        """Check if character meets requirements to equip item."""
        
        # Check class requirements
        if item.requirements and "classes" in item.requirements:
            allowed_classes = item.requirements["classes"]
            if character.character_class.name not in allowed_classes:
                return False
        
        # Check ability score requirements
        if item.requirements and "abilities" in item.requirements:
            for ability, min_score in item.requirements["abilities"].items():
                character_score = getattr(character, ability, 0)
                if character_score < min_score:
                    return False
        
        # Check level requirements
        if item.requirements and "level" in item.requirements:
            if character.level < item.requirements["level"]:
                return False
        
        # Check strength requirement for heavy armor
        if item.type == ItemType.ARMOR and item.strength_requirement:
            if character.strength < item.strength_requirement:
                return False
        
        return True
    
    def _handle_equipment_conflicts(self, character: Character, new_item: Item, 
                                  target_slot: str) -> Dict[str, Any]:
        """Handle conflicts when equipping items (unequip existing items)."""
        
        unequipped_items = []
        
        # Find currently equipped item in target slot
        current_item = self.db.execute(
            select(CharacterInventory).where(
                and_(
                    CharacterInventory.character_id == character.id,
                    CharacterInventory.equipped == True,
                    CharacterInventory.equipped_slot == target_slot
                )
            )
        ).scalar_one_or_none()
        
        if current_item:
            # Unequip current item
            current_item.equipped = False
            current_item.equipped_slot = None
            
            current_item_data = self.db.get(Item, current_item.item_id)
            unequipped_items.append({
                "name": current_item_data.name,
                "slot": target_slot
            })
        
        # Handle two-handed weapons
        if (new_item.type == ItemType.WEAPON and 
            new_item.properties and "two_handed" in new_item.properties):
            
            # Unequip off-hand item
            off_hand_item = self.db.execute(
                select(CharacterInventory).where(
                    and_(
                        CharacterInventory.character_id == character.id,
                        CharacterInventory.equipped == True,
                        CharacterInventory.equipped_slot == "off_hand"
                    )
                )
            ).scalar_one_or_none()
            
            if off_hand_item:
                off_hand_item.equipped = False
                off_hand_item.equipped_slot = None
                
                off_hand_item_data = self.db.get(Item, off_hand_item.item_id)
                unequipped_items.append({
                    "name": off_hand_item_data.name,
                    "slot": "off_hand"
                })
        
        # Handle shields when equipping two-handed weapons
        if target_slot == "main_hand" and new_item.properties and "two_handed" in new_item.properties:
            shield_item = self.db.execute(
                select(CharacterInventory).where(
                    and_(
                        CharacterInventory.character_id == character.id,
                        CharacterInventory.equipped == True,
                        CharacterInventory.equipped_slot == "off_hand"
                    )
                )
            ).scalar_one_or_none()
            
            if shield_item:
                shield_data = self.db.get(Item, shield_item.item_id)
                if shield_data.type == ItemType.SHIELD:
                    shield_item.equipped = False
                    shield_item.equipped_slot = None
                    unequipped_items.append({
                        "name": shield_data.name,
                        "slot": "off_hand"
                    })
        
        return {
            "success": True,
            "unequipped_items": unequipped_items
        }
    
    def _handle_attunement(self, character: Character, inventory_item: CharacterInventory, 
                          item: Item) -> Dict[str, Any]:
        """Handle magic item attunement."""
        
        # Check attunement slots (max 3 in D&D 5e)
        attuned_count = self.db.execute(
            select(CharacterInventory).where(
                and_(
                    CharacterInventory.character_id == character.id,
                    CharacterInventory.attuned == True
                )
            )
        ).scalars().all()
        
        if len(attuned_count) >= 3:
            return {
                "success": False,
                "message": f"Cannot attune to {item.name} - already attuned to 3 items"
            }
        
        # Attune to the item
        inventory_item.attuned = True
        
        return {
            "success": True,
            "message": f"Attuned to {item.name}"
        }
    
    def _calculate_item_stat_effects(self, item: Item, equipped: bool = True) -> Dict[str, Any]:
        """Calculate stat bonuses/penalties from an item."""
        
        multiplier = 1 if equipped else -1
        stat_changes = {}
        
        # Armor class from armor/shields
        if item.armor_class:
            if item.type == ItemType.ARMOR:
                stat_changes["base_ac"] = item.armor_class * multiplier
            elif item.type == ItemType.SHIELD:
                stat_changes["ac_bonus"] = item.armor_class * multiplier
        
        # Stat bonuses from magic items
        if item.effects:
            for effect_type, value in item.effects.items():
                if effect_type.startswith("bonus_"):
                    stat_name = effect_type.replace("bonus_", "")
                    stat_changes[stat_name] = value * multiplier
        
        return stat_changes
    
    def recalculate_character_stats(self, character: Character):
        """Recalculate character stats based on equipped items."""
        
        # Get all equipped items
        equipped_items = self.db.execute(
            select(CharacterInventory, Item).join(
                Item, CharacterInventory.item_id == Item.id
            ).where(
                and_(
                    CharacterInventory.character_id == character.id,
                    CharacterInventory.equipped == True
                )
            )
        ).all()
        
        # Reset base AC to 10 + dex modifier
        base_ac = 10 + character.dexterity_modifier
        ac_bonus = 0
        armor_equipped = False
        
        # Calculate AC from equipped armor and shields
        for inv_item, item in equipped_items:
            if item.type == ItemType.ARMOR and item.armor_class:
                if not armor_equipped:  # Only one armor piece
                    base_ac = item.armor_class
                    
                    # Apply dex modifier with max_dex_bonus limitation
                    if item.max_dex_bonus is not None:
                        dex_bonus = min(character.dexterity_modifier, item.max_dex_bonus)
                    else:
                        dex_bonus = character.dexterity_modifier
                    
                    base_ac += dex_bonus
                    armor_equipped = True
            
            elif item.type == ItemType.SHIELD and item.armor_class:
                ac_bonus += item.armor_class
            
            # Apply magic item bonuses
            if item.effects:
                for effect_type, value in item.effects.items():
                    if effect_type == "bonus_ac":
                        ac_bonus += value
                    elif effect_type == "bonus_strength":
                        character.strength += value
                    elif effect_type == "bonus_dexterity":
                        character.dexterity += value
                    # Add more stat bonuses as needed
        
        # Set final AC
        character.armor_class = base_ac + ac_bonus
    
    def calculate_inventory_weight(self, character_id: str) -> float:
        """Calculate total weight of character's inventory."""
        
        total_weight = 0.0
        
        inventory_items = self.db.execute(
            select(CharacterInventory, Item).join(
                Item, CharacterInventory.item_id == Item.id
            ).where(CharacterInventory.character_id == character_id)
        ).all()
        
        for inv_item, item in inventory_items:
            item_weight = float(item.weight or 0)
            total_weight += item_weight * inv_item.quantity
        
        return total_weight
    
    def calculate_inventory_value(self, character_id: str) -> float:
        """Calculate total value of character's inventory."""
        
        total_value = 0.0
        
        inventory_items = self.db.execute(
            select(CharacterInventory, Item).join(
                Item, CharacterInventory.item_id == Item.id
            ).where(CharacterInventory.character_id == character_id)
        ).all()
        
        for inv_item, item in inventory_items:
            item_value = float(item.cost_gp or 0)
            total_value += item_value * inv_item.quantity
        
        return total_value
    
    def get_available_equipment_slots(self, character: Character) -> List[str]:
        """Get list of equipment slots not currently occupied."""
        
        all_slots = [
            "head", "neck", "chest", "back", "arms", "hands", "waist", "legs", "feet",
            "main_hand", "off_hand", "ring_1", "ring_2", "trinket_1", "trinket_2"
        ]
        
        occupied_slots = self.db.execute(
            select(CharacterInventory.equipped_slot).where(
                and_(
                    CharacterInventory.character_id == character.id,
                    CharacterInventory.equipped == True,
                    CharacterInventory.equipped_slot.isnot(None)
                )
            )
        ).scalars().all()
        
        return [slot for slot in all_slots if slot not in occupied_slots]
    
    def identify_item(self, character_id: str, inventory_item_id: str) -> Dict[str, Any]:
        """Identify a magic item (reveal its properties)."""
        
        try:
            inventory_item = self.db.get(CharacterInventory, inventory_item_id)
            if not inventory_item or inventory_item.character_id != character_id:
                return {
                    "success": False,
                    "message": "Item not found in character inventory"
                }
            
            if inventory_item.identified:
                return {
                    "success": False,
                    "message": "Item is already identified"
                }
            
            item = self.db.get(Item, inventory_item.item_id)
            if not item.is_magical:
                return {
                    "success": False,
                    "message": "Item is not magical and doesn't need identification"
                }
            
            # Mark as identified
            inventory_item.identified = True
            self.db.commit()
            
            return {
                "success": True,
                "message": f"Identified {item.name}",
                "item_properties": {
                    "name": item.name,
                    "description": item.description,
                    "properties": item.properties,
                    "effects": item.effects,
                    "attunement_required": item.attunement_required
                }
            }
            
        except Exception as e:
            logger.error(f"Error identifying item: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Failed to identify item: {str(e)}"
            }