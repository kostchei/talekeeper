-- Normalize monster types to remove parentheticals, prefixes, and variations

-- Remove parentheticals like "dragon (chromatic)" -> "dragon"
UPDATE monsters
SET type = TRIM(SUBSTR(type, 1, INSTR(type || ' ', '(') - 1))
WHERE type LIKE '%(%';

-- Remove "or small " prefix
UPDATE monsters
SET type = REPLACE(type, 'or small ', '')
WHERE type LIKE 'or small %';

-- Normalize swarms: "swarm of tiny beasts" -> "beast"
UPDATE monsters
SET type = RTRIM(REPLACE(REPLACE(type, 'swarm of tiny ', ''), 's', ''))
WHERE type LIKE 'swarm of tiny %';

-- Fix specific edge cases
UPDATE monsters SET type = 'beast' WHERE type = 'beat';
UPDATE monsters SET type = 'giant' WHERE name = 'Stone Giant';

-- Remove trailing spaces
UPDATE monsters SET type = TRIM(type) WHERE type LIKE '% ';
