import re

with open("fatcat.py", "r", encoding="utf-8") as f:
    fatcat_code = f.read()

# Match SYS_MSG mapping
match = re.search(r'(SYS_MSG\s*=\s*\{.*?\n\}\n)', fatcat_code, re.DOTALL)
if not match:
    print("SYS_MSG not found in fatcat.py")
    exit(1)

sys_msg_block = match.group(1)

# Remove SYS_MSG from fatcat.py
fatcat_code = fatcat_code.replace(sys_msg_block, "from i18n import SYS_MSG\n")
with open("fatcat.py", "w", encoding="utf-8") as f:
    f.write(fatcat_code)

# Prepare the new keys
new_keys = {
    "en": {
        "sync_status_err": "XIVAPI v2 Status %d for Language %s on Page %d",
        "sync_page_processed": "   Language %s, Page %d: %d entries processed (%d valid entries added).",
        "sync_final_page": "✅ Final page reached for Language %s (total %d pages).",
        "sync_no_row_id": "Could not determine last row_id on page %d, pausing sync for %s.",
        "sync_safety_limit": "⚠️ Safety limit (100 pages) reached for Language %s.",
        "sync_net_err": "Network Error (%s): %s",
        "sync_start": "━━━ Starting Full Sync for XIVAPI v2 ━━━",
        "sync_lang_start": "📥 Downloading data for Language: %s",
        "sync_complete": "━━━ Full Scan Complete: (%d entries processed/saved) ━━━",
        "sync_empty": "⚠️ No relevant content found, or V2 API did not return results."
    },
    "de": {
        "sync_status_err": "XIVAPI v2 Status %d für Sprache %s auf Seite %d",
        "sync_page_processed": "   Sprache %s, Seite %d: %d Einträge verarbeitet (davon %d gültige neu ins Dict).",
        "sync_final_page": "✅ Letzte Seite für Sprache %s erreicht (insgesamt %d Seiten).",
        "sync_no_row_id": "Konnte keine letzte row_id ermitteln auf Seite %d, pausiere Sync für %s.",
        "sync_safety_limit": "⚠️ Sicherheitsgrenze (100 Seiten) für Sprache %s erreicht.",
        "sync_net_err": "Netzwerkfehler (%s): %s",
        "sync_start": "━━━ Starte Full-Sync von XIVAPI v2 ━━━",
        "sync_lang_start": "📥 Lade Daten für Sprache: %s",
        "sync_complete": "━━━ Vollständiger Scan abgeschlossen: (%d Einträge gespeichert) ━━━",
        "sync_empty": "⚠️ Keine relevanten Inhalte gefunden oder V2 API lieferte keine Ergebnisse."
    },
    "fr": {
        "sync_status_err": "Statut XIVAPI v2 %d pour la Langue %s sur la Page %d",
        "sync_page_processed": "   Langue %s, Page %d: %d entrées traitées (%d entrées valides ajoutées).",
        "sync_final_page": "✅ Page finale atteinte pour la Langue %s (total %d pages).",
        "sync_no_row_id": "Impossible de déterminer le dernier row_id sur la page %d, pause de la synchro pour %s.",
        "sync_safety_limit": "⚠️ Limite de sécurité (100 pages) atteinte pour la Langue %s.",
        "sync_net_err": "Erreur Réseau (%s): %s",
        "sync_start": "━━━ Démarrage de la Sync Complète pour XIVAPI v2 ━━━",
        "sync_lang_start": "📥 Téléchargement des données pour la Langue: %s",
        "sync_complete": "━━━ Scan Complet Terminé: (%d entrées traitées/sauvegardées) ━━━",
        "sync_empty": "⚠️ Aucun contenu pertinent trouvé, ou l'API V2 n'a pas retourné de résultats."
    },
    "ja": {
        "sync_status_err": "XIVAPI v2 ステータス %d (言語 %s, ページ %d)",
        "sync_page_processed": "   言語 %s, ページ %d: %d 個のエントリを処理しました (%d 個の有効なエントリを追加)。",
        "sync_final_page": "✅ 言語 %s の最後のページに到達しました (合計 %d ページ)。",
        "sync_no_row_id": "ページ %d で最後の row_id が見つかりませんでした。%s の同期を一時停止します。",
        "sync_safety_limit": "⚠️ 言語 %s の安全制限 (100ページ) に達しました。",
        "sync_net_err": "ネットワークエラー (%s): %s",
        "sync_start": "━━━ XIVAPI v2 の完全同期を開始します ━━━",
        "sync_lang_start": "📥 データをダウンロード中 (言語: %s)",
        "sync_complete": "━━━ 完全スキャン完了: (%d 個のエントリを処理/保存しました) ━━━",
        "sync_empty": "⚠️ 関連するコンテンツが見つかりませんでした。または V2 API が結果を返しませんでした。"
    }
}

# we need to inject the new keys into sys_msg_block string
for lang in ["en", "de", "fr", "ja"]:
    to_inject = "\n"
    for k, v in new_keys[lang].items():
        v = v.replace('"', '\\"') # escape quotes
        to_inject += f'        "{k}": "{v}",\n'
    # Find the block for the language
    # '    "en": {\n'
    pattern = r'(\s*"' + lang + r'":\s*\{\n)'
    sys_msg_block = re.sub(pattern, r'\g<1>' + to_inject, sys_msg_block)

# Append to i18n.py
with open("i18n.py", "a", encoding="utf-8") as f:
    f.write("\n\n")
    f.write(sys_msg_block)

print("Moved SYS_MSG successfully!")
