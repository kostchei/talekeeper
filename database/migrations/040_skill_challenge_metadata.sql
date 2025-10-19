CREATE TABLE IF NOT EXISTS skill_challenge_metadata (
    template_id TEXT NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    PRIMARY KEY (template_id, metadata_key),
    FOREIGN KEY (template_id) REFERENCES skill_challenge_templates(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_challenge_metadata_template
ON skill_challenge_metadata(template_id);
