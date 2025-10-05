ALTER TABLE monsters ADD COLUMN aquatic_only INTEGER DEFAULT 0;

UPDATE monsters SET aquatic_only = 1 WHERE
    (speed LIKE '%swim%' AND speed NOT LIKE '%walk%' AND speed NOT LIKE '%fly%')
    OR name IN ('Piranha', 'Seahorse', 'Giant Seahorse', 'Swarm of Piranhas');
