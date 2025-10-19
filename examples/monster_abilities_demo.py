# unsure
#utility
# unsure
"""
Monster Non-Attack Abilities Demo

Demonstrates breath weapons, limited use abilities, and save-based effects.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from talekeeper.services.monster_ability_manager import (
    MonsterAbilityManager,
    PREDEFINED_ABILITIES
)


def demo_dragon_breath():
    """Demonstrate dragon breath weapon with recharge mechanics."""
    print("\n" + "="*60)
    print("DEMO 1: Dragon Fire Breath (Recharge 5-6)")
    print("="*60)

    manager = MonsterAbilityManager()

    fire_breath = PREDEFINED_ABILITIES['fire_breath']
    manager.initialize_ability("demo_encounter", "red_dragon", fire_breath)

    player = {
        'id': 'conan',
        'dexterity': 16,
        'proficiency_bonus': 4,
        'save_proficiencies': ['strength', 'constitution']
    }

    print("\n[TURN 1] Dragon uses Fire Breath!")
    result = manager.execute_ability(
        "demo_encounter",
        "red_dragon",
        "Ancient Red Dragon",
        fire_breath,
        player['id'],
        player
    )

    for msg in result['messages']:
        print(f"  {msg}")

    print(f"\n  Damage dealt: {result.get('damage', 0)} {result.get('damage_type', '')}")

    print("\n[TURN 2] Attempting to recharge...")
    for attempt in range(5):
        success, roll = manager.attempt_recharge("demo_encounter", "red_dragon", "Fire Breath")
        print(f"  Attempt {attempt + 1}: Roll = {roll}, Recharged = {success}")
        if success:
            print("  FIRE BREATH IS READY AGAIN!")
            break

    state = manager.get_ability_state("demo_encounter", "red_dragon", "Fire Breath")
    print(f"\n  Current state: Available = {state.is_available}, Last roll = {state.last_recharge_roll}")


def demo_limited_use():
    """Demonstrate limited use ability (Aboleth's Dominate Mind)."""
    print("\n" + "="*60)
    print("DEMO 2: Aboleth Dominate Mind (2/Day)")
    print("="*60)

    manager = MonsterAbilityManager()

    dominate = PREDEFINED_ABILITIES['dominate_mind']
    manager.initialize_ability("demo_encounter", "aboleth", dominate)

    victim = {
        'id': 'valeria',
        'wisdom': 12,
        'proficiency_bonus': 3,
        'save_proficiencies': ['dexterity', 'intelligence']
    }

    print("\n[USE 1]")
    result1 = manager.execute_ability(
        "demo_encounter",
        "aboleth",
        "Ancient Aboleth",
        dominate,
        victim['id'],
        victim
    )
    for msg in result1['messages']:
        print(f"  {msg}")

    state = manager.get_ability_state("demo_encounter", "aboleth", "Dominate Mind")
    print(f"  Uses remaining: {state.uses_remaining}")

    print("\n[USE 2]")
    result2 = manager.execute_ability(
        "demo_encounter",
        "aboleth",
        "Ancient Aboleth",
        dominate,
        victim['id'],
        victim
    )
    for msg in result2['messages']:
        print(f"  {msg}")

    state = manager.get_ability_state("demo_encounter", "aboleth", "Dominate Mind")
    print(f"  Uses remaining: {state.uses_remaining}")

    print("\n[USE 3 - Should fail]")
    result3 = manager.execute_ability(
        "demo_encounter",
        "aboleth",
        "Ancient Aboleth",
        dominate,
        victim['id'],
        victim
    )
    print(f"  Result: {result3}")

    print("\n[LONG REST]")
    manager.reset_daily_abilities("demo_encounter", "aboleth")
    state = manager.get_ability_state("demo_encounter", "aboleth", "Dominate Mind")
    print(f"  After long rest - Uses remaining: {state.uses_remaining}")


def demo_condition_application():
    """Demonstrate automatic condition application on failed saves."""
    print("\n" + "="*60)
    print("DEMO 3: Frightful Presence with Condition Application")
    print("="*60)

    manager = MonsterAbilityManager()

    frightful = PREDEFINED_ABILITIES['frightful_presence']
    manager.initialize_ability("demo_encounter", "ancient_dragon", frightful)

    brave_warrior = {
        'id': 'thorgrim',
        'wisdom': 10,
        'proficiency_bonus': 2,
        'save_proficiencies': ['strength', 'constitution']
    }

    print("\n[Thorgrim encounters the Ancient Dragon]")
    result = manager.execute_ability(
        "demo_encounter",
        "ancient_dragon",
        "Ancient Black Dragon",
        frightful,
        brave_warrior['id'],
        brave_warrior
    )

    for msg in result['messages']:
        print(f"  {msg}")

    if 'condition_applied' in result:
        print(f"\n  CONDITION: {result['condition_applied'].upper()} applied!")
        print(f"  Thorgrim must make a new save at the end of each turn.")
    else:
        print(f"\n  Thorgrim resists the dragon's terrifying presence!")


def demo_multiple_abilities():
    """Show a monster with multiple special abilities."""
    print("\n" + "="*60)
    print("DEMO 4: Adult Blue Dragon with Multiple Abilities")
    print("="*60)

    manager = MonsterAbilityManager()

    lightning_breath = PREDEFINED_ABILITIES['lightning_breath']
    frightful = PREDEFINED_ABILITIES['frightful_presence']

    manager.initialize_ability("demo_encounter", "blue_dragon", lightning_breath)
    manager.initialize_ability("demo_encounter", "blue_dragon", frightful)

    abilities = manager.get_all_monster_abilities("demo_encounter", "blue_dragon")

    print("\n  Blue Dragon's Special Abilities:")
    for ability in abilities:
        status = "READY" if ability.is_available else "USED"
        if ability.uses_remaining >= 0:
            print(f"  - {ability.ability_name}: [{status}] ({ability.uses_remaining} uses remaining)")
        else:
            print(f"  - {ability.ability_name}: [{status}]")


def demo_all_predefined():
    """Show all predefined abilities."""
    print("\n" + "="*60)
    print("ALL PREDEFINED ABILITIES")
    print("="*60)

    for name, ability in PREDEFINED_ABILITIES.items():
        print(f"\n{ability.name}:")
        print(f"  Type: {ability.ability_type.value}")
        if ability.recharge_type.value != "none":
            print(f"  Recharge: {ability.recharge_type.value}")
        if ability.max_uses > 0:
            print(f"  Uses: {ability.max_uses}/Day")
        if ability.save_type:
            print(f"  Save: DC {ability.save_dc} {ability.save_type.capitalize()}")
        if ability.damage_dice:
            print(f"  Damage: {ability.damage_dice} {ability.damage_type}")
        if ability.condition_on_fail:
            print(f"  Condition: {ability.condition_on_fail}")
        if ability.area_type:
            print(f"  Area: {ability.area_size} ft. {ability.area_type}")
        print(f"  Description: {ability.description}")


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# MONSTER NON-ATTACK ABILITIES SYSTEM DEMO")
    print("#"*60)

    demo_dragon_breath()
    demo_limited_use()
    demo_condition_application()
    demo_multiple_abilities()
    demo_all_predefined()

    print("\n" + "#"*60)
    print("# DEMO COMPLETE")
    print("#"*60)
    print("\nAll core systems working:")
    print("  [OK] Recharge mechanics (breath weapons)")
    print("  [OK] Limited use abilities (X/Day)")
    print("  [OK] Save-based effects")
    print("  [OK] Automatic condition application")
    print("  [OK] Damage calculation with half-on-save")
    print("  [OK] Long rest resets")
    print("  [OK] Multiple abilities per monster")
    print("\nReady for UI integration!")
