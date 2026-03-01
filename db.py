"""
db.py – Asynchroner Datenbank-Layer
=====================================
Verwaltet die SQLite-Datenbank 'planner.db' mit aiosqlite.
Stellt CRUD-Operationen für Guild-Settings, Content-Cache, Events
und Anmeldungen (Signups) bereit.
"""

import aiosqlite
import difflib
import pathlib

# Pfad zur Datenbank-Datei erzwingt das exakte Verzeichnis von db.py
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DB_PATH = BASE_DIR / "planner.db"


# ──────────────────────────────────────────────────────────────────────
#  DATENBANK-INITIALISIERUNG
# ──────────────────────────────────────────────────────────────────────

async def init_db() -> None:
    """
    Erstellt alle benötigten Tabellen, falls sie noch nicht existieren.
    Wird beim Bot-Start aufgerufen.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Performance-Upgrade: Aktiviere den WAL-Modus
        await db.execute("PRAGMA journal_mode=WAL;")

        # Guild-Einstellungen: welcher Kanal für Events, welcher für Logs, Zeitzone, Sprache, Servername
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id            INTEGER PRIMARY KEY,
                guild_name          TEXT,
                event_channel_id    INTEGER,
                event_channel_name  TEXT,
                log_channel_id      INTEGER,
                log_channel_name    TEXT,
                logging_enabled     INTEGER DEFAULT 0,
                timezone            TEXT DEFAULT 'Europe/Berlin',
                language            TEXT DEFAULT 'en'
            )
        """)
        
        # MIGRATION: Sicherstellen, dass language bei alten DBs nachgerüstet wird
        try:
            await db.execute("ALTER TABLE guild_settings ADD COLUMN language TEXT DEFAULT 'en'")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

        # MIGRATION: Sicherstellen, dass guild_name bei alten DBs nachgerüstet wird
        try:
            await db.execute("ALTER TABLE guild_settings ADD COLUMN guild_name TEXT")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

        # MIGRATION: event_channel_name und log_channel_name
        try:
            await db.execute("ALTER TABLE guild_settings ADD COLUMN event_channel_name TEXT")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE guild_settings ADD COLUMN log_channel_name TEXT")
        except aiosqlite.OperationalError:
            pass

        await db.execute("""
            CREATE TABLE IF NOT EXISTS content_cache (
                id            INTEGER PRIMARY KEY,
                content_type_id INTEGER,
                name_de       TEXT,
                name_en       TEXT,
                name_fr       TEXT,
                name_ja       TEXT,
                image_url     TEXT
            )
        """)

        # Events, die von Usern erstellt werden
        await db.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id      INTEGER NOT NULL,
                guild_name    TEXT,
                title         TEXT NOT NULL,
                time          TEXT NOT NULL,
                content_name  TEXT,
                creator_id    INTEGER NOT NULL,
                creator_name  TEXT,
                unique_jobs   INTEGER DEFAULT 0,
                max_players   INTEGER DEFAULT 8,
                message_id    INTEGER,
                channel_id    INTEGER,
                channel_name  TEXT,
                timezone_type TEXT DEFAULT 'local',
                unix_timestamp INTEGER,
                event_duration TEXT,
                free_text     TEXT,
                is_active     INTEGER DEFAULT 1
            )
        """)

        # MIGRATION: guild_name und channel_name in events
        try:
            await db.execute("ALTER TABLE events ADD COLUMN guild_name TEXT")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE events ADD COLUMN channel_name TEXT")
        except aiosqlite.OperationalError:
            pass
            
        # MIGRATION: is_active (Soft-Delete)
        try:
            await db.execute("ALTER TABLE events ADD COLUMN is_active INTEGER DEFAULT 1")
        except aiosqlite.OperationalError:
            pass

        # MIGRATION: Sicherstellen, dass creator_name bei alten DBs nachgerüstet wird
        try:
            await db.execute("ALTER TABLE events ADD COLUMN creator_name TEXT")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

        # MIGRATION: Sicherstellen, dass timezone_type und unix_timestamp nachgerüstet werden
        try:
            await db.execute("ALTER TABLE events ADD COLUMN timezone_type TEXT DEFAULT 'local'")
        except aiosqlite.OperationalError:
            pass
            
        try:
            await db.execute("ALTER TABLE events ADD COLUMN unix_timestamp INTEGER")
        except aiosqlite.OperationalError:
            pass

        # MIGRATION: event_duration und free_text
        try:
            await db.execute("ALTER TABLE events ADD COLUMN event_duration TEXT")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE events ADD COLUMN free_text TEXT")
        except aiosqlite.OperationalError:
            pass

        # Anmeldungen für Events
        await db.execute("""
            CREATE TABLE IF NOT EXISTS signups (
                event_id   INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                user_name  TEXT,
                guild_id   INTEGER,
                guild_name TEXT,
                role       TEXT,
                job        TEXT,
                timestamp  TEXT NOT NULL,
                status     TEXT DEFAULT 'accepted',
                PRIMARY KEY (event_id, user_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE
            )
        """)

        # MIGRATION: guild_id und guild_name in signups
        try:
            await db.execute("ALTER TABLE signups ADD COLUMN guild_id INTEGER")
        except aiosqlite.OperationalError:
            pass
        try:
            await db.execute("ALTER TABLE signups ADD COLUMN guild_name TEXT")
        except aiosqlite.OperationalError:
            pass

        # MIGRATION: Sicherstellen, dass user_name bei alten DBs nachgerüstet wird
        try:
            await db.execute("ALTER TABLE signups ADD COLUMN user_name TEXT")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

        # MIGRATION: status-Spalte für RSVP (accepted/tentative/declined)
        try:
            await db.execute("ALTER TABLE signups ADD COLUMN status TEXT DEFAULT 'accepted'")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

            await db.execute("""
            CREATE TABLE IF NOT EXISTS user_links (
                user_id TEXT PRIMARY KEY,
                main_role TEXT,
                main_job TEXT,
                preferred_language TEXT
            )
            """)

        # MIGRATION: Sicherstellen, dass preferred_language bei alten DBs nachgerüstet wird
        try:
            await db.execute("ALTER TABLE user_links ADD COLUMN preferred_language TEXT")
        except aiosqlite.OperationalError:
            pass # Spalte existiert bereits

        await db.commit()


# ──────────────────────────────────────────────────────────────────────
#  GUILD SETTINGS
# ──────────────────────────────────────────────────────────────────────

async def set_event_channel(guild_id: int, channel_id: int, guild_name: str, event_channel_name: str | None = None, timezone: str | None = None) -> None:
    """Setzt den Event-Channel (und optional die Zeitzone) für eine Guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        if timezone:
            await db.execute("""
                INSERT INTO guild_settings (guild_id, guild_name, event_channel_id, event_channel_name, timezone)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    guild_name = excluded.guild_name,
                    event_channel_id = excluded.event_channel_id,
                    event_channel_name = excluded.event_channel_name,
                    timezone = excluded.timezone
            """, (guild_id, guild_name, channel_id, event_channel_name, timezone))
        else:
            await db.execute("""
                INSERT INTO guild_settings (guild_id, guild_name, event_channel_id, event_channel_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET 
                    guild_name = excluded.guild_name,
                    event_channel_id = excluded.event_channel_id,
                    event_channel_name = excluded.event_channel_name
            """, (guild_id, guild_name, channel_id, event_channel_name))
        await db.commit()


async def get_event_channel(guild_id: int) -> int | None:
    """Gibt die Event-Channel-ID für eine Guild zurück (oder None)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT event_channel_id FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        return row["event_channel_id"] if row else None


async def set_timezone(guild_id: int, timezone: str, guild_name: str) -> None:
    """Setzt die Zeitzone für eine Guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, guild_name, timezone)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                guild_name = excluded.guild_name,
                timezone = excluded.timezone
        """, (guild_id, guild_name, timezone))
        await db.commit()


async def get_timezone(guild_id: int) -> str:
    """Gibt die Zeitzone für eine Guild zurück (Default: 'Europe/Berlin')."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT timezone FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        return row["timezone"] if row and row["timezone"] else "Europe/Berlin"


async def set_language(guild_id: int, language: str, guild_name: str) -> None:
    """Setzt die Sprache für eine Guild (en, de, fr, ja)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, guild_name, language)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                guild_name = excluded.guild_name,
                language = excluded.language
        """, (guild_id, guild_name, language))
        await db.commit()


async def get_language(guild_id: int) -> str:
    """Gibt die Sprache für eine Guild zurück (Default: 'en')."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT language FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        return row["language"] if row and row["language"] else "en"


async def set_log_channel(guild_id: int, guild_name: str, channel_id: int, enabled: bool, log_channel_name: str | None = None) -> None:
    """Aktiviert/deaktiviert das Logging und setzt den Log-Channel."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO guild_settings (guild_id, guild_name, log_channel_id, log_channel_name, logging_enabled)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                guild_name = excluded.guild_name,
                log_channel_id = excluded.log_channel_id,
                log_channel_name = excluded.log_channel_name,
                logging_enabled = excluded.logging_enabled
        """, (guild_id, guild_name, channel_id, log_channel_name, int(enabled)))
        await db.commit()


async def disable_logging(guild_id: int) -> None:
    """Deaktiviert das Logging für eine Guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE guild_settings SET logging_enabled = 0
            WHERE guild_id = ?
        """, (guild_id,))
        await db.commit()


async def get_log_settings(guild_id: int) -> dict | None:
    """
    Gibt die Log-Einstellungen zurück:
    {'log_channel_id': int, 'logging_enabled': bool} oder None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT log_channel_id, logging_enabled FROM guild_settings WHERE guild_id = ?",
            (guild_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                "log_channel_id": row["log_channel_id"],
                "logging_enabled": bool(row["logging_enabled"]),
            }
        return None


# ──────────────────────────────────────────────────────────────────────
#  CONTENT CACHE (XIVAPI-Daten)
# ──────────────────────────────────────────────────────────────────────

async def bulk_upsert_content(entries: list[dict]) -> int:
    """
    Fügt mehrere Inhalte ein oder ersetzt sie (INSERT OR REPLACE).
    Jeder Dict-Eintrag braucht: id, name_de, name_en, name_fr, name_ja.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany("""
            INSERT OR REPLACE INTO content_cache
                (id, content_type_id, name_de, name_en, name_fr, name_ja, image_url)
            VALUES
                (:id, :content_type_id, :name_de, :name_en, :name_fr, :name_ja, :image_url)
        """, entries)
        await db.commit()
    return len(entries)


async def search_content(query: str, lang: str = "en", limit: int = 25) -> list[dict]:
    """
    Sucht Inhalte im Cache über ALLE Sprachversionen (OR-Verknüpfung).
    Gibt eine Liste von Dicts zurück, bei der 'name' bereits der in
    'lang' übersetzten Version entspricht.
    """
    if lang not in ("de", "en", "fr", "ja"):
        lang = "en"
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # 1. Schnelle exakte LIKE Suche versuchen (Für Teile von Wörtern)
        like_query = f"%{query}%"
        cursor = await db.execute(
            f"SELECT id, content_type_id, COALESCE(name_{lang}, name_en) AS name, image_url "
            "FROM content_cache "
            "WHERE name_de LIKE ? OR name_en LIKE ? OR name_fr LIKE ? OR name_ja LIKE ? "
            f"ORDER BY COALESCE(name_{lang}, name_en) LIMIT ?",
            (like_query, like_query, like_query, like_query, limit)
        )
        exact_rows = await cursor.fetchall()
        
        if len(exact_rows) > 0:
            return [dict(row) for row in exact_rows]
            
        # 2. Fuzzy Suche / Tippfehler Toleranz
        cursor = await db.execute(
            f"SELECT id, content_type_id, COALESCE(name_{lang}, name_en) AS name, image_url "
            "FROM content_cache"
        )
        all_rows = await cursor.fetchall()
        
        names = [row["name"] for row in all_rows if row["name"]]
        # Finde ähnlichste Namen (Toleranz 0.6 = moderate Übereinstimmung)
        close_matches = difflib.get_close_matches(query, names, n=limit, cutoff=0.5)
        
        results = []
        for match in close_matches:
            # Finde die Original-Row für diesen Match (erstes Vorkommen)
            for row in all_rows:
                if row["name"] == match:
                    results.append(dict(row))
                    break
                    
        return results


async def get_content(name: str, lang: str = "en") -> dict | None:
    """
    Gibt einen einzelnen Inhalt aus dem Cache zurück anhand des Namens.
    Sucht in allen Sprachversionen und gibt `name_{lang}` als `name` zurück.
    """
    if lang not in ("de", "en", "fr", "ja"):
        lang = "en"
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            f"SELECT id, COALESCE(name_{lang}, name_en) AS name, image_url "
            "FROM content_cache "
            "WHERE name_de = ? OR name_en = ? OR name_fr = ? OR name_ja = ?",
            (name, name, name, name)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_content_all_langs(name: str) -> dict | None:
    """
    Gibt einen Inhalt mit allen 4 Sprachversionen zurück.
    Returns dict mit name_en, name_de, name_fr, name_ja, image_url oder None.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, name_de, name_en, name_fr, name_ja, image_url "
            "FROM content_cache "
            "WHERE name_de = ? OR name_en = ? OR name_fr = ? OR name_ja = ?",
            (name, name, name, name)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None





async def get_content_count() -> int:
    """Gibt die Anzahl der Einträge im Content-Cache zurück."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM content_cache")
        row = await cursor.fetchone()
        return row[0]


# ──────────────────────────────────────────────────────────────────────
#  EVENTS
# ──────────────────────────────────────────────────────────────────────

async def create_event(
    guild_id: int,
    title: str,
    event_time: str,
    content_name: str,
    creator_id: int,
    creator_name: str,
    unique_jobs: bool,
    max_players: int,
    timezone_type: str = "local",
    unix_timestamp: int | None = None,
    event_duration: str | None = None,
    free_text: str | None = None,
    guild_name: str | None = None,
    channel_name: str | None = None,
) -> int:
    """
    Erstellt ein neues Event und gibt die event_id zurück.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO events (guild_id, guild_name, title, time, content_name, creator_id, creator_name, unique_jobs, max_players, timezone_type, unix_timestamp, event_duration, free_text, channel_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (guild_id, guild_name, title, event_time, content_name, creator_id, creator_name, int(unique_jobs), max_players, timezone_type, unix_timestamp, event_duration, free_text, channel_name))
        await db.commit()
        return cursor.lastrowid


async def update_event_message(event_id: int, message_id: int, channel_id: int) -> None:
    """Speichert die Discord-Message-ID und Channel-ID des Event-Embeds."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE events SET message_id = ?, channel_id = ? WHERE event_id = ?",
            (message_id, channel_id, event_id)
        )
        await db.commit()


async def get_event(event_id: int) -> dict | None:
    """Gibt ein Event als Dict zurück."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_upcoming_events(minutes_ahead: int = 10) -> list[dict]:
    """
    Gibt alle Events zurück, die in den nächsten X Minuten starten.
    Wird vom Reminder-Task genutzt.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Da wir das Datum als "DD.MM.YYYY HH:MM" speichern, ist ein purer SQL-Vergleich schwierig.
        # Wir holen alle aktiven Events, deren message_id gesetzt ist und prüfen in Python.
        cursor = await db.execute("SELECT * FROM events WHERE message_id IS NOT NULL AND is_active = 1")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_all_events(guild_id: int | None = None) -> list[dict]:
    """
    Gibt ALLE existierenden Events zurück.
    Wenn guild_id gesetzt ist, werden nur die Events dieses Servers geladen.
    Nützlich für Auto-Cleanup.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if guild_id:
            cursor = await db.execute("SELECT * FROM events WHERE guild_id = ? AND is_active = 1", (guild_id,))
        else:
            cursor = await db.execute("SELECT * FROM events WHERE is_active = 1")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def delete_event_and_signups(event_id: int) -> None:
    """Löscht ein Event und explizit alle zugehörigen Anmeldungen."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM signups WHERE event_id = ?", (event_id,))
        await db.execute("DELETE FROM events WHERE event_id = ?", (event_id,))
        await db.commit()


async def archive_event(event_id: int) -> None:
    """Setzt is_active = 0, wodurch das Event in den Listen ausgeblendet wird (Soft-Delete)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE events SET is_active = 0 WHERE event_id = ?", (event_id,))
        await db.commit()


async def purge_ancient_data() -> int:
    """
    Sucht nach Events, die älter als 3 Jahre (1095 Tage) sind, und löscht diese sowie 
    die zugehörigen Signups vollständig aus der Datenbank (Hard Delete).
    Gibt die Anzahl der gelöschten Events zurück.
    """
    import time
    three_years_ago = int(time.time() - (1095 * 24 * 60 * 60))
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Zuerst alle Anmeldungen löschen, die zu The Ancient Events gehören
        await db.execute(
            "DELETE FROM signups WHERE event_id IN (SELECT event_id FROM events WHERE unix_timestamp IS NOT NULL AND unix_timestamp < ?)", 
            (three_years_ago,)
        )
        
        # Dann die Events selbst hart löschen
        cursor = await db.execute(
            "DELETE FROM events WHERE unix_timestamp IS NOT NULL AND unix_timestamp < ?", 
            (three_years_ago,)
        )
        deleted_events_count = cursor.rowcount
        await db.commit()
        
        return deleted_events_count


# ──────────────────────────────────────────────────────────────────────
#  SIGNUPS (Anmeldungen)
# ──────────────────────────────────────────────────────────────────────

async def signup_user(event_id: int, user_id: int, user_name: str, role: str | None, job: str | None, timestamp: str, status: str = "accepted", guild_id: int | None = None, guild_name: str | None = None) -> bool:
    """
    Meldet einen User für ein Event an. Gibt True zurück bei Erfolg,
    False wenn der User bereits angemeldet ist (wird dann aktualisiert).
    status: 'accepted', 'tentative' oder 'declined'.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO signups (event_id, user_id, user_name, guild_id, guild_name, role, job, timestamp, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(event_id, user_id) DO UPDATE SET
                user_name = excluded.user_name,
                guild_id = excluded.guild_id,
                guild_name = excluded.guild_name,
                role = excluded.role,
                job = excluded.job,
                timestamp = excluded.timestamp,
                status = excluded.status
        """, (event_id, user_id, user_name, guild_id, guild_name, role, job, timestamp, status))
        await db.commit()
        return True


async def remove_signup(event_id: int, user_id: int) -> bool:
    """Meldet einen User von einem Event ab. Gibt True zurück wenn erfolgreich."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM signups WHERE event_id = ? AND user_id = ?",
            (event_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_signups(event_id: int) -> list[dict]:
    """Gibt alle Anmeldungen für ein Event als Liste von Dicts zurück."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM signups WHERE event_id = ? ORDER BY timestamp",
            (event_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_signup_count(event_id: int) -> int:
    """Gibt die Anzahl der aktiven Anmeldungen (accepted + tentative) zurück. Declined zählt nicht."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM signups WHERE event_id = ? AND COALESCE(status, 'accepted') != 'declined'",
            (event_id,)
        )
        row = await cursor.fetchone()
        return row[0]


async def get_used_jobs(event_id: int) -> list[str]:
    """Gibt eine Liste aller belegten Jobs für ein Event zurück (nur accepted/tentative)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT job FROM signups WHERE event_id = ? AND COALESCE(status, 'accepted') != 'declined' AND job IS NOT NULL",
            (event_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


# ──────────────────────────────────────────────────────────────────────
#  USER SETTINGS
# ──────────────────────────────────────────────────────────────────────

async def set_user_language(user_id: int, language: str) -> None:
    """Setzt die bevorzugte Sprache für einen Nutzer in user_links."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_links (user_id, preferred_language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
                preferred_language = excluded.preferred_language
        """, (str(user_id), language))
        await db.commit()


async def get_user_language(user_id: int) -> str | None:
    """Gibt die bevorzugte Sprache eines Nutzers zurück (oder None)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT preferred_language FROM user_links WHERE user_id = ?",
            (str(user_id),)
        )
        row = await cursor.fetchone()
        return row["preferred_language"] if row and row["preferred_language"] else None
