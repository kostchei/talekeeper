# core
# core
"""
Proficiency Bonus Calculation System

D&D 2024 proficiency bonus scales with total character level:
- Levels 1-4: +2
- Levels 5-8: +3  
- Levels 9-12: +4
- Levels 13-16: +5
- Levels 17-20: +6

This affects:
- Attack rolls (weapon/spell proficiency)
- Saving throws (proficient saves only)
- Skill checks (proficient skills only)
- Spell save DC calculation
"""


def get_proficiency_bonus(character_level: int) -> int:
    """Get proficiency bonus based on character level."""
    if character_level >= 17:
        return 6
    elif character_level >= 13:
        return 5
    elif character_level >= 9:
        return 4
    elif character_level >= 5:
        return 3
    else:  # Levels 1-4
        return 2


def get_proficiency_bonus_from_context(context: dict) -> int:
    """Get proficiency bonus from character context."""
    level = context.get('level', 1)
    return get_proficiency_bonus(level)


# POTENTIAL_DEAD_CODE: Function 'get_proficiency_bonus_from_character' appears unused
def get_proficiency_bonus_from_character(character: dict) -> int:
    """Get proficiency bonus from character dict."""
    level = character.get('level', 1)
    return get_proficiency_bonus(level)