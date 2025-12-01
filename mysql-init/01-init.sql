-- Westval MySQL Initialization Script

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS westval CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE westval;

-- Grant privileges
GRANT ALL PRIVILEGES ON westval.* TO 'westval_user'@'%';
FLUSH PRIVILEGES;

-- Set timezone
SET time_zone = '+00:00';

-- Enable strict mode for data integrity
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- Performance optimizations
SET GLOBAL max_connections = 200;
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL innodb_log_file_size = 268435456;  -- 256MB

-- Character set settings
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;