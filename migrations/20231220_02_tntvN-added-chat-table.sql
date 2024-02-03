-- added chat table
-- transactional: false
-- depends: 20231220_01_azBFT-added-user-table
CREATE TABLE chat (
    chat_id BINARY(16) PRIMARY KEY,
    owner_id BINARY(16),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES user(user_id)
);

