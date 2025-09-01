"""
Test damage calculation with Yalks' actual stats.
"""

def test_yalks_damage():
    """Test damage for Yalks' stats: STR 19 (+4), DEX 16 (+3), CON 19 (+4)."""
    
    # Yalks' stats
    character_context = {
        'strength': 19,     # +4 modifier
        'dexterity': 16,    # +3 modifier
        'constitution': 19, # +4 modifier
        'level': 1
    }
    
    # Scimitar stats (finesse weapon)
    scimitar = {
        'damage_dice': '1d6',
        'damage_type': 'slashing',
        'weapon_properties': ['finesse', 'light'],
        'damage_bonus': 0
    }
    
    def calculate_damage(weapon, is_off_hand=False):
        damage_dice = weapon.get('damage_dice', '1d4')
        damage_type = weapon.get('damage_type', 'slashing')
        
        # Get ability modifier for damage
        weapon_props = weapon.get('weapon_properties', [])
        if 'finesse' in weapon_props:
            str_mod = (character_context.get('strength', 10) - 10) // 2
            dex_mod = (character_context.get('dexterity', 10) - 10) // 2
            ability_mod = max(str_mod, dex_mod)  # Choose higher
        else:
            ability_mod = (character_context.get('strength', 10) - 10) // 2
        
        # Off-hand attacks don't add ability modifier to damage
        if is_off_hand:
            ability_mod = 0
        
        # Magic weapon damage bonus
        magic_bonus = weapon.get('damage_bonus', 0)
        total_bonus = ability_mod + magic_bonus
        
        if total_bonus > 0:
            return f"{damage_dice}+{total_bonus} {damage_type}"
        elif total_bonus < 0:
            return f"{damage_dice}{total_bonus} {damage_type}"
        else:
            return f"{damage_dice} {damage_type}"
    
    print("=== YALKS DAMAGE TEST ===")
    print(f"Yalks' Stats: STR 19 (+4), DEX 16 (+3), CON 19 (+4)")
    print(f"Weapon: Scimitar (finesse, light)")
    print()
    print(f"Expected:")
    print(f"  Main-hand: 1d6+4 slashing (uses higher of STR +4 or DEX +3)")
    print(f"  Off-hand:  1d6 slashing   (no ability modifier)")
    print()
    print(f"Calculated:")
    print(f"  Main-hand: {calculate_damage(scimitar, is_off_hand=False)}")
    print(f"  Off-hand:  {calculate_damage(scimitar, is_off_hand=True)}")
    
    # Test what modifiers are being used
    str_mod = (character_context.get('strength', 10) - 10) // 2
    dex_mod = (character_context.get('dexterity', 10) - 10) // 2
    chosen_mod = max(str_mod, dex_mod)
    
    print()
    print(f"Modifier calculation:")
    print(f"  STR modifier: +{str_mod}")
    print(f"  DEX modifier: +{dex_mod}")
    print(f"  Finesse uses: +{chosen_mod} (higher of the two)")

if __name__ == "__main__":
    test_yalks_damage()