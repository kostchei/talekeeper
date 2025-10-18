-- Add fires_burn_used_this_round column to character_combat_state
-- This tracks whether Fire's Burn (Goliath Fire Giant Heritage) has been applied this round

ALTER TABLE character_combat_state
ADD COLUMN fires_burn_used_this_round BOOLEAN DEFAULT 0;
