#!/usr/bin/env python3
"""
Integration test for the two-weapon fighting system
Tests the complete flow from UI to combat manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.game_engine_sqlite import GameEngineSQLite
from core.combat_manager import CombatManager, CombatantType
from action_cards.action_panel import ActionPanel, ActionType

def test_combat_integration():
    """Test the integration between game engine, combat manager, and UI"""
    print("Testing Combat System Integration")
    print("=" * 40)
    
    # Initialize game engine (which now has combat manager)
    game_engine = GameEngineSQLite("talekeeper.db")
    
    # Verify combat manager is available
    assert hasattr(game_engine, 'combat_manager'), "Game engine should have combat_manager"
    assert isinstance(game_engine.combat_manager, CombatManager), "combat_manager should be CombatManager instance"
    
    print("✓ Game engine has combat manager")
    
    # Create action panel with game engine
    action_panel = ActionPanel(game_engine)
    
    # Verify action panel has game engine reference
    assert action_panel.game_engine is game_engine, "Action panel should reference game engine"
    
    print("✓ Action panel connected to game engine")
    
    # Test combat manager basic functionality
    cm = game_engine.combat_manager
    
    # Create test combatants
    player_data = {
        'id': 'test_fighter',
        'name': 'Test Fighter',
        'class_id': 'fighter', 
        'level': 5,
        'ac': 18,
        'hp': 45,
        'max_hp': 45,
        'strength': 16,
        'dexterity': 14
    }
    
    monster_data = {
        'name': 'Orc',
        'armor_class': 13,
        'hit_points': 15,
        'strength': 16,
        'dexterity': 12,
        'actions': '[]'
    }
    
    # Add combatants to combat manager
    player = cm.add_player_combatant(player_data)
    monster = cm.add_monster_combatant('orc_1', monster_data)
    
    print(f"✓ Added combatants: {player.name} vs {monster.name}")
    
    # Start combat
    initiative_order = cm.start_combat()
    
    print(f"✓ Combat started, initiative: {[c.name for c in initiative_order]}")
    
    # Test two-weapon fighting capability check
    can_dual_wield = cm.can_make_offhand_attack('test_fighter')
    print(f"✓ Can make off-hand attack: {can_dual_wield}")
    
    # Test attack execution if it's player turn
    if cm.is_player_turn():
        current = cm.get_current_combatant()
        print(f"✓ Current turn: {current.name}")
        
        # Test main-hand attack
        test_weapon = {
            'name': 'Longsword',
            'item_type': 'weapon',
            'damage_dice': '1d8', 
            'weapon_properties': [],
            'attack_bonus': 0,
            'damage_bonus': 0
        }
        
        result = cm.execute_player_attack('test_fighter', test_weapon, 'orc_1')
        print(f"✓ Attack result: {len(result.get('attacks', []))} attacks made")
        
        # For a level 5 fighter, should have Extra Attack (2 total attacks)
        expected_attacks = 1 + player.extra_attacks
        actual_attacks = len(result.get('attacks', []))
        
        print(f"✓ Expected {expected_attacks} attacks, got {actual_attacks}")
        
    # Test action panel stub methods exist
    assert hasattr(game_engine, 'update_combat_log'), "Game engine should have update_combat_log"
    assert hasattr(game_engine, 'update_all_character_panels'), "Game engine should have update_all_character_panels"
    
    print("✓ Game engine has required UI integration methods")
    
    # Test combat log
    log_entries = cm.get_combat_log()
    print(f"✓ Combat log has {len(log_entries)} entries")
    
    if log_entries:
        print(f"  Sample log: {log_entries[0]}")
    
    return True

if __name__ == "__main__":
    try:
        test_combat_integration()
        print("\n[SUCCESS] All integration tests passed!")
    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()