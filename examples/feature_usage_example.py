# unsure
#utility
# unsure
"""
Feature System Usage Examples

This module demonstrates how to use the new feature system in the TaleKeeper application.
It shows integration patterns for UI components and game mechanics.
"""

from typing import Dict, List, Optional, Any
from core.feature_integration import get_feature_integration


class FeatureUsageExamples:
    """Examples of how to use the feature system in different contexts."""
    
    def __init__(self):
        self.integration = get_feature_integration()
    
    def combat_example(self, character_id: str, target_ac: int = 15):
        """Example of using features during combat."""
        print(f"=== Combat Example for Character {character_id} ===")
        
        # Get available combat features
        combat_context = {
            "is_combat": True,
            "is_first_attack": True,
            "bonus_action_available": True,
            "reaction_available": True
        }
        
        features = self.integration.get_available_features(character_id, combat_context)
        combat_features = [f for f in features if f['type'] in ['action', 'bonus_action', 'reaction']]
        
        print(f"Available combat features: {len(combat_features)}")
        for feature in combat_features:
            print(f"  - {feature['name']} ({feature['type']}) - {feature.get('uses_remaining', '∞')} uses")
        
        # Example: Fighter using Action Surge
        action_surge = next((f for f in features if f['name'] == 'Action Surge'), None)
        if action_surge and action_surge.get('uses_remaining', 0) > 0:
            print("\nUsing Action Surge...")
            result = self.integration.use_feature(character_id, 'Action Surge')
            if result['success']:
                print(f"✓ Action Surge activated! Extra action available.")
                print(f"  Uses remaining: {result.get('uses_remaining', 0)}")
        
        # Example: Barbarian entering Rage
        rage = next((f for f in features if f['name'] == 'Rage'), None)
        if rage and rage.get('uses_remaining', 0) > 0:
            print("\nEntering Rage...")
            result = self.integration.use_feature(character_id, 'Rage')
            if result['success']:
                print(f"✓ Rage activated!")
                print(f"  Damage resistance: {result.get('damage_resistance', [])}")
                print(f"  Rage damage bonus: +{result.get('rage_damage_bonus', 0)}")
    
    def attack_example(self, character_id: str, weapon_type: str = "finesse"):
        """Example of attack resolution with features."""
        print(f"\n=== Attack Example for Character {character_id} ===")
        
        # Set up attack context
        attack_context = {
            "is_attack": True,
            "weapon": {
                "finesse": weapon_type == "finesse",
                "ranged": weapon_type == "ranged",
                "damage_type": "piercing"
            },
            "has_advantage": True,  # Could be from various sources
            "ally_within_5ft": False
        }
        
        # Check for Sneak Attack (Rogue)
        result = self.integration.use_feature(character_id, 'Sneak Attack', attack_context)
        if result.get('success'):
            print(f"✓ Sneak Attack triggered!")
            print(f"  Extra damage: {result.get('extra_damage_dice', '0d6')}")
            print(f"  Damage type: {result.get('damage_type', 'piercing')}")
        
        # Check for Reckless Attack (Barbarian)
        if attack_context.get('is_first_attack'):
            reckless_result = self.integration.use_feature(character_id, 'Reckless Attack', attack_context)
            if reckless_result.get('success'):
                print(f"✓ Reckless Attack activated!")
                print("  Player gains advantage on attacks")
                print("  Enemies gain advantage until next turn")
    
    def defense_example(self, character_id: str, incoming_damage: int = 20):
        """Example of using defensive features."""
        print(f"\n=== Defense Example for Character {character_id} ===")
        
        # Apply passive defensive features
        passive_mods = self.integration.apply_passive_features(character_id)
        
        if 'armor_class_unarmored' in passive_mods:
            print(f"Unarmored Defense AC: {passive_mods['armor_class_unarmored']}")
        
        # Defensive reaction context
        defense_context = {
            "is_hit_by_attack": True,
            "damage": incoming_damage,
            "attack_type": "weapon"
        }
        
        # Try Uncanny Dodge (Rogue)
        uncanny_result = self.integration.use_feature(character_id, 'Uncanny Dodge', defense_context)
        if uncanny_result.get('success'):
            print(f"✓ Uncanny Dodge used!")
            print(f"  Damage reduced by {uncanny_result.get('damage_reduced', 0)}")
            print(f"  Final damage: {uncanny_result.get('final_damage', incoming_damage)}")
    
    def rest_example(self, character_id: str):
        """Example of rest processing."""
        print(f"\n=== Rest Example for Character {character_id} ===")
        
        # Show features before rest
        features_before = self.integration.get_available_features(character_id)
        depleted = [f for f in features_before if f.get('uses_remaining', 1) == 0]
        
        print(f"Features needing rest: {len(depleted)}")
        for feature in depleted:
            print(f"  - {feature['name']} (0/{feature.get('uses_max', '?')} uses)")
        
        # Process short rest
        print("\nTaking a short rest...")
        rest_result = self.integration.process_rest(character_id, "short")
        
        if rest_result.get('success'):
            print("✓ Short rest completed!")
            
            # Show restored features
            features_after = self.integration.get_available_features(character_id)
            restored = [f for f in features_after 
                       if f['name'] in [d['name'] for d in depleted] 
                       and f.get('uses_remaining', 0) > 0]
            
            print(f"Features restored: {len(restored)}")
            for feature in restored:
                print(f"  + {feature['name']} ({feature.get('uses_remaining')}/{feature.get('uses_max')} uses)")
    
    def level_up_example(self, character_id: str, new_level: int):
        """Example of handling level ups with new features."""
        print(f"\n=== Level Up Example for Character {character_id} ===")
        
        from core.feature_definitions import ClassFeatures
        import sqlite3
        
        # Get character class
        conn = sqlite3.connect("talekeeper.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT class_id, subclass_id FROM characters WHERE id = ?", (character_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("Character not found")
            return
        
        class_name = row['class_id']
        subclass = row['subclass_id']
        
        # Get new features at this level
        new_features = ClassFeatures.get_feature_at_level(class_name, new_level, subclass)
        
        print(f"Leveling up to {new_level}!")
        print(f"New features available: {len(new_features)}")
        
        for feature in new_features:
            print(f"  + {feature.name}")
            print(f"    {feature.description}")
            if feature.scaling and new_level in feature.scaling:
                scaling_info = feature.scaling[new_level]
                if 'uses' in scaling_info:
                    print(f"    Uses: {scaling_info['uses']}")
        
        # Reinitialize features with new level
        # (In practice, you'd update the character level first)
        print(f"\nReinitializing features for level {new_level}...")
        success = self.integration.initialize_character_features(character_id)
        
        if success:
            print("✓ Features updated successfully!")
            
            # Show all available features
            all_features = self.integration.get_available_features(character_id)
            print(f"Total features available: {len(all_features)}")


def run_all_examples():
    """Run all examples with available characters."""
    import sqlite3
    
    conn = sqlite3.connect("talekeeper.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get sample characters for each class
    examples = FeatureUsageExamples()
    
    # Test with Fighter
    cursor.execute("SELECT id, name FROM characters WHERE class_id = 'Fighter' LIMIT 1")
    fighter = cursor.fetchone()
    if fighter:
        examples.combat_example(fighter['id'])
        examples.rest_example(fighter['id'])
    
    # Test with Barbarian
    cursor.execute("SELECT id, name FROM characters WHERE class_id = 'Barbarian' LIMIT 1")
    barbarian = cursor.fetchone()
    if barbarian:
        examples.combat_example(barbarian['id'])
        examples.defense_example(barbarian['id'])
    
    # Test with Rogue
    cursor.execute("SELECT id, name FROM characters WHERE class_id = 'Rogue' LIMIT 1")
    rogue = cursor.fetchone()
    if rogue:
        examples.attack_example(rogue['id'])
        examples.defense_example(rogue['id'])
    
    conn.close()


if __name__ == "__main__":
    run_all_examples()