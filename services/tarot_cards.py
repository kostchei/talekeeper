# core
# core
import random
from typing import Dict, Any, Optional


TAROT_CARDS = {
    "BALANCE": {
        "upright": {
            "place": "A symmetrical chamber where opposing forces meet in harmony",
            "situation": "Choices that require careful weighing of consequences",
            "creature": "A fair-minded guardian judging intruders"
        },
        "reversed": {
            "place": "An unbalanced space tilting toward chaos",
            "situation": "Judgment clouded by prejudice or desperation",
            "creature": "A biased foe acting on blind hatred"
        }
    },
    "BEAST": {
        "upright": {
            "place": "Primal wilderness where nature reigns supreme",
            "situation": "Raw instinct and survival in untamed lands",
            "creature": "A powerful predator in its domain"
        },
        "reversed": {
            "place": "A corrupted natural space twisted by dark forces",
            "situation": "Bestial rage without purpose or control",
            "creature": "A maddened creature beyond reason"
        }
    },
    "CAMPFIRE": {
        "upright": {
            "place": "A warm gathering place offering rest and safety",
            "situation": "Fellowship and shared stories amid danger",
            "creature": "A protective guardian of travelers"
        },
        "reversed": {
            "place": "Cold ashes and abandoned refuge",
            "situation": "Betrayal where trust once dwelled",
            "creature": "A false friend lying in wait"
        }
    },
    "CAVERN": {
        "upright": {
            "place": "Deep underground passages hiding secrets",
            "situation": "Delving into darkness seeking hidden truth",
            "creature": "A dweller of the depths defending its lair"
        },
        "reversed": {
            "place": "A collapsing tunnel threatening burial",
            "situation": "Trapped in darkness with no escape",
            "creature": "A predator hunting in complete blackness"
        }
    },
    "CORPSE": {
        "upright": {
            "place": "A site of death holding lessons from the past",
            "situation": "Learning from endings to begin anew",
            "creature": "Remains that speak of what came before"
        },
        "reversed": {
            "place": "A charnel house of senseless slaughter",
            "situation": "Death without meaning or redemption",
            "creature": "The animated dead refusing to rest"
        }
    },
    "DRAGON": {
        "upright": {
            "place": "A legendary lair of ancient power and wealth",
            "situation": "Facing overwhelming might that tests courage",
            "creature": "A terrible force of primordial majesty"
        },
        "reversed": {
            "place": "Ruins of greed and hoarded treasures",
            "situation": "Avarice leading to inevitable destruction",
            "creature": "A tyrant grown mad with power"
        }
    },
    "FLAMES": {
        "upright": {
            "place": "A place of cleansing fire and transformation",
            "situation": "Destruction making way for renewal",
            "creature": "A being of pure elemental fury"
        },
        "reversed": {
            "place": "An inferno consuming everything indiscriminately",
            "situation": "Uncontrolled devastation leaving only ash",
            "creature": "Destruction personified without purpose"
        }
    },
    "MAZE": {
        "upright": {
            "place": "Twisting passages that challenge perception",
            "situation": "A puzzle requiring patience and insight",
            "creature": "A cunning guardian of secret ways"
        },
        "reversed": {
            "place": "Endless loops driving explorers to madness",
            "situation": "Confusion without hope of solution",
            "creature": "A maddened soul lost in endless wandering"
        }
    },
    "MONSTROSITY": {
        "upright": {
            "place": "Where nature's rules are broken and remade",
            "situation": "Confronting the unnatural and aberrant",
            "creature": "A thing that should not exist"
        },
        "reversed": {
            "place": "A breeding ground of chaos and mutation",
            "situation": "Corruption spreading beyond containment",
            "creature": "An abomination growing ever worse"
        }
    },
    "RUINS": {
        "upright": {
            "place": "Ancient stones whispering of lost glory",
            "situation": "Finding strength in what survives",
            "creature": "A remnant of a fallen civilization"
        },
        "reversed": {
            "place": "Crumbling decay threatening collapse",
            "situation": "The weight of failure crushing hope",
            "creature": "A guardian unable to prevent decline"
        }
    },
    "SKULL": {
        "upright": {
            "place": "A reminder of mortality focusing resolve",
            "situation": "Facing death with clarity and purpose",
            "creature": "Death itself given form and intent"
        },
        "reversed": {
            "place": "A mass grave of meaningless carnage",
            "situation": "Fear of death paralyzing action",
            "creature": "Undeath that mocks the living"
        }
    },
    "TAVERN": {
        "upright": {
            "place": "A lively gathering place full of rumors",
            "situation": "Opportunities found in social exchange",
            "creature": "A hospitable host with useful knowledge"
        },
        "reversed": {
            "place": "A den of vice and dangerous dealings",
            "situation": "Deception hiding behind friendly faces",
            "creature": "A predatory figure exploiting the unwary"
        }
    },
    "TOWER": {
        "upright": {
            "place": "A stronghold standing against all odds",
            "situation": "Sudden revelation shattering illusions",
            "creature": "A proud defender of high ground"
        },
        "reversed": {
            "place": "A crumbling edifice of failed ambition",
            "situation": "Catastrophic collapse of false security",
            "creature": "A fallen power refusing to accept defeat"
        }
    },
    "UNDEAD": {
        "upright": {
            "place": "Where death's grip refuses to release",
            "situation": "Confronting unfinished business from the past",
            "creature": "A restless spirit bound to this world"
        },
        "reversed": {
            "place": "A necropolis of mindless hunger",
            "situation": "The past consuming the present",
            "creature": "Soulless undeath spreading corruption"
        }
    },
    "VOID": {
        "upright": {
            "place": "An empty space pregnant with possibility",
            "situation": "The unknown offering both terror and wonder",
            "creature": "A being from beyond mortal comprehension"
        },
        "reversed": {
            "place": "Nihilistic emptiness draining all meaning",
            "situation": "Despair in the face of cosmic indifference",
            "creature": "A horror from the spaces between"
        }
    },
    "WARRIOR": {
        "upright": {
            "place": "A battlefield where courage is tested",
            "situation": "Conflict demanding strength and discipline",
            "creature": "A skilled fighter with a code of honor"
        },
        "reversed": {
            "place": "A site of brutal, senseless violence",
            "situation": "Aggression without purpose or honor",
            "creature": "A berserker lost to bloodlust"
        }
    }
}


def draw_tarot_card() -> Dict[str, Any]:
    card_name = random.choice(list(TAROT_CARDS.keys()))
    orientation = random.choice(["upright", "reversed"])

    card_data = TAROT_CARDS[card_name]
    meanings = card_data[orientation]

    aspect = random.choice(["place", "situation", "creature"])
    detail = meanings[aspect]

    return {
        "name": card_name,
        "orientation": orientation,
        "aspect": aspect,
        "detail": detail,
        "full_meanings": meanings
    }


def get_tarot_inspiration(card: Optional[Dict[str, Any]] = None) -> str:
    if card is None:
        card = draw_tarot_card()

    return card["detail"]
