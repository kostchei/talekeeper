"""
CR to XP Conversion Utility

D&D 2024 Challenge Rating to Experience Points conversion.
Used throughout TaleKeeper for monster XP calculations since the
database stores CR but not XP values.

Reference: D&D 2024 Dungeon Master's Guide, Chapter 3
"""

from typing import Dict

# Official D&D 2024 CR to XP conversion table
CR_TO_XP: Dict[str, int] = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000
}


def cr_to_xp(challenge_rating: str) -> int:
    """
    Convert Challenge Rating to Experience Points.

    Args:
        challenge_rating: CR as string (e.g., "1/4", "5", "10")

    Returns:
        XP value for that CR

    Examples:
        >>> cr_to_xp("1/4")
        50
        >>> cr_to_xp("10")
        5900
        >>> cr_to_xp("0")
        10
    """
    if not challenge_rating:
        return 10

    cr_str = str(challenge_rating).strip()

    # Direct lookup
    if cr_str in CR_TO_XP:
        return CR_TO_XP[cr_str]

    # If not found, try to estimate
    try:
        if '/' in cr_str:
            # Fractional CR (e.g., "1/4")
            numerator, denominator = cr_str.split('/')
            cr_float = float(numerator) / float(denominator)
        else:
            cr_float = float(cr_str)

        # Estimate XP for unknown CRs using exponential formula
        if cr_float < 1:
            # For fractional CRs, interpolate
            estimated_xp = int(25 + (75 * cr_float))
        else:
            # For CR 1+, use exponential growth
            estimated_xp = int(200 * (cr_float ** 1.5))

        print(f"[CR_TO_XP] Warning: Unknown CR '{cr_str}', estimated {estimated_xp} XP")
        return max(10, estimated_xp)

    except (ValueError, ZeroDivisionError):
        print(f"[CR_TO_XP] Error: Invalid CR '{cr_str}', defaulting to 10 XP")
        return 10


def get_xp_for_encounter(monsters: list) -> int:
    """
    Calculate total XP for an encounter of monsters.

    Args:
        monsters: List of monster dicts with 'challenge_rating' field

    Returns:
        Total XP for the encounter

    Examples:
        >>> monsters = [
        ...     {'name': 'Goblin', 'challenge_rating': '1/4'},
        ...     {'name': 'Goblin', 'challenge_rating': '1/4'}
        ... ]
        >>> get_xp_for_encounter(monsters)
        100
    """
    total_xp = 0

    for monster in monsters:
        cr = monster.get('challenge_rating', '0')
        monster_xp = cr_to_xp(cr)
        total_xp += monster_xp

    return total_xp


def get_most_powerful_monster(monsters: list) -> dict:
    """
    Get the most powerful monster from a list based on CR.

    Args:
        monsters: List of monster dicts with 'challenge_rating' field

    Returns:
        The monster with the highest CR, or None if empty list

    Examples:
        >>> monsters = [
        ...     {'name': 'Goblin', 'challenge_rating': '1/4'},
        ...     {'name': 'Aboleth', 'challenge_rating': '10'},
        ...     {'name': 'Kobold', 'challenge_rating': '1/8'}
        ... ]
        >>> strongest = get_most_powerful_monster(monsters)
        >>> strongest['name']
        'Aboleth'
    """
    if not monsters:
        return None

    # Calculate XP for each monster and find max
    monsters_with_xp = [(monster, cr_to_xp(monster.get('challenge_rating', '0'))) for monster in monsters]

    # Return the monster with highest XP
    return max(monsters_with_xp, key=lambda pair: pair[1])[0]


# Quick reference for common CRs
COMMON_CRS = {
    'Rat': '0',
    'Kobold': '1/8',
    'Goblin': '1/4',
    'Orc': '1/2',
    'Owlbear': '3',
    'Troll': '5',
    'Young Dragon': '10',
    'Adult Dragon': '17',
    'Ancient Dragon': '24',
    'Tarrasque': '30'
}


if __name__ == "__main__":
    # Test the conversion
    print("CR to XP Conversion Tests:")
    print("-" * 40)

    test_crs = ["0", "1/8", "1/4", "1/2", "1", "5", "10", "20", "30"]

    for cr in test_crs:
        xp = cr_to_xp(cr)
        print(f"CR {cr:>4} = {xp:,} XP")

    print()
    print("Example Encounters:")
    print("-" * 40)

    # Example: 4 Goblins
    goblins = [{'name': 'Goblin', 'challenge_rating': '1/4'} for _ in range(4)]
    print(f"4 Goblins (CR 1/4): {get_xp_for_encounter(goblins)} XP")

    # Example: 1 Aboleth
    aboleth = [{'name': 'Aboleth', 'challenge_rating': '10'}]
    print(f"1 Aboleth (CR 10): {get_xp_for_encounter(aboleth)} XP")

    # Example: Mixed encounter
    mixed = [
        {'name': 'Goblin', 'challenge_rating': '1/4'},
        {'name': 'Goblin', 'challenge_rating': '1/4'},
        {'name': 'Hobgoblin', 'challenge_rating': '1/2'}
    ]
    print(f"2 Goblins + 1 Hobgoblin: {get_xp_for_encounter(mixed)} XP")

    # Test most powerful
    strongest = get_most_powerful_monster(mixed + aboleth)
    print(f"\nMost powerful: {strongest['name']} (CR {strongest['challenge_rating']})")
