import random

TRAP_TYPES = ['Setback', 'Dangerous']
# Deadly traps are reserved for trap dungeon scenarios only.
TRAP_DETAILS = {
    '1-4': {
        'Setback': {'dc': 10, 'toHit': 3, 'damage': '1d10', 'xp': 25,
                    'description': 'snare, net, simple pit',
                    'effects': 'chance of restraint, exhaustion'},
        'Dangerous': {'dc': 12, 'toHit': 6, 'damage': '2d10', 'xp': 450,
                      'description': 'rolling ball, falling block, slashing scythe blade, spiked pit',
                      'effects': 'chance of injury - crush, slash, pierce'},
        # Deadly traps to be used in trap dungeons only
        'Deadly': {'dc': 16, 'toHit': 9, 'damage': '4d10', 'xp': 1800,
                   'description': 'poisoned spikes, diseased surface, gas',
                   'effects': 'chance of poison, disease'},
    },
    '5-10': {
        'Setback': {'dc': 10, 'toHit': 4, 'damage': '2d10', 'xp': 200,
                    'description': 'rolling ball, falling block, slashing scythe blade, spiked pit',
                    'effects': 'chance of injury - crush, slash, pierce'},
        'Dangerous': {'dc': 12, 'toHit': 7, 'damage': '4d10', 'xp': 1100,
                      'description': 'poisoned spikes, diseased surface, gas',
                      'effects': 'chance of poison, disease'},
        # Deadly traps to be used in trap dungeons only
        'Deadly': {'dc': 17, 'toHit': 10, 'damage': '10d10', 'xp': 10000,
                   'description': 'filling pit, filling room with water or sand, crushing, gas',
                   'effects': 'chance of drowning/suffocation'},
    },
    '11-16': {
        'Setback': {'dc': 11, 'toHit': 4, 'damage': '4d10', 'xp': 700,
                    'description': 'poisoned spikes, diseased surface, gas',
                    'effects': 'chance of poison, disease'},
        'Dangerous': {'dc': 12, 'toHit': 7, 'damage': '10d10', 'xp': 2300,
                      'description': 'filling pit, filling room with water or sand, crushing, gas',
                      'effects': 'chance of drowning/suffocation'},
        # Deadly traps to be used in trap dungeons only
        'Deadly': {'dc': 19, 'toHit': 11, 'damage': '18d10', 'xp': 25000,
                   'description': 'magic, fire, acid',
                   'effects': 'chance of soul destruction, petrification or complete disintegration'},
    },
    '17-20': {
        'Setback': {'dc': 11, 'toHit': 5, 'damage': '10d10', 'xp': 1800,
                    'description': 'filling pit, filling room with water or sand, crushing, gas',
                    'effects': 'chance of drowning/suffocation'},
        'Dangerous': {'dc': 12, 'toHit': 8, 'damage': '18d10', 'xp': 8400,
                      'description': 'magic, fire, acid',
                      'effects': 'chance of soul destruction, petrification or complete disintegration'},
        # Deadly traps to be used in trap dungeons only
        'Deadly': {'dc': 20, 'toHit': 12, 'damage': '24d10', 'xp': 33000,
                   'description': 'magic, fire, acid',
                   'effects': 'chance of soul destruction, petrification or complete disintegration'},
    }
}

HAZARDS = [
    {'name': 'Quicksand', 'dc': 15,
     'effect': 'Creature is restrained and sinks 1d4 feet per round.'},
    {'name': 'Poisonous Fumes', 'dc': 13,
     'effect': 'Con save or take 1d6 poison damage and be poisoned.'},
    {'name': 'Falling Rocks', 'dc': 14,
     'effect': 'Dex save or take 2d6 bludgeoning damage.'},
]

PRONOUN_SETS = [
    {'subject': 'he', 'object': 'him', 'possessive': 'his'},
    {'subject': 'she', 'object': 'her', 'possessive': 'her'},
    {'subject': 'they', 'object': 'them', 'possessive': 'their'},
]

HOMELAND_OPTIONS = [
    'Aquilonia',
    'Skeldir',
    'Tengri',
    'Cathay',
    'Nihon',
    'Carramoor',
    'Lusitania',
    'Kurzil',
    "Q'haran",
]

ARC_OPTIONS = ['Lolth', 'Bloodwar', 'Vecna']

NAMES_BY_HOMELAND = {
    'Aquilonia': ['Cassian', 'Lucia', 'Vespira', 'Gaius', 'Octavia'],
    'Skeldir': ['Bjorn', 'Ingrid', 'Eira', 'Leif', 'Solveig'],
    'Tengri': ['Temur', 'Altan', 'Sarnai', 'Bolor', 'Erden'],
    'Cathay': ['Liang', 'Mei', 'Shen', 'Jian', 'Lian'],
    'Nihon': ['Haruto', 'Aiko', 'Ren', 'Sora', 'Kei'],
    'Carramoor': ['Eamon', 'Saoirse', 'Declan', 'Niamh', 'Ronan'],
    'Lusitania': ['Mateo', 'Isadora', 'Rui', 'Bianca', 'Louren'],
    'Kurzil': ['Azar', 'Farah', 'Javed', 'Soraya', 'Reza'],
    "Q'haran": ['Nadir', 'Layla', 'Samir', 'Mira', 'Karim'],
}

DEFAULT_NAMES = ['Arin', 'Selene', 'Taran', 'Lyra', 'Jorin']

WILD_FEATURES = [
    'a crevasse, rock, ice or lava across your path',
    'a crevasse, rock, ice or lava parallel to your path',
    'a cave or sinkhole: rock, ice or lava',
    'a steep slope up',
    'a steep slope down',
    'a peak',
    'the base of a cliff',
    'the edge of a cliff',
    'boulders or other broken ground',
    'some brush and heather',
    'a dense grove of firs',
    'a medium stand of trees',
    'a ridgeline across your path',
    'a ridgeline parallel to your path',
    'a gully across your path',
    'a gully parallel to your path',
    'a river or water course, parallel to your path',
    'a river or water course, across your path',
    'a treacherous surface of ice and wet rocks',
    'a drift of deep snow',
    'a bridge',
    'a ruin',
    'a lone building',
    'a monument',
    'a hotspring',
    'raised ground, a hill or outcrop',
    'a crossroad',
    'a mountain pass',
    'a sheltered bay',
    'a ford river crossing',
    'where two rivers meet',
    'an open mine working',
    'a standing stone marking ley lines',
    'a hidden resting place, hard to find',
]

STAT_WEIGHTS = {
    'strength': 2,
    'intelligence': 15,
    'wisdom': 5,
    'dexterity': 4,
    'charisma': 4,
}

SKILLS = [
    {'skill': 'Athletics', 'stat': 'Strength'},
    {'skill': 'Knowledge Arcana', 'stat': 'Intelligence'},
    {'skill': 'Knowledge Nature', 'stat': 'Intelligence'},
    {'skill': 'Investigation', 'stat': 'Intelligence'},
    {'skill': 'Knowledge Religion', 'stat': 'Intelligence'},
    {'skill': 'a choice of crafting tools or kit', 'stat': 'Intelligence'},
    {'skill': 'Knowledge History', 'stat': 'Intelligence'},
    {'skill': 'a choice of gaming set or musical instrument', 'stat': 'Charisma'},
    {'skill': 'Animal Handling', 'stat': 'Wisdom'},
    {'skill': 'Insight', 'stat': 'Wisdom'},
    {'skill': 'Medicine', 'stat': 'Wisdom'},
    {'skill': 'Survival', 'stat': 'Wisdom'},
    {'skill': 'Perception', 'stat': 'Wisdom'},
    {'skill': 'Stealth', 'stat': 'Dexterity'},
    {'skill': 'Acrobatics', 'stat': 'Dexterity'},
    {'skill': 'Sleight of Hand', 'stat': 'Dexterity'},
    {'skill': 'Intimidation', 'stat': 'Charisma'},
    {'skill': 'Performance', 'stat': 'Charisma'},
    {'skill': 'Persuasion', 'stat': 'Charisma'},
    {'skill': 'Deception', 'stat': 'Charisma'},
]

SKILLS_BY_STAT = {}
for entry in SKILLS:
    SKILLS_BY_STAT.setdefault(entry['stat'].lower(), []).append(entry)

CHECK_TYPES = ('Simple Skill Check', 'Resource Swap', 'Skill Challenge')

RESOURCES_GAIN = [
    {
        'name': 'Health',
        'description': 'regain hit dice worth of healing',
        'tiers': {
            1: '1 hit die',
            2: '2 hit dice',
            3: '4 hit dice',
            4: '6 hit dice',
            5: '8 hit dice',
        }
    },
    {
        'name': 'Food',
        'description': 'gain 2d6 + proficiency bonus pounds of food and gallons of water',
    },
    {
        'name': 'Revitalised',
        'description': 'reduce your exhaustion by one level',
    },
    {
        'name': 'Godliness',
        'description': 'improve piety with a chosen god by one',
    },
    {
        'name': 'Cleansing',
        'description': 'reduce corruption by one',
    },
    {
        'name': 'Directions to a Hoard',
        'description': 'the next encounter drops a hoard',
    },
    {
        'name': 'Henching Opportunity',
        'description': 'recruit a hench-thing from this faction, limited by charisma',
    },
    {
        'name': 'Factional Mission',
        'description': 'gain access to an important mission for this faction',
    },
    {
        'name': 'Downtime Opportunity',
        'description': 'choose a downtime activity for 7 days, normal rules apply',
    },
    {
        'name': 'Mystical Empowerment',
        'description': 'regain a spell or class ability of an appropriate tier',
        'tiers': {
            1: 'level 1 ability or spell (0–1)',
            2: 'level 5 ability or spell (2–3)',
            3: 'level 7 ability or spell (4)',
            4: 'level 9 ability or spell (5)',
            5: 'level 11 ability or spell (6)',
        }
    },
    {
        'name': 'Wealth',
        'description': 'coin or other portable wealth worth',
        'tiers': {
            1: '500 sp or 1d100×10 sp',
            2: '375 gp or (2d100+25)×3 gp',
            3: '750 gp or 2d6×100+50 gp',
            4: '7,500 gp or 2d6×1000+500 gp',
            5: '75,000 gp or 2d6×10000+5000 gp',
        }
    },
]

RESOURCES_LOSS = [
    {
        'name': 'Health',
        'description': 'take damage equal to',
        'tiers': {
            1: '1d10 hit points',
            2: '2d10 hit points',
            3: '4d10 hit points',
            4: '10d10 hit points',
            5: '18d10 hit points',
        }
    },
    {
        'name': 'Reputation',
        'description': 'lose one level of faction reputation',
    },
    {
        'name': 'Exhaustion',
        'description': 'gain one level of exhaustion',
    },
    {
        'name': 'Corruption',
        'description': 'increase your corruption by one',
    },
    {
        'name': 'Piety',
        'description': 'reduce piety with a favored god by one',
    },
    {
        'name': 'Power Spent',
        'description': 'lose a spell slot, rage, or class ability use',
    },
    {
        'name': 'Disease',
        'description': 'contract cackle fever, sewer plague, or sight rot',
    },
    {
        'name': 'Poisoning',
        'description': 'suffer assassin’s blood: 1d12 damage and poisoned for 24 hours',
    },
    {
        'name': 'Food Stores',
        'description': 'lose supplies worth',
        'tiers': {
            1: '1d6 pounds of food or water',
            2: '2d6 pounds of food or water',
            3: '3d6 pounds of food or water',
            4: '4d6 pounds of food or water',
            5: '5d6 pounds of food or water',
        }
    },
    {
        'name': 'Wealth',
        'description': 'damage or lose gear worth',
        'tiers': {
            1: '25 gp',
            2: '100 gp',
            3: '250 gp',
            4: '2,500 gp',
            5: '25,000 gp',
        }
    },
]

SKILL_TIERS = [
    {'min': 1, 'max': 4, 'dc': 14, 'xp': 25, 'tier': 1,
     'descriptor': 'one of the least-known champions of'},
    {'min': 5, 'max': 8, 'dc': 16, 'xp': 250, 'tier': 2,
     'descriptor': 'a worthy representative of'},
    {'min': 9, 'max': 12, 'dc': 18, 'xp': 550, 'tier': 3,
     'descriptor': 'a leader among the people of'},
    {'min': 13, 'max': 16, 'dc': 20, 'xp': 1100, 'tier': 4,
     'descriptor': 'a paragon of'},
    {'min': 17, 'max': 20, 'dc': 21, 'xp': 2000, 'tier': 5,
     'descriptor': 'one of the most epic heroes of'},
]


def _trap_level_range(level: int) -> str:
    if level <= 4:
        return '1-4'
    if level <= 10:
        return '5-10'
    if level <= 16:
        return '11-16'
    return '17-20'


def generate_trap(level: int) -> dict:
    trap_type = random.choice(TRAP_TYPES)
    level_range = _trap_level_range(level)
    details = TRAP_DETAILS[level_range][trap_type]
    return {'type': trap_type, **details}


def generate_hazard() -> dict:
    return random.choice(HAZARDS)


def generate_skill_challenge(level: int) -> dict:
    varied_level = max(1, min(20, level + random.randint(-4, 4)))
    tier = next((t for t in SKILL_TIERS if t['min'] <= varied_level <= t['max']), SKILL_TIERS[-1])

    weighted_stats = []
    for stat, weight in STAT_WEIGHTS.items():
        weighted_stats.extend([stat] * weight)
    stat_key = random.choice(weighted_stats)
    skill = random.choice(SKILLS_BY_STAT[stat_key])

    homeland = random.choice(HOMELAND_OPTIONS)
    arc = random.choice(ARC_OPTIONS)
    wild_feature = random.choice(WILD_FEATURES)
    pronouns = random.choice(PRONOUN_SETS)
    names = NAMES_BY_HOMELAND.get(homeland, DEFAULT_NAMES)
    guide_name = random.choice(names)

    intro = (
        f"In {homeland}, near {wild_feature}, you encounter {guide_name}. "
        f"{pronouns['subject'].capitalize()} is {tier['descriptor']} {homeland} "
        f"and carries a quest tied to the {arc} arc."
    )

    gain = random.choice(RESOURCES_GAIN)
    loss_primary = random.choice(RESOURCES_LOSS)
    remaining_losses = [entry for entry in RESOURCES_LOSS if entry is not loss_primary]
    loss_secondary = random.choice(remaining_losses) if remaining_losses else loss_primary

    def format_resource(resource: dict, tier_value: int) -> str:
        name = resource['name'].strip()
        description = resource['description'].strip()
        tier_detail = resource.get('tiers', {}).get(tier_value)
        if tier_detail:
            description = f"{description} ({tier_detail.strip()})"
        text = f"{name} - {description}".strip()
        return ' '.join(text.split())

    gain_text = format_resource(gain, tier['tier'])
    loss_text = format_resource(loss_primary, tier['tier'])
    loss_secondary_text = format_resource(loss_secondary, tier['tier'])

    xp_success = tier['xp']
    xp_failure = xp_success // 2

    check_type = random.choice(CHECK_TYPES)
    details = []
    if check_type == 'Simple Skill Check':
        dc = tier['dc']
        details.extend([
            'Check Type: Simple Skill Check',
            f"Make a DC {dc} {skill['skill']} ({skill['stat']}) check.",
            f"Success: {gain_text}.",
            f"Failure: {loss_text}.",
        ])
        failure_text = loss_text
    elif check_type == 'Resource Swap':
        dc = max(5, tier['dc'] - 3)
        details.extend([
            'Check Type: Resource Swap',
            f"Make a DC {dc} {skill['skill']} ({skill['stat']}) check to broker the exchange.",
            f"Success: {gain_text}, but it costs {loss_text}.",
            f"Failure: You also suffer {loss_secondary_text}.",
        ])
        failure_text = f"{loss_text}; additionally {loss_secondary_text}"
    else:
        dc = max(5, tier['dc'] - 3)
        details.extend([
            'Check Type: Skill Challenge',
            f"Group check using {skill['skill']} ({skill['stat']}) at DC {dc}.",
            'Earn twice as many successes as participants before failures equal the number of participants.',
            f"Success: {gain_text}.",
            f"Failure: {loss_text}.",
        ])
        failure_text = loss_text

    details.append(f"XP Rewards: Success {xp_success} • Failure {xp_failure}")

    text = '\n'.join([intro, '', *details])

    return {
        'type': check_type,
        'skill': skill['skill'],
        'stat': skill['stat'],
        'dc': dc,
        'xp_success': xp_success,
        'xp_failure': xp_failure,
        'success': gain_text,
        'failure': failure_text,
        'intro': intro,
        'text': text,
    }
