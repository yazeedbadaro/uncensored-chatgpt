-- added content table
-- transactional: false
-- depends: 20231220_02_tntvN-added-chat-table
CREATE TABLE content (
    content_id BINARY(16) PRIMARY KEY,
    chat_id BINARY(16),
    content TEXT,
    role ENUM('user', 'bot'),
    n_tokens INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chat(chat_id)
);

