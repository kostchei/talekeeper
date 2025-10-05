-- D&D 2024 Core Cantrips (Level 0 Spells)
-- Phase 1: Essential cantrips for character creation
-- Source: D&D 2024 SRD

INSERT OR IGNORE INTO spells (id, name, level, school, casting_time, range_value, components, duration, concentration, ritual, description, higher_levels, source, classes) VALUES

-- COMBAT CANTRIPS (8 total)

('eldritch_blast', 'Eldritch Blast', 0, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'A beam of crackling energy streaks toward a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Force damage.',
 'The spell creates more than one beam when you reach certain levels: two beams at level 5, three beams at level 11, and four beams at level 17. You can direct the beams at the same target or at different ones. Make a separate attack roll for each beam.',
 'PHB', '["warlock"]'),

('fire_bolt', 'Fire Bolt', 0, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'You hurl a mote of fire at a creature or object within range. Make a ranged spell attack against the target. On a hit, the target takes 1d10 Fire damage. A flammable object hit by this spell ignites if it isn''t being worn or carried.',
 'This spell''s damage increases by 1d10 when you reach level 5 (2d10), level 11 (3d10), and level 17 (4d10).',
 'PHB', '["wizard", "sorcerer"]'),

('sacred_flame', 'Sacred Flame', 0, 'Evocation', '1 action', '60 feet', 'V, S', 'Instantaneous', 0, 0,
 'Flame-like radiance descends on a creature that you can see within range. The target must succeed on a Dexterity saving throw or take 1d8 Radiant damage. The target gains no benefit from cover for this saving throw.',
 'The spell''s damage increases by 1d8 when you reach level 5 (2d8), level 11 (3d8), and level 17 (4d8).',
 'PHB', '["cleric"]'),

('chill_touch', 'Chill Touch', 0, 'Necromancy', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0,
 'You create a ghostly, skeletal hand in the space of a creature within range. Make a ranged spell attack against the creature. On a hit, the target takes 1d8 Necrotic damage, and it can''t regain Hit Points until the start of your next turn. Until then, the hand clings to the target. If you hit an Undead target, it also has Disadvantage on attack rolls against you until the end of your next turn.',
 'This spell''s damage increases by 1d8 when you reach level 5 (2d8), level 11 (3d8), and level 17 (4d8).',
 'PHB', '["wizard", "warlock", "sorcerer"]'),

('ray_of_frost', 'Ray of Frost', 0, 'Evocation', '1 action', '60 feet', 'V, S', 'Instantaneous', 0, 0,
 'A frigid beam of blue-white light streaks toward a creature within range. Make a ranged spell attack against the target. On a hit, it takes 1d8 Cold damage, and its Speed is reduced by 10 feet until the start of your next turn.',
 'The spell''s damage increases by 1d8 when you reach level 5 (2d8), level 11 (3d8), and level 17 (4d8).',
 'PHB', '["wizard", "sorcerer"]'),

('poison_spray', 'Poison Spray', 0, 'Necromancy', '1 action', '10 feet', 'V, S', 'Instantaneous', 0, 0,
 'You extend your hand toward a creature you can see within range and project a puff of noxious gas from your palm. The creature must succeed on a Constitution saving throw or take 1d12 Poison damage.',
 'This spell''s damage increases by 1d12 when you reach level 5 (2d12), level 11 (3d12), and level 17 (4d12).',
 'PHB', '["wizard", "warlock", "sorcerer", "druid"]'),

('shocking_grasp', 'Shocking Grasp', 0, 'Evocation', '1 action', 'Touch', 'V, S', 'Instantaneous', 0, 0,
 'Lightning springs from your hand to deliver a shock to a creature you try to touch. Make a melee spell attack against the target. You have Advantage on the attack roll if the target is wearing armor made of metal. On a hit, the target takes 1d8 Lightning damage, and it can''t take Reactions until the start of its next turn.',
 'The spell''s damage increases by 1d8 when you reach level 5 (2d8), level 11 (3d8), and level 17 (4d8).',
 'PHB', '["wizard", "sorcerer"]'),

('acid_splash', 'Acid Splash', 0, 'Evocation', '1 action', '60 feet', 'V, S', 'Instantaneous', 0, 0,
 'You hurl a bubble of acid. Choose one creature you can see within range, or choose two creatures you can see within range that are within 5 feet of each other. A target must succeed on a Dexterity saving throw or take 1d6 Acid damage.',
 'This spell''s damage increases by 1d6 when you reach level 5 (2d6), level 11 (3d6), and level 17 (4d6).',
 'PHB', '["wizard", "sorcerer"]'),

-- UTILITY CANTRIPS (12 total)

('light', 'Light', 0, 'Evocation', '1 action', 'Touch', 'V, M (a firefly or phosphorescent moss)', '1 hour', 0, 0,
 'You touch one object that is no larger than 10 feet in any dimension. Until the spell ends, the object sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet. The light can be colored as you like. Covering the object with something opaque blocks the light. The spell ends if you cast it again or dismiss it as an action. If you target an object held or worn by a hostile creature, that creature must succeed on a Dexterity saving throw to avoid the spell.',
 '',
 'PHB', '["wizard", "cleric", "bard", "sorcerer"]'),

('prestidigitation', 'Prestidigitation', 0, 'Transmutation', '1 action', '10 feet', 'V, S', '1 hour', 0, 0,
 'You create one of the following magical effects within range: a harmless sensory effect, light or snuff out a candle/torch/small campfire, clean or soil an object no larger than 1 cubic foot, chill/warm/flavor up to 1 cubic foot of nonliving material for 1 hour, make a color/small mark/symbol appear on an object or surface for 1 hour, or create a nonmagical trinket or illusory image that fits in your hand and lasts until the end of your next turn. If you cast this spell multiple times, you can have up to three of its non-instantaneous effects active at a time.',
 '',
 'PHB', '["wizard", "warlock", "bard", "sorcerer"]'),

('minor_illusion', 'Minor Illusion', 0, 'Illusion', '1 action', '30 feet', 'S, M (a bit of fleece)', '1 minute', 0, 0,
 'You create a sound or an image of an object within range that lasts for the duration. The illusion also ends if you dismiss it as an action or cast this spell again. If you create a sound, its volume can range from a whisper to a scream. If you create an image of an object, it must be no larger than a 5-foot cube. The image can''t create sound, light, smell, or any other sensory effect. Physical interaction with the image reveals it to be an illusion. If a creature uses its action to examine the sound or image, it can determine that it is an illusion with a successful Intelligence (Investigation) check against your spell save DC.',
 '',
 'PHB', '["wizard", "warlock", "bard", "sorcerer"]'),

('message', 'Message', 0, 'Transmutation', '1 action', '120 feet', 'V, S, M (a short piece of copper wire)', 'Instantaneous', 0, 0,
 'You point your finger toward a creature within range and whisper a message. The target (and only the target) hears the message and can reply in a whisper that only you can hear. You can cast this spell through solid objects if you are familiar with the target and know it is beyond the barrier. Magical silence, 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood blocks the spell. The spell doesn''t have to follow a straight line and can travel freely around corners or through openings.',
 '',
 'PHB', '["wizard", "bard", "sorcerer"]'),

('mending', 'Mending', 0, 'Transmutation', '1 minute', 'Touch', 'V, S, M (two lodestones)', 'Instantaneous', 0, 0,
 'This spell repairs a single break or tear in an object you touch, such as a broken chain link, two halves of a broken key, a torn cloak, or a leaking wineskin. As long as the break or tear is no larger than 1 foot in any dimension, you mend it, leaving no trace of the former damage. This spell can physically repair a magic item or construct, but it can''t restore magic to such an object.',
 '',
 'PHB', '["wizard", "cleric", "druid", "bard", "sorcerer"]'),

('thaumaturgy', 'Thaumaturgy', 0, 'Transmutation', '1 action', '30 feet', 'V', '1 minute', 0, 0,
 'You manifest a minor wonder within range. You create an instantaneous, harmless sensory effect, such as a shower of sparks, a puff of wind, faint musical notes, or an odd odor. You instantaneously light or snuff out a candle, torch, or small campfire. You instantaneously open or close an unlocked door or window. You alter the appearance of your eyes for 1 minute. You create an instantaneous sound that originates from a point of your choice within range, such as a rumble of thunder, the cry of a raven, or ominous whispers. You cause harmless tremors in the ground for 1 minute. You create an instantaneous, harmless sensory effect within a 20-foot cube, such as falling leaves, a gust of wind, faint music, or a smell.',
 '',
 'PHB', '["cleric"]'),

('spare_the_dying', 'Spare the Dying', 0, 'Necromancy', '1 action', 'Touch', 'V, S', 'Instantaneous', 0, 0,
 'You touch a living creature that has 0 Hit Points. The creature becomes Stable. This spell has no effect on Undead or Constructs.',
 '',
 'PHB', '["cleric"]'),

('resistance', 'Resistance', 0, 'Abjuration', '1 action', 'Touch', 'V, S, M (a miniature cloak)', 'Concentration, up to 1 minute', 1, 0,
 'You touch one willing creature. Once before the spell ends, the target can roll a d4 and add the number rolled to one saving throw of its choice. It can roll the die before or after making the saving throw. The spell then ends.',
 '',
 'PHB', '["cleric", "druid"]'),

('true_strike', 'True Strike', 0, 'Divination', '1 action', '30 feet', 'S, M (a weapon with which you have proficiency and that is worth at least 1 CP)', 'Instantaneous', 0, 0,
 'Guided by a flash of magical insight, you make one attack with the weapon used in the spell''s casting. The attack uses your spellcasting ability for the attack and damage rolls instead of using Strength or Dexterity. If the attack deals damage, it can be Radiant damage or the weapon''s normal damage type (your choice).',
 '',
 'PHB', '["wizard", "warlock", "bard", "sorcerer"]'),

('dancing_lights', 'Dancing Lights', 0, 'Illusion', '1 action', '120 feet', 'V, S, M (a bit of phosphorus or wychwood, or a glowworm)', 'Concentration, up to 1 minute', 1, 0,
 'You create up to four torch-sized lights within range, making them appear as torches, lanterns, or glowing orbs that hover in the air for the duration. You can also combine the four lights into one glowing vaguely humanoid form of Medium size. Whichever form you choose, each light sheds Dim Light in a 10-foot radius. As a Bonus Action on your turn, you can move the lights up to 60 feet to a new spot within range. A light must be within 20 feet of another light created by this spell, and a light winks out if it exceeds the spell''s range.',
 '',
 'PHB', '["wizard", "bard", "sorcerer"]');