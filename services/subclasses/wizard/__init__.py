# core
# core
"""
Wizard Subclasses Package

Contains all Wizard arcane tradition implementations.
"""

from .evocation import EvocationDefinition

# Registry of all wizard subclasses
WIZARD_SUBCLASSES = {
    'evocation': EvocationDefinition,
}

def get_wizard_subclass(subclass_name: str):
    """Get a wizard subclass definition by name."""
    return WIZARD_SUBCLASSES.get(subclass_name.lower())