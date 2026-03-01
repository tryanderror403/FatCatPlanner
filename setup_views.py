"""
setup_views.py – Interactive Setup Wizard
=========================================
Bietet das interaktive Menü für /fcsetup mit drei Schritten:
1. Sprachauswahl (Language)
2. Kanal-Auswahl (Channel)
3. Zeitzonen-Auswahl (Timezone)
"""

import discord
from discord import ui
import logging
import db
from i18n import t

log = logging.getLogger("fatcat")

# Gängige Zeitzonen für das Dropdown-Menü
COMMON_TIMEZONES = [
    "Europe/Berlin",
    "Europe/London",
    "Europe/Paris",
    "US/Eastern",
    "US/Central",
    "US/Pacific",
    "Asia/Tokyo",
    "Australia/Sydney",
    "UTC"
]

class SetupTimezoneSelect(ui.Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label=tz, value=tz)
            for tz in COMMON_TIMEZONES
        ]
        super().__init__(
            placeholder="Select a Timezone...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected_tz = self.values[0]
        
        await db.set_timezone(self.guild_id, selected_tz, interaction.guild.name)
        msg_complete = await t(self.guild_id, "setup_timezone_chosen", user_id=interaction.user.id, timezone=selected_tz)
        
        # Komplett fertig
        await interaction.edit_original_response(
            content=msg_complete,
            view=None
        )


class SetupTimezoneView(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.add_item(SetupTimezoneSelect(guild_id))


class SetupChannelSelect(ui.ChannelSelect):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        super().__init__(
            placeholder="Select the Event Channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected_channel = self.values[0]
        
        # Speichere Event Channel (inkl. Kanalname)
        await db.set_event_channel(self.guild_id, selected_channel.id, interaction.guild.name, event_channel_name=selected_channel.name)
        log.info(
            "[Guild: %s (%d)] Event-Channel set to '%s' (%d).",
            interaction.guild.name, self.guild_id, selected_channel.name, selected_channel.id,
        )
        
        # Nächster Schritt: Zeitzone
        msg_timezone = await t(self.guild_id, "setup_channel_chosen", user_id=interaction.user.id, channel=selected_channel.mention)
        view = SetupTimezoneView(self.guild_id)
        
        await interaction.edit_original_response(
            content=msg_timezone,
            view=view
        )


class SetupChannelView(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.add_item(SetupChannelSelect(guild_id))


class SetupLanguageSelect(ui.Select):
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label="English", value="en", emoji="🇬🇧"),
            discord.SelectOption(label="Deutsch", value="de", emoji="🇩🇪"),
            discord.SelectOption(label="Français", value="fr", emoji="🇫🇷"),
            discord.SelectOption(label="日本語", value="ja", emoji="🇯🇵")
        ]
        super().__init__(
            placeholder="Select your Language...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected_lang = self.values[0]
        
        # Speichere Sprache
        await db.set_language(self.guild_id, selected_lang, interaction.guild.name)
        log.info("Language for Guild %d (%s) set to '%s'.", self.guild_id, interaction.guild.name, selected_lang)
        
        # Nächster Schritt: Event Channel
        msg_lang = await t(self.guild_id, "setup_lang_chosen", user_id=interaction.user.id)
        msg_channel = await t(self.guild_id, "setup_select_channel", user_id=interaction.user.id)
        
        view = SetupChannelView(self.guild_id)
        await interaction.edit_original_response(
            content=f"{msg_lang}\n\n{msg_channel}",
            view=view
        )


class SetupLanguageView(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.add_item(SetupLanguageSelect(guild_id))
