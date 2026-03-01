"""
i18n.py – Internationalization (i18n) System
============================================
Bietet ein simples Lokalisierungs-System für Fat Cat Planner.
Lädt die Sprache für eine spezifizierte Guild und gibt den passenden
Textstring zurück (Fallback: Englisch).
"""

import db

# Globale Übersetzungs-Tabelle
# Struktur: { key: { 'en': str, 'de': str, 'fr': str, 'ja': str } }
TRANSLATIONS = {
    # ── Setup Wizard ──
    "setup_welcome": {
        "en": "Hello! I am Fat Cat Planner. Please select your preferred language to start the configuration.",
        "de": "Hallo! Ich bin Fat Cat Planner. Bitte wähle deine bevorzugte Sprache, um die Konfiguration zu starten.",
        "fr": "Bonjour! Je suis Fat Cat Planner. Veuillez sélectionner votre langue préférée pour commencer la configuration.",
        "ja": "こんにちは！ファットキャットプランナーです。設定を開始するには、お好みの言語を選択してください。"
    },
    "setup_lang_chosen": {
        "en": "Language set to **English**. Let's continue configuring your server.",
        "de": "Sprache auf **Deutsch** gesetzt. Lass uns mit der Konfiguration fortfahren.",
        "fr": "Langue définie sur **Français**. Continuons la configuration de votre serveur.",
        "ja": "言語を**日本語**に設定しました。サーバーの設定を続けましょう。"
    },
    "setup_select_channel": {
        "en": "Please select the text channel where events should be posted.",
        "de": "Bitte wähle den Textkanal aus, in dem die Events gepostet werden sollen.",
        "fr": "Veuillez sélectionner le salon textuel où les événements doivent être publiés.",
        "ja": "イベントが投稿されるテキストチャンネルを選択してください。"
    },
    "setup_channel_chosen": {
        "en": "Event channel set to {channel}. Now, please select your server's timezone.",
        "de": "Event-Kanal auf {channel} gesetzt. Bitte wähle nun die Zeitzone deines Servers.",
        "fr": "Salon des événements défini sur {channel}. Maintenant, veuillez sélectionner le fuseau horaire de votre serveur.",
        "ja": "イベントチャンネルを {channel} に設定しました。次に、サーバーのタイムゾーンを選択してください。"
    },
    "setup_timezone_chosen": {
        "en": "✅ Setup complete! Timezone set to **{timezone}**.\nYou can use `/fccreate` to create your first event.",
        "de": "✅ Setup abgeschlossen! Zeitzone auf **{timezone}** gesetzt.\nDu kannst nun `/fccreate` nutzen, um dein erstes Event zu erstellen.",
        "fr": "✅ Configuration terminée! Fuseau horaire défini sur **{timezone}**.\nVous pouvez utiliser `/fccreate` pour créer votre premier événement.",
        "ja": "✅ 設定が完了しました！タイムゾーンを **{timezone}** に設定しました。\n`/fccreate` を使用して最初のイベントを作成できます。"
    },
    "setup_required": {
        "en": "❌ Setup required! An admin must run `/fcsetup` first.",
        "de": "❌ Setup erforderlich! Ein Admin muss zuerst `/fcsetup` ausführen.",
        "fr": "❌ Configuration requise! Un administrateur doit d'abord exécuter `/fcsetup`.",
        "ja": "❌ 設定が必要です！管理者が最初に `/fcsetup` を実行する必要があります。"
    },

    # ── fccreate (DM Flow) ──
    "create_check_dms": {
        "en": "📬 I have sent you a **DM**! Create your event there.",
        "de": "📬 Ich habe dir eine **DM** geschickt! Erstelle dein Event dort.",
        "fr": "📬 Je vous ai envoyé un **MP**! Créez votre événement là-bas.",
        "ja": "📬 **DM** を送信しました！そこでイベントを作成してください。"
    },
    "create_no_dms": {
        "en": "❌ I cannot send you a DM! Please enable direct messages from server members.",
        "de": "❌ Ich kann dir keine DM senden! Bitte aktiviere DMs von Server-Mitgliedern.",
        "fr": "❌ Je ne peux pas vous envoyer de MP! Veuillez activer les messages directs des membres du serveur.",
        "ja": "❌ DMを送信できません！サーバーメンバーからのダイレクトメッセージを有効にしてください。"
    },
    "create_no_results": {
        "en": "❌ No results found. Please choose **Manual Input**.",
        "de": "❌ Keine Ergebnisse gefunden. Bitte wähle **Manuelle Eingabe**.",
        "fr": "❌ Aucun résultat. Veuillez choisir **Saisie manuelle**.",
        "ja": "❌ 結果が見つかりません。**手動入力** を選択してください。",
    },
    "create_manual": {
        "en": "Manual / Not in list",
        "de": "Manuell / Nicht in Liste",
        "fr": "Manuel / Pas dans la liste",
        "ja": "手動 / リストにない",
    },
    "create_placeholder": {
        "en": "Select the content...",
        "de": "Wähle den Inhalt aus...",
        "fr": "Sélectionnez le contenu...",
        "ja": "コンテンツを選択...",
    },
    "create_found": {
        "en": "✨ **{count} results found.** Select the content:",
        "de": "✨ **{count} Ergebnisse gefunden.** Wähle den Inhalt aus:",
        "fr": "✨ **{count} résultats trouvés.** Sélectionnez le contenu :",
        "ja": "✨ **{count}件の結果が見つかりました。**コンテンツを選択してください：",
    },
    "create_select_duty": {
        "en": "Please select a duty (or click 'Manual Input').\n*Type to search.*",
        "de": "Bitte wähle den Inhalt aus (oder klicke auf 'Manuelle Eingabe').\n*Tippen zum Suchen.*",
        "fr": "Veuillez sélectionner une mission (ou cliquez sur 'Saisie manuelle').\n*Tapez pour rechercher.*",
        "ja": "コンテンツを選択してください（または「手動入力」をクリック）。\n*入力して検索します。*"
    },
    "create_btn_manual": {
        "en": "Manual Input",
        "de": "Manuelle Eingabe",
        "fr": "Saisie manuelle",
        "ja": "手動入力"
    },
    "create_prompt_name": {
        "en": "Enter a custom name for your event:",
        "de": "Gib einen Namen für das Event ein:",
        "fr": "Entrez un nom personnalisé pour votre événement:",
        "ja": "イベントのカスタム名を入力してください："
    },
    "create_prompt_size": {
        "en": "Please select the group size:",
        "de": "Bitte wähle die Gruppengröße:",
        "fr": "Veuillez sélectionner la taille du groupe:",
        "ja": "グループの人数を選択してください："
    },
    "create_size_4": { "en": "4 Players (Light Party)", "de": "4 Spieler", "fr": "4 Joueurs", "ja": "4人 (ライトパーティ)" },
    "create_size_8": { "en": "8 Players (Full Party)", "de": "8 Spieler", "fr": "8 Joueurs", "ja": "8人 (フルパーティ)" },
    "create_size_24": { "en": "24 Players (Alliance)", "de": "24 Spieler", "fr": "24 Joueurs", "ja": "24人 (アライアンス)" },
    
    "create_prompt_time": {
        "en": "When should the event start?",
        "de": "Wann soll das Event starten?",
        "fr": "Quand l'événement doit-il commencer?",
        "ja": "イベントはいつ開始しますか？"
    },
    "create_prompt_time_hint": {
        "en": "Enter time (e.g. `18:00`, `02.21. 18:00` or `02/21/26 18:00`).",
        "de": "Gib die Zeit ein (z.B. `18:00`, `21.02. 18:00` oder `21/02/26 18:00`).",
        "fr": "Entrez l'heure (ex. `18:00`, `21.02. 18:00` ou `21/02/26 18:00`).",
        "ja": "時間を入力してください（例：`18:00`、`21.02. 18:00` または `21/02/26 18:00`）。"
    },
    "create_prompt_timezone_type": {
        "en": "Please choose the timezone context for your entered time:",
        "de": "Bitte wähle die Zeitzone für deine Eingabe:",
        "fr": "Veuillez choisir le contexte de fuseau horaire pour votre heure :",
        "ja": "入力した時間のタイムゾーンコンテキストを選択してください："
    },
    "create_tz_info_title": {
        "en": "🕒 Timezone Context",
        "de": "🕒 Zeitzonen-Kontext",
        "fr": "🕒 Contexte du fuseau horaire",
        "ja": "🕒 タイムゾーンコンテキスト"
    },
    "create_tz_info_server": { "en": "⚔️ FFXIV Server Time", "de": "⚔️ FFXIV Server Time", "fr": "⚔️ Heure Serveur FFXIV", "ja": "⚔️ FFXIV サーバー時間" },
    "create_tz_info_guild": { "en": "🐱 Event (Guild) Time", "de": "🐱 Event (Guild) Time", "fr": "🐱 Heure (Guilde)", "ja": "🐱 イベント (ギルド) 時間" },
    "create_tz_info_local": { "en": "💻 Your Local Time", "de": "💻 Deine lokale Zeit", "fr": "💻 Votre heure locale", "ja": "💻 あなたのローカル時間" },
    "create_tz_info_hint": {
        "en": "Note: If you do not use Server Time and your local time differs from the Event Time, you must adjust your input to match the Event Time.",
        "de": "Hinweis: Wenn du nicht die Serverzeit nutzt und deine lokale Zeit von der Event-Zeit abweicht, musst du die Eingabe an die Event-Zeit anpassen.",
        "fr": "Remarque : Si vous n'utilisez pas l'heure du serveur et que votre heure locale diffère de l'heure de l'événement, vous devez ajuster votre saisie pour correspondre à l'heure de l'événement.",
        "ja": "注意：サーバー時間を使用せず、ローカル時間がイベント時間と異なる場合は、入力内容をイベント時間に合わせて調整する必要があります。"
    },
    "create_tz_type_local": { "en": "Event (Guild) Time", "de": "Event (Guild) Time", "fr": "Heure (Guilde)", "ja": "イベント (ギルド) 時間" },
    "create_tz_type_server": { "en": "FFXIV Server Time", "de": "FFXIV Server Time", "fr": "Heure Serveur FFXIV", "ja": "FFXIV サーバー時間" },
    "embed_time_local": { "en": "(Guild Time)", "de": "(Guild Time)", "fr": "(Heure Guilde)", "ja": "(ギルド時間)" },
    "embed_time_server": { "en": "(FFXIV Server Time)", "de": "(FFXIV Server Time)", "fr": "(Heure Serveur FFXIV)", "ja": "(FFXIVサーバー時間)" },
    "embed_time_local_label": { "en": "Local Time", "de": "Lokale Zeit", "fr": "Heure Locale", "ja": "ローカル時間" },
    "create_time_confirm": {
        "en": "Detected: **{time_str}**. Is this correct?",
        "de": "Erkannt: **{time_str}**. Korrekt?",
        "fr": "Reconnu: **{time_str}**. Est-ce correct?",
        "ja": "検出されました: **{time_str}**. よろしいですか？"
    },
    "create_time_past": {
        "en": "This date is in the past. Please enter a future time.",
        "de": "Dieses Datum liegt in der Vergangenheit. Bitte gib eine zukünftige Zeit an.",
        "fr": "Cette date est dans le passé. Veuillez entrer une heure future.",
        "ja": "この日時は過去のものです。未来の時間を入力してください。"
    },
    "create_time_past_abort": {
        "en": "Events cannot be scheduled in the past! Please restart the process using `/fccreate` in the designated channel.",
        "de": "Events können nicht in der Vergangenheit liegen! Bitte starte den Prozess mit `/fccreate` im vorgesehenen Kanal neu.",
        "fr": "Les événements ne peuvent pas être programmés dans le passé ! Veuillez recommencer le processus en utilisant `/fccreate` dans le canal prévu.",
        "ja": "過去の日時でイベントを予定することはできません！指定されたチャンネルで `/fccreate` を使用してプロセスをやり直してください。"
    },
    "create_time_abort": {
        "en": "Process aborted. Please restart event creation in the event channel using `/fccreate`.",
        "de": "Vorgang abgebrochen. Bitte starte die Event-Erstellung im Event-Kanal mit `/fccreate` erneut.",
        "fr": "Processus annulé. Veuillez recommencer la création de l'événement dans le canal d'événement avec `/fccreate`.",
        "ja": "処理が中断されました。イベントチャンネルで `/fccreate` を使ってイベント作成をやり直してください。"
    },
    "event_reminder_dm": {
        "en": "🔔 Reminder: The event **{event_name}** starts in 10 minutes! Get ready.",
        "de": "🔔 Erinnerung: Das Event **{event_name}** startet in 10 Minuten! Mach dich bereit.",
        "fr": "🔔 Rappel: L'événement **{event_name}** commence dans 10 minutes! Préparez-vous.",
        "ja": "🔔 リマインダー：イベント **{event_name}** が10分後に始まります！ 準備してください。"
    },
    "create_time_error_hint": {
        "en": "I couldn't read the time. Try this: {current_time_example}",
        "de": "Ich konnte die Zeit nicht lesen. Versuche es so: {current_time_example}",
        "fr": "Je n'ai pas pu lire l'heure. Essayez ceci : {current_time_example}",
        "ja": "時間を認識できませんでした。次のように入力してみてください：{current_time_example}"
    },
    "create_dm_error": {
        "en": "A technical error occurred. Please restart the process in the channel using `/fccreate`.",
        "de": "Ein technischer Fehler ist aufgetreten. Bitte starte den Vorgang im Kanal mit `/fccreate` neu.",
        "fr": "Une erreur technique s'est produite. Veuillez recommencer le processus dans le canal avec `/fccreate`.",
        "ja": "技術的なエラーが発生しました。チャンネルで `/fccreate` を使ってプロセスを再開してください。"
    },
    "create_invalid_time": {
        "en": "❌ Invalid time format! Please try again.",
        "de": "❌ Ungültiges Zeitformat! Bitte versuche es erneut.",
        "fr": "❌ Format d'heure invalide! Veuillez réessayer.",
        "ja": "❌ 無効な時刻形式です！もう一度お試しください。"
    },
    "create_prompt_unique": {
        "en": "Should duplicate jobs be prohibited? (e.g. no 2 White Mages)",
        "de": "Sollen doppelte Jobs verboten sein? (z.B. keine 2 Weißmagier)",
        "fr": "Les jobs en double doivent-ils être interdits? (ex. pas 2 Mages Blancs)",
        "ja": "重複ジョブを禁止しますか？（例：白魔道士2人は不可）"
    },
    "create_prompt_duration": {
        "en": "How long will the event last? Type the duration in hours (e.g. `2` or `1.5`), or press the button for open end.",
        "de": "Wie lange soll das Event gehen? Tippe die Dauer in Stunden ein (z.B. `2` oder `1.5`), oder klicke auf den Button für ein offenes Ende.",
        "fr": "Combien de temps durera l'événement? Tapez la durée en heures (ex. `2` ou `1.5`), ou appuyez sur le bouton pour fin ouverte.",
        "ja": "イベントは何時間ですか？時間を入力してください（例：`2` または `1.5`）、またはボタンを押して終了未定にしてください。"
    },
    "create_duration_1h": { "en": "1 hour", "de": "1 Stunde", "fr": "1 heure", "ja": "1時間" },
    "create_duration_1_5h": { "en": "1.5 hours", "de": "1,5 Stunden", "fr": "1,5 heures", "ja": "1.5時間" },
    "create_duration_2h": { "en": "2 hours", "de": "2 Stunden", "fr": "2 heures", "ja": "2時間" },
    "create_duration_3h": { "en": "3 hours", "de": "3 Stunden", "fr": "3 heures", "ja": "3時間" },
    "create_duration_open": { "en": "Open end", "de": "Offenes Ende", "fr": "Fin ouverte", "ja": "終了未定" },
    "create_prompt_freetext": {
        "en": "Would you like to leave a note for participants? (e.g. *Don't forget buff food!*)\nType your message or press **Skip**.",
        "de": "Möchtest du den Teilnehmern noch etwas mitteilen? (z.B. *Bufffood nicht vergessen!*)\nSchreibe deine Nachricht oder klicke **Überspringen**.",
        "fr": "Souhaitez-vous laisser un message aux participants? (ex. *N'oubliez pas la nourriture!*)\nÉcrivez votre message ou appuyez sur **Passer**.",
        "ja": "参加者へのメモはありますか？（例：*バフフードを忘れずに！*）\nメッセージを入力するか、**スキップ**を押してください。"
    },
    "create_btn_skip": { "en": "Skip", "de": "Überspringen", "fr": "Passer", "ja": "スキップ" },
    "create_freetext_saved": {
        "en": "✅ Note saved!",
        "de": "✅ Hinweis gespeichert!",
        "fr": "✅ Note enregistrée!",
        "ja": "✅ メモを保存しました！"
    },
    "embed_field_duration": { "en": "Duration", "de": "Dauer", "fr": "Durée", "ja": "所要時間" },
    "embed_field_freetext": { "en": "📝 Note", "de": "📝 Hinweis", "fr": "📝 Note", "ja": "📝 メモ" },
    "embed_time_from_to": { "en": "From / To", "de": "Von / Bis", "fr": "De / À", "ja": "開始 / 終了" },
    "create_btn_yes": { "en": "Yes", "de": "Ja", "fr": "Oui", "ja": "はい" },
    "create_btn_no": { "en": "No", "de": "Nein", "fr": "Non", "ja": "いいえ" },
    "create_success": {
        "en": "✅ Your event has been successfully posted in {channel}!",
        "de": "✅ Dein Event wurde erfolgreich in {channel} gepostet!",
        "fr": "✅ Votre événement a été publié avec succès dans {channel}!",
        "ja": "✅ イベントが {channel} に正常に投稿されました！"
    },
    "log_event_created": {
        "en": "🆕 New event created: **{event_name}** by **{user_name}** for **{date_time}**.",
        "de": "🆕 Neues Event erstellt: **{event_name}** von **{user_name}** für den **{date_time}**.",
        "fr": "🆕 Nouvel événement créé: **{event_name}** par **{user_name}** pour le **{date_time}**.",
        "ja": "🆕 新しいイベントが作成されました：**{event_name}** （作成者：**{user_name}**、日時：**{date_time}**）"
    },
    "log_event_auto_cleaned": {
        "en": "🧹 Event **{event_name}** (ID: {event_id}) was automatically removed after 8h.",
        "de": "🧹 Event **{event_name}** (ID: {event_id}) wurde nach 8h automatisch entfernt.",
        "fr": "🧹 L'événement **{event_name}** (ID: {event_id}) a été automatiquement supprimé après 8h.",
        "ja": "🧹 イベント **{event_name}** (ID: {event_id}) は8時間経過後に自動削除されました。"
    },
    
    # ── Embed & Buttons ──
    "embed_field_time": { "en": "Time", "de": "Zeit", "fr": "Heure", "ja": "時間" },
    "embed_field_players": { "en": "Players", "de": "Spieler", "fr": "Joueurs", "ja": "プレイヤー" },
    "embed_field_unique": { "en": "Unique Jobs", "de": "Unique Jobs", "fr": "Jobs Uniques", "ja": "重複ジョブ禁止" },
    "embed_btn_signup": { "en": "Sign up / Edit", "de": "Anmelden / Ändern", "fr": "S'inscrire / Modifier", "ja": "参加 / 変更" },
    "embed_btn_leave": { "en": "Leave", "de": "Abmelden", "fr": "Se désinscrire", "ja": "辞退" },
    "embed_btn_delete": { "en": "Delete Event", "de": "Event löschen", "fr": "Supprimer l'événement", "ja": "イベントを削除" },

    # ── RSVP Buttons & Embed ──
    "embed_btn_accept": { "en": "Accept", "de": "Zusage", "fr": "Accepter", "ja": "参加" },
    "embed_btn_tentative": { "en": "Tentative", "de": "Vielleicht", "fr": "Peut-être", "ja": "未定" },
    "embed_btn_decline": { "en": "Decline", "de": "Absage", "fr": "Décliner", "ja": "辞退" },
    "embed_field_tentative": { "en": "⚖️ Tentative ({count})", "de": "⚖️ Vielleicht ({count})", "fr": "⚖️ Peut-être ({count})", "ja": "⚖️ 未定 ({count})" },
    "embed_field_declined": { "en": "🚫 Declined ({count})", "de": "🚫 Absagen ({count})", "fr": "🚫 Déclinés ({count})", "ja": "🚫 辞退 ({count})" },
    "signup_declined_success": { "en": "🚫 You have declined the event.", "de": "🚫 Du hast das Event abgesagt.", "fr": "🚫 Vous avez décliné l'événement.", "ja": "🚫 イベントを辞退しました。" },
    "signup_tentative_success": { "en": "⚖️ Registered as tentative – {job_name}!", "de": "⚖️ Als Vielleicht angemeldet – {job_name}!", "fr": "⚖️ Inscrit comme peut-être – {job_name} !", "ja": "⚖️ 未定として登録 – {job_name}！" },

    # ── Timezone Status & Date Formats ──
    "tz_status_title": { "en": "🌐 Timezone Overview", "de": "🌐 Zeitzonen-Übersicht", "fr": "🌐 Aperçu du fuseau horaire", "ja": "🌐 タイムゾーンの概要" },
    "tz_status_sys": { "en": "System Time (Bot Server)", "de": "Systemzeit (Bot-Server)", "fr": "Heure du système (Serveur Bot)", "ja": "システム時間 (ボットサーバー)" },
    "tz_status_server": { "en": "Event Time (Discord Server)", "de": "Event-Zeit (Discord-Server)", "fr": "Heure de l'événement (Serveur Discord)", "ja": "イベント時間 (Discordサーバー)" },
    "tz_status_ping": { "en": "Next Background Check", "de": "Nächster Background-Check", "fr": "Prochaine vérification", "ja": "次回のバックグラウンドチェック" },
    "tz_status_req": { "en": "Requested by", "de": "Angefordert von", "fr": "Demandé par", "ja": "リクエスト元" },
    "tz_status_dst_active": { "en": "Daylight Saving Time active", "de": "Sommerzeit aktiv", "fr": "Heure d'été active", "ja": "夏時間有効" },
    "tz_status_dst_inactive": { "en": "Standard Time active", "de": "Normalzeit aktiv", "fr": "Heure standard active", "ja": "標準時有効" },
    "tz_status_no_event": { "en": "No active event on this server.", "de": "Kein aktives Event auf diesem Server.", "fr": "Aucun événement actif", "ja": "このサーバーにアクティブなイベントはありません。" },
    "date_format_full": { "en": "%m/%d/%Y %I:%M:%S %p %Z", "de": "%d.%m.%Y %H:%M:%S %Z", "fr": "%d/%m/%Y %H:%M:%S %Z", "ja": "%Y年%m月%d日 %H:%M:%S %Z" },

    # ── Embed Footer ──
    "embed_footer_creator": {
        "en": "Event ID: {event_id} | Created by: {creator}",
        "de": "Event-ID: {event_id} | Erstellt von: {creator}",
        "fr": "ID Événement: {event_id} | Créé par: {creator}",
        "ja": "イベントID: {event_id} | 作成者: {creator}"
    },
    "embed_unknown_creator": { "en": "Unknown", "de": "Unbekannt", "fr": "Inconnu", "ja": "不明" },

    # ── Select Prompts ──
    "prompt_choose_role": { "en": "Select your role...", "de": "Wähle deine Rolle...", "fr": "Choisissez votre rôle...", "ja": "ロールを選択..." },
    "prompt_available_jobs": { "en": "{count} available jobs", "de": "{count} verfügbare Jobs", "fr": "{count} jobs disponibles", "ja": "利用可能なジョブ {count}個" },
    "prompt_choose_job": { "en": "Select your job...", "de": "Wähle deinen Job...", "fr": "Choisissez votre job...", "ja": "ジョブを選択..." },
    "prompt_job_taken": { "en": "❌ Already taken", "de": "❌ Bereits belegt", "fr": "❌ Déjà pris", "ja": "❌ すでに使用中" },
    "prompt_job_available": { "en": "✅ Available", "de": "✅ Verfügbar", "fr": "✅ Disponible", "ja": "✅ 利用可能" },
    "prompt_no_jobs": { "en": "No jobs available", "de": "Keine Jobs verfügbar", "fr": "Aucun job disponible", "ja": "ジョブがありません" },

    # ── Roles ──
    "role_tank": { "en": "Tank", "de": "Verteidiger", "fr": "Tank", "ja": "タンク" },
    "role_healer": { "en": "Healer", "de": "Heiler", "fr": "Soigneur", "ja": "ヒーラー" },
    "role_dps": { "en": "DPS", "de": "Angreifer", "fr": "DPS", "ja": "DPS" },
    "role_allrounder": { "en": "Allrounder", "de": "Allrounder", "fr": "Touche-à-tout", "ja": "オールラウンダー" },

    # ── Jobs ──
    "job_Paladin (PLD)": { "en": "Paladin (PLD)", "de": "Paladin (PLD)", "fr": "Paladin (PLD)", "ja": "ナイト (PLD)" },
    "job_Warrior (WAR)": { "en": "Warrior (WAR)", "de": "Krieger (WAR)", "fr": "Guerrier (WAR)", "ja": "戦士 (WAR)" },
    "job_Dark Knight (DRK)": { "en": "Dark Knight (DRK)", "de": "Dunkelritter (DRK)", "fr": "Chevalier noir (DRK)", "ja": "暗黒騎士 (DRK)" },
    "job_Gunbreaker (GNB)": { "en": "Gunbreaker (GNB)", "de": "Revolverklinge (GNB)", "fr": "Pistosabreur (GNB)", "ja": "ガンブレイカー (GNB)" },
    
    "job_White Mage (WHM)": { "en": "White Mage (WHM)", "de": "Weißmagier (WHM)", "fr": "Mage blanc (WHM)", "ja": "白魔道士 (WHM)" },
    "job_Scholar (SCH)": { "en": "Scholar (SCH)", "de": "Gelehrter (SCH)", "fr": "Érudit (SCH)", "ja": "学者 (SCH)" },
    "job_Astrologian (AST)": { "en": "Astrologian (AST)", "de": "Astrologe (AST)", "fr": "Astromancien (AST)", "ja": "占星術師 (AST)" },
    "job_Sage (SGE)": { "en": "Sage (SGE)", "de": "Weiser (SGE)", "fr": "Sage (SGE)", "ja": "賢者 (SGE)" },
    
    "job_Monk (MNK)": { "en": "Monk (MNK)", "de": "Mönch (MNK)", "fr": "Moine (MNK)", "ja": "モンク (MNK)" },
    "job_Dragoon (DRG)": { "en": "Dragoon (DRG)", "de": "Dragoon (DRG)", "fr": "Chevalier dragon (DRG)", "ja": "竜騎士 (DRG)" },
    "job_Ninja (NIN)": { "en": "Ninja (NIN)", "de": "Ninja (NIN)", "fr": "Ninja (NIN)", "ja": "忍者 (NIN)" },
    "job_Samurai (SAM)": { "en": "Samurai (SAM)", "de": "Samurai (SAM)", "fr": "Samouraï (SAM)", "ja": "侍 (SAM)" },
    "job_Reaper (RPR)": { "en": "Reaper (RPR)", "de": "Schnitter (RPR)", "fr": "Faucheur (RPR)", "ja": "リーパー (RPR)" },
    "job_Viper (VPR)": { "en": "Viper (VPR)", "de": "Viper (VPR)", "fr": "Rôdeur vipère (VPR)", "ja": "ヴァイパー (VPR)" },
    
    "job_Bard (BRD)": { "en": "Bard (BRD)", "de": "Barde (BRD)", "fr": "Barde (BRD)", "ja": "吟遊詩人 (BRD)" },
    "job_Machinist (MCH)": { "en": "Machinist (MCH)", "de": "Maschinist (MCH)", "fr": "Machiniste (MCH)", "ja": "機工士 (MCH)" },
    "job_Dancer (DNC)": { "en": "Dancer (DNC)", "de": "Tänzer (DNC)", "fr": "Danseur (DNC)", "ja": "踊り子 (DNC)" },
    
    "job_Black Mage (BLM)": { "en": "Black Mage (BLM)", "de": "Schwarzmagier (BLM)", "fr": "Mage noir (BLM)", "ja": "黒魔道士 (BLM)" },
    "job_Summoner (SMN)": { "en": "Summoner (SMN)", "de": "Beschwörer (SMN)", "fr": "Invocateur (SMN)", "ja": "召喚士 (SMN)" },
    "job_Red Mage (RDM)": { "en": "Red Mage (RDM)", "de": "Rotmagier (RDM)", "fr": "Mage rouge (RDM)", "ja": "赤魔道士 (RDM)" },
    "job_Pictomancer (PCT)": { "en": "Pictomancer (PCT)", "de": "Piktomant (PCT)", "fr": "Pictomancien (PCT)", "ja": "ピクトマンサー (PCT)" },
    
    "job_Blue Mage (BLU)": { "en": "Blue Mage (BLU)", "de": "Blaumagier (BLU)", "fr": "Mage bleu (BLU)", "ja": "青魔道士 (BLU)" },
    "job_Allrounder": { "en": "Allrounder", "de": "Allrounder", "fr": "Touche-à-tout", "ja": "オールラウンダー" },

    # ── Admin Logs ──
    "log_status_signup": { "en": "✅ Signed Up", "de": "✅ Angemeldet", "fr": "✅ Inscrit", "ja": "✅ 参加登録済み" },
    "log_status_leave": { "en": "❌ Left", "de": "❌ Abgemeldet", "fr": "❌ Désinscrit", "ja": "❌ 辞退済み" },
    "log_title_signup": { "en": "📥 Signup: {content}", "de": "📥 Anmeldung: {content}", "fr": "📥 Inscription: {content}", "ja": "📥 参加登録: {content}" },
    "log_title_leave": { "en": "📤 Leave: {content}", "de": "📤 Abmeldung: {content}", "fr": "📤 Désinscription: {content}", "ja": "📤 辞退: {content}" },
    "log_title_tentative": { "en": "⚖️ Tentative: {content}", "de": "⚖️ Vielleicht: {content}", "fr": "⚖️ Peut-être: {content}", "ja": "⚖️ 未定: {content}" },
    "log_title_decline": { "en": "🚫 Declined: {content}", "de": "🚫 Absage: {content}", "fr": "🚫 Décliné: {content}", "ja": "🚫 辞退: {content}" },
    "log_status_tentative": { "en": "Tentative", "de": "Vielleicht", "fr": "Peut-être", "ja": "未定" },
    "log_status_decline": { "en": "Declined", "de": "Absage", "fr": "Décliné", "ja": "辞退" },
    "log_field_user": { "en": "👤 User", "de": "👤 User", "fr": "👤 Utilisateur", "ja": "👤 ユーザー" },
    "log_field_job": { "en": "🎮 Job", "de": "🎮 Job", "fr": "🎮 Job", "ja": "🎮 ジョブ" },
    "log_field_status": { "en": "🎮 Status", "de": "🎮 Status", "fr": "🎮 Statut", "ja": "🎮 ステータス" },
    "log_field_time": { "en": "📅 Scheduled Time", "de": "📅 Termin", "fr": "📅 Date prévue", "ja": "📅 予定日時" },
    "log_field_players": { "en": "👥 Attendees", "de": "👥 Teilnehmer", "fr": "👥 Participants", "ja": "👥 参加者" },

    # ── Command Descriptions (Discord native) ──
    "cmd_setup": {
        "en": "Starts the interactive setup wizard for language, channel, and timezone.",
        "de": "Startet den interaktiven Setup-Wizard für Sprache, Kanal und Zeitzone.",
        "fr": "Lance l'assistant de configuration interactif (langue, canal, fuseau horaire).",
        "ja": "言語、チャンネル、タイムゾーンの対話型セットアップウィザードを開始します。"
    },
    "cmd_facadminlog": {
        "en": "Enables/Disables event logging in the current channel.",
        "de": "Aktiviert/Deaktiviert das Event-Logging im aktuellen Kanal.",
        "fr": "Active/Désactive la journalisation des événements dans le canal actuel.",
        "ja": "現在のチャンネルでのイベントログを有効/無効にします。"
    },
    "cmd_fctimezone": {
        "en": "Manage timezones",
        "de": "Zeitzonen verwalten",
        "fr": "Gérer les fuseaux horaires",
        "ja": "タイムゾーンを管理する"
    },
    "cmd_fctimezone_set": {
        "en": "Change the timezone for events on the server",
        "de": "Zeitzone für Events auf dem Server ändern",
        "fr": "Modifier le fuseau horaire des événements sur le serveur",
        "ja": "サーバーのイベントのタイムゾーンを変更する"
    },
    "cmd_fctimezone_status": {
        "en": "When is the next background check scheduled?",
        "de": "Wann findet der nächste Background-Check statt?",
        "fr": "Quand aura lieu la prochaine vérification en arrière-plan?",
        "ja": "次回のバックグラウンドチェックはいつですか？"
    },
    "cmd_facadmin": {
        "en": "Bot Administration",
        "de": "Bot Administration",
        "fr": "Administration du bot",
        "ja": "ボット管理"
    },
    "cmd_facadmin_sync": {
        "en": "Forces a global synchronization of all slash commands",
        "de": "Erzwingt globale Synchronisation aller Slash-Commands",
        "fr": "Force une synchronisation globale de toutes les commandes slash",
        "ja": "スラッシュコマンドのグローバル同期を強制します"
    },
    "cmd_fccreate": {
        "en": "Create a new event (the flow runs via DM).",
        "de": "Erstelle ein neues Event (der Flow läuft per DM).",
        "fr": "Créer un nouvel événement (le flux se passe par MP).",
        "ja": "新しいイベントを作成します（フローはDMで実行されます）。"
    },
    "cmd_fctimezone_set_arg": {
        "en": "The new timezone (e.g. Europe/Berlin, UTC)",
        "de": "Die neue Zeitzone (z.B. Europe/Berlin, UTC)",
        "fr": "Le nouveau fuseau horaire (ex. Europe/Paris, UTC)",
        "ja": "新しいタイムゾーン（例：Asia/Tokyo, UTC）"
    },
    "cmd_fcdutyupdate": {
        "en": "Reloads all duties/contents from XIVAPI (may take several minutes).",
        "de": "Lädt alle Duties/Inhalte neu von XIVAPI (dauert evtl. mehrere Minuten).",
        "fr": "Recharge toutes les missions/données de XIVAPI (peut prendre plusieurs minutes).",
        "ja": "XIVAPI からすべてのコンテンツデータをリロードします（数分かかる場合があります）。"
    },

    # ── Notifications ──
    "notif_leave_success": {
        "en": "You have left the event.",
        "de": "Du hast dich vom Event abgemeldet.",
        "fr": "Vous avez quitté l'événement.",
        "ja": "イベントを辞退しました。"
    },
    "notif_no_permission": {
        "en": "🔒 You must be an Administrator or the Event Creator to do this.",
        "de": "🔒 Du musst Administrator oder der Event-Ersteller sein.",
        "fr": "🔒 Vous devez être Administrateur ou le Créateur de l'événement.",
        "ja": "🔒 これを行うには、管理者またはイベント作成者である必要があります。"
    },
    
    # ── Signup Validations ──
    "signup_role_full": {
        "en": "❌ Role '{role_name}' is already full!",
        "de": "❌ Die Rolle '{role_name}' ist bereits voll!",
        "fr": "❌ Le rôle '{role_name}' est déjà complet!",
        "ja": "❌ ロール「{role_name}」はすでに満員です！"
    },
    "signup_job_taken": {
        "en": "❌ Job {job_name} is already taken! (Unique Jobs enabled)",
        "de": "❌ Der Job {job_name} ist bereits belegt! (Unique Jobs aktiv)",
        "fr": "❌ Le job {job_name} est déjà pris! (Jobs Uniques activé)",
        "ja": "❌ ジョブ {job_name} はすでに使用されています！（重複ジョブ禁止）"
    },
    "signup_success": {
        "en": "✅ Registered as {job_name}!",
        "de": "✅ Angemeldet als {job_name}!",
        "fr": "✅ Inscrit en tant que {job_name}!",
        "ja": "✅ {job_name} として登録されました！"
    },
    "signup_allrounder_success": {
        "en": "✅ You have signed up as an Allrounder!",
        "de": "✅ Du hast dich als Allrounder angemeldet!",
        "fr": "✅ Vous vous êtes inscrit en tant que Touche-à-tout!",
        "ja": "✅ オールラウンダーとして登録しました！"
    },
    
    # ── New Strings (v0.1.0) ──
    "embed_field_content": { "en": "Content", "de": "Inhalt", "fr": "Contenu", "ja": "コンテンツ" },
    "embed_field_settings": { "en": "Settings", "de": "Einstellungen", "fr": "Paramètres", "ja": "設定" },
    "embed_no_signups": { "en": "*No signups yet*", "de": "*Noch keine Anmeldungen*", "fr": "*Pas encore d'inscrits*", "ja": "*まだ参加者がいません*" },
    "embed_field_participants": { "en": "Participants", "de": "Teilnehmer", "fr": "Participants", "ja": "参加者" },
    "msg_not_found": { "en": "❌ This event no longer exists.", "de": "❌ Dieses Event existiert nicht mehr.", "fr": "❌ Cet événement n'existe plus.", "ja": "❌ このイベントはもう存在しません。" },
    "msg_event_full": { "en": "❌ The event is already full!", "de": "❌ Das Event ist bereits voll!", "fr": "❌ L'événement est déjà complet!", "ja": "❌ イベントはすでに満員です！" },
    "msg_leave_success": { "en": "✅ You have been successfully removed.", "de": "✅ Du wurdest erfolgreich abgemeldet.", "fr": "✅ Vous avez été désinscrit avec succès.", "ja": "✅ 正常に辞退しました。" },
    "msg_not_signed_up": { "en": "ℹ️ You are not signed up for this event.", "de": "ℹ️ Du bist nicht für dieses Event angemeldet.", "fr": "ℹ️ Vous n'êtes pas inscrit à cet événement.", "ja": "ℹ️ このイベントには登録されていません。" },
    
    "cmd_server_only": { "en": "❌ This command can only be used on a server.", "de": "❌ Dieser Befehl kann nur auf einem Server verwendet werden.", "fr": "❌ Cette commande ne peut être utilisée que sur un serveur.", "ja": "❌ このコマンドはサーバー上でのみ使用できます。" },
    "create_manual_title": { "en": "✍️ **Manual Input**", "de": "✍️ **Manuelle Eingabe**", "fr": "✍️ **Saisie manuelle**", "ja": "✍️ **手動入力**" },
    "create_timeout": { "en": "⏰ Timeout – Event creation cancelled.", "de": "⏰ Zeitüberschreitung – Event-Erstellung abgebrochen.", "fr": "⏰ Délai d'attente dépassé – Création annulée.", "ja": "⏰ タイムアウト – イベント作成がキャンセルされました。" },
    "create_no_name": { "en": "❌ No name entered – Cancelled.", "de": "❌ Kein Name eingegeben – Abbruch.", "fr": "❌ Aucun nom entré – Annulé.", "ja": "❌ 名前が入力されていません – キャンセルしました。" },
    "create_no_selection": { "en": "⏰ No selection made – Event creation cancelled.", "de": "⏰ Keine Auswahl – Event-Erstellung abgebrochen.", "fr": "⏰ Aucune sélection – Création annulée.", "ja": "⏰ 選択されていません – イベント作成がキャンセルされました。" },
    "create_title": { "en": "🐱 **Fat Cat Planner – Event**", "de": "🐱 **Fat Cat Planner – Event**", "fr": "🐱 **Fat Cat Planner – Événement**", "ja": "🐱 **ファットキャットプランナー – イベント**" },
    "create_duty_not_found": { "en": "❌ Event not found – Cancelled.", "de": "❌ Event nicht gefunden – Abbruch.", "fr": "❌ Événement introuvable – Annulé.", "ja": "❌ イベントが見つかりません – キャンセルしました。" },
    "create_group_size": { "en": "Group size", "de": "Gruppengröße", "fr": "Taille du groupe", "ja": "グループサイズ" },
    "create_unique_timeout": { "en": "⏰ No selection – Duplicates will be allowed.", "de": "⏰ Keine Auswahl – Duplikate werden erlaubt.", "fr": "⏰ Aucune sélection – Les doublons seront autorisés.", "ja": "⏰ 選択なし – 重複が許可されます。" },
    "create_no_setup_channel": { "en": "❌ This server has no setup channel configured yet.", "de": "❌ Dieser Server hat noch keinen Setup-Kanal konfiguriert.", "fr": "❌ Ce serveur n'a pas encore configuré de canal de configuration.", "ja": "❌ このサーバーにはまだ設定チャンネルがありません。" },
    "create_no_post_permission": { "en": "❌ I don't have permission to post in the event channel.", "de": "❌ Ich habe keine Berechtigung, im Event-Channel zu posten.", "fr": "❌ Je n'ai pas la permission de publier dans le canal d'événement.", "ja": "❌ イベントチャンネルに投稿する権限がありません。" },
    
    "reminder_title": { "en": "⏰ Event Reminder!", "de": "⏰ Event-Erinnerung!", "fr": "⏰ Rappel d'événement!", "ja": "⏰ イベントリマインダー！" },
    "reminder_desc": { 
        "en": "**{event_name}** starts in less than **10 minutes**!\n\n📅 Scheduled: `{event_time}`\n👥 Participants: {signups}/{max_players}",
        "de": "**{event_name}** startet in weniger als **10 Minuten**!\n\n📅 Geplant: `{event_time}`\n👥 Teilnehmer: {signups}/{max_players}",
        "fr": "**{event_name}** commence dans moins de **10 minutes**!\n\n📅 Prévu: `{event_time}`\n👥 Participants: {signups}/{max_players}",
        "ja": "**{event_name}** が **10分未満** で開始します！\n\n📅 予定: `{event_time}`\n👥 参加者: {signups}/{max_players}"
    },
    
    "admin_invalid_tz": { 
        "en": "❌ Invalid timezone: **{timezone}**\nUse the autocomplete or enter a valid IANA timezone.",
        "de": "❌ Ungültige Zeitzone: **{timezone}**\nNutze das Autocomplete oder gib eine gültige IANA-Zeitzone ein.",
        "fr": "❌ Fuseau horaire invalide: **{timezone}**\nUtilisez l'autocomplétion ou entrez un fuseau horaire IANA valide.",
        "ja": "❌ 無効なタイムゾーン: **{timezone}**\nオートコンプリートを使用するか、有効なIANAタイムゾーンを入力してください。"
    },
    "admin_tz_updated_title": { "en": "🌐 Timezone updated", "de": "🌐 Zeitzone aktualisiert", "fr": "🌐 Fuseau horaire mis à jour", "ja": "🌐 タイムゾーン更新" },
    "admin_tz_updated_desc": {
        "en": "Events will now be scheduled in the timezone **{timezone}**.\nCurrent local time: {timestamp_str}",
        "de": "Events werden ab jetzt in der Zeitzone **{timezone}** geplant.\nAktuelle lokale Zeit: {timestamp_str}",
        "fr": "Les événements seront désormais planifiés dans le fuseau horaire **{timezone}**.\nHeure locale actuelle: {timestamp_str}",
        "ja": "イベントは今後 **{timezone}** タイムゾーンで計画されます。\n現在のローカル時間: {timestamp_str}"
    },
    "admin_log_toggle_req": { "en": "❌ Please specify `on` or `off` for the toggle argument.", "de": "❌ Bitte gib `on` oder `off` für das Toggle-Argument an.", "fr": "❌ Veuillez spécifier `on` ou `off` pour l'argument.", "ja": "❌ トグル引数には `on` または `off` を指定してください。" },
    "admin_log_channel_req": { "en": "❌ Please specify a log channel: `/facadminlog on #channel`", "de": "❌ Bitte gib einen Log-Channel an: `/facadminlog on #channel`", "fr": "❌ Veuillez spécifier un canal de log: `/facadminlog on #channel`", "ja": "❌ ログチャンネルを指定してください: `/facadminlog on #channel`" },
    "admin_log_enabled_title": { "en": "✅ Logging enabled", "de": "✅ Logging aktiviert", "fr": "✅ Journalisation activée", "ja": "✅ ログ有効" },
    "admin_log_enabled_desc": { "en": "Log messages will be sent to {channel}.", "de": "Log-Nachrichten werden an {channel} gesendet.", "fr": "Les messages de log seront envoyés à {channel}.", "ja": "ログメッセージは {channel} に送信されます。" },
    "admin_log_disabled_title": { "en": "✅ Logging disabled", "de": "✅ Logging deaktiviert", "fr": "✅ Journalisation désactivée", "ja": "✅ ログ無効" },
    "admin_log_disabled_desc": { "en": "Event logging has been turned off.", "de": "Event-Logging wurde ausgeschaltet.", "fr": "La journalisation des événements a été désactivée.", "ja": "イベントログはオフになりました。" },
    "admin_update_start": { "en": "⏳ Content update from XIVAPI started in the background. This may take a few minutes.", "de": "⏳ Content-Update von XIVAPI wurde im Hintergrund gestartet. Dies kann einige Minuten dauern.", "fr": "⏳ La mise à jour du contenu via XIVAPI a démarré en arrière-plan. Cela peut prendre quelques minutes.", "ja": "⏳ XIVAPIからのコンテンツ更新がバックグラウンドで開始されました。数分かかる場合があります。" },
    "admin_sync_success": { "en": "✅ Successfully synchronized {count} command(s) globally.", "de": "✅ Erfolgreich {count} Command(s) global synchronisiert.", "fr": "✅ {count} commande(s) synchronisée(s) globalement avec succès.", "ja": "✅ {count} のコマンドをグローバルに同期しました。" },
    "admin_sync_error": { "en": "❌ Error during synchronization: {error}", "de": "❌ Fehler bei der Synchronisation: {error}", "fr": "❌ Erreur lors de la synchronisation: {error}", "ja": "❌ 同期中にエラーが発生しました: {error}" },
    "admin_cleanup_title": { "en": "🧹 Database cleaned", "de": "🧹 Datenbank bereinigt", "fr": "🧹 Base de données nettoyée", "ja": "🧹 データベースをクリーンアップしました" },
    "admin_cleanup_desc": { "en": "**{deleted_count}** old events and their signups have been deleted.", "de": "Es wurden **{deleted_count}** alte Events und deren Anmeldungen gelöscht.", "fr": "**{deleted_count}** anciens événements et leurs inscriptions ont été supprimés.", "ja": "**{deleted_count}** 個の古いイベントと参加登録が削除されました。" },
    "admin_cleanup_error": { "en": "❌ Error during cleanup: {error}", "de": "❌ Fehler bei der Bereinigung: {error}", "fr": "❌ Erreur lors du nettoyage: {error}", "ja": "❌ クリーンアップ中のエラー: {error}" },
    "admin_missing_perms": { "en": "🔒 You need **Administrator** permissions for this command.", "de": "🔒 Du brauchst **Administrator**-Berechtigungen für diesen Befehl.", "fr": "🔒 Vous avez besoin des permissions **Administrateur** pour cette commande.", "ja": "🔒 このコマンドには **管理者** 権限が必要です。" },
    "admin_error_generic": { "en": "❌ An error occurred: {error}", "de": "❌ Ein Fehler ist aufgetreten: {error}", "fr": "❌ Une erreur s'est produite: {error}", "ja": "❌ エラーが発生しました: {error}" },
    "msg_already_full_dm": { "en": "❌ The event is already full! Maximum participants reached.", "de": "❌ Das Event ist bereits voll! Maximale Teilnehmerzahl erreicht.", "fr": "❌ L'événement est déjà complet! Nombre maximum de participants atteint.", "ja": "❌ イベントはすでに満員です！最大参加人数に達しました。" },
    "prompt_choose_role_title": { "en": "🛡️ Choose your role...", "de": "🛡️ Wähle deine Rolle...", "fr": "🛡️ Choisissez votre rôle...", "ja": "🛡️ ロールを選択..." },
    "admin_debug_unknown": { "en": "_(Timezone '{tz_name}' unknown)_", "de": "_(Zeitzone '{tz_name}' unbekannt)_", "fr": "_(Fuseau horaire '{tz_name}' inconnu)_", "ja": "_(タイムゾーン '{tz_name}' 不明)_" },
    "cmd_admin_only": { "en": "🔒 This command is only available for administrators.", "de": "🔒 Dieser Befehl ist nur für Administratoren verfügbar.", "fr": "🔒 Cette commande est réservée aux administrateurs.", "ja": "🔒 このコマンドは管理者専用です。" },
    "user_lang_success": { "en": "Your preferred language has been set.", "de": "Deine bevorzugte Sprache wurde gesetzt.", "fr": "Votre langue préférée a été définie.", "ja": "言語設定が保存されました。" }
}

async def t(guild_id: int | None, key: str, user_id: int | None = None, **kwargs) -> str:
    """
    Holt den übersetzten String für den angegebenen 'key'.
    Priorität: User-Sprache > Server-Sprache > Englisch.
    """
    lang = "en"
    user_lang_found = False
    
    # 1. User-Präferenz prüfen (falls user_id übergeben wurde)
    if user_id:
        user_lang = await db.get_user_language(user_id)
        if user_lang:
            lang = user_lang
            user_lang_found = True
    
    # 2. Falls keine User-Präferenz gefunden, Server-Sprache prüfen
    if not user_lang_found and guild_id:
        guild_lang = await db.get_language(guild_id)
        if guild_lang:
            lang = guild_lang
        
    if lang not in ("en", "de", "fr", "ja"): # Safety Check
        lang = "en"

    # Hole Übersetzungsobjekt
    translation_obj = TRANSLATIONS.get(key)
    if not translation_obj:
        return f"[{key}]"  # Missing key marker für Debugging

    # Hole spezifische Sprache oder falle auf en zurück
    text = translation_obj.get(lang, translation_obj.get("en", f"[{key}]"))

    # Wenn Formatierungs-Argumente mitgegeben wurden
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text # Fallback falls Format-Keys nicht matchen
            
    return text


SYS_MSG = {
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
        "sync_empty": "⚠️ No relevant content found, or V2 API did not return results.",
        "setup_no_env": "❌ No .env file found! Starting Setup-Wizard...",
        "setup_lang": "Which language should the bot use by default? (Deutsch: de, English: en, Français: fr, 日本語: ja): ",
        "setup_token": "Please enter your Discord Bot Token (or press Enter for placeholder): ",
        "setup_owner": "Please enter the Discord User ID of the Owner (Important: Enable Developer Mode (User Settings -> Advanced) in Discord first! Tip: Profile picture bottom left -> Copy User ID): ",
        "setup_done": "✅ Configuration saved to .env file!",
        "token_missing": "❌ DISCORD_TOKEN not found!",
        "banner_sys": "System:",
        "banner_path": "Path:  ",
        "banner_version": "v0.1.0 (Initial Release)",
        "banner_load": "[INFO] Loading configuration...",
        "connected": "✅ Successfully connected to Discord!",
        "online": "🐱 Fat Cat Planner is online!",
        "bot_info": "   Bot:    %s (ID: %d)",
        "guild_info": "   Guilds: %d",
        "bot_info_print": "[INFO] Bot: {} | Guilds: {}",
        "sync_warn": "⚠️ on_ready called again. Skipping setup.",
        "sync_global": "🔄 Synchronizing Slash-Commands globally...",
        "sync_clear_err": "Could not clear Guild %s: %s",
        "sync_done": "✅ %d Slash-Commands globally synchronized.",
        "sync_err": "❌ Error syncing Slash-Commands: %s",
        "reg_views": "🔗 Registering persistent Views...",
        "reg_views_done": "✅ %d persistent Views registered.",
        "cache_empty": "📦 Content cache is empty. Starting automatic XIVAPI background sync...",
        "cache_empty_p": "[SYNC] New XIVAPI data is being loaded in the background...",
        "cache_full": "📦 Content cache has %d entries. Skipping initial sync.",
        "cache_full_p": "✅ XIVAPI data is up to date ({} entries).",
        "db_init": "📦 Initializing database...",
        "db_init_p": "[INFO] Initializing database...",
        "db_ready": "✅ Database ready.",
        "db_ready_p": "✅ Database ready.",
        "cogs_load": "[INFO] Loading modules (Cogs)...",
        "cog_done": "✅ Cog loaded: %s",
        "cog_err": "❌ Error loading %s: %s",
        "cog_err_p": "❌ Error loading {}: {}",
        "connect_p": "[INFO] Connecting to Discord...",
        "login_fail": "❌ Login failed! Check your DISCORD_TOKEN.",
        "login_fail_p": "❌ Login failed! Token invalid.",
        "http_err": "❌ Network error (HTTPException): %s",
        "http_err_p": "❌ Network error. Cannot connect to Discord.",
        "unexp_err": "❌ Unexpected error: %s",
        "unexp_err_p": "❌ Unexpected error starting the bot.",
        "sig_term": "Received signal %s. Shutting down bot safely...",
        "quit_prompt": "\nDo you really want to stop the bot? (y/n): ",
        "quit_user": "👋 Fat Cat Planner was stopped by the user.",
        "quit_user_p": "Bot stopped. See you soon!",
        "quit_already": "Bot process was already interrupted. Restart it!",
        "quit_bg": "👋 Fat Cat Planner was stopped."
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
        "sync_empty": "⚠️ Keine relevanten Inhalte gefunden oder V2 API lieferte keine Ergebnisse.",
        "setup_no_env": "❌ Keine .env Datei gefunden! Starte Setup-Wizard...",
        "setup_lang": "In welcher Sprache soll der Bot standardmäßig antworten? (Deutsch: de, English: en, Français: fr, 日本語: ja): ",
        "setup_token": "Bitte gib deinen Discord-Token ein (oder drücke Enter für Platzhalter): ",
        "setup_owner": "Bitte gib die Discord-Nutzer-ID des Owners ein (Wichtig: Zuerst Entwicklermodus (Benutzereinstellungen -> Erweitert) in Discord aktivieren! Tipp: Profilbild unten links -> Nutzer-ID kopieren): ",
        "setup_done": "✅ Konfiguration wurde in der .env Datei gespeichert!",
        "token_missing": "❌ DISCORD_TOKEN nicht gefunden!",
        "banner_sys": "System:",
        "banner_path": "Pfad:  ",
        "banner_version": "v0.1.0 (Erster Release)",
        "banner_load": "[INFO] Lade Konfiguration...",
        "connected": "✅ Erfolgreich zu Discord verbunden!",
        "online": "🐱 Fat Cat Planner ist online!",
        "bot_info": "   Bot:    %s (ID: %d)",
        "guild_info": "   Guilds: %d",
        "bot_info_print": "[INFO] Bot: {} | Gilden: {}",
        "sync_warn": "⚠️ on_ready wurde erneut aufgerufen. Überspringe Setup.",
        "sync_global": "🔄 Synchronisiere Slash-Commands global...",
        "sync_clear_err": "Konnte Guild %s nicht bereinigen: %s",
        "sync_done": "✅ %d Slash-Commands global synchronisiert.",
        "sync_err": "❌ Fehler beim Sync der Slash-Commands: %s",
        "reg_views": "🔗 Registriere persistent Views...",
        "reg_views_done": "✅ %d persistent Views registriert.",
        "cache_empty": "📦 Content-Cache ist leer. Starte automatischen XIVAPI Hintergrund-Sync...",
        "cache_empty_p": "[SYNC] Neue XIVAPI-Daten werden im Hintergrund geladen...",
        "cache_full": "📦 Content-Cache enthält %d Einträge. Überspringe initialen Sync.",
        "cache_full_p": "✅ XIVAPI-Daten aktuell ({} Einträge).",
        "db_init": "📦 Initialisiere Datenbank...",
        "db_init_p": "[INFO] Initialisiere Datenbank...",
        "db_ready": "✅ Datenbank bereit.",
        "db_ready_p": "✅ Datenbank bereit.",
        "cogs_load": "[INFO] Lade Module (Cogs)...",
        "cog_done": "✅ Cog geladen: %s",
        "cog_err": "❌ Fehler beim Laden von %s: %s",
        "cog_err_p": "❌ Fehler beim Laden von {}: {}",
        "connect_p": "[INFO] Verbinde zu Discord...",
        "login_fail": "❌ Login fehlgeschlagen! Überprüfe deinen DISCORD_TOKEN.",
        "login_fail_p": "❌ Login fehlgeschlagen! Token ungültig.",
        "http_err": "❌ Netzwerkfehler (HTTPException): %s",
        "http_err_p": "❌ Netzwerkfehler. Kann nicht mit Discord verbinden.",
        "unexp_err": "❌ Unerwarteter Fehler: %s",
        "unexp_err_p": "❌ Unerwarteter Fehler beim Starten des Bots.",
        "sig_term": "Signal %s empfangen. Beende Bot sauber...",
        "quit_prompt": "\nMöchtest du den Bot wirklich beenden? (j/n): ",
        "quit_user": "👋 Fat Cat Planner wurde durch Benutzer beendet.",
        "quit_user_p": "Bot beendet. Bis bald!",
        "quit_already": "Bot-Prozess wurde bereits unterbrochen. Starte ihn neu!",
        "quit_bg": "👋 Fat Cat Planner wurde gestoppt."
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
        "sync_empty": "⚠️ Aucun contenu pertinent trouvé, ou l'API V2 n'a pas retourné de résultats.",
        "setup_no_env": "❌ Aucun fichier .env trouvé ! Lancement de l'assistant...",
        "setup_lang": "Dans quelle langue le bot doit-il répondre par défaut ? (Deutsch: de, English: en, Français: fr, 日本語: ja): ",
        "setup_token": "Veuillez entrer votre Token Discord (ou Entrée pour ignorer): ",
        "setup_owner": "Veuillez entrer l'ID d'utilisateur Discord du propriétaire (Important: Activez d'abord le mode développeur (Paramètres utilisateur -> Avancés) ! Astuce: Photo de profil en bas à gauche -> Copier l'ID): ",
        "setup_done": "✅ Configuration sauvegardée dans le fichier .env !",
        "token_missing": "❌ DISCORD_TOKEN introuvable !",
        "banner_sys": "Système:",
        "banner_path": "Chemin: ",
        "banner_version": "v0.1.0 (Version Initiale)",
        "banner_load": "[INFO] Chargement de la configuration...",
        "connected": "✅ Connecté avec succès à Discord !",
        "online": "🐱 Fat Cat Planner est en ligne !",
        "bot_info": "   Bot:    %s (ID: %d)",
        "guild_info": "   Guildes: %d",
        "bot_info_print": "[INFO] Bot: {} | Guildes: {}",
        "sync_warn": "⚠️ on_ready appelé à nouveau. Configuration ignorée.",
        "sync_global": "🔄 Synchronisation globale des commandes slash...",
        "sync_clear_err": "Impossible de nettoyer la guilde %s: %s",
        "sync_done": "✅ %d Commandes slash synchronisées globalement.",
        "sync_err": "❌ Erreur lors de la synchronisation des commandes: %s",
        "reg_views": "🔗 Enregistrement des vues persistantes...",
        "reg_views_done": "✅ %d vues persistantes enregistrées.",
        "cache_empty": "📦 Le cache de contenu est vide. Démarrage de la synchronisation XIVAPI...",
        "cache_empty_p": "[SYNC] Nouvelles données XIVAPI chargées en arrière-plan...",
        "cache_full": "📦 Le cache de contenu contient %d entrées. Synchronisation initiale ignorée.",
        "cache_full_p": "✅ Les données XIVAPI sont à jour ({} entrées).",
        "db_init": "📦 Initialisation de la base de données...",
        "db_init_p": "[INFO] Initialisation de la base de données...",
        "db_ready": "✅ Base de données prête.",
        "db_ready_p": "✅ Base de données prête.",
        "cogs_load": "[INFO] Chargement des modules (Cogs)...",
        "cog_done": "✅ Cog chargé: %s",
        "cog_err": "❌ Erreur de chargement pour %s: %s",
        "cog_err_p": "❌ Erreur de chargement pour {}: {}",
        "connect_p": "[INFO] Connexion à Discord...",
        "login_fail": "❌ Échec de la connexion ! Vérifiez votre DISCORD_TOKEN.",
        "login_fail_p": "❌ Échec de la connexion ! Token invalide.",
        "http_err": "❌ Erreur réseau (HTTPException): %s",
        "http_err_p": "❌ Erreur réseau. Impossible de se connecter à Discord.",
        "unexp_err": "❌ Erreur inattendue: %s",
        "unexp_err_p": "❌ Erreur inattendue lors du démarrage du bot.",
        "sig_term": "Signal %s reçu. Arrêt sécurisé du bot...",
        "quit_prompt": "\nVoulez-vous vraiment arrêter le bot ? (o/n): ",
        "quit_user": "👋 Fat Cat Planner a été arrêté par l'utilisateur.",
        "quit_user_p": "Bot arrêté. À bientôt !",
        "quit_already": "Le processus du bot a déjà été interrompu. Redémarrez-le !",
        "quit_bg": "👋 Fat Cat Planner a été arrêté."
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
        "sync_empty": "⚠️ 関連するコンテンツが見つかりませんでした。または V2 API が結果を返しませんでした。",
        "setup_no_env": "❌ .envファイルが見つかりません！ セットアップウィザードを開始します...",
        "setup_lang": "ボットのデフォルト言語を何にしますか？ (Deutsch: de, English: en, Français: fr, 日本語: ja): ",
        "setup_token": "Discordボットトークンを入力してください (プレースホルダーの場合はEnter): ",
        "setup_owner": "オーナーのDiscordユーザーIDを入力してください (重要: 最初に開発者モード(ユーザー設定 -> 詳細設定)を有効にしてください！ヒント: 左下のプロフィール画像 -> ユーザーIDをコピー): ",
        "setup_done": "✅ 設定が.envファイルに保存されました！",
        "token_missing": "❌ DISCORD_TOKENが見つかりません！",
        "banner_sys": "システム:",
        "banner_path": "パス:  ",
        "banner_version": "v0.1.0 (初期リリース)",
        "banner_load": "[INFO] 設定を読み込んでいます...",
        "connected": "✅ Discordに正常に接続されました！",
        "online": "🐱 Fat Cat Plannerがオンラインです！",
        "bot_info": "   ボット:  %s (ID: %d)",
        "guild_info": "   ギルド:  %d",
        "bot_info_print": "[INFO] ボット: {} | ギルド: {}",
        "sync_warn": "⚠️ on_readyが再呼び出しされました。セットアップをスキップします。",
        "sync_global": "🔄 スラッシュコマンドをグローバルに同期中...",
        "sync_clear_err": "ギルド %s をクリアできませんでした: %s",
        "sync_done": "✅ %d 個のスラッシュコマンドをグローバルに同期しました。",
        "sync_err": "❌ スラッシュコマンドの同期に失敗しました: %s",
        "reg_views": "🔗 永続ビューを登録中...",
        "reg_views_done": "✅ %d 個の永続ビューを登録しました。",
        "cache_empty": "📦 コンテンツキャッシュが空です。XIVAPIバックグラウンド同期を開始します...",
        "cache_empty_p": "[SYNC] 新しいXIVAPIデータをバックグラウンドで読み込んでいます...",
        "cache_full": "📦 コンテンツキャッシュには %d 個のエントリがあります。初期同期をスキップします。",
        "cache_full_p": "✅ XIVAPIデータは最新です ({} エントリ)。",
        "db_init": "📦 データベースを初期化中...",
        "db_init_p": "[INFO] データベースを初期化中...",
        "db_ready": "✅ データベース準備完了。",
        "db_ready_p": "✅ データベース準備完了。",
        "cogs_load": "[INFO] モジュール(Cogs)を読み込んでいます...",
        "cog_done": "✅ Cog読み込み完了: %s",
        "cog_err": "❌ %s の読み込みエラー: %s",
        "cog_err_p": "❌ {} の読み込みエラー: {}",
        "connect_p": "[INFO] Discordに接続しています...",
        "login_fail": "❌ ログインに失敗しました！ DISCORD_TOKENを確認してください。",
        "login_fail_p": "❌ ログインに失敗しました！ トークンが無効です。",
        "http_err": "❌ ネットワークエラー (HTTPException): %s",
        "http_err_p": "❌ ネットワークエラー。Discordに接続できません。",
        "unexp_err": "❌ 予期しないエラー: %s",
        "unexp_err_p": "❌ ボットの起動中に予期しないエラーが発生しました。",
        "sig_term": "シグナル %s を受信しました。ボットを安全にシャットダウンします...",
        "quit_prompt": "\n本当にボットを停止しますか？ (y/n): ",
        "quit_user": "👋 Fat Cat Plannerはユーザーによって停止されました。",
        "quit_user_p": "ボットが停止しました。またね！",
        "quit_already": "ボットのプロセスはすでに中断されています。再起動してください！",
        "quit_bg": "👋 Fat Cat Plannerが停止しました。"
    }
}
