from datetime import datetime, UTC

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from constants import GuildEventType, AutoResponseMatchType, RoleMenuType, RoleMenuMode, XPSettingsMessageCountMode, \
    XPDefaults
from models import BaseModel, BaseModelMixin, SnowflakeID, Json, AwareDateTime


class GuildSettings(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_settings'

    guild_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    guild_name: Mapped[str] = mapped_column(nullable=False)  # type: ignore[arg-type]
    currently_in_guild: Mapped[bool] = mapped_column(nullable=False, default=True)
    role_persistence_enabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    logging_channel_id: Mapped[int] = mapped_column(SnowflakeID(),  # type: ignore[arg-type]
                                                    nullable=True,
                                                    default=None)

    events: Mapped[list['GuildEvent']] = relationship('GuildEvent',
                                                      back_populates='guild_settings',
                                                      uselist=True)
    channels_settings: Mapped[list['GuildChannelSettings']] = relationship('GuildChannelSettings',
                                                                           back_populates='guild_settings',
                                                                           uselist=True)
    autoroles: Mapped[list['GuildAutorole']] = relationship('GuildAutorole',
                                                            back_populates='guild_settings',
                                                            uselist=True)
    auto_responses: Mapped[list['GuildAutoResponse']] = relationship('GuildAutoResponse',
                                                                     back_populates='guild_settings',
                                                                     uselist=True)
    role_menus: Mapped[list['GuildRoleMenu']] = relationship('GuildRoleMenu',
                                                             back_populates='guild_settings',
                                                             uselist=True)
    xp_settings: Mapped['GuildXPSettings'] = relationship('GuildXPSettings',
                                                          back_populates='guild_settings',
                                                          uselist=False)
    music_settings: Mapped['GuildMusicSettings'] = relationship('GuildMusicSettings',
                                                                back_populates='guild_settings',
                                                                uselist=False)
    user_xps: Mapped[list['GuildUserXP']] = relationship('GuildUserXP',
                                                         back_populates='guild_settings',
                                                         uselist=True)


class GuildEvent(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_event'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey(GuildSettings.id),  # type: ignore[arg-type]
                                                   nullable=False)
    event_type: Mapped[str] = mapped_column(GuildEventType.as_orm_enum(), nullable=False)
    event_metadata: Mapped[dict | None] = mapped_column(Json(), nullable=True)  # type: ignore[arg-type]
    event_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                 nullable=False)

    guild_settings: Mapped[GuildSettings] = relationship(GuildSettings,
                                                         back_populates='events',
                                                         uselist=False)


class GuildChannelSettings(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_channel_settings'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    channel_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    message_limiting_role_id: Mapped[int | None] = mapped_column(SnowflakeID(), nullable=True)  # type: ignore[arg-type]
    is_gallery_channel: Mapped[bool] = mapped_column(default=False, nullable=False)

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='channels_settings',
                                                           uselist=False)


class GuildAutorole(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_autorole'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    role_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='autoroles',
                                                           uselist=False)


class GuildUserRoles(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_user_roles'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    user_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    role_ids: Mapped[list[int]] = mapped_column(Json(), nullable=True)  # type: ignore[arg-type]

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings', uselist=False)


class GuildAutoResponse(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_auto_response'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    trigger_text: Mapped[str] = mapped_column(nullable=False)
    response_text: Mapped[str] = mapped_column(nullable=False)
    match_type: Mapped[str] = mapped_column(AutoResponseMatchType.as_orm_enum(),
                                            default=AutoResponseMatchType.EXACT,
                                            nullable=False)
    delete_original: Mapped[bool] = mapped_column(default=False, nullable=False)

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='auto_responses',
                                                           uselist=False)


class GuildRoleMenu(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_role_menu'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    channel_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    message_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    menu_type: Mapped[str] = mapped_column(RoleMenuType.as_orm_enum(), default=RoleMenuType.BUTTON,
                                           nullable=False)
    menu_mode: Mapped[str] = mapped_column(RoleMenuMode.as_orm_enum(), default=RoleMenuMode.SINGLE,
                                           nullable=False)
    role_restriction_description: Mapped[str | None] = mapped_column(nullable=True)

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='role_menus',
                                                           uselist=False)
    restricted_roles: Mapped[list['GuildRoleMenuRestrictedRole']] = relationship('GuildRoleMenuRestrictedRole',
                                                                                 back_populates='role_menu',
                                                                                 uselist=True)


class GuildRoleMenuRestrictedRole(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_role_menu_restricted_role'

    guild_role_menu_id: Mapped[int] = mapped_column(ForeignKey('guild_role_menu.id'),  # type: ignore[arg-type]
                                                    nullable=False)
    role_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]

    role_menu: Mapped['GuildRoleMenu'] = relationship('GuildRoleMenu',
                                                      back_populates='restricted_roles',
                                                      uselist=False)


class GuildXPSettings(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_xp_settings'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    xp_gain_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    xp_gain_timeframe: Mapped[int] = mapped_column(default=XPDefaults.TIMEFRAME_FOR_XP, nullable=False)
    xp_gain_minimum: Mapped[int] = mapped_column(default=XPDefaults.MIN_XP_GIVEN, nullable=False)
    xp_gain_maximum: Mapped[int] = mapped_column(default=XPDefaults.MAX_XP_GIVEN, nullable=False)
    message_count_mode: Mapped[str] = mapped_column(XPSettingsMessageCountMode.as_orm_enum(),
                                                    default=XPSettingsMessageCountMode.PER_MESSAGE,
                                                    nullable=False)
    xp_decay_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    xp_decay_per_day_percentage: Mapped[float] = mapped_column(default=XPDefaults.DECAY_XP_PERCENTAGE,
                                                               nullable=False)
    xp_decay_grace_period_days: Mapped[int] = mapped_column(default=XPDefaults.DECAY_DAYS_GRACE,
                                                            nullable=False)
    booster_xp_gain_multiplier: Mapped[float] = mapped_column(default=XPDefaults.BOOSTER_GAIN_MULTIPLIER,
                                                              nullable=False)
    level_up_message_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    level_up_message_channel_id: Mapped[int | None] = mapped_column(SnowflakeID(),  # type: ignore[arg-type]
                                                                    nullable=True)
    level_up_message_text: Mapped[str | None] = mapped_column(default=XPDefaults.LEVEL_UP_MESSAGE,
                                                              nullable=True)
    level_up_message_minimum_level: Mapped[int] = mapped_column(default=XPDefaults.LEVEL_UP_MESSAGE_MINIMUM_LEVEL,
                                                                nullable=False)
    max_level: Mapped[int | None] = mapped_column(nullable=True, default=XPDefaults.MAX_LEVEL)
    stack_level_roles: Mapped[bool] = mapped_column(default=True, nullable=False)
    level_role_earn_message_text: Mapped[str | None] = mapped_column(default=XPDefaults.LEVEL_ROLE_EARN_MESSAGE,
                                                                     nullable=True)

    level_roles: Mapped[list['GuildXPLevelRole']] = relationship('GuildXPLevelRole',
                                                                 back_populates='xp_settings',
                                                                 uselist=True)
    ignored_channels: Mapped[list['GuildXPIgnoredChannel']] = relationship('GuildXPIgnoredChannel',
                                                                           back_populates='xp_settings',
                                                                           uselist=True)
    ignored_roles: Mapped[list['GuildXPIgnoredRole']] = relationship('GuildXPIgnoredRole',
                                                                     back_populates='xp_settings',
                                                                     uselist=True)
    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='xp_settings',
                                                           uselist=False)


class GuildXPLevelRole(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_xp_level_role'

    guild_xp_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_xp_settings.id'),  # type: ignore[arg-type]
                                                      nullable=False)
    level: Mapped[int] = mapped_column(nullable=False)
    role_id: Mapped[int] = mapped_column(SnowflakeID(),  # type: ignore[arg-type]
                                         nullable=False)

    xp_settings: Mapped['GuildXPSettings'] = relationship('GuildXPSettings',
                                                          back_populates='level_roles',
                                                          uselist=False)


class GuildXPIgnoredChannel(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_xp_ignored_channel'

    guild_xp_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_xp_settings.id'),  # type: ignore[arg-type]
                                                      nullable=False)
    channel_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]

    xp_settings: Mapped['GuildXPSettings'] = relationship('GuildXPSettings',
                                                          back_populates='ignored_channels',
                                                          uselist=False)


class GuildXPIgnoredRole(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_xp_ignored_role'

    guild_xp_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_xp_settings.id'),  # type: ignore[arg-type]
                                                      nullable=False)
    role_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]

    xp_settings: Mapped['GuildXPSettings'] = relationship('GuildXPSettings',
                                                          back_populates='ignored_roles',
                                                          uselist=False)


class GuildMusicSettings(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_music_settings'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    music_channel_id: Mapped[int | None] = mapped_column(SnowflakeID(), nullable=True)  # type: ignore[arg-type]
    music_header_message_id: Mapped[int | None] = mapped_column(SnowflakeID(), nullable=True)  # type: ignore[arg-type]
    music_player_message_id: Mapped[int | None] = mapped_column(SnowflakeID(), nullable=True)  # type: ignore[arg-type]

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings',
                                                           back_populates='music_settings',
                                                           uselist=False)


class GuildUserXP(BaseModel, BaseModelMixin):
    __tablename__ = 'guild_user_xp'

    guild_settings_id: Mapped[int] = mapped_column(ForeignKey('guild_settings.id'),  # type: ignore[arg-type]
                                                   nullable=False)
    user_id: Mapped[int] = mapped_column(SnowflakeID(), nullable=False)  # type: ignore[arg-type]
    user_username: Mapped[str] = mapped_column(nullable=False)
    xp: Mapped[int] = mapped_column(default=0, nullable=False)
    level: Mapped[int] = mapped_column(default=0, nullable=False)
    message_count: Mapped[int] = mapped_column(default=0, nullable=False)
    latest_gain_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                       nullable=False,
                                                       default=datetime.now(UTC))
    latest_level_up_message_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                                   nullable=True)
    decayed_xp: Mapped[int] = mapped_column(default=0, nullable=False)
    latest_decay_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                        nullable=True)
    latest_message_time: Mapped[datetime] = mapped_column(AwareDateTime(),  # type: ignore[arg-type]
                                                          nullable=False,
                                                          default=datetime.now(UTC))

    guild_settings: Mapped['GuildSettings'] = relationship('GuildSettings', back_populates='user_xps')
