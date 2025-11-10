-- Migration 047: Fix Warlock Invocations for D&D 2024 SRD compliance
-- Adds missing Pact invocations and corrects prerequisites

-- Add the three Pact invocations that are missing
-- These have NO prerequisites and can be selected at level 1

-- Pact of the Blade
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES (
    'pact_of_the_blade',
    'Pact of the Blade',
    'As a Bonus Action, you can conjure a pact weapon in your hand—a Simple or Martial Melee weapon of your choice with which you bond—or create a bond with a magic weapon you touch. Until the bond ends, you have proficiency with the weapon, and you can use it as a Spellcasting Focus. Whenever you attack with the bonded weapon, you can use your Charisma modifier for the attack and damage rolls instead of using Strength or Dexterity.',
    '{}',
    'passive',
    '{"pact_weapon": true, "charisma_attack": true, "weapon_proficiency": true}'
);

-- Pact of the Chain
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES (
    'pact_of_the_chain',
    'Pact of the Chain',
    'You learn the Find Familiar spell and can cast it as a Magic action without expending a spell slot. When you cast the spell, you choose one of the normal forms for your familiar or one of the following special forms: Imp, Pseudodragon, Quasit, Skeleton, Sphinx of Wonder, Sprite, or Venomous Snake. Additionally, when you take the Attack action, you can forgo one of your own attacks to allow your familiar to make one attack of its own with its Reaction.',
    '{}',
    'passive',
    '{"find_familiar": true, "special_familiars": ["imp", "pseudodragon", "quasit", "skeleton", "sphinx_of_wonder", "sprite", "venomous_snake"], "familiar_attack": true}'
);

-- Pact of the Tome
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES (
    'pact_of_the_tome',
    'Pact of the Tome',
    'Stitching together strands of shadow, you conjure forth a book in your hand at the end of a Short or Long Rest. This Book of Shadows contains eldritch magic that only you can access. When the book appears, choose three cantrips, and choose two level 1 spells that have the Ritual tag. The spells can be from any class''s spell list. While the book is on your person, you have the chosen spells prepared, and they function as Warlock spells for you. You can use the book as a Spellcasting Focus.',
    '{}',
    'passive',
    '{"book_of_shadows": true, "bonus_cantrips": 3, "bonus_rituals": 2}'
);

-- Fix Fiendish Vigor - should require Level 2+ Warlock
UPDATE invocations
SET prerequisites = '{"level": 2}'
WHERE id = 'fiendish_vigor';

-- Fix Eldritch Mind - should have NO prerequisite
UPDATE invocations
SET prerequisites = '{}'
WHERE id = 'eldritch_mind';

-- Update warlock progression table - Level 1 should have 1 invocation, not 0
UPDATE warlock_pact_progression
SET invocations_known = 1
WHERE level = 1;

-- Level 2 should have 2 invocations (not 2, but confirming)
-- Level 3 keeps 2 invocations
-- The progression is: 1, 2, 2, 2, 3, 3, 4, 4, 5...
-- This matches the 2024 SRD which shows level 2 jumping to 3 invocations
UPDATE warlock_pact_progression
SET invocations_known = 3
WHERE level = 2;
