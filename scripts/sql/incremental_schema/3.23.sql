-- Add unique indices to guild settings tables.
-- Deletion shouldn't be necessary as there shouldn't be any duplicates, but just in case.

DELETE g1 FROM guild_music_settings g1
INNER JOIN guild_music_settings g2
    ON g1.guild_settings_id = g2.guild_settings_id AND g1.id < g2.id WHERE g1.id > 0;

CREATE UNIQUE INDEX guild_music_settings_guild_settings_id_uq
           ON guild_music_settings (guild_settings_id);

DELETE g1 FROM guild_xp_settings g1
INNER JOIN guild_xp_settings g2
    ON g1.guild_settings_id = g2.guild_settings_id AND g1.id < g2.id WHERE g1.id > 0;

CREATE UNIQUE INDEX guild_xp_settings_guild_settings_id_uq
           ON guild_xp_settings (guild_settings_id);

INSERT INTO custom_data (name, code, data)
VALUES ('Current database schema metadata', 'db_schema_metadata', '{"version": 3.23}') ON DUPLICATE KEY
UPDATE data =
VALUES (DATA);
