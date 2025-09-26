-- Markboard Database Schema
-- MySQL 8.0+ required for proper JSON support and modern features

-- Create database (run separately if needed)
-- CREATE DATABASE IF NOT EXISTS markboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE markboard;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- Teams table
CREATE TABLE teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner_id (owner_id),
    INDEX idx_name (name)
);

-- Team members table
CREATE TABLE team_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('member', 'admin') DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_team_user (team_id, user_id),
    INDEX idx_team_id (team_id),
    INDEX idx_user_id (user_id)
);

-- Files table
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content LONGTEXT,
    owner_id INT NOT NULL,
    team_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL,
    INDEX idx_owner_id (owner_id),
    INDEX idx_team_id (team_id),
    INDEX idx_name (name),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    INDEX idx_deleted_at (deleted_at)
);

-- File versions table for tracking changes
CREATE TABLE file_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL,
    content LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    INDEX idx_file_id (file_id),
    INDEX idx_created_at (created_at)
);

-- Activity logs table
CREATE TABLE activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_resource_id (resource_id),
    INDEX idx_created_at (created_at)
);

-- Sample data insertion (commented out - uncomment and modify as needed)

-- Create an admin user (password: 'admin123' hashed with bcrypt)
-- You'll need to generate the actual hash using bcrypt with 12 rounds
-- Example: python -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt(12)).decode())"
/*
INSERT INTO users (email, password_hash, is_admin, created_at) VALUES
('admin@markboard.com', '$2b$12$HASH_PLACEHOLDER_REPLACE_WITH_ACTUAL_HASH', TRUE, NOW());

-- Create a sample team
INSERT INTO teams (name, description, owner_id, created_at) VALUES
('Sample Team', 'A sample team for testing', 1, NOW());

-- Add admin to the team
INSERT INTO team_members (team_id, user_id, role, joined_at) VALUES
(1, 1, 'admin', NOW());

-- Create a sample file
INSERT INTO files (name, content, owner_id, team_id, created_at, updated_at) VALUES
('Welcome.md', '# Welcome to Markboard\n\nThis is a sample markdown file.', 1, 1, NOW(), NOW());
*/

-- Instructions for generating admin password hash:
-- 1. Install bcrypt: pip install bcrypt
-- 2. Run: python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_PASSWORD', bcrypt.gensalt(12)).decode())"
-- 3. Replace $2b$12$HASH_PLACEHOLDER_REPLACE_WITH_ACTUAL_HASH with the generated hash
-- 4. Uncomment and run the INSERT statements above