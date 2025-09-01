"""
Test what the equipment service returns for weapons.
"""

from services.equipment import equipment_service

def test_equipment_service():
    """Test equipment service weapon data."""
    
    weapons_to_test = ['Scimitar', 'Longsword', 'Greataxe', 'Dagger']
    
    print("=== EQUIPMENT SERVICE TEST ===")
    
    for weapon_name in weapons_to_test:
        print(f"\n--- {weapon_name} ---")
        item_data = equipment_service.get_item(weapon_name)
        
        if item_data:
            print(f"Found: {item_data.get('name', 'NO NAME')}")
            print(f"Type: {item_data.get('item_type', 'NO TYPE')}")
            print(f"Damage dice: {item_data.get('damage_dice', 'NO DAMAGE_DICE')}")
            print(f"Damage type: {item_data.get('damage_type', 'NO DAMAGE_TYPE')}")
            print(f"Properties: {item_data.get('weapon_properties', 'NO PROPERTIES')}")
            print(f"Weight: {item_data.get('weight_lb', 'NO WEIGHT')}")
            print(f"Full data keys: {list(item_data.keys())}")
        else:
            print("NOT FOUND")
    
    # Test the database directly
    print(f"\n=== DATABASE DIRECT CHECK ===")
    import sqlite3
    
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, item_type, damage_dice, damage_type, weapon_properties
        FROM equipment 
        WHERE name IN ('Scimitar', 'Longsword', 'Greataxe')
        ORDER BY name
    """)
    
    weapons = cursor.fetchall()
    
    if weapons:
        for name, item_type, damage_dice, damage_type, weapon_props in weapons:
            print(f"{name}: {damage_dice} {damage_type}, type={item_type}, props={weapon_props}")
    else:
        print("No weapons found in database")
    
    conn.close()

if __name__ == "__main__":
    test_equipment_service()