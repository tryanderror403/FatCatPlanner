"""
fatcat.py – Fat Cat Planner – Hauptdatei
==========================================
Der Entry-Point für den FFXIV Discord Bot.
Lädt Umgebungsvariablen, initialisiert die Datenbank, synchronisiert
XIVAPI-Daten beim ersten Start und registriert alle Cogs.

Starten mit:
    python3 fatcat.py

Voraussetzungen:
    - .env Datei mit DISCORD_TOKEN=...
    - pip install -r requirements.txt
"""

import asyncio
import logging
import os
import sys
import pathlib
import shutil
import re
import platform

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────
#  LOKALISIERUNG FÜR TERMINAL & LOGS
# ──────────────────────────────────────────────────────────────────────
from i18n import SYS_MSG


import db
from xivapi_sync import sync_content_from_xivapi
from views import EventSignupView
from i18n import t

# ──────────────────────────────────────────────────────────────────────
#  STATUS-ROTATION (5 Texte, alle 5 Minuten)
# ──────────────────────────────────────────────────────────────────────

STATUS_TEXTS = [
    "Plans your next Event",
    "Organizing the Party...",
    "Feeding the Fat Cat...",
    "Waiting for the Tank...",
    "Polishing the Relic Weapons...",
]

# Index für die aktuelle Status-Position
_status_index = 0

# ──────────────────────────────────────────────────────────────────────
#  LOGGING KONFIGURIEREN
# ──────────────────────────────────────────────────────────────────────

import logging.handlers

BASE_DIR = pathlib.Path(__file__).parent.resolve()
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_formatter = logging.Formatter(
    fmt="%(asctime)s │ %(name)-18s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=LOG_DIR / "fatcat.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)
file_handler.setFormatter(log_formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[stream_handler, file_handler],
)
log = logging.getLogger("fatcat")

# discord.py-Logging etwas ruhiger stellen
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)

# ──────────────────────────────────────────────────────────────────────
#  UMGEBUNGSVARIABLEN LADEN UND SETUP-WIZARD
# ──────────────────────────────────────────────────────────────────────

ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    print("EN: No .env file found! Starting Setup-Wizard...")
    print("DE: Keine .env-Datei gefunden! Setup-Assistent wird gestartet...")
    print("FR: Aucun fichier .env trouvé ! Démarrage de l'assistant de configuration...")
    print("JA: .envファイルが見つかりません！セットアップウィザードを開始します...\n")
    
    lang = ""
    token = ""
    while lang not in ("de", "en", "fr", "ja"):
        lang = input("Select Language / Sprache wählen / Choisir la langue / 言語を選択 (Deutsch: de, English: en, Français: fr, 日本語: ja): ").strip().lower()

    _sys = SYS_MSG.get(lang, SYS_MSG["en"])
    token = input(_sys["setup_token"]).strip()
    owner_str = input(_sys["setup_owner"]).strip()
    if not owner_str:
        owner_str = "0"
    
    token_comment = ""
    if not token:
        if lang == "de":
            token_comment = "# Hier den Discord-Bot-Token eintragen\n"
            token = "dein_discord_token_hier"
        elif lang == "en":
            token_comment = "# Insert your Discord bot token here\n"
            token = "your_discord_token_here"
        elif lang == "fr":
            token_comment = "# Insérez votre jeton de bot Discord ici\n"
            token = "votre_jeton_ici"
        elif lang == "ja":
            token_comment = "# ここにDiscordボットのトークンを入力してください\n"
            token = "ここにトークンを入力"

    ENV_EXAMPLE = BASE_DIR / ".env.example"
    if ENV_EXAMPLE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_PATH)
        content = ENV_PATH.read_text(encoding="utf-8")
    else:
        content = ""
    
    if "DISCORD_TOKEN=" in content:
        if token_comment:
            content = re.sub(r'DISCORD_TOKEN=.*', f'{token_comment.strip()}\nDISCORD_TOKEN={token}', content)
        else:
            content = re.sub(r'DISCORD_TOKEN=.*', f'DISCORD_TOKEN={token}', content)
    else:
        content += f"\n{token_comment}DISCORD_TOKEN={token}\n"
        
    if "DEFAULT_LANGUAGE=" in content:
        content = re.sub(r'DEFAULT_LANGUAGE=.*', f'DEFAULT_LANGUAGE={lang}', content)
    else:
        content += f"\nDEFAULT_LANGUAGE={lang}\n"
        
    if "OWNER_ID=" in content:
        content = re.sub(r'OWNER_ID=.*', f'OWNER_ID={owner_str}', content)
    else:
        content += f"\nOWNER_ID={owner_str}\n"
        
    ENV_PATH.write_text(content.strip() + "\n", encoding="utf-8")
    print(_sys["setup_done"])

load_dotenv(dotenv_path=ENV_PATH)
TOKEN = os.getenv("DISCORD_TOKEN")
SYS_LANG = os.getenv("DEFAULT_LANGUAGE", "en").lower()
if SYS_LANG not in SYS_MSG:
    SYS_LANG = "en"
sys_msg = SYS_MSG[SYS_LANG]

if not TOKEN:
    log.critical(sys_msg["token_missing"])
    sys.exit(1)

# ──────────────────────────────────────────────────────────────────────
#  BOT-KONFIGURATION
# ──────────────────────────────────────────────────────────────────────

# ANSI Farben für Konsolenausgabe
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    """Zeigt das Start-Banner mit System-Infos an."""
    os_name = platform.system()
    if os_name == "Darwin":
        os_name = "macOS"
        
    print(f"\n{Colors.OKCYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKGREEN}  🐱 FAT CAT PLANNER - {sys_msg['banner_version']}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}")
    print(f"{Colors.BOLD}{sys_msg['banner_sys']}{Colors.ENDC} {os_name} ({platform.release()})")
    print(f"{Colors.BOLD}{sys_msg['banner_path']}{Colors.ENDC} {BASE_DIR}")
    print(f"{Colors.OKCYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{Colors.ENDC}")
    print(f"{Colors.OKCYAN}{sys_msg['banner_load']}{Colors.ENDC}")

# Intents definieren – wir brauchen Messages für Prefix-Commands
# und Members für User-Informationen
intents = discord.Intents.default()
intents.message_content = True  # Nötig für Prefix-Commands (!)
intents.members = True          # Nötig für User-Mentions in Embeds

class I18nTranslator(discord.app_commands.Translator):
    async def translate(
        self,
        string: discord.app_commands.locale_str,
        locale: discord.Locale,
        context: discord.app_commands.TranslationContext
    ) -> str | None:
        lang = "en"
        if locale == discord.Locale.german:
            lang = "de"
        elif locale == discord.Locale.french:
            lang = "fr"
        elif locale == discord.Locale.japanese:
            lang = "ja"
            
        from i18n import TRANSLATIONS
        
        key_map = {
            "Startet den interaktiven Setup-Wizard für Sprache, Kanal und Zeitzone.": "cmd_setup",
            "Aktiviert/Deaktiviert das Event-Logging im aktuellen Kanal.": "cmd_facadminlog",
            "Zeitzonen verwalten": "cmd_fctimezone",
            "Zeitzone für Events auf dem Server ändern": "cmd_fctimezone_set",
            "Wann findet der nächste Background-Check statt?": "cmd_fctimezone_status",
            "Bot Administration": "cmd_facadmin",
            "Erzwingt globale Synchronisation aller Slash-Commands": "cmd_facadmin_sync",
            "Erstelle ein neues Event (der Flow läuft per DM).": "cmd_fccreate",
            "Die neue Zeitzone (z.B. Europe/Berlin, UTC)": "cmd_fctimezone_set_arg",
            "Lädt alle Duties/Inhalte neu von XIVAPI (dauert evtl. mehrere Minuten).": "cmd_fcdutyupdate",
        }
        
        # Check if the string message exists in our map
        key = key_map.get(string.message)
        if key and key in TRANSLATIONS and lang in TRANSLATIONS[key]:
            return TRANSLATIONS[key][lang]
            
        return None

class FatCatBot(commands.Bot):
    async def setup_hook(self):
        await self.tree.set_translator(I18nTranslator())

# Bot erstellen mit Prefix "!" für klassische Befehle
bot = FatCatBot(
    command_prefix="!",
    intents=intents,
    description="🐱 Fat Cat Planner – Der FFXIV Raid-Planungs-Bot",
    help_command=None,  # Wir nutzen unseren eigenen /fchelp Befehl
)

# ──────────────────────────────────────────────────────────────────────
#  LISTE DER COGS (Erweiterungsmodule)
# ──────────────────────────────────────────────────────────────────────

COGS = [
    "cogs.admin",    # /fcsetup, /facadminlog, /fcdutyupdate
    "cogs.events",   # /fccreate, Reminder-Task
    "cogs.utils",    # /fctime, /fchelp
]

# ──────────────────────────────────────────────────────────────────────
#  STATUS-ROTATION TASK
# ──────────────────────────────────────────────────────────────────────

@tasks.loop(minutes=5)
async def rotate_status():
    """Wechselt den 'Spielt gerade'-Status alle 5 Minuten."""
    global _status_index
    activity = discord.Game(name=STATUS_TEXTS[_status_index])
    await bot.change_presence(activity=activity)
    _status_index = (_status_index + 1) % len(STATUS_TEXTS)


# ──────────────────────────────────────────────────────────────────────
#  ON_READY EVENT
# ──────────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    """
    Wird aufgerufen, wenn der Bot erfolgreich mit Discord verbunden ist.
    - Initialisiert die Datenbank
    - Synchronisiert Slash-Commands
    - Lädt XIVAPI-Daten (beim ersten Start)
    - Registriert persistent Views
    """
    print(f"{Colors.OKGREEN}{sys_msg['connected']}{Colors.ENDC}")
    log.info("━" * 60)
    log.info(sys_msg['online'])
    log.info(sys_msg['bot_info'], bot.user.name, bot.user.id)
    log.info(sys_msg['guild_info'], len(bot.guilds))
    log.info("━" * 60)
    
    print(f"{Colors.OKCYAN}" + sys_msg['bot_info_print'].format(bot.user.name, len(bot.guilds)) + f"{Colors.ENDC}")

    if getattr(bot, "_ready_done", False):
        log.info(sys_msg['sync_warn'])
        return
    bot._ready_done = True

    # ── Status-Rotation starten ──
    if not rotate_status.is_running():
        rotate_status.start()

    # ── Slash-Commands synchronisieren ──
    log.info(sys_msg['sync_global'])
    try:
        # Dubletten-Schutz: Lösche mögliche alte Guild-Commands, bevor wir global syncen.
        # So vermeiden wir die gefürchteten doppelten Slash-Einträge.
        for guild in bot.guilds:
            try:
                bot.tree.clear_commands(guild=guild)
                await bot.tree.sync(guild=guild)
            except Exception as e:
                log.warning(sys_msg['sync_clear_err'], guild.id, e)
            
        synced = await bot.tree.sync()
        log.info(sys_msg['sync_done'], len(synced))
    except Exception as e:
        log.error(sys_msg['sync_err'], e)

    # ── Persistent Views registrieren ──
    # Damit die Buttons auch nach einem Bot-Neustart funktionieren,
    # müssen wir die Views für alle bestehenden Events registrieren.
    log.info(sys_msg['reg_views'])
    await _register_persistent_views()

    # ── XIVAPI Content-Sync beim ersten Start ──
    # Automatischen Background-Sync starten, wenn DB leer ist
    content_count = await db.get_content_count()
    if content_count == 0:
        log.info(sys_msg['cache_empty'])
        print(f"{Colors.OKCYAN}" + sys_msg['cache_empty_p'] + f"{Colors.ENDC}")
        bot.loop.create_task(sync_content_from_xivapi())
    else:
        log.info(sys_msg['cache_full'], content_count)
        print(f"{Colors.OKGREEN}" + sys_msg['cache_full_p'].format(content_count) + f"{Colors.ENDC}")


async def _register_persistent_views():
    """
    Registriert EventSignupViews für alle bestehenden Events,
    damit die Buttons nach einem Bot-Neustart weiterhin funktionieren.
    """
    import aiosqlite
    async with aiosqlite.connect(db.DB_PATH) as database:
        database.row_factory = aiosqlite.Row
        cursor = await database.execute(
            "SELECT event_id, guild_id FROM events WHERE message_id IS NOT NULL AND is_active = 1"
        )
        rows = await cursor.fetchall()

    registered = 0
    for row in rows:
        guild_id = row["guild_id"]
        txt_accept = await t(guild_id, "embed_btn_accept")
        txt_tentative = await t(guild_id, "embed_btn_tentative")
        txt_decline = await t(guild_id, "embed_btn_decline")
        
        view = EventSignupView(row["event_id"], txt_accept, txt_tentative, txt_decline)
        bot.add_view(view)
        registered += 1

    if registered > 0:
        log.info(sys_msg['reg_views_done'], registered)


# ──────────────────────────────────────────────────────────────────────
#  BOT STARTEN
# ──────────────────────────────────────────────────────────────────────

async def main():
    """Hauptfunktion: Initialisiert DB, lädt Cogs und startet den Bot."""
    print_banner()
    
    async with bot:
        # ── Datenbank initialisieren (VOR dem Laden der Cogs!) ──
        # So existieren die Tabellen schon, wenn z.B. der Reminder-Task startet.
        log.info(sys_msg['db_init'])
        print(f"{Colors.OKCYAN}" + sys_msg['db_init_p'] + f"{Colors.ENDC}")
        await db.init_db()
        log.info(sys_msg['db_ready'])
        print(f"{Colors.OKGREEN}" + sys_msg['db_ready_p'] + f"{Colors.ENDC}")

        # Alle Cogs laden
        print(f"{Colors.OKCYAN}" + sys_msg['cogs_load'] + f"{Colors.ENDC}")
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                log.info(sys_msg['cog_done'], cog)
            except Exception as e:
                log.error(sys_msg['cog_err'], cog, e, exc_info=True)
                print(f"{Colors.FAIL}" + sys_msg['cog_err_p'].format(cog, e) + f"{Colors.ENDC}")

        # Bot starten – läuft bis Ctrl+C
        print(f"{Colors.OKCYAN}" + sys_msg['connect_p'] + f"{Colors.ENDC}")
        
        try:
            await bot.start(TOKEN)
        except discord.errors.LoginFailure:
            log.critical(sys_msg['login_fail'])
            print(f"{Colors.FAIL}" + sys_msg['login_fail_p'] + f"{Colors.ENDC}")
        except discord.errors.HTTPException as e:
            log.error(sys_msg['http_err'], e)
            print(f"{Colors.FAIL}" + sys_msg['http_err_p'] + f"{Colors.ENDC}")
        except Exception as e:
            log.error(sys_msg['unexp_err'], e, exc_info=True)
            print(f"{Colors.FAIL}" + sys_msg['unexp_err_p'] + f"{Colors.ENDC}")


if __name__ == "__main__":
    def _shutdown_handler(signum, frame):
        """Handler für SIGTERM (Systemd/Service). Fährt den Bot sofort runter."""
        log.info(sys_msg['sig_term'], signum)
        sys.exit(0)

    import signal
    try:
        signal.signal(signal.SIGTERM, _shutdown_handler)
    except AttributeError:
        pass # Auf einigen OS (Windows) gibt es kein SIGTERM in signal
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Im interaktiven Terminal fragen wir kurz nach
        if sys.stdin.isatty():
            try:
                print(f"\n{Colors.WARNING}{sys_msg['quit_prompt']}{Colors.ENDC}", end="", flush=True)
                ans = input().strip().lower()
                if ans in ("j", "y", "ja", "yes", "o", "oui"):
                    log.info(sys_msg['quit_user'])
                    print(f"{Colors.OKGREEN}{sys_msg['quit_user_p']}{Colors.ENDC}")
                else:
                    print(f"{Colors.OKCYAN}{sys_msg['quit_already']}{Colors.ENDC}")
            except (KeyboardInterrupt, EOFError):
                pass
        else:
            # Lief als Background/Service und es gab ein Ctrl+C artiges Event
            log.info(sys_msg['quit_bg'])
