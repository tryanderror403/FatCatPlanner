"""
cogs/events.py – Event-Erstellung & Reminder
===============================================
Enthält den DM-basierten Event-Flow (/fccreate) und den
Background-Reminder-Task, der 10 Minuten vor Event-Start warnt.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

import db
from ffxiv_data import COLORS
from cogs.utils import safe_defer
from i18n import t
from views import (
    DutySelectView,
    PartySizeView,
    UniqueJobsView,
    EventSignupView,
    build_event_embed,
    TimezoneTypeView,
    SkipView,
)

log = logging.getLogger("fatcat.events")

def guess_party_size(name: str, content_type_id: int | None = None) -> int:
    """Schätzt die Gruppengröße anhand des Inhalts-Namens oder der ContentTypeID."""
    if content_type_id in (4, 5):
        return 8
    if content_type_id == 24:
        return 24

    name_lower = name.lower()
    
    # 24-player Alliance Raids
    alliance_words = [
        "allianz", "alliance", "yorha", "ivalice", "myths of the realm",
        "aglaia", "euphrosyne", "thaleia", "echoes of vana",
        "weeping city", "void ark", "dun scaith", 
        "labyrinth", "syrcus", "world of darkness", "copied factory",
        "puppets", "paradigm"
    ]
    if any(w in name_lower for w in alliance_words):
        return 24
        
    # 8-player Trials & Raids
    raid_words = [
        "savage", "episch", "extreme", "fatal", "ultimate", "raid", "trial", "prüfung",
        "bahamut", "alexander", "omega", "eden", "pandæmonium", "anabaseios", 
        "asphodelos", "abyssos", "arkadion", "weapon", "götterdämmerung", "minnesänger",
        "minstrel", "traumprüfung", "unreal", "zenit", "letzte läuterung", "extrem"
    ]
    if any(w in name_lower for w in raid_words):
        return 8
        
    # Default
    return 4


import pytz

class EventsCog(commands.Cog, name="Events"):
    """Cog für Event-Erstellung und -Verwaltung."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._reminded_events: set[int] = set()

    async def cog_load(self):
        """Startet den Reminder-Task und den Cleanup-Task."""
        self.reminder_task.start()
        self.cleanup_task.start()

    async def cog_unload(self):
        """Stoppt die Background-Tasks."""
        self.reminder_task.cancel()
        self.cleanup_task.cancel()

    # ──────────────────────────────────────────────────────────────────
    #  /fccreate – Event erstellen (DM-basierter Flow)
    # ──────────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="fccreate", description="Erstelle ein neues Event (der Flow läuft per DM).")
    async def fccreate(self, ctx: commands.Context):
        """
        Startet den Event-Erstellungs-Flow:
        1. Antwort im Server: "Ich habe dir eine DM geschickt"
        2. Im DM: Duty auswählen (oder manuell), Zeit angeben, Unique Jobs wählen
        3. Embed wird im Event-Channel gepostet
        """
        await ctx.defer(ephemeral=True)
        
        if not ctx.guild:
            await ctx.send(
                await t(None, "cmd_server_only", user_id=ctx.author.id),
                ephemeral=True,
            )
            return

        event_channel_id = await db.get_event_channel(ctx.guild.id)
        if not event_channel_id:
            msg = await t(ctx.guild.id, "setup_required", user_id=ctx.author.id)
            await ctx.send(
                msg,
                ephemeral=True,
            )
            return

        msg_dm = await t(ctx.guild.id, "create_check_dms", user_id=ctx.author.id)
        await ctx.send(
            msg_dm,
            ephemeral=True,
        )

        try:
            creator_name = ctx.author.display_name or ctx.author.global_name or ctx.author.name
            dm_channel = await ctx.author.create_dm()
            await self._run_dm_flow(ctx, dm_channel, creator_name)
        except discord.errors.Forbidden:
            msg_no_dms = await t(ctx.guild.id, "create_no_dms", user_id=ctx.author.id)
            await ctx.send(
                msg_no_dms,
                ephemeral=True,
            )
        except Exception as e:
            log.error("Error in DM flow: %s", e, exc_info=True)
            try:
                await ctx.send(
                    await t(ctx.guild.id, "admin_error_generic", user_id=ctx.author.id, error=str(e)),
                    ephemeral=True,
                )
            except discord.errors.HTTPException:
                pass


    #  MANUELLER FLOW: Event-Name + Gruppengröße
    # ──────────────────────────────────────────────────────────────────

    async def _ask_manual_name_and_size(
        self, dm: discord.DMChannel, user, guild_id: int | None
    ) -> tuple[str, int] | None:
        """
        Fragt den User nach Event-Name und Gruppengröße.
        Returns (name, max_players) oder None bei Timeout/Abbruch.
        """
        prompt_name = await t(guild_id, "create_prompt_name", user_id=user.id)
        await dm.send(f"{await t(guild_id, 'create_manual_title', user_id=user.id)}\n\n{prompt_name}\n(z.B. 'FC Glamour Contest', 'Mapping Night')")

        def check_dm(msg):
            return msg.author.id == user.id and isinstance(msg.channel, discord.DMChannel)

        try:
            name_msg = await self.bot.wait_for("message", check=check_dm, timeout=120)
        except asyncio.TimeoutError:
            await dm.send(await t(guild_id, "create_timeout", user_id=user.id))
            return None

        event_name = name_msg.content.strip()
        if not event_name:
            await dm.send(await t(guild_id, "create_no_name", user_id=user.id))
            return None

        # Gruppengröße wählen
        prompt_size = await t(guild_id, "create_prompt_size", user_id=user.id)
        size_4 = await t(guild_id, "create_size_4", user_id=user.id)
        size_8 = await t(guild_id, "create_size_8", user_id=user.id)
        size_24 = await t(guild_id, "create_size_24", user_id=user.id)
        
        size_view = PartySizeView(size_4, size_8, size_24)
        await dm.send(
            f"✅ **{event_name}** – {prompt_size}",
            view=size_view,
        )

        timed_out = await size_view.wait()
        if timed_out or size_view.max_players is None:
            await dm.send(await t(guild_id, "create_no_selection", user_id=user.id))
            return None

        return (event_name, size_view.max_players)

    # ──────────────────────────────────────────────────────────────────
    #  DM-FLOW: Event erstellen (Slash-Command Version)
    # ──────────────────────────────────────────────────────────────────

    async def _run_dm_flow(self, ctx: commands.Context, dm: discord.DMChannel, creator_name: str):
        """
        Führt den kompletten Event-Erstellungs-Flow in der DM durch.
        Verwendet Views und wait_for für interaktive Eingaben.
        Unterstützt manuelle Eingabe wenn "manuell" getippt wird.
        """
        try:
            guild = ctx.guild
            user = ctx.author

            # ── Schritt 1: Duty auswählen oder Manuell ──
            guild_id = guild.id if guild else None
            result_step_1 = await self._step_select_duty(dm, user, guild_id)
            if not result_step_1:
                return
            selected_duty_name, max_players = result_step_1

            if not selected_duty_name:
                return

            # ── Schritt 1.5: Zeitzone (Local/Server) ──
            timezone_type = await self._step_ask_timezone_type(dm, guild, user)
            if timezone_type is None:
                return

            # ── Schritt 2: Datum/Uhrzeit ──
            time_result = await self._step_ask_time(dm, user, guild, selected_duty_name, max_players, timezone_type)
            if time_result is None:
                return
            event_time, unix_timestamp = time_result

            # ── Schritt 2.5: Dauer ──
            event_duration = await self._step_ask_duration(dm, guild, user)

            # ── Schritt 3: Unique Jobs? ──
            unique_jobs = await self._step_ask_unique_jobs(dm, guild, user)

            # ── Schritt 3.5: Freitext (optional) ──
            free_text = await self._step_ask_freetext(dm, guild, user)

            # ── Schritt 4: Event erstellen & posten ──
            await self._step_create_and_post(
                dm, guild, user, creator_name, selected_duty_name, event_time, unique_jobs, max_players, timezone_type, unix_timestamp, event_duration, free_text
            )
        except Exception as e:
            log.error("Global error in _run_dm_flow: %s", e, exc_info=True)
            try:
                guild_id = ctx.guild.id if ctx.guild else None
                error_msg = await t(guild_id, "create_dm_error", user_id=ctx.author.id)
                await dm.send(error_msg)
            except Exception:
                pass

    # ──────────────────────────────────────────────────────────────────
    #  GEMEINSAME SCHRITTE (verwendet von beiden DM-Flows)
    # ──────────────────────────────────────────────────────────────────

    async def _step_ask_timezone_type(self, dm: discord.DMChannel, guild: discord.Guild, user=None) -> str | None:
        """Schritt 1.5: Local Time vs Server Time abfragen mit Info-Embed."""
        uid = user.id if user else None
        txt_prompt = await t(guild.id, "create_prompt_timezone_type", user_id=uid)
        txt_local = await t(guild.id, "create_tz_type_local", user_id=uid)
        txt_server = await t(guild.id, "create_tz_type_server", user_id=uid)
        
        # ── Embed bauen ──
        # Aktuelle UTC Zeit
        now_utc = datetime.now(timezone.utc)
        
        # Gilden Zeit
        server_tz_name = await db.get_timezone(guild.id)
        try:
            guild_tz = pytz.timezone(server_tz_name)
        except pytz.UnknownTimeZoneError:
            guild_tz = pytz.timezone("Europe/Berlin")
        now_guild = datetime.now(guild_tz)

        # Discord Timestamp (dynamisch in Clients)
        unix_ts = int(now_utc.timestamp())

        # Übersetzungen Field-Titel
        title_info = await t(guild.id, "create_tz_info_title", user_id=uid)
        f_server = await t(guild.id, "create_tz_info_server", user_id=uid)
        f_guild = await t(guild.id, "create_tz_info_guild", user_id=uid)
        f_local = await t(guild.id, "create_tz_info_local", user_id=uid)
        hint_str = await t(guild.id, "create_tz_info_hint", user_id=uid)

        embed = discord.Embed(
            title=title_info,
            color=COLORS["primary"],
        )
        embed.add_field(name=f_server, value=f"`{now_utc.strftime('%H:%M')} UTC`", inline=False)
        embed.add_field(name=f_guild, value=f"`{now_guild.strftime('%H:%M')}`", inline=False)
        embed.add_field(name=f_local, value=f"<t:{unix_ts}:T>", inline=False)
        
        embed.description = f"*{hint_str}*"

        tz_view = TimezoneTypeView(txt_local, txt_server)
        
        await dm.send(f"🕒 {txt_prompt}", embed=embed, view=tz_view)
        timed_out = await tz_view.wait()
        if timed_out or not tz_view.timezone_type:
            await dm.send(await t(guild.id, "create_no_selection", user_id=uid))
            return None
        return tz_view.timezone_type

    async def _step_select_duty(
        self, dm: discord.DMChannel, user, guild_id: int | None
    ) -> tuple[str | None, int]:
        """
        Schritt 1: Duty auswählen oder manuell eingeben.
        Returns (duty_name, max_players) oder (None, 0) bei Abbruch.
        """
        msg_prompt = await t(guild_id, "create_select_duty", user_id=user.id)
        await dm.send(f"{await t(guild_id, 'create_title', user_id=user.id)}\n\n{msg_prompt}")

        def check_dm(msg):
            return msg.author.id == user.id and isinstance(msg.channel, discord.DMChannel)

        try:
            search_msg = await self.bot.wait_for("message", check=check_dm, timeout=120)
        except asyncio.TimeoutError:
            await dm.send(await t(guild_id, "create_timeout", user_id=user.id))
            return (None, 0)

        search_text = search_msg.content.strip()

        # ── Direkt manuell? ──
        if search_text.lower() in ("manuell", "manual", "m"):
            result = await self._ask_manual_name_and_size(dm, user, guild_id)
            if not result:
                return (None, 0)
            return result

        # ── Suche im Content-Cache ──
        lang = await db.get_language(guild_id) if guild_id else "en"
        # Nutzersprache hat Priorität
        if user:
            user_lang = await db.get_user_language(user.id)
            if user_lang:
                lang = user_lang
        results = await db.search_content(search_text, lang=lang, limit=25)

        # ── Dropdown mit Ergebnissen + Manuell-Hinweis ──
        txt_manual = await t(guild_id, "create_manual", user_id=user.id)
        txt_placeholder = await t(guild_id, "create_placeholder", user_id=user.id)
        duty_view = DutySelectView(results, guild_id or 0, user.id, txt_manual, txt_placeholder)
        
        if results:
            msg_found = await t(guild_id, "create_found", user_id=user.id, count=len(results))
        else:
            msg_found = await t(guild_id, "create_no_results", user_id=user.id)

        await dm.send(
            msg_found,
            view=duty_view,
        )

        # Gleichzeitig auf Dropdown-Auswahl ODER "manuell"-Text warten
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(duty_view.wait(), name="duty_select"),
                asyncio.create_task(
                    self.bot.wait_for("message", check=check_dm, timeout=300),
                    name="manual_msg",
                ),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        selected_duty_id = None
        selected_duty_name = None
        manual_chosen = False

        for task in done:
            if task.get_name() == "manual_msg":
                try:
                    msg = task.result()
                    if msg.content.strip().lower() in ("manuell", "manual", "m"):
                        manual_chosen = True
                except Exception:
                    pass
            elif task.get_name() == "duty_select":
                timed_out = task.result()
                if not timed_out and getattr(duty_view, "selected_duty", None):
                    if duty_view.selected_duty == "manual_entry":
                        manual_chosen = True
                    else:
                        selected_duty_id = duty_view.selected_duty

        if manual_chosen:
            result = await self._ask_manual_name_and_size(dm, user, guild_id)
            return result if result else (None, 0)
        elif selected_duty_id:
            # We must iterate explicitly if it's considered just 'Sized'
            duty_data = None
            for d in results: # type: ignore
                if str(d.get("id")) == selected_duty_id:
                    duty_data = d
                    break
            
            if not duty_data:
                 await dm.send(await t(guild_id, "create_duty_not_found", user_id=user.id))
                 return (None, 0)
            
            # tell Pyre2 duty_data is not None here
            assert duty_data is not None
            selected_duty_name = duty_data.get("name") or "Unbekannt"
            content_type_id = duty_data.get("content_type_id")
            
            # Automatische Größenerkennung
            max_players = guess_party_size(selected_duty_name, content_type_id)
            
            # Wir überspringen die manuelle Abfrage bei bekannten Inhalten
            return (selected_duty_name, max_players)
        else:
            await dm.send(await t(guild_id, "create_no_selection", user_id=user.id))
            return (None, 0)

    async def _step_ask_time(
        self, dm: discord.DMChannel, user, guild: discord.Guild, duty_name: str, max_players: int, timezone_type: str = "local"
    ) -> tuple[str, int] | None:
        """Schritt 2: Datum/Uhrzeit abfragen mit flexiblen Formaten."""
        txt_time = await t(guild.id, "create_prompt_time", user_id=user.id)
        txt_hint = await t(guild.id, "create_prompt_time_hint", user_id=user.id)
        await dm.send(
            f"✅ **{duty_name}**!\n"
            f"   {await t(guild.id, 'create_group_size', user_id=user.id)}: **{max_players}**\n\n"
            f"📅 {txt_time}\n"
            f"*{txt_hint}*"
        )

        def check_dm(msg):
            return msg.author.id == user.id and isinstance(msg.channel, discord.DMChannel)

        server_tz_name = await db.get_timezone(guild.id)
        if timezone_type == "server":
            guild_tz = pytz.UTC
        else:
            try:
                guild_tz = pytz.timezone(server_tz_name)
            except pytz.UnknownTimeZoneError:
                guild_tz = pytz.timezone("Europe/Berlin")

        for attempt in range(3):
            try:
                time_msg = await self.bot.wait_for("message", check=check_dm, timeout=120)
            except asyncio.TimeoutError:
                await dm.send(await t(guild.id, "create_timeout", user_id=user.id))
                return None

            raw_time = time_msg.content.strip()

            if raw_time.lower() in ("abbrechen", "cancel", "stop", "exit"):
                abort_msg = await t(guild.id, "create_time_abort", user_id=user.id)
                await dm.send(f"❌ {abort_msg}")
                return None

            # Intelligente Korrektur der Zeit (z.B. 18.00 -> 18:00 am Ende des Strings)
            import re
            raw_time_fixed = re.sub(r'(\d{1,2})[\.,](\d{2})$', r'\1:\2', raw_time.strip())

            # Tolerante Ersetzung von Trennzeichen im Datum: '-', '/' und ',' -> '.'
            clean_time = raw_time_fixed.replace("-", ".").replace("/", ".").replace(",", ".")
            
            # Um doppelte Punkte wie "21.02.. 18:00" zu vermeiden:
            clean_time = re.sub(r'\.+', '.', clean_time)

            # Format prüfen
            parsed_aware = None
            now = datetime.now(guild_tz)
            now_utc = datetime.now(timezone.utc)

            # Liste der unterstützten Formate in absteigender Genauigkeit
            formats_to_try = [
                "%d.%m.%Y %H:%M",   # 21.02.2026 18:00
                "%d.%m.%y %H:%M",   # 21.02.26 18:00
                "%Y.%m.%d %H:%M",   # 2026.02.21 18:00
                "%y.%m.%d %H:%M",   # 26.02.21 18:00
                "%d.%m. %H:%M",     # 21.02. 18:00 (Impliziert dieses Jahr)
                "%d.%m %H:%M",      # 21.02 18:00 (Ohne abschließenden Punkt)
                "%m.%d. %H:%M",     # 02.21. 18:00 (MM.DD. US/JP Style)
                "%m.%d %H:%M",      # 02.21 18:00 (MM.DD US/JP Style)
                "%H:%M",            # 18:00 (Impliziert heute)
            ]

            for fmt in formats_to_try:
                try:
                    parsed = datetime.strptime(clean_time, fmt)
                    
                    # Wenn das Format kein Jahr enthält (1900 ist Default in strptime), setzen wir das aktuelle Jahr
                    if parsed.year == 1900:
                        parsed = parsed.replace(year=now.year)
                        
                        # Wenn das Format auch keinen Monat/Tag enthält (nur Uhrzeit 01.01.1900), setzen wir HEUTE
                        if parsed.month == 1 and parsed.day == 1 and "%d" not in fmt:
                            parsed = parsed.replace(month=now.month, day=now.day)

                    # Lokalisieren und normalisieren
                    parsed_aware_temp = guild_tz.normalize(guild_tz.localize(parsed))
                    
                    # Optional: Wenn die Zeit bereits heute vergangen ist und nur Uhrzeit, nehmen wir morgen
                    if parsed_aware_temp < now and parsed.month == now.month and parsed.day == now.day and "%d" not in fmt:
                        from datetime import timedelta
                        parsed_aware_temp += timedelta(days=1)
                        
                    parsed_aware = parsed_aware_temp
                    break
                except ValueError:
                    continue

            if not parsed_aware:
                current_time_example = now.strftime("%d.%m. %H:%M")
                error_hint = await t(guild.id, "create_time_error_hint", user_id=user.id, current_time_example=current_time_example)
                await dm.send(f"❌ {error_hint}")
                continue

            assert parsed_aware is not None
            if parsed_aware.timestamp() < now_utc.timestamp():
                past_msg = await t(guild.id, "create_time_past_abort", user_id=user.id)
                await dm.send(f"❌ {past_msg}")
                log.info("Event creation aborted: Time (%s) is in the past.", parsed_aware.isoformat())
                return None

            event_time = parsed_aware.strftime("%d.%m.%Y %H:%M")
            log.info("Event time detected as: %s (%s)", event_time, server_tz_name)
            
            ping_time = parsed_aware.timestamp() - 600
            ping_str = datetime.fromtimestamp(ping_time, guild_tz).strftime("%H:%M")
            log.info("Ping scheduled for: %s", ping_str)
            
            # Zeige Datum zur Kontrolle im Langformat (Discord Timestamp)
            long_time_str = f"{event_time} (<t:{int(parsed_aware.timestamp())}:F>)"
            
            # ── Bestätigungsschritt ──
            confirm_msg = await t(guild.id, "create_time_confirm", user_id=user.id, time_str=long_time_str)
            
            confirm_view = UniqueJobsView(await t(guild.id, "create_btn_yes", user_id=user.id), await t(guild.id, "create_btn_no", user_id=user.id))
            await dm.send(confirm_msg, view=confirm_view)
            
            timed_out = await confirm_view.wait()
            if timed_out or not confirm_view.unique_jobs: # Reuse the view class attributes (unique_jobs = Yes button)
                abort_msg = await t(guild.id, "create_time_abort", user_id=user.id)
                await dm.send(f"❌ {abort_msg}")
                return None

            return (event_time, int(parsed_aware.timestamp()))

        # Wenn der Loop ohne Return durchläuft = 3 Fehlversuche
        abort_msg = await t(guild.id, "create_time_abort", user_id=user.id)
        await dm.send(f"❌ {abort_msg}")
        return None

    async def _step_ask_unique_jobs(self, dm: discord.DMChannel, guild: discord.Guild, user=None) -> bool:
        """Schritt 3: Unique Jobs abfragen."""
        uid = user.id if user else None
        txt_unique = await t(guild.id, "create_prompt_unique", user_id=uid)
        txt_yes = await t(guild.id, "create_btn_yes", user_id=uid)
        txt_no = await t(guild.id, "create_btn_no", user_id=uid)
        
        unique_view = UniqueJobsView(txt_yes, txt_no)
        await dm.send(
            f"⚙️ {txt_unique}",
            view=unique_view,
        )
        timed_out = await unique_view.wait()
        if timed_out:
            await dm.send(await t(guild.id, "create_unique_timeout", user_id=uid))
        return unique_view.unique_jobs

    async def _step_ask_duration(self, dm: discord.DMChannel, guild: discord.Guild, user) -> str | None:
        """Schritt 2.5: Dauer abfragen via Texteingabe ODER Button für offenes Ende."""
        uid = user.id if user else None
        txt_prompt = await t(guild.id, "create_prompt_duration", user_id=uid)
        txt_open = await t(guild.id, "create_duration_open", user_id=uid)

        open_end_view = SkipView(txt_skip=f"♾️ {txt_open}")
        await dm.send(f"⏱️ {txt_prompt}", view=open_end_view)

        def check_dm(msg):
            return msg.author.id == user.id and isinstance(msg.channel, discord.DMChannel)

        # Wait for either Open End button or typed message
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(open_end_view.wait(), name="open_btn"),
                asyncio.create_task(
                    self.bot.wait_for("message", check=check_dm, timeout=120),
                    name="text_msg",
                ),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        for task in done:
            if task.get_name() == "text_msg":
                try:
                    reply = task.result()
                    text = reply.content.strip().lower()
                    # Zahl parsen (z.B. "2", "1.5", "1,5")
                    text = text.replace(",", ".").replace("h", "").strip()
                    try:
                        hours = float(text)
                        if 0 < hours <= 24:
                            return f"{hours}h"
                    except ValueError:
                        pass
                except Exception:
                    pass
            elif task.get_name() == "open_btn":
                if open_end_view.skipped:
                    return "open"

        return None

    async def _step_ask_freetext(self, dm: discord.DMChannel, guild: discord.Guild, user) -> str | None:
        """Schritt 3.5: Optionaler Freitext."""
        uid = user.id if user else None
        txt_prompt = await t(guild.id, "create_prompt_freetext", user_id=uid)
        txt_skip = await t(guild.id, "create_btn_skip", user_id=uid)

        skip_view = SkipView(txt_skip)
        await dm.send(f"📝 {txt_prompt}", view=skip_view)

        def check_dm(msg):
            return msg.author.id == user.id and isinstance(msg.channel, discord.DMChannel)

        # Wait for either Skip button or text message
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(skip_view.wait(), name="skip_btn"),
                asyncio.create_task(
                    self.bot.wait_for("message", check=check_dm, timeout=180),
                    name="text_msg",
                ),
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        for task in done:
            if task.get_name() == "text_msg":
                try:
                    msg = task.result()
                    text = msg.content.strip()
                    if text and text.lower() not in ("skip", "überspringen", "passer", "スキップ"):
                        saved_msg = await t(guild.id, "create_freetext_saved", user_id=uid)
                        await dm.send(saved_msg)
                        return text
                except Exception:
                    pass
            elif task.get_name() == "skip_btn":
                pass  # Skip clicked, return None

        return None

    async def _step_create_and_post(
        self, dm, guild, user, creator_name, title, event_time, unique_jobs, max_players, timezone_type, unix_timestamp, event_duration=None, free_text=None
    ):
        """Schritt 4: Event in DB erstellen und im Channel posten."""
        event_channel_id = await db.get_event_channel(guild.id)

        if not guild.id or not event_channel_id:
            await dm.send(await t(guild.id, "create_no_setup_channel", user_id=user.id))
            return

        event_channel = guild.get_channel(event_channel_id)

        if not event_channel:
            await dm.send(await t(guild.id, "create_no_setup_channel", user_id=user.id))
            return

        # ── Event in DB erstellen ──
        event_id = await db.create_event(
            guild_id=guild.id,
            title=title,
            event_time=event_time,
            content_name=title,
            creator_id=user.id,
            creator_name=creator_name,
            unique_jobs=unique_jobs,
            max_players=max_players,
            timezone_type=timezone_type,
            unix_timestamp=unix_timestamp,
            event_duration=event_duration,
            free_text=free_text,
            guild_name=guild.name,
            channel_name=event_channel.name,
        )

        # ── Embed & View erzeugen ──
        from views import build_event_embed, EventSignupView
        event_data = await db.get_event(event_id)
        
        if event_data:
             event_data["creator_name"] = creator_name

        txt_accept = await t(guild.id, "embed_btn_accept")
        txt_tentative = await t(guild.id, "embed_btn_tentative")
        txt_decline = await t(guild.id, "embed_btn_decline")

        embed = await build_event_embed(event_data)
        
        # Terminal-Check (Wichtig): Ausgabe der Embed Image URL
        if embed.image and getattr(embed.image, "url", None):
            print(f"DEBUG-URL: {embed.image.url}")
            
        signup_view = EventSignupView(event_id, txt_accept, txt_tentative, txt_decline)

        try:
            posted_msg = await event_channel.send(embed=embed, view=signup_view)
            await db.update_event_message(event_id, posted_msg.id, event_channel.id)
        except discord.errors.Forbidden:
            await dm.send(await t(guild.id, "create_no_post_permission", user_id=user.id))
            return

        msg_success = await t(guild.id, "create_success", user_id=user.id, channel=event_channel.mention)
        await dm.send(
            f"{msg_success}\n\n"
            f"📌 **{title}**\n"
            f"📅 {event_time}\n"
            f"🆔 Event-ID: `{event_id}`"
        )
        
        # ── Admin-Log posten ──
        try:
            settings = await db.get_log_settings(guild.id)
            if settings and settings["logging_enabled"] and settings["log_channel_id"]:
                log_channel = guild.get_channel(settings["log_channel_id"])
                if log_channel:
                    # Content-Name in Serversprache für den Fließtext
                    lang = await db.get_language(guild.id)
                    content_data = await db.get_content(title, lang=lang)
                    content_display = content_data.get("name", title) if content_data else title

                    admin_log_msg = await t(
                        guild.id, 
                        "log_event_created", 
                        event_name=content_display, 
                        user_name=creator_name, 
                        date_time=event_time
                    )
                    await log_channel.send(admin_log_msg)
        except Exception as e:
            log.error("Error sending Admin Log for new event: %s", e, exc_info=True)

        log.info(
            "[Guild: %s (%d)] [Channel: %s (%d)] Event #%d created: '%s' by User %d (%s).",
            guild.name, guild.id, event_channel.name, event_channel.id, event_id, title, user.id, creator_name,
        )

    # ──────────────────────────────────────────────────────────────────
    #  REMINDER BACKGROUND-TASK (jede Minute)
    # ──────────────────────────────────────────────────────────────────

    @tasks.loop(minutes=1.0)
    async def reminder_task(self):
        """
        Prüft jede Minute, ob Events in den nächsten 10 Minuten starten.
        Sendet eine Erinnerung an alle Teilnehmer im Event-Channel.
        """
        try:
            # get_upcoming_events liefert nun ALLE Events mit message_id
            all_events = await db.get_upcoming_events(minutes_ahead=10)
            upcoming = []
            
            for event in all_events:
                 guild_id = event.get("guild_id")
                 if not guild_id:
                     continue
                 
                 # Neu: Nutze unix_timestamp falls vorhanden
                 unix_ts = event.get("unix_timestamp")
                 if unix_ts:
                     now_utc = datetime.now(timezone.utc)
                     delta = (unix_ts - now_utc.timestamp()) / 60.0
                     if 0 < delta <= 10.0:
                         upcoming.append(event)
                     continue

                 server_tz_name = await db.get_timezone(guild_id)
                 try:
                     server_tz = pytz.timezone(server_tz_name)
                 except pytz.UnknownTimeZoneError:
                     server_tz = pytz.timezone("Europe/Berlin")

                 now = datetime.now(server_tz)

                 # Event Time als DD.MM.YYYY HH:MM erwartet
                 time_str = event["time"]
                 for fmt in ["%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M"]:
                     try:
                         dt_naive = datetime.strptime(time_str, fmt)
                         dt_aware = server_tz.normalize(server_tz.localize(dt_naive))
                         delta = (dt_aware - now).total_seconds() / 60.0
                         
                         if 0 < delta <= 10.0:
                             upcoming.append(event)
                         break
                     except ValueError:
                         pass

            for event in upcoming:
                event_id = event["event_id"]

                if event_id in self._reminded_events:
                    continue

                self._reminded_events.add(event_id)

                signups = await db.get_signups(event_id)
                if not signups:
                    continue

                # Nur accepted + tentative User pingen (declined nicht)
                active_signups = [s for s in signups if s.get("status", "accepted") != "declined"]
                if not active_signups:
                    continue

                mentions = " ".join(f"<@{s['user_id']}>" for s in active_signups)

                channel_id = event.get("channel_id")
                if not channel_id:
                    continue

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    continue

                title_str = await t(event.get("guild_id"), "reminder_title")
                desc_str = await t(
                    event.get("guild_id"),
                    "reminder_desc",
                    event_name=event['title'],
                    event_time=event['time'],
                    signups=len(signups),
                    max_players=event['max_players']
                )
                embed = discord.Embed(
                    title=title_str,
                    description=desc_str,
                    color=COLORS["warning"],
                )

                try:
                    await channel.send(content=mentions, embed=embed)
                    log.info("Reminder for event #%d sent.", event_id)
                except discord.errors.Forbidden:
                    log.warning("No permission to send reminder in channel %d.", channel_id)

                # ── DM an jeden Teilnehmer senden ──
                dm_count = 0
                guild_id = event.get("guild_id")
                
                for s in active_signups:
                    try:
                        reminder_msg = await t(guild_id, "event_reminder_dm", user_id=s["user_id"], event_name=event["title"])
                        user = self.bot.get_user(s["user_id"])
                        if not user:
                            user = await self.bot.fetch_user(s["user_id"])
                        
                        if user:
                            await user.send(reminder_msg)
                            dm_count += 1
                    except discord.errors.Forbidden:
                        pass # DMs geschlossen, ignorieren
                    except Exception as ex:
                        log.debug("Could not send reminder DM to %s: %s", s["user_id"], ex)

                log.info("Ping: %d DMs sent to attendees of event #%d", dm_count, event_id)

        except Exception as e:
            log.error("Error in reminder task: %s", e, exc_info=True)

    @reminder_task.before_loop
    async def before_reminder_task(self):
        """Wartet, bis der Bot bereit ist, bevor der Task startet."""
        await self.bot.wait_until_ready()

    # ──────────────────────────────────────────────────────────────────
    #  AUTO-CLEANUP BACKGROUND-TASK (jede Stunde)
    # ──────────────────────────────────────────────────────────────────

    @tasks.loop(hours=1.0)
    async def cleanup_task(self):
        """
        Löscht jede Stunde alle Events und deren Anmeldungen,
        die mehr als 8 Stunden in der Vergangenheit liegen.
        Löscht auch die zugehörige Discord-Nachricht und sendet
        eine Info in den Admin-Log-Kanal.
        """
        try:
            import pytz
            from i18n import t

            events = await db.get_all_events()
            now_utc = datetime.now(timezone.utc)
            # Pro Guild: Liste der bereinigten Event-Infos (für Admin-Log)
            cleaned_per_guild: dict[int, list[dict]] = {}

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

                event_id = event["event_id"]
                event_title = event.get("title", "Unknown")
                channel_id = event.get("channel_id")
                message_id = event.get("message_id")

                # ── Discord-Nachricht löschen ──
                if channel_id and message_id:
                    try:
                        guild = self.bot.get_guild(guild_id)
                        if guild:
                            channel = guild.get_channel(channel_id)
                            if channel:
                                msg = await channel.fetch_message(message_id)
                                await msg.delete()
                                log.info("🗑️ Deleted Discord message %d for event #%d in guild %d.", message_id, event_id, guild_id)
                    except discord.NotFound:
                        log.debug("Message %d for event #%d already deleted.", message_id, event_id)
                    except (discord.Forbidden, discord.HTTPException) as e:
                        log.warning("Could not delete message %d for event #%d: %s", message_id, event_id, e)
                    except Exception as e:
                        log.error("Unexpected error deleting message for event #%d: %s", event_id, e, exc_info=True)

                # ── Event in DB archivieren (Soft-Delete) ──
                await db.archive_event(event_id)

                if guild_id not in cleaned_per_guild:
                    cleaned_per_guild[guild_id] = []
                cleaned_per_guild[guild_id].append({"event_id": event_id, "title": event_title})

            # ── Admin-Log & Konsolen-Log ──
            for g_id, cleaned_events in cleaned_per_guild.items():
                log.info("📦 Auto-Cleanup: Server %d – %d Event(s) archiviert.", g_id, len(cleaned_events))

                try:
                    settings = await db.get_log_settings(g_id)
                    if settings and settings["logging_enabled"] and settings["log_channel_id"]:
                        guild = self.bot.get_guild(g_id)
                        if guild:
                            log_channel = guild.get_channel(settings["log_channel_id"])
                            if log_channel:
                                for ev in cleaned_events:
                                    log_msg = await t(
                                        g_id,
                                        "log_event_auto_cleaned",
                                        event_name=ev["title"],
                                        event_id=ev["event_id"],
                                    )
                                    await log_channel.send(log_msg)
                except Exception as e:
                    log.error("Error sending auto-cleanup admin log for guild %d: %s", g_id, e, exc_info=True)

        except Exception as e:
            log.error("Error in auto cleanup task: %s", e, exc_info=True)

    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        """Wartet, bis der Bot bereit ist, bevor der Cleanup-Task startet."""
        await self.bot.wait_until_ready()


# ──────────────────────────────────────────────────────────────────────
#  COG SETUP
# ──────────────────────────────────────────────────────────────────────

async def setup(bot: commands.Bot):
    """Fügt den EventsCog zum Bot hinzu."""
    await bot.add_cog(EventsCog(bot))
