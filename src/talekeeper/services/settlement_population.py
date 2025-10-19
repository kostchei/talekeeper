# core
# category: utility
import random
from typing import Optional

# Deterministic seed offsets per settlement tier to keep population rolls stable per hex.
_SEED_OFFSETS = {
    'hamlet': 0x1F1F1F1F,
    'village': 0x2B2B2B2B,
    'town_small': 0x35353535,
    'town_medium': 0x41414141,
    'town_large': 0x4D4D4D4D,
}

_HAMLET_OPTIONS = [25, 75, 150, 200]
_VILLAGE_OPTIONS = [200, 500, 1000, 1500]


def determine_population(settlement_type: Optional[str], seed: int) -> int:
    """Return a deterministic population representative for a settlement.

    The values align with the vendor planning document population tiers so that
    economy, long rest, and UI displays stay in sync.
    """
    if not settlement_type or settlement_type == 'empty':
        return 0

    # Ensure the RNG is deterministic without relying on Python's hash randomization.
    base_seed = (seed & 0xFFFFFFFF) ^ _SEED_OFFSETS.get(settlement_type, 0x12345678)
    rng = random.Random(base_seed)

    if settlement_type == 'hamlet':
        return rng.choice(_HAMLET_OPTIONS)
    if settlement_type == 'village':
        return rng.choice(_VILLAGE_OPTIONS)
    if settlement_type == 'town_small':
        return 2000
    if settlement_type == 'town_medium':
        return 5000
    if settlement_type == 'town_large':
        return 10000

    return 0
