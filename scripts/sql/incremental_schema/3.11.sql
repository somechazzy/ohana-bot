INSERT INTO custom_data (name, code, data)
VALUES ('Current database schema metadata', 'db_schema_metadata', '{"version": 3.11}') ON DUPLICATE KEY
UPDATE data =
VALUES (DATA);