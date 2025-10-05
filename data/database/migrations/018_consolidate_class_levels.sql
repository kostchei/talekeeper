INSERT OR REPLACE INTO character_class_levels (character_id, class_name, level, hit_die_type)
SELECT
    c.id,
    c.class_id,
    c.level,
    CASE LOWER(c.class_id)
        WHEN 'barbarian' THEN 12
        WHEN 'fighter' THEN 10
        WHEN 'paladin' THEN 10
        WHEN 'ranger' THEN 10
        WHEN 'cleric' THEN 8
        WHEN 'rogue' THEN 8
        WHEN 'warlock' THEN 8
        WHEN 'monk' THEN 8
        WHEN 'bard' THEN 8
        WHEN 'druid' THEN 8
        WHEN 'wizard' THEN 6
        WHEN 'sorcerer' THEN 6
        ELSE 8
    END
FROM characters c
WHERE c.class_id IS NOT NULL
  AND c.class_id != ''
  AND NOT EXISTS (
      SELECT 1 FROM character_class_levels ccl
      WHERE ccl.character_id = c.id
        AND LOWER(ccl.class_name) = LOWER(c.class_id)
  );