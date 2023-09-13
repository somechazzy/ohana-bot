import discord
from globals_.constants import RoleMenuImagePlacement, RoleMenuType, XPSettingsKey
from guild_prefs_handler.guild_prefs_component import GuildPrefsComponent
from slashes.base_slashes import BaseSlashes


class AdminSlashes(BaseSlashes):

    def __init__(self, interaction):
        super().__init__(interaction=interaction)
        self.guild_prefs_component = GuildPrefsComponent()

    async def preprocess_and_validate(self, **kwargs):
        if not await super().preprocess_and_validate(guild_only=True,
                                                     **kwargs):
            return False
        return True

    @staticmethod
    def extract_role_menu_params(role_menu_message, role_menu_config):
        role_menu_embed: discord.Embed = role_menu_message.embeds[0]
        role_menu_name = role_menu_embed.author.name
        role_menu_description = role_menu_embed.title
        role_menu_type = role_menu_config['type']
        role_menu_mode = role_menu_config['mode']
        restricted_to_roles = role_menu_config['restricted_to_roles']
        restricted_description = role_menu_config['restricted_description']
        added_roles_map = {}
        role_index = 1
        if role_menu_type == RoleMenuType.SELECT:
            for select_menu in role_menu_message.components[0].children:
                for option in select_menu.options:
                    if not role_menu_message.guild.get_role(int(option.value)):
                        continue
                    added_roles_map[int(option.value)] = {
                        "alias": option.label,
                        "emoji": option.emoji,
                        "rank": role_index,
                        "role": role_menu_message.guild.get_role(int(option.value))
                    }
                    role_index += 1
        else:
            for component in role_menu_message.components:
                for button in component.children:
                    if not role_menu_message.guild.get_role(int(button.custom_id)):
                        continue
                    added_roles_map[int(button.custom_id)] = {
                        "alias": button.label,
                        "emoji": button.emoji,
                        "rank": role_index,
                        "role": role_menu_message.guild.get_role(int(button.custom_id))
                    }
                    role_index += 1

        if role_menu_embed.image:
            image_url = role_menu_embed.image.url
            image_placement = RoleMenuImagePlacement.IMAGE
        elif role_menu_embed.thumbnail:
            image_url = role_menu_embed.thumbnail.url
            image_placement = RoleMenuImagePlacement.THUMBNAIL
        else:
            image_url = None
            image_placement = RoleMenuImagePlacement.THUMBNAIL

        role_menu_footer = role_menu_embed.footer.text
        role_menu_color = role_menu_embed.color

        return role_menu_name, role_menu_description, role_menu_type, role_menu_mode, added_roles_map, \
            restricted_to_roles, image_url, image_placement, role_menu_footer, role_menu_color, \
            restricted_description

    async def validate_xp_roles_and_channels(self):
        xp_settings = self.guild_prefs.xp_settings

        levels_to_remove = []
        for level, role_id in xp_settings[XPSettingsKey.LEVEL_ROLES].items():
            if not self.guild.get_role(int(role_id)):
                levels_to_remove.append(level)
        for level in levels_to_remove:
            xp_settings[XPSettingsKey.LEVEL_ROLES].pop(level)

        channels_to_remove = []
        for channel_id in xp_settings[XPSettingsKey.IGNORED_CHANNELS]:
            if not self.guild.get_channel(int(channel_id)):
                channels_to_remove.append(channel_id)
        for channel_id in channels_to_remove:
            xp_settings[XPSettingsKey.IGNORED_CHANNELS].remove(channel_id)

        roles_to_remove = []
        for role_id in xp_settings[XPSettingsKey.IGNORED_ROLES]:
            if not self.guild.get_role(int(role_id)):
                xp_settings[XPSettingsKey.IGNORED_ROLES].remove(role_id)
        for role_id in roles_to_remove:
            xp_settings[XPSettingsKey.IGNORED_ROLES].remove(role_id)

        if levels_to_remove or channels_to_remove or roles_to_remove:
            await self.guild_prefs_component.set_xp_settings(guild=self.guild, settings=xp_settings)
