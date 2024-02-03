-- added user table
-- transactional: false
-- depends:
CREATE TABLE user (
    user_id BINARY(16) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(60) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

