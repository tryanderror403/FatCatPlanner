"""
cogs/utils.py – Utility-Befehle
=================================
Enthält allgemeine Hilfsbefehle wie /fctime.
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

import db
from ffxiv_data import get_eorzea_time, get_utc_time, COLORS
from i18n import t

log = logging.getLogger("fatcat.utils")


async def safe_defer(
    interaction: discord.Interaction, ephemeral: bool = True, thinking: bool = False
) -> bool:
    """
    Führt sicher ein defer() auf der Interaktion aus.
    Fängt HTTPExceptions ab (z.B. Interaktion abgelaufen, bereits beantwortet)
    und loggt nur eine Warnung, anstatt den Befehl zum Absturz zu bringen.
    Gibt True zurück, wenn defer erfolgreich war, sonst False.
    """
    try:
        if thinking:
            await interaction.response.defer(ephemeral=ephemeral, thinking=True)
        else:
            await interaction.response.defer(ephemeral=ephemeral)
        return True
    except discord.errors.NotFound:
        log.warning("Interaction expired (NotFound), defer skipped.")
        return False
    except discord.errors.HTTPException:
        log.warning("Interaction already answered (HTTPException), defer skipped.")
        return False
    except Exception as e:
        log.warning("Unexpected error during defer: %s", e)
        return False


class UtilsCog(commands.Cog, name="Utils"):
    """Cog für allgemeine Utility-Befehle."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ──────────────────────────────────────────────────────────────────
    #  /fctime – Eorzea-Zeit & UTC anzeigen
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="fctime", description="Zeigt die aktuelle Eorzea-Zeit und UTC-Serverzeit.")
    async def fctime(self, ctx: commands.Context):
        """Gibt die aktuelle Eorzea-Zeit und UTC-Zeit als private Nachricht aus."""
        eorzea = get_eorzea_time()
        utc = get_utc_time()

        embed = discord.Embed(
            title="🕐 Aktuelle Zeiten",
            color=COLORS["info"],
        )
        embed.add_field(
            name="🌙 Eorzea-Zeit",
            value=f"```{eorzea}```",
            inline=True,
        )
        embed.add_field(
            name="🌍 UTC-Serverzeit",
            value=f"```{utc}```",
            inline=True,
        )
        embed.set_footer(text="Eorzea-Zeit = Echtzeit × 20.5714…")

        # Ephemeral = nur für den User sichtbar wenn per Slash aufgerufen
        await ctx.send(embed=embed, ephemeral=True)

    # ──────────────────────────────────────────────────────────────────
    #  /fcmylanguage – Benutzersprache einstellen
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="fcmylanguage", description="Zeigt ein Menü, um deine persönliche Sprache zu wählen.")
    @app_commands.describe(language="Wähle deine bevorzugte Sprache")
    @app_commands.choices(
        language=[
            app_commands.Choice(name="Deutsch", value="de"),
            app_commands.Choice(name="English", value="en"),
            app_commands.Choice(name="Français", value="fr"),
            app_commands.Choice(name="日本語", value="ja"),
        ]
    )
    async def fcmylanguage(self, ctx: commands.Context, language: str):
        """Setzt die persönliche Sprache des Benutzers."""
        await db.set_user_language(ctx.author.id, language)
        # Direkt die neue Sprache für die Bestätigung nutzen
        msg = await t(ctx.guild.id if ctx.guild else None, "user_lang_success", user_id=ctx.author.id)
        await ctx.send(f"✅ {msg}", ephemeral=True)

    # ──────────────────────────────────────────────────────────────────
    #  /fchelp – Hilfe anzeigen (User)
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="fchelp", description="Zeigt alle verfügbaren Nutzer-Befehle des Fat Cat Planners.")
    async def fchelp(self, ctx: commands.Context):
        """Zeigt eine Übersicht aller Nutzer-Befehle."""
        embed = discord.Embed(
            title="🐱 Fat Cat Planner – Befehle",
            description="Hier sind alle verfügbaren Befehle für Nutzer:",
            color=COLORS["primary"],
        )

        embed.add_field(
            name="🎮 Event- & Nutzer-Befehle",
            value=(
                "`/fccreate` – Neues Event anlegen\n"
                "`/fcregister` – Deinen Charakter verknüpfen (Lodestone)\n"
                "`/fcmylanguage` – Eigene Sprache einstellen\n"
                "`/fctime` – Aktuelle Eorzea- und Serverzeit anzeigen\n"
            ),
            inline=False,
        )

        embed.set_footer(text="Admins finden weitere Befehle unter /fachelp")
        await ctx.send(embed=embed, ephemeral=True)

    # ──────────────────────────────────────────────────────────────────
    #  /fachelp – Hilfe anzeigen (Admin)
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="fachelp", description="Zeigt alle administrativen Befehle.")
    @app_commands.default_permissions(administrator=True)
    async def fachelp(self, ctx: commands.Context):
        """Zeigt eine Übersicht aller Administrator-Befehle."""
        
        # Check permissions block (can also use is_admin_or_owner in admin cog style, but this is simple enough)
        is_owner = await self.bot.is_owner(ctx.author)
        is_admin = ctx.author.guild_permissions.administrator if ctx.guild else False
        
        if not (is_admin or is_owner):
            await ctx.send(await t(ctx.guild.id if ctx.guild else None, "cmd_admin_only", user_id=ctx.author.id), ephemeral=True)
            return

        embed = discord.Embed(
            title="🐱 Fat Cat Planner – Admin-Befehle",
            description="Diese Befehle sind nur für Administratoren verfügbar:",
            color=COLORS["primary"],
        )

        embed.add_field(
            name="🔧 Setup & Konfiguration",
            value=(
                "`/facsetup` – Initiales Setup (Event-Channel, Zeitzone)\n"
                "`/factimezone set` – Zeitzone nachträglich ändern\n"
                "`/facadminlog [on/off]` – Administrative Logs aktivieren/deaktivieren\n"
                "`/facdutyupdate` – Lokalen Duty-Cache mit XIVAPI aktualisieren\n"
            ),
            inline=False,
        )

        embed.set_footer(text="Normale Nutzerbefehle findest du unter /fchelp")
        await ctx.send(embed=embed, ephemeral=True)


# ──────────────────────────────────────────────────────────────────────
#  COG SETUP
# ──────────────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot):
    """Fügt den UtilsCog zum Bot hinzu."""
    await bot.add_cog(UtilsCog(bot))
