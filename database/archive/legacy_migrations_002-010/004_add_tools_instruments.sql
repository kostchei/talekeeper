-- Migration: Add all SRD tools and musical instruments as uncommon rarity
-- This adds artisan's tools, other tools, and musical instruments from the D&D SRD

-- Artisan's Tools
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ('Alchemist Supplies', 'Tools for creating chemical compounds and identifying substances.', 'tool', 'uncommon', 50, 8.0),
    ('Brewer Supplies', 'Equipment for brewing beer and detecting poison in drinks.', 'tool', 'uncommon', 20, 9.0),
    ('Calligrapher Supplies', 'Inks, quills, and paper for writing with artistic flair.', 'tool', 'uncommon', 10, 5.0),
    ('Carpenter Tools', 'Saws, hammers, and chisels for working wood.', 'tool', 'uncommon', 8, 6.0),
    ('Cartographer Tools', 'Compass, calipers, and parchment for mapmaking.', 'tool', 'uncommon', 15, 6.0),
    ('Cobbler Tools', 'Tools for making and repairing leather goods and shoes.', 'tool', 'uncommon', 5, 5.0),
    ('Cook Utensils', 'Pots, pans, and utensils for preparing food.', 'tool', 'uncommon', 1, 8.0),
    ('Glassblower Tools', 'Pipes, molds, and blocks for shaping glass.', 'tool', 'uncommon', 30, 5.0),
    ('Jeweler Tools', 'Small tools for cutting gems and working precious metals.', 'tool', 'uncommon', 25, 2.0),
    ('Leatherworker Tools', 'Knives, needles, and thread for working leather.', 'tool', 'uncommon', 5, 5.0),
    ('Mason Tools', 'Chisels, hammers, and trowels for working stone.', 'tool', 'uncommon', 10, 8.0),
    ('Painter Supplies', 'Pigments, brushes, and canvas for creating art.', 'tool', 'uncommon', 10, 5.0),
    ('Potter Tools', 'Clay, glazes, and tools for making ceramic items.', 'tool', 'uncommon', 10, 3.0),
    ('Smith Tools', 'Hammers, tongs, and anvil for working metal.', 'tool', 'uncommon', 20, 8.0),
    ('Tinker Tools', 'Various small tools for working with clockwork and mechanisms.', 'tool', 'uncommon', 50, 10.0),
    ('Weaver Tools', 'Thread, needles, and loom for creating textiles.', 'tool', 'uncommon', 1, 5.0),
    ('Woodcarver Tools', 'Knives and chisels for carving wood.', 'tool', 'uncommon', 1, 5.0);

-- Other Tools
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ("Disguise Kit", "Cosmetics, hair dye, and props for changing appearance.", 'tool', 'uncommon', 25, 3.0),
    ("Forgery Kit", "Pens, inks, and seals for creating false documents.", 'tool', 'uncommon', 15, 5.0),
    ("Herbalism Kit", "Pouches, vials, and tools for identifying plants.", 'tool', 'uncommon', 5, 3.0),
    ("Navigator's Tools", "Compass, sextant, and charts for navigation.", 'tool', 'uncommon', 25, 2.0),
    ("Poisoner's Kit", "Vials, chemicals, and tools for handling poison.", 'tool', 'uncommon', 50, 2.0),
    ("Thieves' Tools", "Lock picks and small tools for disarming traps.", 'tool', 'uncommon', 25, 1.0);

-- Gaming Sets
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ('Dice Set', 'A set of gaming dice.', 'tool', 'uncommon', 0.1, 0.0),
    ('Dragonchess Set', 'An ornate chess set with dragon pieces.', 'tool', 'uncommon', 1, 0.5),
    ('Playing Cards', 'A deck of cards for various games.', 'tool', 'uncommon', 0.5, 0.0),
    ('Three-Dragon Ante Set', 'A popular card game set.', 'tool', 'uncommon', 1, 0.5);

-- Musical Instruments
INSERT OR IGNORE INTO equipment (
    name, description, item_type, rarity, cost_gp, weight_lb
) VALUES 
    ('Bagpipes', 'Wind instrument with multiple pipes and air reservoir.', 'instrument', 'uncommon', 30, 6.0),
    ('Drum', 'Percussion instrument with stretched skin head.', 'instrument', 'uncommon', 6, 3.0),
    ('Dulcimer', 'Stringed instrument played with hammers.', 'instrument', 'uncommon', 25, 10.0),
    ('Flute', 'Woodwind instrument played sideways.', 'instrument', 'uncommon', 2, 1.0),
    ('Horn', 'Brass wind instrument.', 'instrument', 'uncommon', 3, 2.0),
    ('Lute', 'Plucked string instrument with rounded back.', 'instrument', 'uncommon', 35, 2.0),
    ('Lyre', 'Small stringed instrument with curved frame.', 'instrument', 'uncommon', 30, 2.0),
    ('Pan Flute', 'Multiple pipes of different lengths bound together.', 'instrument', 'uncommon', 12, 2.0),
    ('Shawm', 'Double-reed woodwind instrument.', 'instrument', 'uncommon', 2, 1.0),
    ('Viol', 'Bowed string instrument.', 'instrument', 'uncommon', 30, 1.0);