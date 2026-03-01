# 🐱 Fat Cat Planner — Changelog

[🇬🇧 English](#english) | [🇩🇪 Deutsch](#deutsch) | [🇫🇷 Français](#français) | [🇯🇵 日本語](#日本語)

---

# English

## [0.1.0] – 2026-03-01

### 🎉 Initial Release

#### Core Features
- **Multilingual System**: Full support for 4 languages (DE, EN, FR, JA) across all commands, embeds and DM flows.
- **Language Priority**: Strict separation between server language (public embeds, logs) and user language (DMs, ephemeral messages).
- **XIVAPI v2 Integration**: Automatic background sync of all Duty Finder content including Dawntrail (Level 90–100).

#### Event System
- **DM Flow**: Interactive event creation via direct message with duty search, time input, duration (including open-end button) and optional free text.
- **Quad-Language Event Embeds**: Event title in all 4 languages, content image from XIVAPI, from/to time display with Discord timestamps.
- **RSVP System**: Three registration statuses (🟩 Accept, 🟦 Tentative, 🟥 Decline) with job/role selection. Declined users don't count against the player limit.
- **Unique Jobs**: Optional mode where each job can only be selected once per event.
- **Reminders**: Automatic channel ping + DM to all active participants 10 minutes before event start.
- **Auto-Cleanup**: Hourly auto-cleanup of expired events (> 8h), including Discord message deletion and admin log notifications.

#### Admin Features
- **Setup Wizard** (`/facsetup`): Interactive configuration of language, event channel and timezone.
- **Admin Logging**: Detailed log embeds for event creations and every status change (Accept/Tentative/Decline) in the server language.
- **Timezone Management**: Support for all IANA timezones with autocomplete.
- **Duty Update**: Manual XIVAPI sync via `/facdutyupdate`.

#### Infrastructure
- **Hybrid Commands**: All commands available as slash commands and with `!` prefix.
- **Persistent Views**: Event buttons remain functional after bot restarts.
- **Cross-Platform**: Start scripts for Windows, Linux and Raspberry Pi (systemd service).
- **Security**: Owner/Administrator permission system for admin commands.

---

# Deutsch

## [0.1.0] – 2026-03-01

### 🎉 Erstveröffentlichung

#### Kern-Features
- **Multilinguales System**: Vollständige Unterstützung für 4 Sprachen (DE, EN, FR, JA) in allen Befehlen, Embeds und DM-Flows.
- **Sprach-Priorität**: Strikte Trennung zwischen Server-Sprache (öffentliche Embeds, Logs) und User-Sprache (DMs, ephemerale Nachrichten).
- **XIVAPI v2 Integration**: Automatischer Hintergrund-Sync aller Duty-Finder-Inhalte inkl. Dawntrail (Level 90–100).

#### Event-System
- **DM-Flow**: Interaktive Event-Erstellung per Privatnachricht mit Duty-Suche, Zeitabfrage, Dauer (inkl. Open-End-Button) und optionalem Freitext.
- **Viersprachige Event-Embeds**: Event-Titel in allen 4 Sprachen, Content-Bild aus XIVAPI, Von/Bis-Zeitanzeige mit Discord-Timestamps.
- **RSVP-System**: Drei Anmeldestatus (🟩 Zusage, 🟦 Vielleicht, 🟥 Absage) mit Job-/Rollen-Auswahl. Abgesagte User zählen nicht gegen das Spielerlimit.
- **Unique-Jobs**: Optionaler Modus, bei dem jeder Job nur einmal pro Event belegt werden kann.
- **Erinnerungen**: Automatischer Kanal-Ping + DM an alle aktiven Teilnehmer 10 Minuten vor Eventstart.
- **Auto-Cleanup**: Stündliche Auto-Bereinigung abgelaufener Events (> 8h), inkl. Discord-Nachrichtenlöschung und Admin-Log.

#### Admin-Funktionen
- **Setup-Wizard** (`/facsetup`): Interaktive Einrichtung von Sprache, Event-Kanal und Zeitzone.
- **Admin-Logging**: Detaillierte Log-Embeds für Event-Erstellungen und jede Statusänderung (Zusage/Vielleicht/Absage) in der Serversprache.
- **Zeitzonen-Management**: Unterstützung aller IANA-Zeitzonen mit Autocomplete.
- **Duty-Update**: Manueller XIVAPI-Sync via `/facdutyupdate`.

#### Infrastruktur
- **Hybrid Commands**: Alle Befehle als Slash-Commands und mit `!`-Präfix nutzbar.
- **Persistent Views**: Event-Buttons bleiben nach Bot-Neustarts funktionsfähig.
- **Cross-Platform**: Startskripte für Windows, Linux und Raspberry Pi (Systemd-Service).
- **Sicherheit**: Owner/Administrator-Berechtigungssystem für Admin-Befehle.

---

# Français

## [0.1.0] – 2026-03-01

### 🎉 Version initiale

#### Fonctionnalités principales
- **Système multilingue** : Prise en charge complète de 4 langues (DE, EN, FR, JA) dans toutes les commandes, embeds et flux en MP.
- **Priorité linguistique** : Séparation stricte entre la langue du serveur (embeds publics, logs) et la langue de l'utilisateur (MP, messages éphémères).
- **Intégration XIVAPI v2** : Synchronisation automatique en arrière-plan de tout le contenu de l'Outil de mission, y compris Dawntrail (Niveau 90–100).

#### Système d'événements
- **Flux en MP** : Création interactive d'événements par message privé avec recherche de donjon, saisie d'horaire, durée (y compris bouton durée libre) et texte libre optionnel.
- **Embeds quadrilingues** : Titre de l'événement dans les 4 langues, image XIVAPI, affichage horaire de/à avec timestamps Discord.
- **Système RSVP** : Trois statuts d'inscription (🟩 Accepter, 🟦 Peut-être, 🟥 Décliner) avec sélection de job/rôle. Les déclins ne comptent pas dans la limite.
- **Jobs uniques** : Mode optionnel où chaque job ne peut être sélectionné qu'une seule fois par événement.
- **Rappels** : Ping automatique dans le canal + MP à tous les participants actifs 10 minutes avant le début.
- **Nettoyage automatique** : Nettoyage automatique horaire des événements expirés (> 8h), suppression des messages Discord et notification admin.

#### Fonctionnalités administrateur
- **Assistant de configuration** (`/facsetup`) : Configuration interactive de la langue, du canal et du fuseau horaire.
- **Journalisation** : Embeds de log détaillés pour les créations et chaque changement de statut dans la langue du serveur.
- **Gestion des fuseaux horaires** : Prise en charge de tous les fuseaux IANA avec autocomplétion.
- **Mise à jour** : Synchronisation XIVAPI manuelle via `/facdutyupdate`.

#### Infrastructure
- **Commandes hybrides** : Toutes les commandes disponibles en slash et avec le préfixe `!`.
- **Vues persistantes** : Les boutons restent fonctionnels après un redémarrage du bot.
- **Multi-plateforme** : Scripts de démarrage pour Windows, Linux et Raspberry Pi (service systemd).
- **Sécurité** : Système de permissions Propriétaire/Administrateur.

---

# 日本語

## [0.1.0] – 2026-03-01

### 🎉 初回リリース

#### コア機能
- **多言語システム**: すべてのコマンド、Embed、DMフローで4言語（DE、EN、FR、JA）を完全サポート。
- **言語優先順位**: サーバー言語（公開Embed、ログ）とユーザー言語（DM、エフェメラルメッセージ）の厳密な分離。
- **XIVAPI v2統合**: Dawntrail（レベル90〜100）を含むコンテンツファインダーの全データをバックグラウンドで自動同期。

#### イベントシステム
- **DMフロー**: コンテンツ検索、時刻入力、所要時間（オープンエンドボタン含む）、フリーテキスト付きのインタラクティブなイベント作成。
- **4言語イベントEmbed**: 4言語でのタイトル、XIVAPIの画像、Discordタイムスタンプ付きの開始/終了時刻。
- **RSVPシステム**: 3つの参加ステータス（🟩 参加、🟦 未定、🟥 辞退）とジョブ/ロール選択。辞退はプレイヤー上限にカウントされません。
- **ユニークジョブ**: 各ジョブがイベントごとに1回のみ選択可能なモード。
- **リマインダー**: イベント開始10分前に全参加者へチャンネルピング＋DM。
- **自動クリーンアップ**: 8時間以上経過したイベントの毎時自動削除（Discord メッセージ削除・管理ログ通知付き）。

#### 管理者機能
- **セットアップウィザード** (`/facsetup`): 言語、チャンネル、タイムゾーンのインタラクティブ設定。
- **管理ログ**: イベント作成と全ステータス変更の詳細ログEmbedをサーバー言語で記録。
- **タイムゾーン管理**: オートコンプリート付きの全IANAタイムゾーンサポート。
- **コンテンツ更新**: `/facdutyupdate` による手動XIVAPI同期。

#### インフラストラクチャ
- **ハイブリッドコマンド**: 全コマンドがスラッシュコマンドと `!` プレフィックスの両方で利用可能。
- **永続ビュー**: Bot再起動後もイベントボタンが機能を維持。
- **クロスプラットフォーム**: Windows、Linux、Raspberry Pi用の起動スクリプト。
- **セキュリティ**: 管理者コマンド用のオーナー/管理者権限システム。
