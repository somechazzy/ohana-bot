-- USE `ohana`;

-- GUILD SETTINGS TABLES

CREATE TABLE IF NOT EXISTS guild_settings
(
    id                       INT AUTO_INCREMENT PRIMARY KEY,
    guild_id                 VARCHAR(30)                             NOT NULL,
    guild_name               VARCHAR(256)                            NOT NULL COMMENT 'Latest observed guild name - not necessarily up to date',
    currently_in_guild       TINYINT     DEFAULT 1                   NOT NULL,
    role_persistence_enabled TINYINT     DEFAULT 0                   NOT NULL,
    logging_channel_id       VARCHAR(30) DEFAULT NULL                NULL,
    created_at               DATETIME    DEFAULT CURRENT_TIMESTAMP() NULL,
    updated_at               DATETIME    DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_settings_guild_id_idx UNIQUE (guild_id)
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_event
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id INT                                  NOT NULL,
    event_type        ENUM ('JOIN', 'LEAVE')               NOT NULL,
    event_metadata    LONGTEXT                             NULL COMMENT 'To include extra data such as member count and guild name upon event' CHECK (JSON_VALID(`event_metadata`)),
    event_time        DATETIME                             NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_event_id_uq UNIQUE (id),
    CONSTRAINT guild_event_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_channel_settings
(
    id                       INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id        INT                                     NOT NULL,
    channel_id               VARCHAR(30)                             NOT NULL,
    message_limiting_role_id VARCHAR(30) DEFAULT NULL                NULL,
    is_gallery_channel       TINYINT     DEFAULT 0                   NOT NULL,
    created_at               DATETIME    DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at               DATETIME    DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_channel_settings_id_uq UNIQUE (id),
    CONSTRAINT guild_channel_settings_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_autorole
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id INT                                  NOT NULL,
    role_id           VARCHAR(30)                          NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_autorole_id_uq UNIQUE (id),
    CONSTRAINT guild_autorole_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_user_roles
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id INT                                  NOT NULL,
    user_id           VARCHAR(30)                          NOT NULL,
    role_ids          LONGTEXT                             NOT NULL COMMENT 'JSON array of role IDs, e.g. [123456789012345678, 234567890123456789]' CHECK (JSON_VALID(`role_ids`)),
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_user_roles_id_uq UNIQUE (id),
    CONSTRAINT guild_user_roles_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT guild_user_roles_user_id_uq UNIQUE (guild_settings_id, user_id)
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_auto_response
(
    id                INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id INT                                       NOT NULL,
    trigger_text      VARCHAR(4096)                             NOT NULL,
    response_text     VARCHAR(4096)                             NOT NULL,
    match_type        ENUM ('EXACT', 'CONTAINS', 'STARTS_WITH') NOT NULL DEFAULT 'EXACT',
    delete_original   TINYINT  DEFAULT 0                        NOT NULL,
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP()      NOT NULL,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP()      NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_auto_response_id_uq UNIQUE (id),
    CONSTRAINT guild_auto_response_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_role_menu
(
    id                           INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id            INT                                       NOT NULL,
    channel_id                   VARCHAR(30)                               NOT NULL,
    message_id                   VARCHAR(30)                               NOT NULL,
    menu_type                    ENUM ('BUTTON', 'SELECT')                 NOT NULL DEFAULT 'BUTTON',
    menu_mode                    ENUM ('SINGLE', 'MULTI')                  NOT NULL DEFAULT 'SINGLE',
    role_restriction_description VARCHAR(1024) DEFAULT NULL                NULL,
    created_at                   DATETIME      DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at                   DATETIME      DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_role_menu_id_uq UNIQUE (id),
    CONSTRAINT guild_role_menu_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_role_menu_restricted_role
(
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    guild_role_menu_id INT                                  NOT NULL,
    role_id            VARCHAR(30)                          NOT NULL,
    created_at         DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_role_menu_restricted_role_id_uq UNIQUE (id),
    CONSTRAINT guild_role_menu_restricted_role_menu_id_guild_role_menu_fk FOREIGN KEY (guild_role_menu_id) REFERENCES guild_role_menu (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_xp_settings
(
    id                             INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id              INT                                                               NOT NULL,
    xp_gain_enabled                TINYINT                               DEFAULT 1                   NOT NULL,
    xp_gain_timeframe              INT                                   DEFAULT 60                  NOT NULL,
    xp_gain_minimum                INT                                   DEFAULT 20                  NOT NULL,
    xp_gain_maximum                INT                                   DEFAULT 40                  NOT NULL,
    message_count_mode             ENUM ('PER_MESSAGE', 'PER_TIMEFRAME') DEFAULT 'PER_MESSAGE'       NOT NULL,
    xp_decay_enabled               TINYINT                               DEFAULT 0                   NOT NULL,
    xp_decay_per_day_percentage    DECIMAL(5, 2)                         DEFAULT 1.00                NOT NULL,
    xp_decay_grace_period_days     INT                                   DEFAULT 7                   NOT NULL,
    booster_xp_gain_multiplier     DECIMAL(5, 2)                         DEFAULT 0.00                NOT NULL,
    level_up_message_enabled       TINYINT                               DEFAULT 0                   NOT NULL,
    level_up_message_channel_id    VARCHAR(30)                           DEFAULT NULL                NULL,
    level_up_message_text          VARCHAR(4096)                         DEFAULT NULL                NULL,
    level_up_message_minimum_level INT                                   DEFAULT 1                   NOT NULL,
    max_level                      INT                                   DEFAULT 400                 NOT NULL,
    stack_level_roles              TINYINT                               DEFAULT 1                   NOT NULL,
    level_role_earn_message_text   VARCHAR(4096)                         DEFAULT NULL                NULL,
    created_at                     DATETIME                              DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at                     DATETIME                              DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_xp_settings_id_uq UNIQUE (id),
    CONSTRAINT guild_xp_settings_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_xp_level_role
(
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    guild_xp_settings_id INT                                  NOT NULL,
    level                INT                                  NOT NULL,
    role_id              VARCHAR(30)                          NOT NULL,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_xp_level_role_id_uq UNIQUE (id),
    CONSTRAINT guild_xp_level_role_xp_settings_id_guild_xp_settings_fk FOREIGN KEY (guild_xp_settings_id) REFERENCES guild_xp_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_xp_ignored_channel
(
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    guild_xp_settings_id INT                                  NOT NULL,
    channel_id           VARCHAR(30)                          NOT NULL,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_xp_ignored_channel_id_uq UNIQUE (id),
    CONSTRAINT guild_xp_ignored_channel_xp_settings_id_guild_xp_settings_fk FOREIGN KEY (guild_xp_settings_id) REFERENCES guild_xp_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_xp_ignored_role
(
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    guild_xp_settings_id INT                                  NOT NULL,
    role_id              VARCHAR(30)                          NOT NULL,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at           DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_xp_ignored_role_id_uq UNIQUE (id),
    CONSTRAINT guild_xp_ignored_role_xp_settings_id_guild_xp_settings_fk FOREIGN KEY (guild_xp_settings_id) REFERENCES guild_xp_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_user_xp
(
    id                           INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id            INT                                  NOT NULL,
    user_id                      VARCHAR(30)                          NOT NULL,
    user_username                VARCHAR(512)                         NOT NULL COMMENT 'Latest observed username - not necessarily up to date',
    xp                           BIGINT                               NOT NULL DEFAULT 0,
    level                        INT                                  NOT NULL DEFAULT 0,
    message_count                INT                                  NOT NULL DEFAULT 0,
    latest_gain_time             DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    latest_level_up_message_time DATETIME DEFAULT NULL                NULL,
    decayed_xp                   BIGINT                               NOT NULL DEFAULT 0,
    latest_decay_time            DATETIME DEFAULT NULL                NULL,
    latest_message_time          DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    created_at                   DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at                   DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_user_xp_id_uq UNIQUE (id),
    CONSTRAINT guild_user_xp_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT guild_user_xp_user_id_uq UNIQUE (guild_settings_id, user_id)
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS guild_music_settings
(
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    guild_settings_id       INT                                     NOT NULL,
    music_channel_id        VARCHAR(30) DEFAULT NULL                NULL,
    music_header_message_id VARCHAR(30) DEFAULT NULL                NULL,
    music_player_message_id VARCHAR(30) DEFAULT NULL                NULL,
    created_at              DATETIME    DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at              DATETIME    DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT guild_music_settings_id_uq UNIQUE (id),
    CONSTRAINT guild_music_settings_guild_settings_id_guild_settings_fk FOREIGN KEY (guild_settings_id) REFERENCES guild_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

-- USER TABLES

CREATE TABLE IF NOT EXISTS user_settings
(
    id                              INT AUTO_INCREMENT PRIMARY KEY,
    user_id                         VARCHAR(30)                                         NOT NULL,
    timezone                        VARCHAR(64)                                         NULL,
    relayed_reminders_disabled      TINYINT                 DEFAULT 0                   NOT NULL,
    blocked_from_relaying_reminders TINYINT                 DEFAULT 0                   NOT NULL,
    preferred_animanga_provider     ENUM ('ANILIST', 'MAL') DEFAULT 'MAL'               NOT NULL,
    created_at                      DATETIME                DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at                      DATETIME                DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT user_settings_user_id_uq UNIQUE (user_id)
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user_username
(
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_settings_id INT                                  NOT NULL,
    username         VARCHAR(256)                         NOT NULL,
    provider         ENUM ('ANILIST', 'MAL')              NOT NULL,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT user_username_id_uq UNIQUE (id),
    CONSTRAINT user_username_user_settings_id_user_settings_fk FOREIGN KEY (user_settings_id) REFERENCES user_settings (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user_reminder
(
    id                         INT AUTO_INCREMENT PRIMARY KEY,
    owner_user_settings_id     INT                                  NOT NULL,
    recipient_user_settings_id INT                                  NOT NULL,
    reminder_text              VARCHAR(4096)                        NOT NULL,
    reminder_time              DATETIME                             NOT NULL,
    is_snoozed                 TINYINT  DEFAULT 0                   NOT NULL,
    snoozed_from_reminder_id   INT                                  NULL,
    status                     ENUM ('ACTIVE', 'ARCHIVED')          NOT NULL DEFAULT 'ACTIVE',
    created_at                 DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at                 DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT user_reminder_id_uq UNIQUE (id),
    CONSTRAINT user_reminder_owner_user_settings_id_user_settings_fk FOREIGN KEY (owner_user_settings_id) REFERENCES user_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT user_reminder_recipient_user_settings_id_user_settings_fk FOREIGN KEY (recipient_user_settings_id) REFERENCES user_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT user_reminder_snoozed_from_reminder_id_user_reminder_fk FOREIGN KEY (snoozed_from_reminder_id) REFERENCES user_reminder (id) ON UPDATE CASCADE ON DELETE SET NULL,
    INDEX reminder_time_idx (reminder_time)
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user_reminder_recurrence
(
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    user_reminder_id     INT                                                   NOT NULL,
    status               ENUM ('ACTIVE', 'INACTIVE')                           NOT NULL DEFAULT 'ACTIVE',
    ends_at              DATETIME             DEFAULT NULL                     NULL,
    recurrence_type      ENUM ('BASIC', 'CONDITIONED')                         NOT NULL,
    basic_interval       INT                  DEFAULT NULL                     NULL,
    basic_unit           ENUM ('HOUR', 'DAY') DEFAULT NULL                     NULL,
    conditioned_type     ENUM ('DAYS_OF_WEEK', 'DAYS_OF_MONTH', 'DAY_OF_YEAR') NULL,
    conditioned_days     VARCHAR(512)         DEFAULT NULL                     NULL COMMENT 'JSON array of days, e.g. [0, 1] (Mon, Tue) for DAYS_OF_WEEK, and [1, 2] for DAYS_OF_MONTH' CHECK (JSON_VALID(`conditioned_days`)),
    conditioned_year_day VARCHAR(64)          DEFAULT NULL                     NULL COMMENT 'Year day in the format of %B %d (e.g. "January 01") for DAY_OF_YEAR',
    created_at           DATETIME             DEFAULT CURRENT_TIMESTAMP()      NOT NULL,
    updated_at           DATETIME             DEFAULT CURRENT_TIMESTAMP()      NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT user_reminder_recurrence_id_uq UNIQUE (id),
    CONSTRAINT user_reminder_recurrence_user_reminder_id_user_reminder_fk FOREIGN KEY (user_reminder_id) REFERENCES user_reminder (id) ON UPDATE CASCADE ON DELETE CASCADE
) collate = utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS user_reminder_blocked_user
(
    id                       INT AUTO_INCREMENT PRIMARY KEY,
    user_settings_id         INT                                  NOT NULL,
    blocked_user_settings_id INT                                  NOT NULL,
    reference_reminder_id    INT                                  NULL,
    created_at               DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at               DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT user_reminder_blocked_user_id_uq UNIQUE (id),
    CONSTRAINT user_reminder_blocked_user_user_settings_id_fk FOREIGN KEY (user_settings_id) REFERENCES user_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT user_reminder_blocked_user_blocked_user_settings_id_fk FOREIGN KEY (blocked_user_settings_id) REFERENCES user_settings (id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT user_reminder_blocked_user_reference_reminder_id_fk FOREIGN KEY (reference_reminder_id) REFERENCES user_reminder (id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT user_reminder_blocked_user_user_id_blocked_id_uq UNIQUE (user_settings_id, blocked_user_settings_id)
) collate = utf8mb4_general_ci;

-- OTHERS

CREATE TABLE IF NOT EXISTS custom_data
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(512)                         NOT NULL,
    code       VARCHAR(256)                         NOT NULL,
    data       LONGTEXT                             NOT NULL CHECK (JSON_VALID(`data`)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP() NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP() NULL ON UPDATE CURRENT_TIMESTAMP(),
    CONSTRAINT custom_data_id_uq UNIQUE (id),
    CONSTRAINT custom_data_code_uq UNIQUE (code)
) collate = utf8mb4_general_ci;

INSERT INTO custom_data (name, code, data)
VALUES ('Current database schema metadata', 'db_schema_metadata', '{"version": 3.11}')
ON DUPLICATE KEY UPDATE
    data = VALUES(data);