"""
xivapi_sync.py – XIVAPI Content-Synchronisation (Full Sync)
================================================================
Migriert auf XIVAPI v2.
Ruft ALLE Einträge aus ContentFinderCondition ab, mit korrekter
Übersetzung (DE/EN/FR/JA) und paginiert nach v2 Schema.

Kategorien (lokal gefiltert):
  CT 2  = Dungeon
  CT 4  = Trial
  CT 5  = Raid (8-Mann/Alliance)
  CT 9  = Deep Dungeon
  CT 22 = Exploratory Missions (Eureka)
  CT 28 = Raid (Ultimate)
  CT 29 = V&C Dungeon
  CT 30 = Field Operation (Bozja/Zadnor)
"""

import asyncio
import logging
import urllib.parse
from typing import Callable, Coroutine, Dict, Any

import aiohttp
import db
import os
from i18n import SYS_MSG

log = logging.getLogger("fatcat.xivapi")

def log_msg(key: str) -> str:
    lang = os.getenv("DEFAULT_LANGUAGE", "en").lower()
    if lang not in SYS_MSG:
        lang = "en"
    return SYS_MSG[lang].get(key, key)

# ──────────────────────────────────────────────────────────────────────
#  KONFIGURATION
# ──────────────────────────────────────────────────────────────────────

XIVAPI_V2_URL = "https://v2.xivapi.com/api/sheet/ContentFinderCondition"

# Felder, die wir von v2 abfragen
FIELDS = "ID,Name,ContentType,Icon,Image"

# Die 4 nötigen Sprachen
LANGUAGES = ["en", "de", "fr", "ja"]

# Nur Inhalte dieser ContentType IDs übernehmen wir
VALID_CONTENT_TYPES = {2, 4, 5, 9, 22, 28, 29, 30}

PAGE_DELAY = 0.2


# ──────────────────────────────────────────────────────────────────────
#  SEITENABRUF (V2)
# ──────────────────────────────────────────────────────────────────────

async def _fetch_language_data(session: aiohttp.ClientSession, lang: str) -> Dict[int, Dict[str, Any]]:
    """
    Lädt alle Seiten von ContentFinderCondition für eine bestimmte Sprache 
    herunter (via Cursor-basierte Paginierung).
    Gibt ein Dictionary {ID: geparste_eintrags_daten} zurück.
    """
    results_by_id = {}
    
    base_url = f"{XIVAPI_V2_URL}?fields={FIELDS}&language={lang}&limit=100"
    after_id = None
    page_count = 0
    
    while True:
        page_count += 1
        url = base_url
        if after_id is not None:
            url += f"&after={after_id}"
            
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    log.warning(log_msg("sync_status_err"), resp.status, lang, page_count)
                    break
                    
                data = await resp.json()
                
                # V2 packt die Einträge in das "rows" Array
                results = data.get("rows", [])
                
                for entry in results:
                    row_id = entry.get("row_id")
                    if row_id is None or row_id == 0:
                        continue
                        
                    fields = entry.get("fields", {})
                        
                    # ── ContentType ──
                    ct_raw = fields.get("ContentType")
                    ct_id = None
                    if isinstance(ct_raw, dict):
                        # V2 verschachtelt ContentType -> value für die ID
                        ct_id = ct_raw.get("value")
                    else:
                        ct_id = ct_raw
                        
                    # ── Filter prüfen ──
                    try:
                        ct_id_int = int(ct_id) if ct_id is not None else -1
                    except ValueError:
                        ct_id_int = -1
                        
                    if ct_id_int not in VALID_CONTENT_TYPES:
                        continue
                        
                    results_by_id[row_id] = {
                        "name": str(fields.get("Name", "")).strip(),
                        "content_type_id": ct_id_int,
                        "content_type": ct_raw,
                        "icon": fields.get("Icon"),
                        "image": fields.get("Image")
                    }
                    
                log.info(log_msg("sync_page_processed"), 
                         lang.upper(), page_count, len(results), len(results_by_id))

                # ── Pagination (after ID) ──
                # Abbruchbedingung: Wenn weniger als 100 Elemente zurückkommen, sind wir am Ende.
                if len(results) < 100:
                    log.info(log_msg("sync_final_page"), lang.upper(), page_count)
                    break
                else:
                    # Der letzte Eintrag liefert uns die ID für den "after" Parameter
                    last_entry = results[-1]
                    after_id = last_entry.get("row_id")
                    if not after_id:
                        log.warning(log_msg("sync_no_row_id"), page_count, lang)
                        break

                    await asyncio.sleep(PAGE_DELAY)
                    
                if page_count > 100:
                    log.warning(log_msg("sync_safety_limit"), lang)
                    break
                    
        except aiohttp.ClientError as e:
            log.error(log_msg("sync_net_err"), lang, e)
            break
            
    return results_by_id


# ──────────────────────────────────────────────────────────────────────
#  HAUPTFUNKTION: FULL SYNC
# ──────────────────────────────────────────────────────────────────────

async def sync_content_from_xivapi(
    progress_callback: Callable[[str], Coroutine] | None = None
) -> int:
    """
    Full Sync: Lädt ALLE Einträge aus ContentFinderCondition über XIVAPI v2
    und speichert die relevanten Inhalte in der DB.
    
    Da v2 oft je Request-Sprache übersetzt, laden wir EN, DE, FR, JA
    separat herunter und aggregieren am Ende die lokalen Daten nach der ID.

    Args:
        progress_callback: Ein optionaler async Callback, der währenddessen Text-Feedback gibt.

    Returns:
        Anzahl der gespeicherten Einträge.
    """
    log.info(log_msg("sync_start"))
    if progress_callback:
        await progress_callback("Sync: Starte API v2 Abruf...")

    lang_data = {}

    async with aiohttp.ClientSession() as session:
        for lang in LANGUAGES:
            if progress_callback is not None:
                await progress_callback(f"Sync: Lade Sprache '{lang.upper()}' (Paginiert)...")
            log.info(log_msg("sync_lang_start"), lang)
            lang_data[lang] = await _fetch_language_data(session, lang)
            
    if progress_callback:
        await progress_callback("Sync: Verarbeite verknüpfte Daten...")

    # Englisch als Basis verwenden, um durch alle validen IDs zu iterieren
    base_data = lang_data.get("en", {})
    all_ids = set()
    if not base_data:
        # Fallback falls EN ausfiel: alle jemals in den anderen Sprachen gefundenen IDs kombinieren
        for d in lang_data.values():
            all_ids.update(d.keys())
    else:
        all_ids = set(base_data.keys())

    all_parsed = []

    for entry_id in all_ids:
        # Übersetzungen zusammensuchen
        names = {}
        for lang in LANGUAGES:
            val = lang_data.get(lang, {}).get(entry_id, {})
            names[lang] = val.get("name", "")

        # Finde Basis-Daten (ContentType ID / Icon) aus einer existierenden Sprache
        base_val = lang_data.get("en", {}).get(entry_id, {})
        if not base_val:
            for lang in LANGUAGES:
                base_val = lang_data.get(lang, {}).get(entry_id, {})
                if base_val:
                    break
                    
        if not base_val:
            continue

        primary_name = names.get("de") or names.get("en")
        if not primary_name:
            continue
            
        name_de = names.get("de") or names.get("en")

        # ── Image URL (Icon) ──
        # Wir suchen unter dem Schlüssel "image" prioritär, dann "icon", dann Fallback auf "content_type"
        image_url = None
        icon_id_int = 0

        # Versuch 1: Spezifisches "Image"
        image_obj = base_val.get("image")
        if isinstance(image_obj, dict):
            img_id = image_obj.get("id")
            if img_id is not None:
                icon_id_int = int(img_id)
        elif isinstance(image_obj, (int, str)) and str(image_obj).isdigit():
            icon_id_int = int(image_obj)

        # Versuch 2: Normales "icon" (meist generische Kategorie)
        if icon_id_int == 0:
            icon_obj = base_val.get("icon")
            icon_fallback = None
            if isinstance(icon_obj, dict):
                icon_fallback = icon_obj.get("id")
            elif isinstance(icon_obj, (int, str)) and str(icon_obj).isdigit():
                icon_fallback = int(icon_obj)
            
            if icon_fallback is not None:
                icon_id_int = int(icon_fallback)

        # Versuch 3: Fallback auf ContentType Icon, wenn beides 0 oder None ist
        if icon_id_int == 0:
            ct_obj = base_val.get("content_type")
            if isinstance(ct_obj, dict):
                ct_fields = ct_obj.get("fields")
                if isinstance(ct_fields, dict):
                    fallback_icon = ct_fields.get("Icon")
                    if isinstance(fallback_icon, dict):
                        fallback_id = fallback_icon.get("id")
                        if fallback_id is not None:
                            icon_id_int = int(fallback_id)

        if icon_id_int > 0:
            folder_id = (icon_id_int // 1000) * 1000
            image_url = f"https://xivapi.com/i/{folder_id:06d}/{icon_id_int:06d}.png"

        all_parsed.append({
            "id": entry_id,
            "content_type_id": base_val.get("content_type_id"),
            "name_de": name_de,
            "name_en": names.get("en") or "",
            "name_fr": names.get("fr") or "",
            "name_ja": names.get("ja") or "",
            "image_url": image_url,
        })

    # ── In Datenbank schreiben ──
    if all_parsed:
        count = int(await db.bulk_upsert_content(all_parsed))
        log.info(log_msg("sync_complete"), count)
        if progress_callback is not None:
            await progress_callback(f"Sync: ✓ Abgeschlossen! {count} Einträge wurden aktualisiert.")
        return count
    else:
        log.warning(log_msg("sync_empty"))
        if progress_callback is not None:
            await progress_callback("Sync: ⚠️ Keine Einträge gefunden.")
        return 0
