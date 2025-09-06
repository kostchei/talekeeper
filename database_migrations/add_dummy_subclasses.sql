-- DUMMY SUBCLASS DATA - For development reference only
-- These are placeholder entries and features are not implemented

-- Create subclasses table if not exists
CREATE TABLE IF NOT EXISTS subclasses (
    id TEXT PRIMARY KEY,
    class_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    source TEXT DEFAULT 'PHB',
    is_implemented INTEGER DEFAULT 0,  -- Flag to indicate if actually implemented
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

-- Fighter Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('champion', 'fighter', 'Champion', 'DUMMY - A master of martial combat, skilled with a variety of weapons and armor', 0),
('battle_master', 'fighter', 'Battle Master', 'DUMMY - Those who employ martial techniques passed down through generations', 0),
('eldritch_knight', 'fighter', 'Eldritch Knight', 'DUMMY - Fighters who combine martial mastery with careful study of magic', 0);

-- Barbarian Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('berserker', 'barbarian', 'Path of the Berserker', 'DUMMY - For barbarians, rage is a means to an end—that end being violence', 0),
('totem_warrior', 'barbarian', 'Path of the Totem Warrior', 'DUMMY - A spiritual journey, as the barbarian accepts a spirit animal as guide', 0),
('ancestral_guardian', 'barbarian', 'Path of the Ancestral Guardian', 'DUMMY - Barbarians who draw on the spirits of ancestors', 0);

-- Rogue Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('thief', 'rogue', 'Thief', 'DUMMY - You hone your skills in the larcenous arts', 0),
('assassin', 'rogue', 'Assassin', 'DUMMY - You focus on the grim art of death', 0),
('arcane_trickster', 'rogue', 'Arcane Trickster', 'DUMMY - Rogues who enhance their skills with magic', 0);

-- Wizard Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('evocation', 'wizard', 'School of Evocation', 'DUMMY - Masters of spectacular magical effects', 0),
('necromancy', 'wizard', 'School of Necromancy', 'DUMMY - Focused on magic that manipulates life and death', 0),
('abjuration', 'wizard', 'School of Abjuration', 'DUMMY - Masters of protective magic and wards', 0);

-- Cleric Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('life', 'cleric', 'Life Domain', 'DUMMY - Gods of life promote vitality and health', 0),
('war', 'cleric', 'War Domain', 'DUMMY - Gods of war inspire warriors to great feats', 0),
('knowledge', 'cleric', 'Knowledge Domain', 'DUMMY - Gods of knowledge value learning and understanding', 0);

-- Paladin Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('devotion', 'paladin', 'Oath of Devotion', 'DUMMY - Bound to the loftiest ideals of justice and virtue', 0),
('vengeance', 'paladin', 'Oath of Vengeance', 'DUMMY - A solemn commitment to punish those who have committed grievous sins', 0),
('ancients', 'paladin', 'Oath of the Ancients', 'DUMMY - Paladins who cast their lot with the side of light', 0);

-- Ranger Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('hunter', 'ranger', 'Hunter', 'DUMMY - Emulating the Hunter archetype means accepting a role as guardian', 0),
('beast_master', 'ranger', 'Beast Master', 'DUMMY - Rangers who form bonds with beasts', 0),
('gloom_stalker', 'ranger', 'Gloom Stalker', 'DUMMY - At home in the darkest places', 0);

-- Warlock Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('fiend', 'warlock', 'The Fiend', 'DUMMY - You have made a pact with a fiend from the lower planes', 0),
('archfey', 'warlock', 'The Archfey', 'DUMMY - Your patron is a lord or lady of the fey', 0),
('great_old_one', 'warlock', 'The Great Old One', 'DUMMY - Your patron is a mysterious entity', 0);

-- Sorcerer Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('draconic', 'sorcerer', 'Draconic Bloodline', 'DUMMY - Your magic comes from draconic heritage', 0),
('wild_magic', 'sorcerer', 'Wild Magic', 'DUMMY - Your magic comes from the forces of chaos', 0),
('shadow_magic', 'sorcerer', 'Shadow Magic', 'DUMMY - You draw power from the Shadowfell', 0);

-- Bard Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('lore', 'bard', 'College of Lore', 'DUMMY - Bards who know something about most things', 0),
('valor', 'bard', 'College of Valor', 'DUMMY - Bards whose tales keep alive the memory of heroes', 0),
('glamour', 'bard', 'College of Glamour', 'DUMMY - Bards who mastered their craft in the Feywild', 0);

-- Druid Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('land', 'druid', 'Circle of the Land', 'DUMMY - Mystics and sages who safeguard ancient knowledge', 0),
('moon', 'druid', 'Circle of the Moon', 'DUMMY - Druids who guard the wilderness like fierce predators', 0),
('spores', 'druid', 'Circle of Spores', 'DUMMY - Druids who find beauty in decay', 0);

-- Monk Subclasses (DUMMY)
INSERT OR IGNORE INTO subclasses (id, class_id, name, description, is_implemented) VALUES
('open_hand', 'monk', 'Way of the Open Hand', 'DUMMY - Masters of unarmed combat', 0),
('shadow', 'monk', 'Way of Shadow', 'DUMMY - Monks who follow the tradition of stealth and subterfuge', 0),
('four_elements', 'monk', 'Way of the Four Elements', 'DUMMY - Monks who harness the power of the elements', 0);

-- Create subclass_features table for future use (DUMMY STRUCTURE)
CREATE TABLE IF NOT EXISTS subclass_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subclass_id TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    feature_description TEXT,
    mechanics TEXT,  -- JSON for mechanical effects
    is_implemented INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subclass_id) REFERENCES subclasses(id),
    UNIQUE(subclass_id, level, feature_name)
);

-- Add some example features for Champion (DUMMY - NOT IMPLEMENTED)
INSERT OR IGNORE INTO subclass_features (subclass_id, level, feature_name, feature_description, is_implemented) VALUES
('champion', 3, 'Improved Critical', 'DUMMY - Your weapon attacks score a critical hit on a roll of 19 or 20', 0),
('champion', 3, 'Remarkable Athlete', 'DUMMY - You have Advantage on Initiative rolls and Strength (Athletics) checks', 0),
('champion', 7, 'Additional Fighting Style', 'DUMMY - You gain another Fighting Style feat of your choice', 0),
('champion', 10, 'Heroic Warrior', 'DUMMY - Regain HP at start of turn when below half health', 0),
('champion', 15, 'Superior Critical', 'DUMMY - Your weapon attacks score a critical hit on a roll of 18-20', 0),
('champion', 18, 'Survivor', 'DUMMY - Regain HP equal to 10 + CON modifier when below half health', 0);