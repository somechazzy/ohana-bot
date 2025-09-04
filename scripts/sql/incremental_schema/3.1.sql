ALTER TABLE guild_user_xp modify xp BIGINT DEFAULT 0 NOT NULL;
ALTER TABLE guild_user_xp modify decayed_xp BIGINT DEFAULT 0 NOT NULL;

INSERT INTO custom_data (name, code, data)
VALUES ('Current database schema metadata', 'db_schema_metadata', '{"version": 3.1}') ON DUPLICATE KEY
UPDATE data =
VALUES (DATA);