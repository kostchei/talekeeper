# core
# core
"""
Weapon Mastery Effects Processor for TaleKeeper

Handles passive weapon mastery effects that trigger automatically during combat.
Processes weapon masteries from character data and applies effects based on equipped weapons.

Supported Effects:
- Graze: Deal ability modifier damage on missed attacks
- Topple: Force Constitution save or be knocked prone on hit
- Sap: Target has disadvantage on next attack roll on hit
- Slow: Reduce target's speed by 10 feet on hit
- Vex: Gain advantage on next attack against target on hit
- Push: Push target 10 feet away on hit (if one size larger or smaller)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from services.equipment_database import EquipmentDatabase


@dataclass
class MasteryEffect:
    """Represents a weapon mastery effect that can be applied."""
    mastery_name: str
    effect_type: str  # 'on_hit', 'on_miss', 'passive'
    description: str
    requires_save: bool = False
    save_ability: Optional[str] = None
    damage_type: Optional[str] = None


class WeaponMasteryProcessor:
    """Processes weapon mastery effects and applies them during combat."""
    
    def __init__(self):
        self.mastery_definitions = {
            "Graze": MasteryEffect(
                mastery_name="Graze",
                effect_type="on_miss",
                description="Deal ability modifier damage on missed attack",
                damage_type="slashing"
            ),
            "Topple": MasteryEffect(
                mastery_name="Topple", 
                effect_type="on_hit",
                description="Target must make Constitution save or be knocked prone",
                requires_save=True,
                save_ability="constitution"
            ),
            "Sap": MasteryEffect(
                mastery_name="Sap",
                effect_type="on_hit", 
                description="Target has disadvantage on its next attack roll"
            ),
            "Slow": MasteryEffect(
                mastery_name="Slow",
                effect_type="on_hit",
                description="Target's speed is reduced by 10 feet until start of your next turn"
            ),
            "Vex": MasteryEffect(
                mastery_name="Vex",
                effect_type="on_hit",
                description="You have advantage on your next attack roll against target"
            ),
            "Push": MasteryEffect(
                mastery_name="Push",
                effect_type="on_hit",
                description="Push target 10 feet away if no more than one size larger"
            )
        }
    
    def get_available_masteries_for_weapon(self, weapon_name: str) -> List[str]:
        """Get weapon masteries available for a specific weapon type from equipment data."""
        try:
            # Load equipment data from database
            equipment_db = EquipmentDatabase()
            weapon = equipment_db.get_equipment_by_name(weapon_name)
            
            if weapon and weapon.get('item_type') == 'weapon':
                mastery = weapon.get('weapon_mastery')
                return [mastery] if mastery else []
            
            return []
            
        except Exception as e:
            print(f"Error loading weapon mastery data: {e}")
            return []
    
    def check_mastery_applicability(self, character_masteries: List[str], weapon_name: str, mastery_name: str) -> bool:
        """Check if a character can use a specific mastery with a weapon."""
        # Character must have selected the mastery
        if mastery_name not in character_masteries:
            return False
        
        # Weapon must support the mastery
        weapon_masteries = self.get_available_masteries_for_weapon(weapon_name)
        return mastery_name in weapon_masteries
    
    def apply_on_hit_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int, damage_roll: int) -> Dict[str, Any]:
        """Apply weapon mastery effects when an attack hits."""
        effects_applied = []
        character_masteries = character_data.get('weapon_masteries', [])
        
        for mastery_name in character_masteries:
            if not self.check_mastery_applicability(character_masteries, weapon_name, mastery_name):
                continue
            
            mastery = self.mastery_definitions.get(mastery_name)
            if not mastery or mastery.effect_type != "on_hit":
                continue
            
            # Apply the specific mastery effect
            effect_result = self._apply_mastery_effect(mastery, character_data, target_data, attack_roll, damage_roll)
            if effect_result:
                effects_applied.append(effect_result)
        
        return {
            "effects": effects_applied,
            "target_data": target_data  # May be modified by effects
        }
    
    def apply_on_miss_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int) -> Dict[str, Any]:
        """Apply weapon mastery effects when an attack misses."""
        effects_applied = []
        character_masteries = character_data.get('weapon_masteries', [])
        
        for mastery_name in character_masteries:
            if not self.check_mastery_applicability(character_masteries, weapon_name, mastery_name):
                continue
            
            mastery = self.mastery_definitions.get(mastery_name)
            if not mastery or mastery.effect_type != "on_miss":
                continue
            
            # Apply the specific mastery effect
            effect_result = self._apply_mastery_effect(mastery, character_data, target_data, attack_roll, 0)
            if effect_result:
                effects_applied.append(effect_result)
        
        return {
            "effects": effects_applied,
            "additional_damage": sum(effect.get('damage', 0) for effect in effects_applied)
        }
    
    def _apply_mastery_effect(self, mastery: MasteryEffect, character_data: Dict[str, Any], target_data: Dict[str, Any], attack_roll: int, damage_roll: int) -> Optional[Dict[str, Any]]:
        """Apply a specific mastery effect and return the result."""
        result = {
            "mastery": mastery.mastery_name,
            "description": mastery.description
        }
        
        if mastery.mastery_name == "Graze":
            # Deal ability modifier damage on miss
            ability_mod = self._get_attack_ability_modifier(character_data)
            result["damage"] = ability_mod
            result["damage_type"] = mastery.damage_type
            
        elif mastery.mastery_name == "Topple":
            # Force Constitution save or be knocked prone
            dc = 8 + character_data.get('proficiency_bonus', 2) + self._get_attack_ability_modifier(character_data)
            result["save_required"] = True
            result["save_dc"] = dc
            result["save_ability"] = "constitution"
            result["effect"] = "prone"
            
        elif mastery.mastery_name == "Sap":
            # Target has disadvantage on next attack
            result["effect"] = "disadvantage_next_attack"
            result["duration"] = "next_attack"
            
        elif mastery.mastery_name == "Slow":
            # Reduce speed by 10 feet
            result["effect"] = "speed_reduction"
            result["speed_reduction"] = 10
            result["duration"] = "until_start_of_your_next_turn"
            
        elif mastery.mastery_name == "Vex":
            # Gain advantage on next attack against target
            result["effect"] = "advantage_next_attack"
            result["duration"] = "until_end_of_your_next_turn"
            result["target"] = "self"
            
        elif mastery.mastery_name == "Push":
            # Push target 10 feet away
            result["effect"] = "push"
            result["distance"] = 10
            result["size_limit"] = "one_size_larger"
        
        return result
    
    def _get_attack_ability_modifier(self, character_data: Dict[str, Any]) -> int:
        """Get the ability modifier used for attacks (usually Strength or Dexterity)."""
        # Simplified - in real implementation would check weapon properties
        strength_mod = (character_data.get('strength', 10) - 10) // 2
        dexterity_mod = (character_data.get('dexterity', 10) - 10) // 2
        
        # Use higher of Str or Dex for now
        return max(strength_mod, dexterity_mod)


# Test the processor
if __name__ == "__main__":
    processor = WeaponMasteryProcessor()
    
    # Test character with Graze, Topple, and Sap masteries
    test_character = {
        'weapon_masteries': ['Graze', 'Topple', 'Sap'],
        'strength': 16,
        'dexterity': 12,
        'proficiency_bonus': 2,
        'level': 3
    }
    
    # Test Graze mastery on miss with Greatsword
    miss_effects = processor.apply_on_miss_effects(test_character, "Greatsword", {}, 10)
    print(f"Miss effects: {miss_effects}")
    
    # Test Topple mastery on hit with Battleaxe
    hit_effects = processor.apply_on_hit_effects(test_character, "Battleaxe", {}, 15, 8)
    print(f"Hit effects: {hit_effects}")