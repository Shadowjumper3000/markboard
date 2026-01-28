-- Migration: Add invite_code to teams table
-- This allows teams to have unique invite codes for joining

ALTER TABLE teams 
ADD COLUMN invite_code VARCHAR(12) UNIQUE AFTER description;

-- Generate invite codes for existing teams (8 character random alphanumeric)
UPDATE teams 
SET invite_code = CONCAT(
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1),
    SUBSTRING('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', FLOOR(1 + RAND() * 36), 1)
)
WHERE invite_code IS NULL;

-- Make invite_code NOT NULL after populating existing rows
ALTER TABLE teams MODIFY COLUMN invite_code VARCHAR(12) NOT NULL;

-- Add index for faster lookup by invite code
CREATE INDEX idx_invite_code ON teams(invite_code);
