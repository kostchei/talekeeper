import random
{"Level": 1, "Low": 50, "Moderate": 75, "High": 100},
{"Level": 2, "Low": 100, "Moderate": 150, "High": 200},
{"Level": 3, "Low": 150, "Moderate": 225, "High": 400},
{"Level": 4, "Low": 250, "Moderate": 375, "High": 500},
{"Level": 5, "Low": 500, "Moderate": 750, "High": 1100},
{"Level": 6, "Low": 600, "Moderate": 1000, "High": 1400},
{"Level": 7, "Low": 750, "Moderate": 1300, "High": 1700},
# ... more levels as needed
]


# Dummy monster database
MONSTER_DB = [
{"name": "Goblin", "cr": 0.25, "xp": 50, "type": "humanoid"},
{"name": "Orc", "cr": 0.5, "xp": 100, "type": "humanoid"},
{"name": "Orc Warchief", "cr": 2, "xp": 450, "type": "humanoid"},
{"name": "Shadow Demon", "cr": 4, "xp": 1100, "type": "fiend"},
{"name": "Mind Flayer", "cr": 7, "xp": 2900, "type": "aberration"},
# ... extend as needed
]


class RandomBag:
def __init__(self, items: List[Any]):
self.original = items[:]
self.pool = items[:]


def draw(self):
if not self.pool:
self.pool = self.original[:]
item = random.choice(self.pool)
self.pool.remove(item)
return item


class EncounterGenerator:
def __init__(self, frame: CampaignFrame):
self.frame = frame
self.bags: Dict[int, RandomBag] = {}


def get_budget(self, level: int, difficulty: str) -> int:
for entry in XP_BUDGETS:
if entry["Level"] == level:
return entry[difficulty.capitalize()]
raise ValueError("Unknown level")


def generate_encounter(self, level: int) -> Dict[str, Any]:
if level not in self.bags:
# Filter monsters based on CR limits and frame weights
cr_cap = 0.25 * level if level < 5 else 0.5 * level
allowed = [m for m in MONSTER_DB if m["cr"] <= cr_cap and m["type"] in self.frame.monster_type_weights]
weighted_pool = [m for m in allowed for _ in range(int(self.frame.monster_type_weights[m["type"]] * 100))]
self.bags[level] = RandomBag(weighted_pool)


difficulty = random.choices(
population=["low", "moderate", "high"],
weights=[self.frame.difficulty_distribution.get(k, 0) for k in ["low", "moderate", "high"]]
)[0]


budget = self.get_budget(level, difficulty)


if difficulty == "high":
# High encounter = 1 strong monster
while True:
monster = self.bags[level].draw()
if monster["xp"] >= budget * 0.8:
return {
"level": level,
"difficulty": difficulty,
"monsters": [monster],
"total_xp": monster["xp"]
}
else:
# Low/Moderate: build up encounter
encounter = []
total = 0
while total < budget and len(encounter) < 4:
m = self.bags[level].draw()
if total + m["xp"] <= budget:
encounter.append(m)
total += m["xp"]
else:
break
return {
"level": level,
"difficulty": difficulty,
"monsters": encounter,
"total_xp": total
}