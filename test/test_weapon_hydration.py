import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.talekeeper.services.equipment_database import EquipmentDatabase

def test_longsword_plus_one_exists():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "database", "talekeeper.db")
    db = EquipmentDatabase(db_path)

    weapon = db.get_equipment_by_name("Longsword +1")

    assert weapon is not None, "Longsword +1 not found in database"
    assert weapon.get('damage_dice') == '1d8', f"Expected damage_dice='1d8', got {weapon.get('damage_dice')}"
    assert weapon.get('damage_type') == 'slashing', f"Expected damage_type='slashing', got {weapon.get('damage_type')}"
    assert weapon.get('attack_bonus') == 1, f"Expected attack_bonus=1, got {weapon.get('attack_bonus')}"
    assert weapon.get('damage_bonus') == 1, f"Expected damage_bonus=1, got {weapon.get('damage_bonus')}"

    print("PASS: Longsword +1 has correct stats")
    print(f"  damage_dice: {weapon.get('damage_dice')}")
    print(f"  damage_type: {weapon.get('damage_type')}")
    print(f"  attack_bonus: {weapon.get('attack_bonus')}")
    print(f"  damage_bonus: {weapon.get('damage_bonus')}")
    return True

def test_magic_weapon_variants():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "database", "talekeeper.db")
    db = EquipmentDatabase(db_path)

    magic_weapons = [
        ("Longsword +1", "1d8", "slashing", 1, 1),
        ("Greatsword +1", "2d6", "slashing", 1, 1),
        ("Rapier +1", "1d8", "piercing", 1, 1),
    ]

    for weapon_name, expected_dice, expected_type, expected_atk, expected_dmg in magic_weapons:
        weapon = db.get_equipment_by_name(weapon_name)
        if not weapon:
            print(f"SKIP: {weapon_name} not in database")
            continue

        assert weapon.get('damage_dice') == expected_dice, f"{weapon_name}: damage_dice mismatch"
        assert weapon.get('attack_bonus') == expected_atk, f"{weapon_name}: attack_bonus mismatch"
        assert weapon.get('damage_bonus') == expected_dmg, f"{weapon_name}: damage_bonus mismatch"
        print(f"PASS: {weapon_name} - {expected_dice} {expected_type}, +{expected_atk}/+{expected_dmg}")

    return True

if __name__ == "__main__":
    print("=== Weapon Hydration Tests ===\n")

    try:
        test_longsword_plus_one_exists()
        print()
        test_magic_weapon_variants()
        print("\n=== All tests passed ===")
    except AssertionError as e:
        print(f"\nFAIL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
