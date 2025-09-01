"""
Test the damage calculation logic for main-hand vs off-hand weapons.
"""

def test_damage_format():
    """Test the _format_damage logic."""
    
    # Simulate the _format_damage logic from action_panel.py
    def format_damage(weapon, is_off_hand=False, character_strength=16, character_dexterity=16):
        damage_dice = weapon.get('damage_dice', '1d4')
        damage_type = weapon.get('damage_type', 'slashing')
        magic_bonus = weapon.get('magic_bonus', 0)
        
        # Determine ability modifier based on weapon properties
        weapon_properties = weapon.get('weapon_properties', [])
        if 'finesse' in weapon_properties:
            # Use higher of STR or DEX
            str_mod = (character_strength - 10) // 2
            dex_mod = (character_dexterity - 10) // 2
            ability_mod = max(str_mod, dex_mod)
        else:
            # Use STR for melee, DEX for ranged (simplified)
            ability_mod = (character_strength - 10) // 2
        
        # Off-hand attacks don't add ability modifier to damage
        if is_off_hand:
            ability_mod = 0
        
        # Format damage string
        total_bonus = ability_mod + magic_bonus
        if total_bonus > 0:
            return f"{damage_dice}+{total_bonus} {damage_type}"
        elif total_bonus < 0:
            return f"{damage_dice}{total_bonus} {damage_type}"
        else:
            return f"{damage_dice} {damage_type}"
    
    # Test scimitar (finesse weapon)
    scimitar = {
        'damage_dice': '1d6',
        'damage_type': 'slashing',
        'weapon_properties': ['finesse', 'light'],
        'magic_bonus': 0
    }
    
    print("=== SCIMITAR DAMAGE TEST ===")
    print(f"Character: STR 16 (+3), DEX 16 (+3)")
    print(f"Main-hand: {format_damage(scimitar, is_off_hand=False)}")
    print(f"Off-hand:  {format_damage(scimitar, is_off_hand=True)}")
    
    # Test with different stats
    print("\n=== DIFFERENT STATS TEST ===")  
    print(f"Character: STR 12 (+1), DEX 18 (+4)")
    print(f"Main-hand: {format_damage(scimitar, is_off_hand=False, character_strength=12, character_dexterity=18)}")
    print(f"Off-hand:  {format_damage(scimitar, is_off_hand=True, character_strength=12, character_dexterity=18)}")
    
    # Test non-finesse weapon
    longsword = {
        'damage_dice': '1d8', 
        'damage_type': 'slashing',
        'weapon_properties': ['versatile'],
        'magic_bonus': 0
    }
    
    print("\n=== LONGSWORD (NON-FINESSE) TEST ===")
    print(f"Character: STR 16 (+3), DEX 16 (+3)")
    print(f"Main-hand: {format_damage(longsword, is_off_hand=False)}")
    print(f"Off-hand:  {format_damage(longsword, is_off_hand=True)}")

if __name__ == "__main__":
    test_damage_format()