# 🐱 Fat Cat Planner v0.1.0

[🇬🇧 English](#english) | [🇩🇪 Deutsch](#deutsch) | [🇫🇷 Français](#français) | [🇯🇵 日本語](#日本語)

> Data provided by [XIVAPI.com](https://xivapi.com)

---

# English

> A smart, multilingual event planner for FFXIV groups — powered by XIVAPI v2.

## ✨ Feature Overview

### 🌍 Multilingual System
- Full support for **4 languages**: German, English, French, Japanese.
- Automatic background sync of all Duty Finder content from XIVAPI in all 4 languages.

### 🔀 Language Priority
- **Server Language**: Used for public event embeds, admin logs and channel messages.
- **User Language**: Used for DMs, ephemeral messages and personal commands (configurable via `/fcmylanguage`).

### 📩 DM Flow (Event Creation)
- Intuitive event creation via direct message with `/fccreate`.
- Duty search with XIVAPI autocomplete or manual entry.
- Timezone selection (server time or local time) with an info panel.
- Duration prompt (hours or open-ended via button).
- Optional free text for notes.

### 🎌 Quad-Language Event Embeds
- The public embed always displays the event content (Duty name) in all 4 languages.
- Content image from XIVAPI is displayed large and centered.

### ✅ RSVP System

| Button | Status | Action |
|--------|--------|--------|
| 🟩 **Accept** | `accepted` | Role/Job selection (Tank, Healer, DPS, Allrounder) |
| 🟦 **Tentative** | `tentative` | Role/Job selection, shown separately in the embed |
| 🟥 **Decline** | `declined` | No job flow, immediate decline |

- Each click overwrites the previous status.
- Declined users don't count against the player limit and aren't pinged for reminders.
- Unique Jobs mode: Each job can only be selected once per event.

### 📋 Admin Logging
- Every status change (Accept, Tentative, Decline) is logged in the admin log channel.
- Differentiated log embeds with color coding and job/role info.

### ⏰ Reminders
- Automatic reminder 10 minutes before event start (channel ping + DM to all participants).
- Declined users are not pinged.

### 🧹 Auto-Cleanup
- Expired events are automatically removed from the event channel and database after 8 hours (runs hourly).
- An admin log notification is sent for each cleaned event.

## 📌 Command Reference

All commands are available as **Hybrid Commands**: Both as `/slash-command` and with the `!` prefix.

### 👤 User Commands

| Command | Description |
|---------|-------------|
| `/fccreate` | Create a new event (interactive DM flow) |
| `/fcmylanguage` | Set your personal language for DMs and ephemeral messages |
| `/fctime` | Display current Eorzea Time and UTC server time |
| `/fchelp` | Overview of all user commands |

### 🔧 Admin Commands

> Require **Administrator permissions** or the **Owner ID** set in `.env`.

| Command | Description |
|---------|-------------|
| `/facsetup` | Interactive setup wizard (language, event channel, timezone) |
| `/factimezone set <tz>` | Change the server timezone (e.g. `Europe/Berlin`, `UTC`) |
| `/factimezone status` | Show system time, server time and next scheduled ping |
| `/facadminlog on <#channel>` | Enable event logging in a channel |
| `/facadminlog off` | Disable event logging |
| `/facdutyupdate` | Manually trigger XIVAPI content sync |
| `/facadmin sync` | Force global slash command synchronization |
| `/facadmin cleanup` | Manually delete expired events (> 8h) |
| `/fachelp` | Overview of all admin commands |

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A Discord Bot Token ([Developer Portal](https://discord.com/developers/applications))
- `pip install -r requirements.txt`

### First Launch

```bash
# Linux / macOS
./run_bot.sh

# Windows
run_bot.bat

# Raspberry Pi (as background service)
python3 setup_service.py
```

On **first launch** (without a `.env` file), the terminal wizard will ask for:
- **Language**: `de`, `en`, `fr` or `ja`
- **Discord Bot Token**
- **Owner ID** (your Discord User ID for admin permissions)

### Server Configuration

1. Run **`/facsetup`** → Interactive wizard for language, event channel, timezone.
2. Run **`/facadminlog on #log-channel`** → Enable admin logging *(optional)*.
3. Run **`/fccreate`** → Create your first event!

### Shutdown
Safely terminate with `Ctrl + C`.

### 💾 Backups & Updates
- **Auto-Backup**: The bot automatically backs up `planner.db` every 24 hours to the `backups/` folder (keeps last 7 days).
- **Manual Backup & Update**: Run the provided terminal script to safely backup the database before pulling new updates:
  - Linux/Mac: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Restore**: To restore from a backup, **stop the bot**, rename your backup file to `planner.db`, and start the bot again.
> [!IMPORTANT]
> For security reasons, backups and restores must be done manually on the host terminal. There are no Discord commands for this.

---

# Deutsch

> Ein intelligenter, mehrsprachiger Event-Planer für FFXIV-Gruppen — basierend auf XIVAPI v2.

## ✨ Feature-Übersicht

### 🌍 Multilinguales System
- Vollständige Unterstützung für **4 Sprachen**: Deutsch, Englisch, Französisch, Japanisch.
- Automatischer Hintergrund-Sync aller Inhalte des Duty Finders aus XIVAPI in allen 4 Sprachen.

### 🔀 Sprach-Priorität
- **Server-Sprache**: Wird für öffentliche Event-Embeds, Admin-Logs und Kanal-Nachrichten verwendet.
- **User-Sprache**: Wird für DMs, ephemerale Nachrichten und persönliche Befehle verwendet (einstellbar via `/fcmylanguage`).

### 📩 DM-Flow (Event-Erstellung)
- Intuitive Event-Erstellung per Privatnachricht mit `/fccreate`.
- Duty-Suche mit XIVAPI-Autocomplete oder manuelle Eingabe.
- Zeitzonen-Auswahl (Serverzeit oder Lokalzeit) mit Info-Panel.
- Dauer-Abfrage (Stunden oder offenes Ende via Button).
- Optionaler Freitext für Notizen.

### 🎌 Viersprachige Event-Embeds
- Das öffentliche Embed zeigt den Event-Inhalt (Duty-Name) immer in allen 4 Sprachen an.
- Content-Bild aus XIVAPI wird groß und zentral dargestellt.

### ✅ RSVP-System

| Button | Status | Aktion |
|--------|--------|--------|
| 🟩 **Zusage** | `accepted` | Rollen-/Job-Auswahl (Tank, Healer, DPS, Allrounder) |
| 🟦 **Vielleicht** | `tentative` | Rollen-/Job-Auswahl, wird separat im Embed angezeigt |
| 🟥 **Absage** | `declined` | Kein Job-Flow, sofortige Absage |

- Jeder Klick überschreibt den vorherigen Status.
- Abgesagte User zählen nicht gegen das Spielerlimit und werden nicht bei Erinnerungen gepingt.
- Unique-Jobs-Modus: Jeder Job kann nur einmal pro Event belegt werden.

### 📋 Admin-Logging
- Jede Statusänderung (Zusage, Vielleicht, Absage) wird im Admin-Log-Kanal geloggt.
- Differenzierte Log-Embeds mit farbiger Kennzeichnung und Job/Rollen-Info.

### ⏰ Erinnerungen
- Automatische Erinnerung 10 Minuten vor Eventstart (Kanal-Ping + DM an alle Teilnehmer).
- Abgesagte User werden nicht gepingt.

### 🧹 Auto-Cleanup
- Abgelaufene Events werden nach 8 Stunden automatisch aus dem Event-Kanal und der Datenbank entfernt (stündlich).
- Für jedes bereinigte Event wird eine Admin-Log-Benachrichtigung gesendet.

## 📌 Befehlsstruktur

Alle Befehle sind als **Hybrid Commands** verfügbar: Sowohl als `/Slash-Command` als auch mit dem Präfix `!`.

### 👤 User-Befehle

| Befehl | Beschreibung |
|--------|-------------|
| `/fccreate` | Erstelle ein neues Event (interaktiver DM-Flow) |
| `/fcmylanguage` | Persönliche Sprache für DMs und ephemerale Nachrichten einstellen |
| `/fctime` | Aktuelle Eorzea-Zeit und UTC-Serverzeit anzeigen |
| `/fchelp` | Übersicht aller User-Befehle |

### 🔧 Admin-Befehle

> Erfordern **Administrator-Rechte** oder die in `.env` hinterlegte **Owner-ID**.

| Befehl | Beschreibung |
|--------|-------------|
| `/facsetup` | Interaktiver Setup-Wizard (Sprache, Event-Kanal, Zeitzone) |
| `/factimezone set <tz>` | Server-Zeitzone ändern (z.B. `Europe/Berlin`, `UTC`) |
| `/factimezone status` | Systemzeit, Serverzeit und nächsten Ping anzeigen |
| `/facadminlog on <#kanal>` | Event-Logging in einem Kanal aktivieren |
| `/facadminlog off` | Event-Logging deaktivieren |
| `/facdutyupdate` | XIVAPI Content-Sync manuell starten |
| `/facadmin sync` | Globale Slash-Command-Synchronisation erzwingen |
| `/facadmin cleanup` | Abgelaufene Events (> 8h) manuell löschen |
| `/fachelp` | Übersicht aller Admin-Befehle |

## 🚀 Erste Schritte

### Voraussetzungen
- Python 3.11+
- Ein Discord Bot Token ([Developer Portal](https://discord.com/developers/applications))
- `pip install -r requirements.txt`

### Erster Start

```bash
# Linux / macOS
./run_bot.sh

# Windows
run_bot.bat

# Raspberry Pi (als Hintergrunddienst)
python3 setup_service.py
```

Beim **ersten Start** (ohne `.env`-Datei) fragt der Terminal-Wizard nach:
- **Sprache**: `de`, `en`, `fr` oder `ja`
- **Discord Bot Token**
- **Owner-ID** (deine Discord User-ID für Admin-Rechte)

### Server-Konfiguration

1. **`/facsetup`** ausführen → Interaktiver Wizard für Sprache, Event-Kanal, Zeitzone.
2. **`/facadminlog on #log-kanal`** → Admin-Logging aktivieren *(optional)*.
3. **`/fccreate`** → Dein erstes Event erstellen!

### Beenden
Sicher beenden mit `Strg + C`.

### 💾 Backups & Updates
- **Auto-Backup**: Der Bot sichert die `planner.db` automatisch alle 24 Stunden in den `backups/`-Ordner (behält die letzten 7 Tage).
- **Manuelles Backup & Update**: Führe das Update-Skript im Terminal aus. Es erstellt automatisch ein Backup der Datenbank, bevor neue Updates geladen werden:
  - Linux/Mac: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Wiederherstellung (Restore)**: Um ein Backup wiederherzustellen, **stoppe den Bot**, benenne die Backup-Datei in `planner.db` um und starte den Bot neu.
> [!IMPORTANT]
> Aus Sicherheitsgründen müssen Backups und Restores direkt im Host-Terminal durchgeführt werden. Es gibt dafür keine Discord-Befehle.

---

# Français

> Un planificateur d'événements intelligent et multilingue pour les groupes FFXIV — propulsé par XIVAPI v2.

## ✨ Aperçu des fonctionnalités

### 🌍 Système multilingue
- Prise en charge complète de **4 langues** : allemand, anglais, français, japonais.
- Synchronisation automatique en arrière-plan de tout le contenu de l'Outil de mission depuis XIVAPI dans les 4 langues.

### 🔀 Priorité linguistique
- **Langue du serveur** : Utilisée pour les embeds d'événements publics, les logs d'administration et les messages de canal.
- **Langue de l'utilisateur** : Utilisée pour les MP, les messages éphémères et les commandes personnelles (configurable via `/fcmylanguage`).

### 📩 Flux en MP (Création d'événement)
- Création intuitive d'événements par message privé avec `/fccreate`.
- Recherche de donjon avec autocomplétion XIVAPI ou saisie manuelle.
- Sélection du fuseau horaire (heure du serveur ou heure locale) avec panneau d'information.
- Choix de la durée (heures ou durée libre via bouton).
- Texte libre optionnel pour les notes.

### 🎌 Embeds d'événements quadrilingues
- L'embed public affiche toujours le contenu de l'événement (nom du donjon) dans les 4 langues.
- L'image du contenu XIVAPI est affichée en grand format et centrée.

### ✅ Système RSVP

| Bouton | Statut | Action |
|--------|--------|--------|
| 🟩 **Accepter** | `accepted` | Sélection de rôle/job (Tank, Healer, DPS, Allrounder) |
| 🟦 **Peut-être** | `tentative` | Sélection de rôle/job, affiché séparément dans l'embed |
| 🟥 **Décliner** | `declined` | Pas de sélection de job, déclin immédiat |

- Chaque clic écrase le statut précédent.
- Les utilisateurs ayant décliné ne comptent pas dans la limite de joueurs et ne sont pas notifiés.
- Mode Jobs uniques : Chaque job ne peut être sélectionné qu'une seule fois par événement.

### 📋 Journalisation administrative
- Chaque changement de statut (Accepter, Peut-être, Décliner) est enregistré dans le canal de log.
- Embeds de log différenciés avec code couleur et information de job/rôle.

### ⏰ Rappels
- Rappel automatique 10 minutes avant le début de l'événement (ping dans le canal + MP).
- Les utilisateurs ayant décliné ne sont pas notifiés.

### 🧹 Nettoyage automatique
- Les événements expirés sont automatiquement supprimés du canal et de la base de données après 8 heures (exécution horaire).
- Une notification de log admin est envoyée pour chaque événement nettoyé.

## 📌 Référence des commandes

Toutes les commandes sont disponibles en tant que **Commandes hybrides** : `/commande-slash` et préfixe `!`.

### 👤 Commandes utilisateur

| Commande | Description |
|----------|-------------|
| `/fccreate` | Créer un nouvel événement (flux interactif en MP) |
| `/fcmylanguage` | Définir votre langue personnelle pour les MP et messages éphémères |
| `/fctime` | Afficher l'heure éorzéenne et l'heure UTC du serveur |
| `/fchelp` | Aperçu de toutes les commandes utilisateur |

### 🔧 Commandes administrateur

> Nécessitent les **permissions Administrateur** ou l'**ID du propriétaire** défini dans `.env`.

| Commande | Description |
|----------|-------------|
| `/facsetup` | Assistant de configuration interactif (langue, canal, fuseau horaire) |
| `/factimezone set <fh>` | Modifier le fuseau horaire du serveur (ex. `Europe/Paris`, `UTC`) |
| `/factimezone status` | Afficher l'heure système, l'heure serveur et le prochain ping |
| `/facadminlog on <#canal>` | Activer la journalisation dans un canal |
| `/facadminlog off` | Désactiver la journalisation |
| `/facdutyupdate` | Déclencher manuellement la synchronisation XIVAPI |
| `/facadmin sync` | Forcer la synchronisation globale des commandes slash |
| `/facadmin cleanup` | Supprimer manuellement les événements expirés (> 8h) |
| `/fachelp` | Aperçu de toutes les commandes administrateur |

## 🚀 Mise en route

### Prérequis
- Python 3.11+
- Un Token de Bot Discord ([Portail développeur](https://discord.com/developers/applications))
- `pip install -r requirements.txt`

### Premier lancement

```bash
# Linux / macOS
./run_bot.sh

# Windows
run_bot.bat

# Raspberry Pi (service en arrière-plan)
python3 setup_service.py
```

Lors du **premier lancement** (sans fichier `.env`), l'assistant demandera :
- **Langue** : `de`, `en`, `fr` ou `ja`
- **Token du Bot Discord**
- **ID du propriétaire** (votre ID Discord pour les permissions admin)

### Configuration du serveur

1. Exécutez **`/facsetup`** → Assistant interactif pour langue, canal, fuseau horaire.
2. Exécutez **`/facadminlog on #canal-log`** → Activer la journalisation *(optionnel)*.
3. Exécutez **`/fccreate`** → Créez votre premier événement !

### Arrêt
Arrêt sécurisé avec `Ctrl + C`.

### 💾 Sauvegardes & Mises à jour
- **Auto-Backup**: Le bot sauvegarde automatiquement `planner.db` toutes les 24 heures dans le dossier `backups/` (conserve les 7 derniers jours).
- **Sauvegarde manuelle & Mise à jour**: Exécutez le script dans le terminal pour sécuriser la base de données avant la mise à jour :
  - Linux/Mac: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Restauration (Restore)**: Pour restaurer, **arrêtez le bot**, renommez votre fichier de sauvegarde en `planner.db`, et redémarrez le bot.
> [!IMPORTANT]
> Pour des raisons de sécurité, les sauvegardes et restaurations doivent être effectuées manuellement sur le terminal hôte. Il n'y a pas de commandes Discord pour cela.

---

# 日本語

> FFXIV グループ向けのスマートな多言語イベントプランナー — XIVAPI v2搭載

## ✨ 機能概要

### 🌍 多言語システム
- **4言語**完全対応: ドイツ語、英語、フランス語、日本語
- XIVAPIからコンテンツファインダーの全データを4言語でバックグラウンド自動同期

### 🔀 言語の優先順位
- **サーバー言語**: 公開イベントEmbed、管理ログ、チャンネルメッセージに使用
- **ユーザー言語**: DM、エフェメラルメッセージ、個人コマンドに使用（`/fcmylanguage` で設定可能）

### 📩 DMフロー（イベント作成）
- `/fccreate` でダイレクトメッセージによる直感的なイベント作成
- XIVAPIオートコンプリートまたは手動入力によるコンテンツ検索
- タイムゾーン選択（サーバー時間またはローカル時間）と情報パネル
- 所要時間の入力（時間指定またはオープンエンドボタン）
- オプションのフリーテキスト（メモ用）

### 🎌 4言語イベントEmbed
- 公開Embedはイベント内容（コンテンツ名）を常に4言語で表示
- XIVAPIのコンテンツ画像を大きく中央に表示

### ✅ RSVPシステム

| ボタン | ステータス | アクション |
|--------|-----------|-----------|
| 🟩 **参加** | `accepted` | ロール/ジョブ選択（タンク、ヒーラー、DPS、オールラウンダー） |
| 🟦 **未定** | `tentative` | ロール/ジョブ選択、Embedに別途表示 |
| 🟥 **辞退** | `declined` | ジョブ選択なし、即時辞退 |

- クリックするたびに前のステータスが上書きされます
- 辞退したユーザーはプレイヤー上限にカウントされず、リマインダーの通知も受けません
- ユニークジョブモード: 各ジョブはイベントごとに1回のみ選択可能

### 📋 管理ログ
- すべてのステータス変更（参加、未定、辞退）が管理ログチャンネルに記録されます
- 色分けとジョブ/ロール情報付きの差別化されたログEmbed

### ⏰ リマインダー
- イベント開始10分前に自動リマインダー（チャンネルピング＋全参加者へDM）
- 辞退したユーザーには通知されません

### 🧹 自動クリーンアップ
- 期限切れのイベントは8時間後にイベントチャンネルとデータベースから自動的に削除されます（毎時実行）
- クリーンアップされた各イベントについて管理ログ通知が送信されます

## 📌 コマンド一覧

すべてのコマンドは**ハイブリッドコマンド**として利用可能: `/スラッシュコマンド` と `!` プレフィックスの両方に対応

### 👤 ユーザーコマンド

| コマンド | 説明 |
|---------|------|
| `/fccreate` | 新しいイベントを作成（DMでのインタラクティブフロー） |
| `/fcmylanguage` | DM・エフェメラルメッセージ用の個人言語を設定 |
| `/fctime` | 現在のエオルゼア時間とUTCサーバー時間を表示 |
| `/fchelp` | 全ユーザーコマンドの一覧 |

### 🔧 管理者コマンド

> **管理者権限**または `.env` で設定された**オーナーID**が必要です。

| コマンド | 説明 |
|---------|------|
| `/facsetup` | インタラクティブセットアップウィザード（言語、チャンネル、タイムゾーン） |
| `/factimezone set <tz>` | サーバーのタイムゾーンを変更（例: `Asia/Tokyo`, `UTC`） |
| `/factimezone status` | システム時間、サーバー時間、次のピング予定を表示 |
| `/facadminlog on <#チャンネル>` | チャンネルでイベントログを有効化 |
| `/facadminlog off` | イベントログを無効化 |
| `/facdutyupdate` | XIVAPI コンテンツ同期を手動トリガー |
| `/facadmin sync` | グローバルスラッシュコマンド同期を強制実行 |
| `/facadmin cleanup` | 期限切れイベント（8時間以上）を手動削除 |
| `/fachelp` | 全管理者コマンドの一覧 |

## 🚀 はじめに

### 前提条件
- Python 3.11+
- Discord Botトークン（[開発者ポータル](https://discord.com/developers/applications)）
- `pip install -r requirements.txt`

### 初回起動

```bash
# Linux / macOS
./run_bot.sh

# Windows
run_bot.bat

# Raspberry Pi（バックグラウンドサービスとして）
python3 setup_service.py
```

**初回起動時**（`.env` ファイルなし）、ターミナルウィザードが以下を確認します：
- **言語**: `de`, `en`, `fr` または `ja`
- **Discord Botトークン**
- **オーナーID**（管理者権限用のDiscordユーザーID）

### サーバー設定

1. **`/facsetup`** を実行 → 言語、チャンネル、タイムゾーンのインタラクティブウィザード
2. **`/facadminlog on #ログチャンネル`** → 管理ログを有効化 *（任意）*
3. **`/fccreate`** → 最初のイベントを作成！

### シャットダウン
`Ctrl + C` で安全に終了

### 💾 バックアップとアップデート
- **自動バックアップ**: ボットは24時間ごとに `planner.db` を `backups/` フォルダに自動バックアップします（過去7日分を保持）。
- **手動バックアップとアップデート**: データベースを安全にバックアップしてから更新を取得するには、ホストのターミナルでスクリプトを実行してください:
  - Linux/Mac: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **復元 (Restore)**: バックアップから復元するには、**ボットを停止し**、バックアップファイルを `planner.db` に名前変更してからボットを再起動してください。
> [!IMPORTANT]
> セキュリティ保護のため、バックアップや復旧の操作はすべてホストのターミナルで手動で行う必要があります。Discordのコマンドはありません。

---

## 📁 Project Structure

```
FatCatPlanner/
├── fatcat.py          # Entry point, bot init, persistent views
├── db.py              # SQLite database (events, signups, settings)
├── views.py           # Discord UI (buttons, selects, embeds)
├── i18n.py            # Localization (DE/EN/FR/JA)
├── ffxiv_data.py      # FFXIV roles, jobs, custom content
├── xivapi_sync.py     # XIVAPI v2 background sync
├── setup_views.py     # Setup wizard UI
├── cogs/
│   ├── admin.py       # Admin commands
│   ├── events.py      # Event creation, reminders, cleanup
│   └── utils.py       # User commands (/fctime, /fchelp, etc.)
├── .env.example       # Environment variables template
├── requirements.txt   # Python dependencies
├── run_bot.sh         # Linux start script
├── run_bot.bat        # Windows start script
└── setup_service.py   # Systemd service generator
```

## 📜 License & Credits

- **XIVAPI**: All Duty Finder data provided by [xivapi.com](https://xivapi.com)
- **FINAL FANTASY XIV** © SQUARE ENIX CO., LTD. All Rights Reserved.

---

Licensed under GPL-3.0

