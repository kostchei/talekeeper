-- Basic spell data with ritual spells
-- D&D 2024 Core Spells

INSERT OR IGNORE INTO spells (id, name, level, school, casting_time, range_value, components, duration, concentration, ritual, description, higher_levels, source, classes) VALUES
-- Cantrips
('guidance', 'Guidance', 0, 'Divination', '1 action', 'Touch', 'V, S', 'Concentration, up to 1 minute', 1, 0, 'You touch one willing creature. Once before the spell ends, the target can roll a d4 and add the number rolled to one ability check of its choice.', '', 'PHB', '["cleric", "druid"]'),
('mage_hand', 'Mage Hand', 0, 'Conjuration', '1 action', '30 feet', 'V, S', '1 minute', 0, 0, 'A spectral, floating hand appears at a point you choose within range. The hand lasts for the duration or until you dismiss it as an action.', '', 'PHB', '["bard", "sorcerer", "warlock", "wizard"]'),

-- 1st Level Spells
('detect_magic', 'Detect Magic', 1, 'Divination', '1 action', 'Self', 'V, S', 'Concentration, up to 10 minutes', 1, 1, 'For the duration, you sense the presence of magic within 30 feet of you.', '', 'PHB', '["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "wizard"]'),
('identify', 'Identify', 1, 'Divination', '1 minute', 'Touch', 'V, S, M (a pearl worth at least 100 gp)', '1 minute', 0, 1, 'You choose one object that you must touch throughout the casting of the spell. If it is a magic item or some other magic-imbued object, you learn its properties and how to use them.', '', 'PHB', '["bard", "wizard"]'),
('comprehend_languages', 'Comprehend Languages', 1, 'Divination', '1 action', 'Self', 'V, S, M (a pinch of soot and salt)', '1 hour', 0, 1, 'For the duration, you understand the literal meaning of any spoken language that you hear.', '', 'PHB', '["bard", "sorcerer", "warlock", "wizard"]'),
('cure_wounds', 'Cure Wounds', 1, 'Evocation', '1 action', 'Touch', 'V, S', 'Instantaneous', 0, 0, 'A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier.', 'When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d8 for each slot level above 1st.', 'PHB', '["bard", "cleric", "druid", "paladin", "ranger"]'),
('magic_missile', 'Magic Missile', 1, 'Evocation', '1 action', '120 feet', 'V, S', 'Instantaneous', 0, 0, 'You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range.', 'When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st.', 'PHB', '["sorcerer", "wizard"]'),

-- 2nd Level Spells
('augury', 'Augury', 2, 'Divination', '1 minute', 'Self', 'V, S, M (specially marked sticks, bones, or similar tokens worth at least 25 gp)', '1 minute', 0, 1, 'By casting gem-inlaid sticks, rolling dragon bones, laying out ornate cards, or employing some other divining tool, you receive an omen from an otherworldly entity about the results of a specific course of action that you plan to take within the next 30 minutes.', '', 'PHB', '["cleric"]'),
('find_traps', 'Find Traps', 2, 'Divination', '1 action', '120 feet', 'V, S', '1 minute', 0, 1, 'You sense the presence of any trap within range that is within line of sight.', '', 'PHB', '["cleric", "druid", "ranger"]'),

-- 3rd Level Spells
('water_breathing', 'Water Breathing', 3, 'Transmutation', '1 action', '30 feet', 'V, S, M (a short reed or piece of straw)', '24 hours', 0, 1, 'This spell grants up to ten willing creatures you can see within range the ability to breathe underwater until the spell ends.', '', 'PHB', '["druid", "ranger", "sorcerer", "wizard"]'),
('water_walk', 'Water Walk', 3, 'Transmutation', '1 action', '30 feet', 'V, S, M (a piece of cork)', '1 hour', 0, 1, 'This spell grants the ability to move across any liquid surface—such as water, acid, mud, snow, quicksand, or lava—as if it were harmless solid ground.', '', 'PHB', '["cleric", "druid", "ranger", "sorcerer"]'),

-- 4th Level Spells
('divination', 'Divination', 4, 'Divination', '1 action', 'Self', 'V, S, M (incense and a sacrificial offering appropriate to your religion, together worth at least 25 gp)', '1 minute', 0, 1, 'Your magic and an offering put you in contact with a god or a god''s servants. You ask a single question concerning a specific goal, event, or activity to occur within 7 days.', '', 'PHB', '["cleric"]'),

-- 5th Level Spells
('commune', 'Commune', 5, 'Divination', '1 minute', 'Self', 'V, S, M (incense and a vial of holy or unholy water)', '1 minute', 0, 1, 'You contact your deity or a divine proxy and ask up to three questions that can be answered with a yes or no.', '', 'PHB', '["cleric"]'),
('commune_with_nature', 'Commune with Nature', 5, 'Divination', '1 minute', 'Self', 'V, S', '1 minute', 0, 1, 'You briefly become one with nature and gain knowledge of the surrounding territory.', '', 'PHB', '["druid", "ranger"]'),

-- 6th Level Spells
('forbiddance', 'Forbiddance', 6, 'Abjuration', '10 minutes', '40,000 square feet', 'V, S, M (a sprinkling of holy water, rare incense, and powdered ruby worth at least 1,000 gp)', '1 day', 0, 1, 'You create a ward against magical travel that protects up to 40,000 square feet of floor space to a height of 30 feet above the floor.', '', 'PHB', '["cleric"]');