INSERT INTO skill_challenge_templates (id, name, description, base_dc) VALUES
('scaling_climbing', 'Scaling and Climbing', 'Navigate treacherous terrain requiring physical prowess and survival instincts', 14),
('ancient_lore', 'Access to Ancient Lore', 'Uncover forgotten knowledge through research and investigation', 14),
('social_encounter', 'Social Encounter', 'Navigate complex social dynamics and interpersonal challenges', 14),
('raging_river_ford', 'The Raging River Ford', 'Cross dangerous waters safely with skill and preparation', 14),
('calming_wild_beast', 'Calming the Wild Beast', 'Pacify an agitated creature through understanding and patience', 14),
('festival_games', 'The Festival Games', 'Compete in traditional games requiring performance and dexterity', 14),
('haunted_mire', 'Navigating the Haunted Mire', 'Traverse supernatural terrain using knowledge and perception', 14),
('merchant_cipher', 'Deciphering the Merchant''s Cipher', 'Decode secret messages using investigation and tools', 14),
('wilderness_medicine', 'Wilderness Medicine Emergency', 'Provide medical aid in challenging conditions', 14),
('court_intrigue', 'Navigating Court Intrigue', 'Maneuver through noble politics and social manipulation', 14),
('spirit_bridge', 'Spirit Bridge Crossing', 'Traverse ethereal pathways requiring magical and spiritual insight', 14),
('magical_storm', 'Navigate Magical Storm', 'Survive arcane weather phenomena through knowledge and awareness', 14),
('trade_route', 'Negotiate Trade Route', 'Establish favorable business relationships through diplomacy', 14),
('coded_message', 'Decipher Coded Message', 'Unravel hidden communications using analytical skills', 14),
('panicked_civilians', 'Calm Panicked Civilians', 'Restore order during crisis situations', 14),
('forage_purify', 'Forage and Purify', 'Gather safe food and water in wilderness conditions', 14),
('night_watch', 'Night Watch and Camp Security', 'Maintain vigilance and safety during rest periods', 14),
('rescue_cart', 'Rescue the Bogged Cart', 'Free trapped vehicles through teamwork and problem-solving', 14),
('smuggler_cache', 'Smuggler''s Cache', 'Locate and access hidden contraband safely', 14),
('rope_bridge', 'The Rickety Rope Bridge', 'Cross unstable structures requiring balance and careful movement', 14),
('calming_stampede', 'Calming the Stampede', 'Control panicked animals to prevent disaster', 14),
('ancient_ward', 'Disarming the Ancient Ward', 'Safely bypass magical protections through knowledge and investigation', 14),
('icy_crevasse', 'The Icy Crevasse', 'Navigate dangerous ice formations in harsh conditions', 14);

-- Insert skills for each template
INSERT INTO skill_challenge_template_skills (template_id, skill_name, skill_order) VALUES
-- Scaling and Climbing
('scaling_climbing', 'Athletics', 1),
('scaling_climbing', 'Acrobatics', 2),
('scaling_climbing', 'Survival', 3),

-- Access to Ancient Lore
('ancient_lore', 'Investigation', 1),
('ancient_lore', 'Arcana', 2),
('ancient_lore', 'History', 3),

-- Social Encounter
('social_encounter', 'Insight', 1),
('social_encounter', 'Deception', 2),
('social_encounter', 'Persuasion', 3),

-- The Raging River Ford
('raging_river_ford', 'Athletics', 1),
('raging_river_ford', 'Acrobatics', 2),
('raging_river_ford', 'Nature', 3),

-- Calming the Wild Beast
('calming_wild_beast', 'Animal Handling', 1),
('calming_wild_beast', 'Nature', 2),
('calming_wild_beast', 'Survival', 3),

-- The Festival Games
('festival_games', 'Performance', 1),
('festival_games', 'Sleight of Hand', 2),
('festival_games', 'Acrobatics', 3),

-- Navigating the Haunted Mire
('haunted_mire', 'Nature', 1),
('haunted_mire', 'Religion', 2),
('haunted_mire', 'Perception', 3),

-- Deciphering the Merchant's Cipher
('merchant_cipher', 'Investigation', 1),
('merchant_cipher', 'Sleight of Hand', 2),
('merchant_cipher', 'Thieves'' Tools', 3),

-- Wilderness Medicine Emergency
('wilderness_medicine', 'Medicine', 1),
('wilderness_medicine', 'Nature', 2),
('wilderness_medicine', 'Herbalism Kit', 3),

-- Navigating Court Intrigue
('court_intrigue', 'Performance', 1),
('court_intrigue', 'Intimidation', 2),
('court_intrigue', 'Insight', 3),

-- Spirit Bridge Crossing
('spirit_bridge', 'Arcana', 1),
('spirit_bridge', 'Religion', 2),
('spirit_bridge', 'Performance', 3),

-- Navigate Magical Storm
('magical_storm', 'Nature', 1),
('magical_storm', 'Arcana', 2),
('magical_storm', 'Perception', 3),

-- Negotiate Trade Route
('trade_route', 'Persuasion', 1),
('trade_route', 'Investigation', 2),
('trade_route', 'Intimidation', 3),

-- Decipher Coded Message
('coded_message', 'Investigation', 1),
('coded_message', 'History', 2),
('coded_message', 'Insight', 3),

-- Calm Panicked Civilians
('panicked_civilians', 'Performance', 1),
('panicked_civilians', 'Persuasion', 2),
('panicked_civilians', 'Medicine', 3),

-- Forage and Purify
('forage_purify', 'Survival', 1),
('forage_purify', 'Nature', 2),
('forage_purify', 'Medicine', 3),

-- Night Watch and Camp Security
('night_watch', 'Perception', 1),
('night_watch', 'Stealth', 2),
('night_watch', 'Survival', 3),

-- Rescue the Bogged Cart
('rescue_cart', 'Animal Handling', 1),
('rescue_cart', 'Athletics', 2),
('rescue_cart', 'Investigation', 3),

-- Smuggler's Cache
('smuggler_cache', 'Investigation', 1),
('smuggler_cache', 'Perception', 2),
('smuggler_cache', 'Sleight of Hand', 3),

-- The Rickety Rope Bridge
('rope_bridge', 'Acrobatics', 1),
('rope_bridge', 'Sleight of Hand', 2),
('rope_bridge', 'Investigation', 3),

-- Calming the Stampede
('calming_stampede', 'Animal Handling', 1),
('calming_stampede', 'Nature', 2),
('calming_stampede', 'Intimidation', 3),

-- Disarming the Ancient Ward
('ancient_ward', 'Arcana', 1),
('ancient_ward', 'Investigation', 2),
('ancient_ward', 'Religion', 3),

-- The Icy Crevasse
('icy_crevasse', 'Athletics', 1),
('icy_crevasse', 'Survival', 2),
('icy_crevasse', 'Perception', 3);

-- Insert success options for each template
INSERT INTO skill_challenge_template_success (template_id, success_option) VALUES
-- Scaling and Climbing
('scaling_climbing', 'Rest'),
('scaling_climbing', 'Rations'),
('scaling_climbing', 'View of 2 hexes'),

-- Access to Ancient Lore
('ancient_lore', 'Easy Quest'),
('ancient_lore', 'Coin'),

-- Social Encounter
('social_encounter', 'Coin'),
('social_encounter', 'Reputation'),
('social_encounter', 'Rest'),
('social_encounter', 'Item'),

-- The Raging River Ford
('raging_river_ford', 'Inspiration'),
('raging_river_ford', 'Rations'),

-- Calming the Wild Beast
('calming_wild_beast', 'Inspiration'),
('calming_wild_beast', 'Item'),

-- The Festival Games
('festival_games', 'Coin'),
('festival_games', 'Item'),
('festival_games', 'Reputation'),

-- Navigating the Haunted Mire
('haunted_mire', 'Consumable'),
('haunted_mire', 'Inspiration'),

-- Deciphering the Merchant's Cipher
('merchant_cipher', 'Easy Quest'),
('merchant_cipher', 'Coin'),
('merchant_cipher', 'Item'),

-- Wilderness Medicine Emergency
('wilderness_medicine', 'Healing Potion'),
('wilderness_medicine', 'Healer''s Kit'),

-- Navigating Court Intrigue
('court_intrigue', 'Patron'),
('court_intrigue', 'Secrets'),
('court_intrigue', 'Invitation'),

-- Spirit Bridge Crossing
('spirit_bridge', 'Resistance'),
('spirit_bridge', 'Password'),
('spirit_bridge', 'Ethereal Sight'),

-- Navigate Magical Storm
('magical_storm', 'Safe passage'),
('magical_storm', 'Spell Scroll'),
('magical_storm', 'Identify hazard'),

-- Negotiate Trade Route
('trade_route', 'Reputation'),
('trade_route', 'Vendor x0.8 Cost'),
('trade_route', 'Medium Quest'),

-- Decipher Coded Message
('coded_message', 'Easy Quest'),
('coded_message', 'Coin'),
('coded_message', 'Rest'),

-- Calm Panicked Civilians
('panicked_civilians', 'Rest'),
('panicked_civilians', 'Coin'),

-- Forage and Purify
('forage_purify', 'Rations'),
('forage_purify', 'Rest'),

-- Night Watch and Camp Security
('night_watch', 'Rest'),
('night_watch', 'Easy Encounter'),
('night_watch', 'Advantage on next Initiative roll'),

-- Rescue the Bogged Cart
('rescue_cart', 'Item'),
('rescue_cart', 'Coin'),
('rescue_cart', 'Reputation'),

-- Smuggler's Cache
('smuggler_cache', 'Coin'),
('smuggler_cache', 'Consumable'),
('smuggler_cache', 'Easy Quest'),

-- The Rickety Rope Bridge
('rope_bridge', 'View 3 hexes'),
('rope_bridge', 'Potion of Healing'),

-- Calming the Stampede
('calming_stampede', 'Free Lodging'),
('calming_stampede', '+2 Reputation'),

-- Disarming the Ancient Ward
('ancient_ward', 'Hoard'),
('ancient_ward', 'View 2 hexes'),

-- The Icy Crevasse
('icy_crevasse', 'Easy Quest'),
('icy_crevasse', 'Gain Inspiration');

-- Insert failure options for each template
INSERT INTO skill_challenge_template_failure (template_id, failure_option) VALUES
-- Scaling and Climbing
('scaling_climbing', 'Exhaustion'),
('scaling_climbing', 'Falling damage'),
('scaling_climbing', 'Poison condition'),

-- Access to Ancient Lore
('ancient_lore', 'Hard Quest'),
('ancient_lore', 'Rations'),

-- Social Encounter
('social_encounter', 'Lose Coin'),
('social_encounter', 'Poison condition'),

-- The Raging River Ford
('raging_river_ford', 'Exhaustion'),
('raging_river_ford', 'Bludgeoning damage'),
('raging_river_ford', 'Lost Gear'),

-- Calming the Wild Beast
('calming_wild_beast', 'Hard Encounter vs Beasts with disadvantage Initiative'),

-- The Festival Games
('festival_games', 'Easy Encounter vs Humanoids'),

-- Navigating the Haunted Mire
('haunted_mire', 'Hard encounter vs Undead'),
('haunted_mire', 'Exhaustion'),

-- Deciphering the Merchant's Cipher
('merchant_cipher', 'Reputation'),
('merchant_cipher', 'Hard encounter vs Construct'),

-- Wilderness Medicine Emergency
('wilderness_medicine', 'Rations'),
('wilderness_medicine', 'Poisoned'),

-- Navigating Court Intrigue
('court_intrigue', 'Disadvantage with Nobles'),
('court_intrigue', 'Enemy'),
('court_intrigue', 'Banished'),

-- Spirit Bridge Crossing
('spirit_bridge', 'No Rest'),
('spirit_bridge', 'Vulnerability'),
('spirit_bridge', 'Disadvantage on Attacks'),

-- Navigate Magical Storm
('magical_storm', 'Wild Magic'),
('magical_storm', 'Lost'),
('magical_storm', 'Spell slot loss'),

-- Negotiate Trade Route
('trade_route', 'Coin'),
('trade_route', 'Hard Quest'),
('trade_route', 'Hard Encounter vs Humanoids'),

-- Decipher Coded Message
('coded_message', 'Dangerous Trap'),
('coded_message', 'Reputation'),

-- Calm Panicked Civilians
('panicked_civilians', 'Easy Humanoid Encounter'),
('panicked_civilians', 'Reputation'),
('panicked_civilians', 'Bludgeoning damage'),

-- Forage and Purify
('forage_purify', 'Poisoned'),
('forage_purify', 'Hazard'),

-- Night Watch and Camp Security
('night_watch', 'Exhaustion'),
('night_watch', 'Medium Encounter'),

-- Rescue the Bogged Cart
('rescue_cart', 'Exhaustion'),
('rescue_cart', 'Item'),
('rescue_cart', 'Damage'),

-- Smuggler's Cache
('smuggler_cache', 'Dangerous Trap'),
('smuggler_cache', 'Medium Encounter vs Humanoid'),

-- The Rickety Rope Bridge
('rope_bridge', '3d6 bludgeoning'),
('rope_bridge', 'Lose Inspiration'),

-- Calming the Stampede
('calming_stampede', 'Coin'),
('calming_stampede', 'Bludgeoning Damage'),
('calming_stampede', 'Hard encounter vs beasts'),

-- Disarming the Ancient Ward
('ancient_ward', '4d6 Force Damage'),

-- The Icy Crevasse
('icy_crevasse', 'Cold and Bludgeoning Damage');

-- Insert refuse options for each template
INSERT INTO skill_challenge_template_refuse (template_id, refuse_option) VALUES
-- Scaling and Climbing
('scaling_climbing', 'Rations'),

-- Access to Ancient Lore
('ancient_lore', 'None'),

-- Social Encounter
('social_encounter', 'Hard encounter vs humanoids'),
('social_encounter', 'Next Vendor has only 1d6 common items'),

-- The Raging River Ford
('raging_river_ford', 'Rations'),
('raging_river_ford', 'Hard encounter vs beasts'),

-- Calming the Wild Beast
('calming_wild_beast', 'Medium Encounter vs Beasts'),
('calming_wild_beast', 'Rations'),

-- The Festival Games
('festival_games', 'None'),

-- Navigating the Haunted Mire
('haunted_mire', 'Rations'),

-- Deciphering the Merchant's Cipher
('merchant_cipher', 'Vendor x1.2 Cost'),

-- Wilderness Medicine Emergency
('wilderness_medicine', 'Reputation loss'),

-- Navigating Court Intrigue
('court_intrigue', 'Lose access to noble quarter'),

-- Spirit Bridge Crossing
('spirit_bridge', 'Guaranteed difficult combat encounter'),

-- Navigate Magical Storm
('magical_storm', 'Detour: 2x rations, encounter risk'),

-- Negotiate Trade Route
('trade_route', 'Vendor x1.2 Cost'),

-- Decipher Coded Message
('coded_message', 'Hard Quest'),

-- Calm Panicked Civilians
('panicked_civilians', 'Setback trap'),

-- Forage and Purify
('forage_purify', 'Rations'),

-- Night Watch and Camp Security
('night_watch', 'Medium encounter at disadvantage to Initiative roll'),

-- Rescue the Bogged Cart
('rescue_cart', 'Vendor x1.2 Cost'),

-- Smuggler's Cache
('smuggler_cache', 'None'),

-- The Rickety Rope Bridge
('rope_bridge', 'rations'),
('rope_bridge', 'easy beast encounter'),

-- Calming the Stampede
('calming_stampede', 'Reputation'),
('calming_stampede', 'easy encounter vs beasts'),

-- Disarming the Ancient Ward
('ancient_ward', 'sacrifice Coin'),
('ancient_ward', 'rations to go round'),

-- The Icy Crevasse
('icy_crevasse', 'NPC dies + Reputation loss');