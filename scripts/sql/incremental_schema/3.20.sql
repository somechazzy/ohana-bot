ALTER TABLE user_reminder
    MODIFY status ENUM ('ACTIVE', 'ARCHIVED', 'FAILED_ARCHIVED') DEFAULT 'ACTIVE' NOT NULL;

ALTER TABLE user_settings
    ADD last_dm_sent_status ENUM ('SENT', 'FAILED') DEFAULT NULL AFTER timezone;

INSERT INTO custom_data (name, code, data)
VALUES ('Current database schema metadata', 'db_schema_metadata', '{"version": 3.20}') ON DUPLICATE KEY
UPDATE data =
VALUES (DATA);