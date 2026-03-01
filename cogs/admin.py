"""
cogs/admin.py – Admin- & Setup-Befehle
=========================================
Enthält Befehle für Server-Administration:
- /facsetup       → Event-Channel + Zeitzone festlegen
- /factimezone    → Zeitzone nachträglich ändern
- /facadminlog    → Logging ein/ausschalten
- /facdutyupdate  → XIVAPI Content-Sync manuell auslösen
"""

import logging
from datetime import datetime, timezone
import asyncio
import os
import pytz

from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands, tasks

import db
from xivapi_sync import sync_content_from_xivapi
from ffxiv_data import COLORS
from cogs.utils import safe_defer
import setup_views
from i18n import t

log = logging.getLogger("fatcat.admin")

# ──────────────────────────────────────────────────────────────────────
#  ZEITZONEN-LISTE FÜR AUTOCOMPLETE
# ──────────────────────────────────────────────────────────────────────

# Gängige Zeitzonen, die im Autocomplete vorgeschlagen werden.
# Nutzer können trotzdem beliebige pytz/IANA-Bezeichnungen eingeben.
COMMON_TIMEZONES = [
    "Europe/Berlin",
    "Europe/London",
    "Europe/Paris",
    "Europe/Vienna",
    "Europe/Zurich",
    "US/Eastern",
    "US/Central",
    "US/Mountain",
    "US/Pacific",
    "Asia/Tokyo",
    "Australia/Sydney",
    "UTC",
    "GMT",
]


async def timezone_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    """
    Autocomplete-Funktion für Zeitzonen-Parameter.
    Filtert die Liste der gängigen Zeitzonen nach der aktuellen Eingabe.
    """
    query = current.lower()
    matches = [
        app_commands.Choice(name=tz, value=tz)
        for tz in COMMON_TIMEZONES
        if query in tz.lower()
    ]
    return matches[:25]  # Discord-Limit: max 25 Optionen


async def _make_discord_timestamp(tz_name: str) -> str:
    """
    Erzeugt einen Discord-Timestamp (<t:UNIX:F>) für die aktuelle Zeit
    in der angegebenen Zeitzone.
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        unix = int(now.timestamp())
        return f"<t:{unix}:F>"
    except Exception:
        return await t(None, "admin_debug_unknown", tz_name=tz_name)


def _validate_timezone(tz_name: str) -> bool:
    """Prüft, ob eine Zeitzone gültig ist."""
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(tz_name)
        return True
    except (KeyError, Exception):
        return False


def is_admin_or_owner():
    """
    Sicherheits-Check: Prüft, ob der User Administrator-Rechte auf dem Server hat,
    ODER seine ID mit der OWNER_ID aus der .env-Datei übereinstimmt.
    """
    async def predicate(ctx: commands.Context):
        if ctx.guild and ctx.author.guild_permissions.administrator:
            return True
        owner_id_str = os.environ.get("OWNER_ID", "0")
        try:
            owner_id = int(owner_id_str)
        except ValueError:
            owner_id = 0
            
        if ctx.author.id == owner_id:
            return True
            
        raise commands.MissingPermissions(["administrator"])
    return commands.check(predicate)


class AdminCog(commands.Cog, name="Admin"):
    """Cog für Admin- und Setup-Befehle."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auto_backup_task.start()

    def cog_unload(self):
        self.auto_backup_task.cancel()

    # ──────────────────────────────────────────────────────────────────
    #  AUTO BACKUP TASK
    # ──────────────────────────────────────────────────────────────────

    @tasks.loop(hours=24.0)
    async def auto_backup_task(self):
        """Auto-Backup der planner.db einmal täglich (90 Tage Retention, 3 Jahre Deep-Clean)."""
        try:
            import os
            import time
            from pathlib import Path
            import shutil
            from datetime import datetime
            
            base_dir = Path(__file__).parent.parent.resolve()
            backup_dir = base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            db_path = base_dir / "planner.db"
            if not db_path.exists():
                return
                
            # 1. Tages-Backup erstellen
            now_str = datetime.now().strftime("%Y%m%d")
            backup_name = f"planner_backup_{now_str}.db"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(db_path, backup_path)
            
            # 2. Deep Clean: Daten älter als 3 Jahre hard-deleten
            purged_count = await db.purge_ancient_data()
            
            # 3. Alte Backups bereinigen (älter als 90 Tage)
            ninety_days_ago = time.time() - (90 * 24 * 60 * 60)
            cleaned_backups_count = 0
            
            for backup_file in backup_dir.glob("*.db"):
                try:
                    # Prüfen des modifizierten / erstellten Zeitpunkts
                    mtime = os.path.getmtime(backup_file)
                    if mtime < ninety_days_ago:
                        backup_file.unlink(missing_ok=True)
                        cleaned_backups_count += 1
                except Exception as file_exp:
                    log.error("Could not process backup file %s: %s", backup_file.name, file_exp)
            
            # 4. Erweitertes Logging
            log.info("[System] Daily backup completed. Ancient data (>3 years) purged (%d events). Old backups (>90 days) cleaned (%d files).", purged_count, cleaned_backups_count)
            
        except Exception as e:
            log.error("Error during auto-backup and maintenance: %s", e, exc_info=True)

    @auto_backup_task.before_loop
    async def before_auto_backup_task(self):
        await self.bot.wait_until_ready()

    # ──────────────────────────────────────────────────────────────────
    #  /facsetup – Interaktiver Setup Wizard
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="facsetup",
        description="Startet den interaktiven Setup-Wizard für Sprache, Kanal und Zeitzone."
    )
    @app_commands.default_permissions(administrator=True)
    @is_admin_or_owner()
    async def facsetup(self, ctx: commands.Context):
        """Startet den interaktiven Setup-Wizard für die aktuelle Guild."""
        msg_welcome = await t(ctx.guild.id, "setup_welcome", user_id=ctx.author.id)
        view = setup_views.SetupLanguageView(ctx.guild.id)
        
        await ctx.send(
            content=msg_welcome,
            view=view,
            ephemeral=True
        )
        log.info("Setup Wizard started for Guild %d (%s).", ctx.guild.id, ctx.guild.name)



    # ──────────────────────────────────────────────────────────────────
    #  /factimezone – Zeitzonen-Verwaltung (Group)
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_group(
        name="factimezone",
        description="Zeitzonen verwalten",
        fallback="help"
    )
    @app_commands.default_permissions(administrator=True)
    @is_admin_or_owner()
    async def factimezone(self, ctx: commands.Context):
        pass

    @factimezone.command(
        name="set",
        description="Zeitzone für Events auf dem Server ändern",
    )
    @app_commands.describe(timezone="Die neue Zeitzone (z.B. Europe/Berlin, UTC)")
    @app_commands.autocomplete(timezone=timezone_autocomplete)
    async def factimezone_set(self, ctx: commands.Context, timezone: str):
        """Setzt eine neue Zeitzone für die Guild."""
        if not _validate_timezone(timezone):
            await ctx.send(
                await t(ctx.guild.id, "admin_invalid_tz", user_id=ctx.author.id, timezone=timezone),
                ephemeral=True,
            )
            return

        await db.set_timezone(ctx.guild.id, timezone, ctx.guild.name)

        timestamp_str = await _make_discord_timestamp(timezone)
        embed = discord.Embed(
            title=await t(ctx.guild.id, "admin_tz_updated_title", user_id=ctx.author.id),
            description=await t(ctx.guild.id, "admin_tz_updated_desc", user_id=ctx.author.id, timezone=timezone, timestamp_str=timestamp_str),
            color=COLORS["success"],
        )
        await ctx.send(embed=embed, ephemeral=True)
        log.info("Timezone for Guild %d (%s) set to '%s'.", ctx.guild.id, ctx.guild.name, timezone)

    @factimezone.command(
        name="status",
        description="Zeigt Systemzeit, Event-Zeit und nächsten Ping an"
    )
    async def factimezone_status(self, ctx: commands.Context):
        """Gibt ein Debug-Embed mit verschiedenen Zeitzonen und dem nächsten Ping aus."""
        await ctx.defer(ephemeral=True)

        # 1. Systemzeit (UTC)
        now_utc = datetime.now(timezone.utc)
        
        # 2. Lokale Zeit Bot (eingestellte Zeitzone des Servers)
        server_tz_name = await db.get_timezone(ctx.guild.id)
        try:
            server_tz = pytz.timezone(server_tz_name)
        except pytz.UnknownTimeZoneError:
            server_tz = pytz.timezone("Europe/Berlin")
        
        now_local = datetime.now(server_tz)
        
        txt_dst_active = await t(ctx.guild.id, "tz_status_dst_active", user_id=ctx.author.id)
        txt_dst_inactive = await t(ctx.guild.id, "tz_status_dst_inactive", user_id=ctx.author.id)
        dst_status = txt_dst_active if now_local.dst() else txt_dst_inactive
        
        # Localize date parsing
        fmt_date = await t(ctx.guild.id, "date_format_full", user_id=ctx.author.id)
        
        # 1. Systemzeit (UTC)
        system_time_str = now_utc.strftime(fmt_date)
        
        local_time_str = now_local.strftime(fmt_date) + f"\n*({dst_status})*"


        # 3. Nächster geplanter Ping (Events abfragen)
        all_events = await db.get_upcoming_events()
        
        # Filtern auf Events dieser Guild
        guild_events = [e for e in all_events if e.get("guild_id") == ctx.guild.id]
        
        txt_no_event = await t(ctx.guild.id, "tz_status_no_event", user_id=ctx.author.id)
        next_ping_str = txt_no_event
        earliest_ping = None
        earliest_event = None

        now_server = datetime.now(server_tz)

        for event in guild_events:
            time_str = event["time"]
            for fmt in ["%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M"]:
                try:
                    dt_naive = datetime.strptime(time_str, fmt)
                    dt_aware = server_tz.normalize(server_tz.localize(dt_naive))
                    ping_time = dt_aware.timestamp() - 600 # 10 minuten vorher

                    if dt_aware > now_server:
                        if earliest_ping is None or ping_time < earliest_ping:
                            earliest_ping = ping_time
                            earliest_event = event
                    break
                except ValueError:
                    pass

        if earliest_ping and earliest_event:
            # Ping-Zeit formatiert
            ping_dt = datetime.fromtimestamp(earliest_ping, server_tz)
            ping_formatted = ping_dt.strftime(fmt_date)
            next_ping_str = f"**{earliest_event['title']}**\n⏰ {ping_formatted}"

        # 4. Ersteller Name auflösen
        admin_name = ctx.author.display_name or ctx.author.global_name or ctx.author.name

        txt_title = await t(ctx.guild.id, "tz_status_title", user_id=ctx.author.id)
        txt_sys = await t(ctx.guild.id, "tz_status_sys", user_id=ctx.author.id)
        txt_server = await t(ctx.guild.id, "tz_status_server", user_id=ctx.author.id)
        txt_ping = await t(ctx.guild.id, "tz_status_ping", user_id=ctx.author.id)
        txt_req = await t(ctx.guild.id, "tz_status_req", user_id=ctx.author.id)

        embed = discord.Embed(
            title=txt_title,
            color=COLORS["primary"],
        )
        embed.add_field(name=f"🌍 {txt_sys}", value=f"`{system_time_str}`", inline=False)
        embed.add_field(name=f"📍 {txt_server}", value=f"`{local_time_str}`", inline=False)
        embed.add_field(name=f"🔔 {txt_ping}", value=next_ping_str, inline=False)
        embed.set_footer(text=f"{txt_req}: @{admin_name}")

        await ctx.send(embed=embed, ephemeral=True)



    # ──────────────────────────────────────────────────────────────────
    #  /facadminlog – Logging konfigurieren
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="facadminlog",
        description="Aktiviert/Deaktiviert das Event-Logging im aktuellen Kanal."
    )
    @app_commands.describe(
        toggle="'on' zum Aktivieren, 'off' zum Deaktivieren",
        channel="Der Textkanal für Log-Nachrichten (nur bei 'on' nötig).",
    )
    @app_commands.default_permissions(administrator=True)
    @is_admin_or_owner()
    async def facadminlog(
        self,
        ctx: commands.Context,
        toggle: Literal["on", "off"] = None,
        channel: discord.TextChannel = None,
    ):
        """Aktiviert oder deaktiviert das Event-Logging."""
        if toggle is None:
            await ctx.send(
                await t(ctx.guild.id, "admin_log_toggle_req", user_id=ctx.author.id),
                ephemeral=True
            )
            return

        if toggle == "on":
            if not channel:
                await ctx.send(
                    await t(ctx.guild.id, "admin_log_channel_req", user_id=ctx.author.id),
                    ephemeral=True,
                )
                return

            await db.set_log_channel(ctx.guild.id, ctx.guild.name, channel.id, True, log_channel_name=channel.name)
            embed = discord.Embed(
                title=await t(ctx.guild.id, "admin_log_enabled_title", user_id=ctx.author.id),
                description=await t(ctx.guild.id, "admin_log_enabled_desc", user_id=ctx.author.id, channel=channel.mention),
                color=COLORS["success"],
            )
            await ctx.send(embed=embed, ephemeral=True)
            log.info("[Guild: %s (%d)] Logging enabled in channel '%s' (%d).", ctx.guild.name, ctx.guild.id, channel.name, channel.id)

        else:  # off
            await db.disable_logging(ctx.guild.id)
            embed = discord.Embed(
                title=await t(ctx.guild.id, "admin_log_disabled_title", user_id=ctx.author.id),
                description=await t(ctx.guild.id, "admin_log_disabled_desc", user_id=ctx.author.id),
                color=COLORS["warning"],
            )
            await ctx.send(embed=embed, ephemeral=True)
            log.info("Logging disabled for Guild %d (%s).", ctx.guild.id, ctx.guild.name)



    # ──────────────────────────────────────────────────────────────────
    #  /facdutyupdate – Manuelles Content-Sync
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(
        name="facdutyupdate",
        description="Lädt alle Duties/Inhalte neu von XIVAPI (dauert evtl. mehrere Minuten)."
    )
    @app_commands.default_permissions(administrator=True)
    @is_admin_or_owner()
    async def facdutyupdate(self, ctx: commands.Context):
        """Führt einen manuellen XIVAPI Content-Sync aus."""
        await ctx.defer(ephemeral=True)
        await ctx.send(
            await t(ctx.guild.id, "admin_update_start", user_id=ctx.author.id),
            ephemeral=True
        )

        log.info("User %s (%s) triggered manual /fcdutyupdate.", ctx.author.id, ctx.author.name)

        async def background_sync():
            try:
                await sync_content_from_xivapi()
            except Exception as e:
                log.error(f"Error during manual content update: {e}", exc_info=True)

        asyncio.create_task(background_sync())

    # ──────────────────────────────────────────────────────────────────
    #  /facadmin – Admin-Unterbefehle
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_group(
        name="facadmin",
        description="Administrative Befehle zur Bot-Wartung.",
        fallback="help"
    )
    @app_commands.default_permissions(administrator=True)
    @is_admin_or_owner()
    async def facadmin(self, ctx: commands.Context):
        pass

    @facadmin.command(
        name="sync",
        description="Erzwingt globale Synchronisation aller Slash-Commands",
    )
    async def facadmin_sync(self, ctx: commands.Context):
        """Erzwingt globale Synchronisation der Slash-Commands."""
        await ctx.defer(ephemeral=True)
        try:
            synced = await self.bot.tree.sync()
            await ctx.send(await t(ctx.guild.id, "admin_sync_success", user_id=ctx.author.id, count=len(synced)), ephemeral=True)
        except Exception as e:
            await ctx.send(await t(ctx.guild.id, "admin_sync_error", user_id=ctx.author.id, error=str(e)), ephemeral=True)

    @facadmin.command(
        name="cleanup",
        description="Löscht alle abgelaufenen Events und Anmeldungen (> 8h)."
    )
    async def facadmin_cleanup(self, ctx: commands.Context):
        """Manueller Befehl zum Bereinigen der Datenbank von alten Events."""
        await ctx.defer(ephemeral=True)
        
        try:
            import pytz
            from datetime import timezone, timedelta
            events = await db.get_all_events(ctx.guild.id)
            now_utc = datetime.now(timezone.utc)
            deleted_count = 0

            for event in events:
                guild_id = event.get("guild_id")
                if not guild_id:
                    continue

                expired = False

                # Nutze unix_timestamp falls vorhanden
                unix_ts = event.get("unix_timestamp")
                if unix_ts:
                    if now_utc.timestamp() - unix_ts > 28800:  # 8 Stunden
                        expired = True
                else:
                    server_tz_name = await db.get_timezone(guild_id)
                    try:
                        server_tz = pytz.timezone(server_tz_name)
                    except pytz.UnknownTimeZoneError:
                        server_tz = pytz.timezone("Europe/Berlin")

                    time_str = event["time"]
                    event_dt = None
                    for fmt in ["%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M"]:
                        try:
                            dt_naive = datetime.strptime(time_str, fmt)
                            event_dt = server_tz.localize(dt_naive).astimezone(timezone.utc)
                            break
                        except ValueError:
                            pass

                    if event_dt is not None and now_utc - event_dt > timedelta(hours=8):
                        expired = True

                if not expired:
                    continue

                # Discord-Nachricht löschen
                channel_id = event.get("channel_id")
                message_id = event.get("message_id")
                if channel_id and message_id:
                    try:
                        channel = ctx.guild.get_channel(channel_id)
                        if channel:
                            msg = await channel.fetch_message(message_id)
                            await msg.delete()
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass
                    except Exception:
                        pass

                await db.archive_event(event["event_id"])
                deleted_count += 1

            embed = discord.Embed(
                title=await t(ctx.guild.id, "admin_cleanup_title", user_id=ctx.author.id),
                description=await t(ctx.guild.id, "admin_cleanup_desc", user_id=ctx.author.id, deleted_count=deleted_count),
                color=COLORS["success"],
            )
            await ctx.send(embed=embed, ephemeral=True)
            log.info("Admin %s (%s) archived %d expired events.", ctx.author.id, ctx.author.name, deleted_count)
            
        except Exception as e:
            log.error("Error during manual cleanup: %s", e, exc_info=True)
            await ctx.send(await t(ctx.guild.id, "admin_cleanup_error", user_id=ctx.author.id, error=str(e)), ephemeral=True)

    # ──────────────────────────────────────────────────────────────────
    #  Fehlerbehandlung für fehlende Berechtigungen
    # ──────────────────────────────────────────────────────────────────

    @facsetup.error
    @facadminlog.error
    @facdutyupdate.error
    @facadmin_cleanup.error
    @factimezone_set.error
    @factimezone_status.error
    async def on_admin_error(self, ctx: commands.Context, error: commands.CommandError):
        """Zentrale Fehlerbehandlung für Admin-Befehle."""
        try:
            if isinstance(error, commands.MissingPermissions):
                await ctx.send(
                    await t(ctx.guild.id, "admin_missing_perms", user_id=ctx.author.id),
                    ephemeral=True,
                )
            else:
                log.error("Unhandled error: %s", error, exc_info=True)
                await ctx.send(
                    await t(ctx.guild.id, "admin_error_generic", user_id=ctx.author.id, error=str(error)),
                    ephemeral=True,
                )
        except Exception as e:
            log.error("Could not send error notification to Discord: %s", e)


# ──────────────────────────────────────────────────────────────────────
#  COG SETUP (wird von bot.load_extension aufgerufen)
# ──────────────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot):
    """Fügt den AdminCog zum Bot hinzu."""
    await bot.add_cog(AdminCog(bot))
