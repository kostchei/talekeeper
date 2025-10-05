-- D&D 2024 Level 1 Spells
-- Phase 1: Essential spells for character creation
-- Source: D&D 2024 SRD

INSERT OR IGNORE INTO spells (id, name, level, school, casting_time, range_value, components, duration, concentration, ritual, description, higher_levels, source, classes) VALUES

-- UNIVERSAL / MULTI-CLASS SPELLS (10 total)

('shield', 'Shield', 1, 'Abjuration', '1 reaction', 'Self', 'V, S', 'Until the start of your next turn', 0, 0,
 'An invisible barrier of magical force appears and protects you. Until the start of your next turn, you have a +5 bonus to AC, including against the triggering attack, and you take no damage from Magic Missile.',
 '',
 'PHB', '["wizard", "sorcerer"]'),

('mage_armor', 'Mage Armor', 1, 'Abjuration', '1 action', 'Touch', 'V, S, M (a piece of cured leather)', '8 hours', 0, 0,
 'You touch a willing creature who isn''t wearing armor, and a protective magical force surrounds it until the spell ends. The target''s base AC becomes 13 + its Dexterity modifier. The spell ends if the target dons armor or if you dismiss the spell as an action.',
 '',
 'PHB', '["wizard", "sorcerer"]'),

('bless', 'Bless', 1, 'Enchantment', '1 action', '30 feet', 'V, S, M (a sprinkling of holy water)', 'Concentration, up to 1 minute', 1, 0,
 'You bless up to three creatures of your choice within range. Whenever a target makes an attack roll or a saving throw before the spell ends, the target can roll a d4 and add the number rolled to the attack roll or saving throw.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.',
 'PHB', '["cleric", "paladin"]'),

('healing_word', 'Healing Word', 1, 'Abjuration', '1 bonus action', '60 feet', 'V', 'Instantaneous', 0, 0,
 'A creature of your choice that you can see within range regains Hit Points equal to 1d4 + your spellcasting ability modifier. This spell has no effect on Undead or Constructs.',
 'When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d4 for each slot level above 1st.',
 'PHB', '["cleric", "bard", "druid"]'),

('protection_from_evil_and_good', 'Protection from Evil and Good', 1, 'Abjuration', '1 action', 'Touch', 'V, S, M (holy water or powdered silver and iron)', 'Concentration, up to 10 minutes', 1, 0,
 'Until the spell ends, one willing creature you touch is protected against certain types of creatures: Aberrations, Celestials, Elementals, Fey, Fiends, and Undead. The protection grants several benefits. Creatures of those types have Disadvantage on attack rolls against the target. The target also can''t be Charmed, Frightened, or Possessed by them. If the target is already Charmed, Frightened, or Possessed by such a creature, the target has Advantage on any new saving throw against the relevant effect.',
 '',
 'PHB', '["cleric", "paladin", "warlock", "wizard"]'),

('charm_person', 'Charm Person', 1, 'Enchantment', '1 action', '30 feet', 'V, S', '1 hour', 0, 0,
 'You attempt to charm a Humanoid you can see within range. It must make a Wisdom saving throw, and does so with Advantage if you or your companions are fighting it. If it fails the saving throw, it is Charmed by you until the spell ends or until you or your companions do anything harmful to it. The Charmed creature regards you as a friendly acquaintance. When the spell ends, the creature knows it was Charmed by you.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st. The creatures must be within 30 feet of each other when you target them.',
 'PHB', '["bard", "druid", "sorcerer", "warlock", "wizard"]'),

('expeditious_retreat', 'Expeditious Retreat', 1, 'Transmutation', '1 bonus action', 'Self', 'V, S', 'Concentration, up to 10 minutes', 1, 0,
 'This spell allows you to move at an incredible pace. When you cast this spell, and then as a Bonus Action on each of your turns until the spell ends, you can take the Dash action.',
 '',
 'PHB', '["sorcerer", "warlock", "wizard"]'),

('feather_fall', 'Feather Fall', 1, 'Transmutation', '1 reaction', '60 feet', 'V, M (a small feather or piece of down)', '1 minute', 0, 0,
 'Choose up to five falling creatures within range. A falling creature''s rate of descent slows to 60 feet per round until the spell ends. If the creature lands before the spell ends, it takes no falling damage and can land on its feet, and the spell ends for that creature.',
 '',
 'PHB', '["bard", "sorcerer", "wizard"]'),

('speak_with_animals', 'Speak with Animals', 1, 'Divination', '1 action', 'Self', 'V, S', '10 minutes', 0, 1,
 'You gain the ability to comprehend and verbally communicate with Beasts for the duration. The knowledge and awareness of many Beasts is limited by their intelligence, but at minimum, Beasts can give you information about nearby locations and monsters, including whatever they can perceive or have perceived within the past day.',
 '',
 'PHB', '["bard", "druid", "ranger", "warlock"]'),

('disguise_self', 'Disguise Self', 1, 'Illusion', '1 action', 'Self', 'V, S', '1 hour', 0, 0,
 'You make yourself look different until the spell ends or until you use your action to dismiss it. You can seem 1 foot shorter or taller and can appear heavier or lighter. You must adopt a form that has the same basic arrangement of limbs as you have. Otherwise, the extent of the illusion is up to you. The changes wrought by this spell fail to hold up to physical inspection.',
 '',
 'PHB', '["bard", "sorcerer", "wizard"]'),

-- WIZARD-SPECIFIC SPELLS (15 total)

('find_familiar', 'Find Familiar', 1, 'Conjuration', '1 hour', '10 feet', 'V, S, M (10 GP worth of charcoal, incense, and herbs that must be consumed by fire in a brass brazier)', 'Instantaneous', 0, 1,
 'You gain the service of a familiar, a spirit that takes an animal form you choose: Bat, Cat, Frog, Hawk, Lizard, Octopus, Owl, Rat, Raven, Spider, or Weasel. Appearing in an unoccupied space within range, the familiar has the statistics of the chosen form. Your familiar acts independently of you, but it always obeys your commands. In combat, it rolls its own initiative and acts on its own turn. A familiar can''t attack, but it can take other actions as normal. When the familiar drops to 0 Hit Points, it disappears. It reappears after you cast this spell again.',
 '',
 'PHB', '["wizard"]'),

('burning_hands', 'Burning Hands', 1, 'Evocation', '1 action', 'Self (15-foot cone)', 'V, S', 'Instantaneous', 0, 0,
 'As you hold your hands with thumbs touching and fingers spread, a thin sheet of flames shoots forth from your outstretched fingertips. Each creature in a 15-foot Cone must make a Dexterity saving throw. A creature takes 3d6 Fire damage on a failed save, or half as much damage on a successful one. The fire ignites any flammable objects in the area that aren''t being worn or carried.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d6 for each slot level above 1st.',
 'PHB', '["sorcerer", "wizard"]'),

('thunderwave', 'Thunderwave', 1, 'Evocation', '1 action', 'Self (15-foot cube)', 'V, S', 'Instantaneous', 0, 0,
 'A wave of thunderous force sweeps out from you. Each creature in a 15-foot Cube originating from you must make a Constitution saving throw. On a failed save, a creature takes 2d8 Thunder damage and is pushed 10 feet away from you. On a successful save, the creature takes half as much damage and isn''t pushed. In addition, unsecured objects that are completely within the area of effect are automatically pushed 10 feet away from you by the spell''s effect, and the spell emits a thunderous boom audible out to 300 feet.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.',
 'PHB', '["bard", "druid", "sorcerer", "wizard"]'),

('grease', 'Grease', 1, 'Conjuration', '1 action', '60 feet', 'V, S, M (a bit of pork rind or butter)', '1 minute', 0, 0,
 'Slick grease covers the ground in a 10-foot square centered on a point within range and turns it into Difficult Terrain for the duration. When the grease appears, each creature standing in its area must succeed on a Dexterity saving throw or have the Prone condition. A creature that enters the area or ends its turn there must also succeed on a Dexterity saving throw or have the Prone condition.',
 '',
 'PHB', '["wizard"]'),

('sleep', 'Sleep', 1, 'Enchantment', '1 action', '90 feet', 'V, S, M (a pinch of fine sand, rose petals, or a cricket)', 'Concentration, up to 1 minute', 1, 0,
 'This spell sends creatures into a magical slumber. Roll 5d8; the total is how many Hit Points of creatures this spell can affect. Creatures within 20 feet of a point you choose within range are affected in ascending order of their current Hit Points (ignoring Unconscious creatures). Starting with the creature that has the lowest current Hit Points, each creature affected by this spell has the Unconscious condition until the spell ends, the sleeper takes damage, or someone uses an action to shake or slap the sleeper awake. Subtract each creature''s Hit Points from the total before moving on to the creature with the next lowest Hit Points. A creature''s Hit Points must be equal to or less than the remaining total for that creature to be affected.',
 'When you cast this spell using a spell slot of 2nd level or higher, roll an additional 2d8 for each slot level above 1st.',
 'PHB', '["bard", "sorcerer", "wizard"]'),

('color_spray', 'Color Spray', 1, 'Illusion', '1 action', 'Self (15-foot cone)', 'V, S, M (a pinch of powder or sand that is colored red, yellow, and blue)', 'Instantaneous', 0, 0,
 'A dazzling array of flashing, colored light springs from your hand. Roll 6d10; the total is how many Hit Points of creatures this spell can affect. Creatures in a 15-foot Cone originating from you are affected in ascending order of their current Hit Points (ignoring Blinded creatures). Starting with the creature that has the lowest current Hit Points, each creature affected by this spell has the Blinded condition until the end of your next turn. Subtract each creature''s Hit Points from the total before moving on to the creature with the next lowest Hit Points. A creature''s Hit Points must be equal to or less than the remaining total for that creature to be affected.',
 'When you cast this spell using a spell slot of 2nd level or higher, roll an additional 2d10 for each slot level above 1st.',
 'PHB', '["sorcerer", "wizard"]'),

('fog_cloud', 'Fog Cloud', 1, 'Conjuration', '1 action', '120 feet', 'V, S', 'Concentration, up to 1 hour', 1, 0,
 'You create a 20-foot-radius Sphere of fog centered on a point within range. The Sphere is Heavily Obscured. It lasts for the duration or until a wind of moderate or greater speed (at least 10 miles per hour) disperses it.',
 'When you cast this spell using a spell slot of 2nd level or higher, the radius of the fog increases by 20 feet for each slot level above 1st.',
 'PHB', '["druid", "ranger", "sorcerer", "wizard"]'),

('jump', 'Jump', 1, 'Transmutation', '1 action', 'Touch', 'V, S, M (a grasshopper''s hind leg)', '1 minute', 0, 0,
 'You touch a creature. The creature''s jump distance is tripled until the spell ends.',
 '',
 'PHB', '["druid", "ranger", "sorcerer", "wizard"]'),

('longstrider', 'Longstrider', 1, 'Transmutation', '1 action', 'Touch', 'V, S, M (a pinch of dirt)', '1 hour', 0, 0,
 'You touch a creature. The target''s Speed increases by 10 feet until the spell ends.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.',
 'PHB', '["bard", "druid", "ranger", "wizard"]'),

('silent_image', 'Silent Image', 1, 'Illusion', '1 action', '60 feet', 'V, S, M (a bit of fleece)', 'Concentration, up to 10 minutes', 1, 0,
 'You create the image of an object, a creature, or some other visible phenomenon that is no larger than a 15-foot Cube. The image appears at a spot within range and lasts for the duration. The image is purely visual; it isn''t accompanied by sound, smell, or other sensory effects. You can use your action to cause the image to move to any spot within range. As the image changes location, you can alter its appearance so that its movements appear natural for the image. Physical interaction with the image reveals it to be an illusion. A creature can use its action to examine the image with an Intelligence (Investigation) check against your spell save DC. If the check succeeds, the creature discerns that the image is an illusion.',
 '',
 'PHB', '["bard", "sorcerer", "wizard"]'),

('chromatic_orb', 'Chromatic Orb', 1, 'Evocation', '1 action', '90 feet', 'V, S, M (a diamond worth at least 50 GP)', 'Instantaneous', 0, 0,
 'You hurl a 4-inch-diameter sphere of energy at a creature that you can see within range. You choose Acid, Cold, Fire, Lightning, Poison, or Thunder for the type of orb you create, and then make a ranged spell attack against the target. On a hit, the creature takes 3d8 damage of the type you chose.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.',
 'PHB', '["sorcerer", "wizard"]'),

('ice_knife', 'Ice Knife', 1, 'Conjuration', '1 action', '60 feet', 'S, M (a drop of water or piece of ice)', 'Instantaneous', 0, 0,
 'You create a shard of ice and fling it at one creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Piercing damage. Hit or miss, the shard then explodes. The target and each creature within 5 feet of it must succeed on a Dexterity saving throw or take 2d6 Cold damage.',
 'When you cast this spell using a spell slot of 2nd level or higher, the Cold damage increases by 1d6 for each slot level above 1st.',
 'PHB', '["druid", "sorcerer", "wizard"]'),

('ray_of_sickness', 'Ray of Sickness', 1, 'Necromancy', '1 action', '60 feet', 'V, S', 'Instantaneous', 0, 0,
 'A ray of sickening greenish energy lashes out toward a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 2d8 Poison damage and has the Poisoned condition until the end of your next turn.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d8 for each slot level above 1st.',
 'PHB', '["sorcerer", "wizard"]'),

('false_life', 'False Life', 1, 'Necromancy', '1 action', 'Self', 'V, S, M (a small amount of alcohol or distilled spirits)', '1 hour', 0, 0,
 'Bolstering yourself with a necromantic facsimile of life, you gain 1d4 + 4 Temporary Hit Points.',
 'When you cast this spell using a spell slot of 2nd level or higher, you gain 5 additional Temporary Hit Points for each slot level above 1st.',
 'PHB', '["sorcerer", "wizard"]'),

('alarm', 'Alarm', 1, 'Abjuration', '1 minute', '30 feet', 'V, S, M (a tiny bell and a piece of fine silver wire)', '8 hours', 0, 1,
 'You set an alarm against unwanted intrusion. Choose a door, a window, or an area within range that is no larger than a 20-foot Cube. Until the spell ends, an alarm alerts you whenever a creature touches or enters the warded area. When you cast the spell, you can designate creatures that won''t set off the alarm. You also choose whether the alarm is mental or audible. A mental alarm alerts you with a ping in your mind if you are within 1 mile of the warded area. An audible alarm produces the sound of a hand bell for 10 seconds within 60 feet.',
 '',
 'PHB', '["ranger", "wizard"]'),

-- CLERIC-SPECIFIC SPELLS (8 total)

('guiding_bolt', 'Guiding Bolt', 1, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'A flash of light streaks toward a creature of your choice within range. Make a ranged spell attack against the target. On a hit, the target takes 4d6 Radiant damage, and the next attack roll made against this target before the end of your next turn has Advantage.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d6 for each slot level above 1st.',
 'PHB', '["cleric"]'),

('inflict_wounds', 'Inflict Wounds', 1, 'Necromancy', '1 action', 'Touch', 'V, S', 'Instantaneous', 0, 0,
 'Make a melee spell attack against a creature you can reach. On a hit, the target takes 3d10 Necrotic damage.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d10 for each slot level above 1st.',
 'PHB', '["cleric"]'),

('shield_of_faith', 'Shield of Faith', 1, 'Abjuration', '1 bonus action', '60 feet', 'V, S, M (a small parchment with holy text)', 'Concentration, up to 10 minutes', 1, 0,
 'A shimmering field appears and surrounds a creature of your choice within range, granting it a +2 bonus to AC for the duration.',
 '',
 'PHB', '["cleric", "paladin"]'),

('sanctuary', 'Sanctuary', 1, 'Abjuration', '1 bonus action', '30 feet', 'V, S, M (a small silver mirror)', '1 minute', 0, 0,
 'You ward a creature within range against attack. Until the spell ends, any creature who targets the warded creature with an attack or a harmful spell must first make a Wisdom saving throw. On a failed save, the creature must choose a new target or lose the attack or spell. This spell doesn''t protect the warded creature from area effects. If the warded creature makes an attack, casts a spell that affects an enemy, or deals damage to another creature, this spell ends.',
 '',
 'PHB', '["cleric"]'),

('command', 'Command', 1, 'Enchantment', '1 action', '60 feet', 'V', 'Instantaneous', 0, 0,
 'You speak a one-word command to a creature you can see within range. The target must succeed on a Wisdom saving throw or follow the command on its next turn. The spell has no effect if the target is Undead, if it doesn''t understand your language, or if your command is directly harmful to it. Some typical commands and their effects follow. You might issue a command other than one described here. If you do so, the GM determines how the target behaves. If the target can''t follow your command, the spell ends. Approach, Drop, Flee, Grovel, or Halt.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can affect one additional creature for each slot level above 1st. The creatures must be within 30 feet of each other when you target them.',
 'PHB', '["cleric", "paladin"]'),

('bane', 'Bane', 1, 'Enchantment', '1 action', '30 feet', 'V, S, M (a drop of blood)', 'Concentration, up to 1 minute', 1, 0,
 'Up to three creatures of your choice that you can see within range must each make a Charisma saving throw. Whenever a target that fails this saving throw makes an attack roll or a saving throw before the spell ends, the target must roll a d4 and subtract the number rolled from the attack roll or saving throw.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.',
 'PHB', '["bard", "cleric"]'),

('detect_evil_and_good', 'Detect Evil and Good', 1, 'Divination', '1 action', 'Self', 'V, S', 'Concentration, up to 10 minutes', 1, 0,
 'For the duration, you know if there is an Aberration, Celestial, Elemental, Fey, Fiend, or Undead within 30 feet of you, as well as where the creature is located. Similarly, you know if there is a place or object within 30 feet of you that has been consecrated or desecrated. The spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.',
 '',
 'PHB', '["cleric", "paladin"]'),

('detect_poison_and_disease', 'Detect Poison and Disease', 1, 'Divination', '1 action', 'Self', 'V, S, M (a yew leaf)', 'Concentration, up to 10 minutes', 1, 1,
 'For the duration, you can sense the presence and location of poisons, poisonous creatures, and diseases within 30 feet of you. You also identify the kind of poison, poisonous creature, or disease in each case. The spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.',
 '',
 'PHB', '["cleric", "druid", "paladin", "ranger"]'),

-- WARLOCK-SPECIFIC SPELLS (5 total)

('hex', 'Hex', 1, 'Enchantment', '1 bonus action', '90 feet', 'V, S, M (the petrified eye of a newt)', 'Concentration, up to 1 hour', 1, 0,
 'You place a curse on a creature that you can see within range. Until the spell ends, you deal an extra 1d6 Necrotic damage to the target whenever you hit it with an attack. Also, choose one ability when you cast the spell. The target has Disadvantage on ability checks made with the chosen ability. If the target drops to 0 Hit Points before this spell ends, you can use a Bonus Action on a subsequent turn to curse a new creature. A Remove Curse cast on the target ends this spell early.',
 'When you cast this spell using a spell slot of 3rd or 4th level, you can maintain your Concentration on the spell for up to 8 hours. When you use a spell slot of 5th level or higher, you can maintain your Concentration on the spell for up to 24 hours.',
 'PHB', '["warlock"]'),

('hellish_rebuke', 'Hellish Rebuke', 1, 'Evocation', '1 reaction', '60 feet', 'V, S', 'Instantaneous', 0, 0,
 'You point your finger, and the creature that damaged you is momentarily surrounded by hellish flames. The creature must make a Dexterity saving throw. It takes 2d10 Fire damage on a failed save, or half as much damage on a successful one.',
 'When you cast this spell using a spell slot of 2nd level or higher, the damage increases by 1d10 for each slot level above 1st.',
 'PHB', '["warlock"]'),

('unseen_servant', 'Unseen Servant', 1, 'Conjuration', '1 action', '60 feet', 'V, S, M (a piece of string and a bit of wood)', '1 hour', 0, 1,
 'This spell creates an Invisible, mindless, shapeless, Medium force that performs simple tasks at your command until the spell ends. The servant springs into existence in an unoccupied space on the ground within range. It has AC 10, 1 Hit Point, and a Strength of 2, and it can''t attack. If it drops to 0 Hit Points, the spell ends. Once on each of your turns as a Bonus Action, you can mentally command the servant to move up to 15 feet and interact with an object. The servant can perform simple tasks that a human could do, such as fetching things, cleaning, mending, folding clothes, lighting fires, serving food, and pouring wine.',
 '',
 'PHB', '["bard", "warlock", "wizard"]'),

('illusory_script', 'Illusory Script', 1, 'Illusion', '1 minute', 'Touch', 'S, M (a lead-based ink worth at least 10 GP, which the spell consumes)', '10 days', 0, 1,
 'You write on parchment, paper, or some other suitable writing material and imbue it with a potent illusion that lasts for the duration. To you and any creatures you designate when you cast the spell, the writing appears normal, written in your hand, and conveys whatever meaning you intended when you wrote the text. To all others, the writing appears as if it were written in an unknown or magical script that is unintelligible. Alternatively, you can cause the writing to appear to be an entirely different message, written in a different hand and language, though the language must be one you know.',
 '',
 'PHB', '["bard", "warlock", "wizard"]'),

('hideous_laughter', 'Hideous Laughter', 1, 'Enchantment', '1 action', '30 feet', 'V, S, M (tiny tarts and a feather)', 'Concentration, up to 1 minute', 1, 0,
 'A creature of your choice that you can see within range perceives everything as hilariously funny and has the Prone and Incapacitated conditions for the duration. The spell ends on a target if it takes damage or if someone uses an action to shake it out of its stupor. On its turn, the target can make a Wisdom saving throw. On a successful save, the spell ends.',
 '',
 'PHB', '["bard", "warlock", "wizard"]'),

-- PALADIN-SPECIFIC SPELLS (2 total)

('heroism', 'Heroism', 1, 'Enchantment', '1 action', 'Touch', 'V, S', 'Concentration, up to 1 minute', 1, 0,
 'A willing creature you touch is imbued with bravery. Until the spell ends, the creature is immune to the Frightened condition and gains Temporary Hit Points equal to your spellcasting ability modifier at the start of each of its turns. When the spell ends, the target loses any remaining Temporary Hit Points from this spell.',
 'When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.',
 'PHB', '["bard", "paladin"]'),

('searing_smite', 'Searing Smite', 1, 'Evocation', '1 bonus action', 'Self', 'V', 'Concentration, up to 1 minute', 1, 0,
 'The next time you hit a creature with a melee weapon attack during the spell''s duration, your weapon flares with white-hot intensity, and the attack deals an extra 1d6 Fire damage to the target and causes the target to ignite in flames. At the start of each of its turns until the spell ends, the target takes 1d6 Fire damage. A creature can end this damage by using its action to make a Dexterity check against your spell save DC to extinguish the flames.',
 'When you cast this spell using a spell slot of 2nd level or higher, the initial extra damage dealt by the attack increases by 1d6 for each slot level above 1st.',
 'PHB', '["paladin", "ranger"]'),

-- ADDITIONAL PALADIN SPELL (Divine Smite is in SRD)

('divine_smite', 'Divine Smite', 1, 'Evocation', '1 bonus action', 'Self', 'V', 'Instantaneous', 0, 0,
 'The next time you hit a creature with a melee attack during this spell''s duration, your attack deals an extra 2d8 Radiant damage. If the target is a Fiend or an Undead, you deal an extra 3d8 Radiant damage instead.',
 'When you cast this spell using a spell slot of 2nd level or higher, the extra damage on a hit increases by 1d8 for each slot level above 1st.',
 'PHB', '["paladin"]'),

('divine_favor', 'Divine Favor', 1, 'Transmutation', '1 bonus action', 'Self', 'V, S', 'Concentration, up to 1 minute', 1, 0,
 'Your prayer empowers you with divine radiance. Until the spell ends, your weapon attacks deal an extra 1d4 Radiant damage on a hit.',
 '',
 'PHB', '["paladin"]');