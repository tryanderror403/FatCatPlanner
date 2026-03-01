"""
views.py – Discord UI-Komponenten
====================================
Enthält alle Views, Buttons, Selects und Modals für den Fat Cat Planner.
Persistent Views bleiben auch nach Bot-Neustarts aktiv.
"""

import logging
from datetime import datetime, timezone

import discord
from discord import ui

import db
from ffxiv_data import ROLES, JOBS, get_jobs_for_role, COLORS, get_icon_path
from cogs.utils import safe_defer
from i18n import t

log = logging.getLogger("fatcat.views")


# ──────────────────────────────────────────────────────────────────────
#  HILFSFUNKTION: Event-Embed erstellen
# ──────────────────────────────────────────────────────────────────────

async def build_event_embed(event: dict) -> discord.Embed:
    """
    Erstellt ein formatiertes Embed für ein Event.
    Zeigt Titel, Zeit, Inhalt, Teilnehmerliste und Status.
    """
    guild_id = event.get("guild_id")
    event_id = event["event_id"]
    signups = await db.get_signups(event_id)
    max_players = event["max_players"]
    unique_jobs = bool(event["unique_jobs"])

    # ÜBERSETZUNGEN FELD-TITEL
    txt_time = await t(guild_id, "embed_field_time")
    txt_players = await t(guild_id, "embed_field_players")
    txt_unique = await t(guild_id, "embed_field_unique")

    # ── Embed erstellen ──
    embed = discord.Embed(
        title=f"🐱 {event['title']}",
        color=COLORS["primary"],
        timestamp=datetime.now(timezone.utc),
    )

    # ── ZEIT: Von/Bis ──
    timezone_type = event.get("timezone_type", "local")
    unix_timestamp = event.get("unix_timestamp")
    event_duration = event.get("event_duration")
    
    tz_text_key = "embed_time_server" if timezone_type == "server" else "embed_time_local"
    tz_text = await t(guild_id, tz_text_key)

    # Duration in Stunden parsen
    duration_hours = None
    if event_duration and event_duration != "open":
        try:
            duration_hours = float(event_duration.replace("h", ""))
        except ValueError:
            pass

    if unix_timestamp and duration_hours:
        end_timestamp = int(unix_timestamp + duration_hours * 3600)
        txt_from_to = await t(guild_id, "embed_time_from_to")
        time_display = f"📅 <t:{unix_timestamp}:F> – <t:{end_timestamp}:t>"
    elif unix_timestamp:
        time_display = f"<t:{unix_timestamp}:F> {tz_text}"
    else:
        time_display = f"**{event['time']}** {tz_text}"

    embed.add_field(
        name=f"📅 {txt_time}",
        value=time_display,
        inline=True,
    )

    # ── DAUER ──
    if event_duration:
        txt_dur_label = await t(guild_id, "embed_field_duration")
        if event_duration == "open":
            dur_display = await t(guild_id, "create_duration_open")
        else:
            # Zahl extrahieren und sauber formatieren (2.0h → 2h, 1.5h → 1.5h)
            try:
                hours = float(event_duration.replace("h", ""))
                dur_display = f"{int(hours)}h" if hours == int(hours) else f"{hours}h"
            except ValueError:
                dur_display = event_duration
        embed.add_field(
            name=f"⏱️ {txt_dur_label}",
            value=dur_display,
            inline=True,
        )
    # ── Multilingual Content Name ──
    content_name = event.get("content_name", "Unbekannt")
    content_data = await db.get_content_all_langs(content_name)
    
    if content_data:
        lang_lines = []
        for flag, key in [("🇬🇧", "name_en"), ("🇩🇪", "name_de"), ("🇫🇷", "name_fr"), ("🇯🇵", "name_ja")]:
            name_val = content_data.get(key)
            if name_val:
                lang_lines.append(f"{flag} {name_val}")
        content_display = "\n".join(lang_lines) if lang_lines else content_name
    else:
        content_display = content_name

    embed.add_field(
        name=f"🎮 {await t(guild_id, 'embed_field_content')}",
        value=content_display,
        inline=False,
    )
    
    unique_yes = await t(guild_id, "create_btn_yes")
    unique_no = await t(guild_id, "create_btn_no")
    val_unique = unique_yes if unique_jobs else unique_no

    embed.add_field(
        name=f"⚙️ {await t(guild_id, 'embed_field_settings')}",
        value=f"{txt_players}: **{max_players}**\n{txt_unique}: **{val_unique}**",
        inline=True,
    )

    # ── Teilnehmerliste nach Status gruppieren ──
    accepted = [s for s in signups if s.get("status", "accepted") == "accepted"]
    tentative = [s for s in signups if s.get("status") == "tentative"]
    declined = [s for s in signups if s.get("status") == "declined"]
    active_count = len(accepted) + len(tentative)

    if accepted:
        lines = []
        if max_players == 0:
            max_players = 1

        for role in ROLES:
            role_signups = [s for s in accepted if s["role"] == role]
            if role_signups:
                tr_role_title = await t(guild_id, f"role_{role.lower()}")
                lines.append(f"**{ROLES[role]['emoji']} {tr_role_title} ({len(role_signups)})**")
                for s in role_signups:
                    tr_job = await t(guild_id, f"job_{s['job']}")
                    lines.append(f"  └ <@{s['user_id']}> – {tr_job}")

        signup_text = "\n".join(lines)
    else:
        signup_text = await t(guild_id, "embed_no_signups")

    embed.add_field(
        name=f"👥 {await t(guild_id, 'embed_field_participants')} ({active_count}/{max_players})",
        value=signup_text,
        inline=False,
    )

    # ── Vielleicht (Tentative) ──
    if tentative:
        tent_lines = []
        for s in tentative:
            job_key = s.get("job")
            if job_key:
                tr_job = await t(guild_id, f"job_{job_key}")
                tent_lines.append(f"<@{s['user_id']}> – {tr_job}")
            else:
                tent_lines.append(f"<@{s['user_id']}>")
        tent_title = await t(guild_id, "embed_field_tentative", count=len(tentative))
        embed.add_field(
            name=tent_title,
            value="\n".join(tent_lines),
            inline=False,
        )

    # ── Absagen (Declined) ──
    if declined:
        decl_lines = [f"<@{s['user_id']}>" for s in declined]
        decl_title = await t(guild_id, "embed_field_declined", count=len(declined))
        embed.add_field(
            name=decl_title,
            value="\n".join(decl_lines),
            inline=False,
        )

    # ── Content Image (groß, zentral) ──
    content = await db.get_content(event.get("content_name", ""))
    
    if content and content.get("image_url"):
        img_url = content["image_url"]
        if isinstance(img_url, str) and img_url.startswith("http"):
            embed.set_image(url=img_url)

    # ── Optionaler Freitext ──
    free_text = event.get("free_text")
    if free_text:
        txt_freetext_label = await t(guild_id, "embed_field_freetext")
        embed.add_field(
            name=txt_freetext_label,
            value=free_text,
            inline=False,
        )

    # ── Footer ──

    creator_display = event.get("creator_name")

    if not creator_display or creator_display == "Unbekannt":
        creator_id = event.get("creator_id")
        if creator_id:
            try:
                from fatcat import bot
                guild_id = event.get("guild_id")
                guild = bot.get_guild(guild_id) if guild_id else None
                if guild:
                    member = guild.get_member(creator_id)
                    if member:
                        creator_display = member.display_name or member.global_name or member.name
            except Exception as e:
                log.debug("Fallback-Resolving für Creator %s fehlgeschlagen: %s", creator_id, e)

    if not creator_display:
        creator_display = await t(guild_id, "embed_unknown_creator")

    txt_footer = await t(guild_id, "embed_footer_creator", event_id=event_id, creator=creator_display)
    embed.set_footer(text=txt_footer)

    return embed


# ──────────────────────────────────────────────────────────────────────
#  ROLLEN-SELECT (Tank / Healer / DPS)
# ──────────────────────────────────────────────────────────────────────

class RoleSelect(ui.Select):
    """Dropdown zur Auswahl der FFXIV-Rolle (Tank, Healer, DPS)."""

    def __init__(self, event_id: int, tr_roles: dict[str, str], placeholder: str, guild_id: int, rsvp_status: str = "accepted"):
        self.event_id = event_id
        self.guild_id = guild_id
        self.rsvp_status = rsvp_status
        options = [
            discord.SelectOption(
                label=tr_roles[role],
                value=role,
                emoji=ROLES[role]["emoji"],
                description=f"{len(get_jobs_for_role(role))}",
            )
            for role in ROLES
        ]
        super().__init__(
            placeholder=placeholder,
            options=options,
            custom_id=f"role_select:{event_id}",
        )

    async def callback(self, interaction: discord.Interaction):
        """Wenn eine Rolle gewählt wird → zeige die passenden Jobs. Bei Allrounder überspringen."""
        await safe_defer(interaction)
        selected_role = self.values[0]

        if selected_role == "Allrounder":
            event = await db.get_event(self.event_id)
            if not event:
                await interaction.followup.send(await t(self.guild_id, "msg_not_found", user_id=interaction.user.id), ephemeral=True)
                return

            max_players = event["max_players"]
            current_count = await db.get_signup_count(self.event_id)
            if current_count >= max_players:
                await interaction.followup.send(await t(self.guild_id, "msg_event_full", user_id=interaction.user.id), ephemeral=True)
                return

            existing_signups = await db.get_signups(self.event_id)
            was_already_signed_up = any(s["user_id"] == interaction.user.id for s in existing_signups)

            timestamp = datetime.now(timezone.utc).isoformat()
            guild_name = interaction.guild.name if interaction.guild else "DM"
            guild_id_val = interaction.guild.id if interaction.guild else None
            channel_name = interaction.channel.name if hasattr(interaction.channel, 'name') else "unknown"
            channel_id_val = interaction.channel.id if interaction.channel else None
            await db.signup_user(
                event_id=self.event_id,
                user_id=interaction.user.id,
                user_name=interaction.user.display_name or interaction.user.global_name or interaction.user.name,
                role="Allrounder",
                job="Allrounder",
                timestamp=timestamp,
                status=self.rsvp_status,
                guild_id=guild_id_val,
                guild_name=guild_name,
            )

            if was_already_signed_up:
                log.info("[Guild: %s (%s)] [Channel: %s (%s)] Registration Update: User %d (%s) changed their role/job in Event #%d to Allrounder.", guild_name, guild_id_val, channel_name, channel_id_val, interaction.user.id, interaction.user.name, self.event_id)
            else:
                log.info("[Guild: %s (%s)] [Channel: %s (%s)] Registration: User %d (%s) joined Event #%d as Allrounder.", guild_name, guild_id_val, channel_name, channel_id_val, interaction.user.id, interaction.user.name, self.event_id)

            await _send_log_embed(
                interaction,
                event_id=self.event_id,
                user=interaction.user,
                rsvp_status=self.rsvp_status,
                job="Allrounder",
                role="Allrounder",
            )

            await _update_event_embed(interaction, self.event_id)

            msg_signup_success = await t(self.guild_id, "signup_allrounder_success", user_id=interaction.user.id)
            embed = discord.Embed(
                description=msg_signup_success,
                color=ROLES.get("Allrounder", {}).get("color", COLORS["success"]),
            )
            
            icon_path = get_icon_path("Allrounder", is_role=True)
            if icon_path:
                file = discord.File(icon_path, filename="allrounder.png")
                embed.set_thumbnail(url="attachment://allrounder.png")
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # View mit Job-Auswahl basierend auf der gewählten Rolle erstellen
        view = await JobSelectView.create(self.event_id, selected_role, self.guild_id, user_id=interaction.user.id, rsvp_status=self.rsvp_status)

        # Rollen-Icon als Datei anhängen, falls vorhanden
        icon_path = get_icon_path(selected_role, is_role=True)
        attachments = []
        if icon_path:
            attachments = [discord.File(icon_path, filename="role_icon.png")]
            
        tr_role = await t(self.guild_id, f"role_{selected_role.lower()}", user_id=interaction.user.id)
        msg_choose = await t(self.guild_id, "prompt_choose_job", user_id=interaction.user.id)

        await interaction.edit_original_response(
            content=f"{ROLES[selected_role]['emoji']} **{tr_role}**\n{msg_choose}",
            view=view,
            attachments=attachments,
        )


# ──────────────────────────────────────────────────────────────────────
#  JOB-SELECT (dynamisch basierend auf Rolle)
# ──────────────────────────────────────────────────────────────────────

class JobSelect(ui.Select):
    """Dropdown zur Auswahl eines FFXIV-Jobs, gefiltert nach Rolle."""

    def __init__(self, event_id: int, role: str, used_jobs: list[str], unique_jobs: bool, guild_id: int, prompt_taken: str, prompt_avail: str, prompt_none: str, prompt_choose: str, tr_jobs: dict[str, str], rsvp_status: str = "accepted"):
        self.event_id = event_id
        self.role = role
        self.guild_id = guild_id
        self.rsvp_status = rsvp_status

        # Alle Jobs für diese Rolle holen
        all_jobs = get_jobs_for_role(role)

        options = []
        for job in all_jobs:
            # Bei 'Unique Jobs' bereits belegte Jobs deaktivieren
            is_taken = job in used_jobs and unique_jobs
            options.append(
                discord.SelectOption(
                    label=tr_jobs[job],
                    value=job,
                    description=prompt_taken if is_taken else prompt_avail,
                    default=False,
                )
            )

        super().__init__(
            placeholder=prompt_choose,
            options=options if options else [discord.SelectOption(label=prompt_none, value="none")],
            custom_id=f"job_select:{event_id}:{role}",
        )

    async def callback(self, interaction: discord.Interaction):
        """Wenn ein Job gewählt wird → Anmeldung durchführen."""
        await safe_defer(interaction)
        selected_job = self.values[0]

        if selected_job == "none":
            await interaction.followup.send(
                await t(self.guild_id, "prompt_no_jobs", user_id=interaction.user.id), ephemeral=True
            )
            return

        # ── Validierung ──
        event = await db.get_event(self.event_id)
        if not event:
            await interaction.followup.send(
                await t(self.guild_id, "msg_not_found", user_id=interaction.user.id), ephemeral=True
            )
            return

        # Neu aufbauen
        # Da wir im Callback sind, können wir den Namen via interaction auflösen
        # Wir fügen ihn in event temporär ein, damit build_event_embed ihn nutzt
        creator_name = "Unbekannter User"
        if interaction.guild:
            member_obj = interaction.guild.get_member(event["creator_id"])
            if member_obj:
                creator_name = member_obj.display_name or member_obj.global_name or member_obj.name
        
        event["creator_name"] = creator_name

        # Max-Teilnehmer prüfen
        max_players = event["max_players"]
        current_count = await db.get_signup_count(self.event_id)
        if current_count >= max_players:
            await interaction.followup.send(
                await t(self.guild_id, "msg_event_full", user_id=interaction.user.id), ephemeral=True
            )
            return

        # ── Rollenlimit pro Gruppengröße prüfen ──
        # 4 Spieler: 1 Tank, 1 Healer, 2 DPS
        # 8 Spieler: 2 Tanks, 2 Healers, 4 DPS
        # 24 Spieler: 3 Tanks, 6 Healers, 15 DPS
        limits = {
            4: {"Tank": 1, "Healer": 1, "DPS": 2},
            8: {"Tank": 2, "Healer": 2, "DPS": 4},
            24: {"Tank": 3, "Healer": 6, "DPS": 15},
        }

        role_limit = limits.get(max_players, limits[8]).get(self.role, 0)
        existing_signups = await db.get_signups(self.event_id)
        current_role_count = sum(1 for s in existing_signups if s["role"] == self.role)
        
        # User darf den Job wechseln, wenn er bereits in der Rolle ist
        user_already_in_role = any(s["user_id"] == interaction.user.id and s["role"] == self.role for s in existing_signups)

        if not user_already_in_role and current_role_count >= role_limit:
            msg_full = await t(self.guild_id, "signup_role_full", user_id=interaction.user.id, role_name=await t(self.guild_id, f"role_{self.role.lower()}", user_id=interaction.user.id))
            await interaction.followup.send(
                msg_full, 
                ephemeral=True
            )
            return

        # Unique-Job-Check
        if event["unique_jobs"]:
            used_jobs = await db.get_used_jobs(self.event_id)
            # Prüfe ob der Job schon belegt ist (aber nicht vom selben User)
            user_has_job = any(
                s["user_id"] == interaction.user.id and s["job"] == selected_job
                for s in existing_signups
            )
            if selected_job in used_jobs and not user_has_job:
                msg_taken = await t(self.guild_id, "signup_job_taken", user_id=interaction.user.id, job_name=await t(self.guild_id, f"job_{selected_job}", user_id=interaction.user.id))
                await interaction.followup.send(
                    msg_taken,
                    ephemeral=True,
                )
                return

        # ── Anmeldung speichern ──
        was_already_signed_up = any(s["user_id"] == interaction.user.id for s in existing_signups)

        timestamp = datetime.now(timezone.utc).isoformat()
        guild_name = interaction.guild.name if interaction.guild else "DM"
        guild_id_val = interaction.guild.id if interaction.guild else None
        channel_name = interaction.channel.name if hasattr(interaction.channel, 'name') else "unknown"
        channel_id_val = interaction.channel.id if interaction.channel else None
        await db.signup_user(
            event_id=self.event_id,
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.global_name or interaction.user.name,
            role=self.role,
            job=selected_job,
            timestamp=timestamp,
            status=self.rsvp_status,
            guild_id=guild_id_val,
            guild_name=guild_name,
        )

        if was_already_signed_up:
            log.info("[Guild: %s (%s)] [Channel: %s (%s)] Registration Update: User %d (%s) changed their role/job in Event #%d to %s/%s.", guild_name, guild_id_val, channel_name, channel_id_val, interaction.user.id, interaction.user.name, self.event_id, self.role, selected_job)
        else:
            log.info("[Guild: %s (%s)] [Channel: %s (%s)] Registration: User %d (%s) joined Event #%d as %s/%s.", guild_name, guild_id_val, channel_name, channel_id_val, interaction.user.id, interaction.user.name, self.event_id, self.role, selected_job)

        # ── Logging ──
        await _send_log_embed(
            interaction,
            event_id=self.event_id,
            user=interaction.user,
            rsvp_status=self.rsvp_status,
            job=selected_job,
            role=self.role,
        )

        # ── Event-Embed aktualisieren ──
        await _update_event_embed(interaction, self.event_id)

        # ── Bestätigung mit Job-Icon senden ──
        icon_path = get_icon_path(selected_job)
        tr_role = await t(self.guild_id, f"role_{self.role.lower()}", user_id=interaction.user.id)
        tr_job = await t(self.guild_id, f"job_{selected_job}", user_id=interaction.user.id)
        
        if self.rsvp_status == "tentative":
            msg_signup_success = await t(self.guild_id, "signup_tentative_success", user_id=interaction.user.id, job_name=f"{tr_job} ({tr_role})")
        else:
            msg_signup_success = await t(self.guild_id, "signup_success", user_id=interaction.user.id, job_name=f"{tr_job} ({tr_role})")
        
        if icon_path:
            file = discord.File(icon_path, filename="job_icon.png")
            embed = discord.Embed(
                description=msg_signup_success,
                color=ROLES.get(self.role, {}).get("color", COLORS["success"]),
            )
            embed.set_thumbnail(url="attachment://job_icon.png")
            await interaction.followup.send(
                embed=embed, file=file, ephemeral=True,
            )
        else:
            await interaction.followup.send(
                msg_signup_success,
                ephemeral=True,
            )


# ──────────────────────────────────────────────────────────────────────
#  JOB-SELECT VIEW (Wrapper für den Job-Select)
# ──────────────────────────────────────────────────────────────────────

class JobSelectView(ui.View):
    """Temporäre View, die das Job-Dropdown enthält."""

    def __init__(self, event_id: int, role: str):
        super().__init__(timeout=120)  # 2 Minuten Timeout
        self.event_id = event_id
        self.role = role

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Lädt die nötigen Daten und fügt den Job-Select hinzu."""
        return True

    async def on_timeout(self):
        """Deaktiviere die View nach Timeout."""
        pass

    @classmethod
    async def create(cls, event_id: int, role: str, guild_id: int, user_id: int | None = None, rsvp_status: str = "accepted") -> "JobSelectView":
        """Factory-Methode: Erstellt die View mit bereits geladenen Daten."""
        view = cls(event_id, role)
        event = await db.get_event(event_id)
        unique_jobs = bool(event["unique_jobs"]) if event else False
        used_jobs = await db.get_used_jobs(event_id) if unique_jobs else []
        
        prompt_taken = await t(guild_id, "prompt_job_taken", user_id=user_id)
        prompt_avail = await t(guild_id, "prompt_job_available", user_id=user_id)
        prompt_none = await t(guild_id, "prompt_no_jobs", user_id=user_id)
        prompt_choose = await t(guild_id, "prompt_choose_job", user_id=user_id)
        
        all_jobs = get_jobs_for_role(role)
        tr_jobs = {}
        for job in all_jobs:
            tr_jobs[job] = await t(guild_id, f"job_{job}", user_id=user_id)

        view.add_item(JobSelect(event_id, role, used_jobs, unique_jobs, guild_id, prompt_taken, prompt_avail, prompt_none, prompt_choose, tr_jobs, rsvp_status))
        return view


# ──────────────────────────────────────────────────────────────────────
#  ROLLEN-SELECT VIEW (Wrapper)
# ──────────────────────────────────────────────────────────────────────

class RoleSelectView(ui.View):
    """Temporäre View mit dem Rollen-Dropdown."""

    def __init__(self, event_id: int):
        super().__init__(timeout=120)

    @classmethod
    async def create(cls, event_id: int, guild_id: int, user_id: int | None = None, rsvp_status: str = "accepted") -> "RoleSelectView":
        view = cls(event_id)
        
        tr_roles = {
            "Tank": await t(guild_id, "role_tank", user_id=user_id),
            "Healer": await t(guild_id, "role_healer", user_id=user_id),
            "DPS": await t(guild_id, "role_dps", user_id=user_id),
            "Allrounder": await t(guild_id, "role_allrounder", user_id=user_id)
        }
        placeholder = await t(guild_id, "prompt_choose_role", user_id=user_id)
        
        view.add_item(RoleSelect(event_id, tr_roles, placeholder, guild_id, rsvp_status))
        return view


# ──────────────────────────────────────────────────────────────────────
#  EVENT SIGNUP VIEW (Persistent – Anmelden / Abmelden Buttons)
# ──────────────────────────────────────────────────────────────────────

class EventSignupView(ui.View):
    """
    Persistent View mit [Zusage], [Vielleicht] und [Absage] Buttons.
    Bleibt auch nach Bot-Neustarts aktiv dank custom_id.
    """

    def __init__(self, event_id: int, label_accept: str = "", label_tentative: str = "", label_decline: str = ""):
        # timeout=None → Persistent View (kein Auto-Timeout)
        super().__init__(timeout=None)
        self.event_id = event_id
        
        for child in self.children:
            cid = getattr(child, "custom_id", None)
            if cid == "rsvp_accept" and label_accept:
                child.label = label_accept
            elif cid == "rsvp_tentative" and label_tentative:
                child.label = label_tentative
            elif cid == "rsvp_decline" and label_decline:
                child.label = label_decline

    async def _start_role_flow(self, interaction: discord.Interaction, rsvp_status: str):
        """Gemeinsame Logik für Accept und Tentative: Rollen-/Job-Auswahl starten."""
        await safe_defer(interaction, ephemeral=True)
        event = await db.get_event(self.event_id)
        
        if not event:
            await interaction.followup.send(
                await t(interaction.guild.id, "msg_not_found", user_id=interaction.user.id), ephemeral=True
            )
            return

        # Prüfe ob Event voll ist (nur wenn User noch nicht angemeldet)
        existing_signups = await db.get_signups(self.event_id)
        already_signed = any(s["user_id"] == interaction.user.id for s in existing_signups)
        
        if not already_signed:
            current_count = await db.get_signup_count(self.event_id)
            if current_count >= event["max_players"]:
                await interaction.followup.send(
                    await t(interaction.guild.id, "msg_already_full_dm", user_id=interaction.user.id),
                    ephemeral=True,
                )
                return

        # Rollen-Auswahl als ephemeral Message senden
        view = await RoleSelectView.create(self.event_id, interaction.guild.id, user_id=interaction.user.id, rsvp_status=rsvp_status)
        msg_choose = await t(interaction.guild.id, "prompt_choose_role", user_id=interaction.user.id)
        await interaction.followup.send(
            f"🛡️ {msg_choose}",
            view=view,
            ephemeral=True,
        )

    @ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="🟩", custom_id="rsvp_accept")
    async def accept_button(self, interaction: discord.Interaction, button: ui.Button):
        """Zusage – normaler Rollen-/Job-Flow."""
        await self._start_role_flow(interaction, "accepted")

    @ui.button(label="Tentative", style=discord.ButtonStyle.primary, emoji="🟦", custom_id="rsvp_tentative")
    async def tentative_button(self, interaction: discord.Interaction, button: ui.Button):
        """Vielleicht – normaler Rollen-/Job-Flow, aber mit status='tentative'."""
        await self._start_role_flow(interaction, "tentative")

    @ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="🟥", custom_id="rsvp_decline")
    async def decline_button(self, interaction: discord.Interaction, button: ui.Button):
        """Absage – kein Job-Flow, sofort speichern."""
        await safe_defer(interaction, ephemeral=True)
        event = await db.get_event(self.event_id)
        
        if not event:
            await interaction.followup.send(
                await t(interaction.guild.id, "msg_not_found", user_id=interaction.user.id), ephemeral=True
            )
            return

        timestamp = datetime.now(timezone.utc).isoformat()
        guild_name = interaction.guild.name if interaction.guild else "DM"
        guild_id_val = interaction.guild.id if interaction.guild else None
        channel_name = interaction.channel.name if hasattr(interaction.channel, 'name') else "unknown"
        channel_id_val = interaction.channel.id if interaction.channel else None
        await db.signup_user(
            event_id=self.event_id,
            user_id=interaction.user.id,
            user_name=interaction.user.display_name or interaction.user.global_name or interaction.user.name,
            role=None,
            job=None,
            timestamp=timestamp,
            status="declined",
            guild_id=guild_id_val,
            guild_name=guild_name,
        )

        log.info("[Guild: %s (%s)] [Channel: %s (%s)] RSVP Decline: User %d (%s) declined Event #%d.", guild_name, guild_id_val, channel_name, channel_id_val, interaction.user.id, interaction.user.name, self.event_id)

        # Logging
        await _send_log_embed(
            interaction,
            event_id=self.event_id,
            user=interaction.user,
            rsvp_status="declined",
        )

        # Event-Embed aktualisieren
        await _update_event_embed(interaction, self.event_id)

        await interaction.followup.send(
            await t(interaction.guild.id, "signup_declined_success", user_id=interaction.user.id), ephemeral=True
        )


# ──────────────────────────────────────────────────────────────────────
#  DM-FLOW VIEWS (für /fccreate)
# ──────────────────────────────────────────────────────────────────────

class DutySelectView(ui.View):
    """View für die Duty-Auswahl im DM (Schritt 1 des Event-Flows)."""

    def __init__(self, duties: list[dict], guild_id: int, creator_id: int, txt_manual: str = "Manuell", txt_placeholder: str = "Wähle..."):
        super().__init__(timeout=300)  # 5 Minuten
        self.guild_id = guild_id
        self.creator_id = creator_id
        self.selected_duty = None

        options = []
        # Füge manueller Eintrag als allererste Option hinzu
        options.append(discord.SelectOption(
            label=txt_manual,
            value="manual_entry",
            description="",
            emoji="✍️"
        ))

        for duty in duties[:24]:  # Discord-Limit: 25 Optionen total. -1 für manuell
            # Direkt den von db.py übersetzten Namen verwenden
            name_val = duty.get("name")
            label = (name_val if name_val else "???")[:100]
            options.append(
                discord.SelectOption(label=label, value=str(duty.get("id", label)))
            )

        if options:
            select = ui.Select(
                placeholder=txt_placeholder,
                options=options,
                custom_id="duty_select_dm",
            )
            select.callback = self.duty_selected
            self.add_item(select)

    async def duty_selected(self, interaction: discord.Interaction):
        """Callback wenn ein Duty ausgewählt wird."""
        self.selected_duty = interaction.data["values"][0]
        self.stop()
        # Wichtig: View der Nachricht entfernen, damit sie nicht doppelt/verwaist bleibt.
        await interaction.response.edit_message(view=None)


class UniqueJobsView(ui.View):
    """View für die Unique-Jobs-Abfrage im DM (Schritt 3 des Event-Flows)."""

    def __init__(self, txt_yes: str = "Ja", txt_no: str = "Nein"):
        super().__init__(timeout=120)
        self.unique_jobs = False
        
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.style == discord.ButtonStyle.success:
                    child.label = txt_yes
                elif child.style == discord.ButtonStyle.secondary:
                    child.label = txt_no

    @ui.button(label="Ja – Unique Jobs", style=discord.ButtonStyle.success, emoji="✅")
    async def yes_button(self, interaction: discord.Interaction, button: ui.Button):
        self.unique_jobs = True
        self.stop()
        await interaction.response.defer()

    @ui.button(label="Nein – Duplikate erlaubt", style=discord.ButtonStyle.secondary, emoji="❌")
    async def no_button(self, interaction: discord.Interaction, button: ui.Button):
        self.unique_jobs = False
        self.stop()
        await interaction.response.defer()


class PartySizeView(ui.View):
    """View zur Auswahl der Gruppengröße bei manueller Event-Erstellung."""

    def __init__(self, txt_4: str = "4 Spieler", txt_8: str = "8 Spieler", txt_24: str = "24 Spieler"):
        super().__init__(timeout=120)
        self.max_players: int | None = None
        
        # Labels dynamisch aus Argumenten setzen
        buttons = [child for child in self.children if isinstance(child, discord.ui.Button)]
        if len(buttons) >= 3:
            buttons[0].label = txt_4
            buttons[1].label = txt_8
            buttons[2].label = txt_24

    @ui.button(label="4 Spieler (Dungeon)", style=discord.ButtonStyle.primary, emoji="🏰")
    async def btn_4(self, interaction: discord.Interaction, button: ui.Button):
        self.max_players = 4
        self.stop()
        await interaction.response.defer()

    @ui.button(label="8 Spieler (Trial/Raid)", style=discord.ButtonStyle.primary, emoji="⚔️")
    async def btn_8(self, interaction: discord.Interaction, button: ui.Button):
        self.max_players = 8
        self.stop()
        await interaction.response.defer()

    @ui.button(label="24 Spieler (Alliance)", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def btn_24(self, interaction: discord.Interaction, button: ui.Button):
        self.max_players = 24
        self.stop()
        await interaction.response.defer()


class DurationView(ui.View):
    """View zur Auswahl der Event-Dauer."""

    def __init__(self, txt_1h="1h", txt_1_5h="1.5h", txt_2h="2h", txt_3h="3h", txt_open="Open End"):
        super().__init__(timeout=120)
        self.duration: str | None = None

        buttons = [child for child in self.children if isinstance(child, discord.ui.Button)]
        labels = [txt_1h, txt_1_5h, txt_2h, txt_3h, txt_open]
        for i, btn in enumerate(buttons):
            if i < len(labels):
                btn.label = labels[i]

    @ui.button(label="1h", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def btn_1h(self, interaction: discord.Interaction, button: ui.Button):
        self.duration = "1h"
        self.stop()
        await interaction.response.defer()

    @ui.button(label="1.5h", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def btn_1_5h(self, interaction: discord.Interaction, button: ui.Button):
        self.duration = "1.5h"
        self.stop()
        await interaction.response.defer()

    @ui.button(label="2h", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def btn_2h(self, interaction: discord.Interaction, button: ui.Button):
        self.duration = "2h"
        self.stop()
        await interaction.response.defer()

    @ui.button(label="3h", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def btn_3h(self, interaction: discord.Interaction, button: ui.Button):
        self.duration = "3h"
        self.stop()
        await interaction.response.defer()

    @ui.button(label="Open End", style=discord.ButtonStyle.secondary, emoji="♾️")
    async def btn_open(self, interaction: discord.Interaction, button: ui.Button):
        self.duration = "open"
        self.stop()
        await interaction.response.defer()


class SkipView(ui.View):
    """View mit nur einem Skip-Button für optionale Schritte."""

    def __init__(self, txt_skip: str = "Skip"):
        super().__init__(timeout=180)
        self.skipped = False

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.label = txt_skip

    @ui.button(label="Skip", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def btn_skip(self, interaction: discord.Interaction, button: ui.Button):
        self.skipped = True
        self.stop()
        await interaction.response.defer()


class TimezoneTypeView(ui.View):
    """View für die Auswahl Local Time vs Server Time im DM."""

    def __init__(self, txt_local: str, txt_server: str):
        super().__init__(timeout=120)
        self.timezone_type: str | None = None
        
        # Labels dynamisch aus Argumenten setzen
        buttons = [child for child in self.children if isinstance(child, discord.ui.Button)]
        if len(buttons) >= 2:
            buttons[0].label = txt_local
            buttons[1].label = txt_server

    @ui.button(style=discord.ButtonStyle.primary, custom_id="btn_tz_local")
    async def btn_local(self, interaction: discord.Interaction, button: ui.Button):
        self.timezone_type = "local"
        self.stop()
        await interaction.response.defer()

    @ui.button(style=discord.ButtonStyle.primary, custom_id="btn_tz_server")
    async def btn_server(self, interaction: discord.Interaction, button: ui.Button):
        self.timezone_type = "server"
        self.stop()
        await interaction.response.defer()

# ──────────────────────────────────────────────────────────────────────
#  HILFSFUNKTIONEN
# ──────────────────────────────────────────────────────────────────────

async def _send_log_embed(
    interaction: discord.Interaction,
    event_id: int,
    user: discord.User | discord.Member,
    rsvp_status: str = "accepted",
    job: str | None = None,
    role: str | None = None,
) -> None:
    """
    Sendet ein detailliertes Log-Embed in den Admin-Log-Channel.

    Args:
        interaction: Die Discord-Interaction (für Guild-Zugriff).
        event_id:    ID des betroffenen Events.
        user:        Der User, der sich an-/abgemeldet hat.
        rsvp_status: 'accepted', 'tentative', 'declined' oder 'leave'.
        job:         Name des gewählten Jobs (nur bei Anmeldung/Tentative).
        role:        Name der gewählten Rolle (nur bei Anmeldung/Tentative).
    """
    if not interaction.guild:
        return

    # ── Log-Einstellungen aus der Datenbank holen ──
    settings = await db.get_log_settings(interaction.guild.id)
    if not settings or not settings["logging_enabled"] or not settings["log_channel_id"]:
        return

    channel = interaction.guild.get_channel(settings["log_channel_id"])
    if not channel:
        return

    # ── Event-Daten laden ──
    event = await db.get_event(event_id)
    if not event:
        return

    content_name = event.get("content_name", "Unbekannt")
    event_time = event.get("time", "Nicht festgelegt")
    signup_count = await db.get_signup_count(event_id)
    max_players = event.get("max_players", "?")

    # ── Embed bauen (differenziert nach RSVP-Status) ──
    guild_id = interaction.guild.id
    if rsvp_status == "accepted":
        title = await t(guild_id, "log_title_signup", content=content_name)
        color = COLORS["success"]  # Grün
        status_text = await t(guild_id, "log_status_signup")
    elif rsvp_status == "tentative":
        title = await t(guild_id, "log_title_tentative", content=content_name)
        color = COLORS["primary"]  # Blau
        status_text = await t(guild_id, "log_status_tentative")
    elif rsvp_status == "declined":
        title = await t(guild_id, "log_title_decline", content=content_name)
        color = COLORS["error"]  # Rot
        status_text = await t(guild_id, "log_status_decline")
    else:  # "leave" / Fallback
        title = await t(guild_id, "log_title_leave", content=content_name)
        color = COLORS["error"]
        status_text = await t(guild_id, "log_status_leave")

    txt_fuser = await t(guild_id, "log_field_user")
    txt_fjob = await t(guild_id, "log_field_job")
    txt_fstat = await t(guild_id, "log_field_status")
    txt_ftime = await t(guild_id, "log_field_time")
    txt_fnum = await t(guild_id, "log_field_players")

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=datetime.now(timezone.utc),
    )

    # Feld 1: User
    embed.add_field(
        name=f"👤 {txt_fuser}",
        value=f"{user.mention} ({user.display_name})",
        inline=True,
    )

    # Feld 2: Job + Rolle (nur bei Anmeldung/Tentative)
    if rsvp_status in ("accepted", "tentative") and job and role:
        role_emoji = ROLES.get(role, {}).get("emoji", "")
        tr_job = await t(guild_id, f"job_{job}")
        tr_role = await t(guild_id, f"role_{role.lower()}")
        embed.add_field(
            name=f"🎮 {txt_fjob}",
            value=f"**{tr_job}** {role_emoji} {tr_role}",
            inline=True,
        )
    else:
        # Status-Feld für Absage/Leave (kein Job)
        embed.add_field(
            name=f"🎮 {txt_fstat}",
            value=status_text,
            inline=True,
        )

    # Feld 3: Termin
    embed.add_field(
        name=f"📅 {txt_ftime}",
        value=f"`{event_time}`",
        inline=True,
    )

    # Feld 4: Teilnehmerstand
    embed.add_field(
        name=f"👥 {txt_fnum}",
        value=f"**{signup_count}** / **{max_players}**",
        inline=True,
    )

    # Footer mit Event-ID
    embed.set_footer(text=f"Event-ID: #{event_id}")

    # ── Rollen-Icon als Thumbnail anhängen ──
    try:
        if rsvp_status in ("accepted", "tentative") and role:
            icon_path = get_icon_path(job or "", is_role=False) or get_icon_path(role, is_role=True)
        else:
            icon_path = None

        if icon_path:
            file = discord.File(icon_path, filename="log_icon.png")
            embed.set_thumbnail(url="attachment://log_icon.png")
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(embed=embed)
    except discord.errors.Forbidden:
        log.warning("Keine Berechtigung für Log-Channel %d", settings["log_channel_id"])


async def _update_event_embed(interaction: discord.Interaction, event_id: int) -> None:
    """
    Aktualisiert das Event-Embed in der Originalnachricht.
    """
    event = await db.get_event(event_id)
    if not event or not event.get("message_id") or not event.get("channel_id"):
        return

    # Channel und Nachricht holen
    if interaction.guild:
        channel = interaction.guild.get_channel(event["channel_id"])
    else:
        return

    if not channel:
        return

    try:
        message = await channel.fetch_message(event["message_id"])
        embed = await build_event_embed(event)
        await message.edit(embed=embed)
    except (discord.errors.NotFound, discord.errors.Forbidden) as e:
        log.warning("Konnte Event-Embed nicht aktualisieren: %s", e)
