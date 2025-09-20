-- Add speed field to characters table for Fast Movement and other speed modifiers

ALTER TABLE characters ADD COLUMN speed INTEGER DEFAULT 30;

-- Update existing barbarian characters to have Fast Movement if level >= 5
UPDATE characters
SET speed = 40
WHERE LOWER(class_id) = 'barbarian'
AND level >= 5;