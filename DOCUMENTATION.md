# 🐱 Fat Cat Planner v0.1.0 — Documentation

[🇬🇧 English](#english) | [🇩🇪 Deutsch](#deutsch) | [🇫🇷 Français](#français) | [🇯🇵 日本語](#日本語)

> All game data (Dungeons, Raids, Trials) is powered by [XIVAPI.com](https://xivapi.com)

---

# English

## 1. Server Configuration (`/facsetup`)

Before creating any events, you **must** configure the bot.  
Use the command `/facsetup` in any channel. The interactive setup wizard proceeds in this order:

1. **Language**: Choose the server's default language (`de`, `en`, `fr`, `ja`).
2. **Event Channel**: Select the text channel where event embeds will be posted.
3. **Timezone**: Set the server's local timezone (e.g. `Europe/Berlin`).

## 2. Permissions & Security

By default, **only** Server Administrators and the Bot Owner (defined via `OWNER_ID` in the `.env` file) have permission to execute admin commands (`/facsetup`, `/facadminlog`, `/factimezone set`, `/facadmin`).

> **Tip:** Administrators can grant other roles access to these commands via Discord's Integration Settings:  
> *Server Settings → Integrations → Fat Cat Planner*

### Finding Your Discord User ID (for `OWNER_ID`)

1. **Enable Developer Mode**: User Settings → Advanced → Developer Mode (On).
2. **Desktop**: Click your profile picture (bottom left) → *Copy User ID*.
3. **Mobile**: Tap your profile (bottom right) → Tap your avatar again → `...` → *Copy User ID*.

## 3. Step-by-Step Event Creation (`/fccreate`)

Event creation is handled through a private, interactive **Direct Message (DM)** flow.

### Step 1 — Start
Type `/fccreate` in any server channel. The bot sends you a DM.

### Step 2 — Search for Content
In the DM, type the name of the content you want to run (e.g. "Savage", "Dawntrail", "Extreme"). The bot searches its XIVAPI database and presents a dropdown menu with matches.

### Step 3 — Enter Time
The bot is extremely flexible with time formats:

| Feature | Examples | Description |
|---|---|---|
| Time only | `18:00` or `18.00` | If already past today, auto-schedules for tomorrow |
| Separators | `15.30` or `15,30` | Dots/commas auto-convert to `15:30` |
| Full date & time | `21.02.2026 18:00` or `21/02 18:00` | Slashes, dashes, commas in dates all supported |
| Relative date | `21.02. 18:00` | Without year → assumes current year |
| US/JP format | `2026.02.21 18:00` | `YYYY.MM.DD` fully supported |

### Step 4 — Duration
The bot asks how long the event lasts. You can either:
- **Type a number** (e.g. `2` for 2 hours, `1.5` for 90 minutes).
- **Press the "Open End" button** if the event has no fixed end time.

The end time is calculated automatically and shown in the embed as a "From / To" display.

### Step 5 — Free Text (Optional)
The bot asks for an optional note. You can either:
- **Type any text** (e.g. "Bring food! Loot rules: Need/Greed").
- **Press the "Skip" button** to leave it empty.

### Step 6 — Unique Jobs
You will be asked whether to enforce **Unique Jobs**. If activated, no two players can sign up with the same job.

## 4. Manual Event Creation

If the content isn't in the Duty Finder database (e.g. "Glamour Contest", "Treasure Maps"):

During **Step 2**, simply type `manual` or `manuell`. The bot will ask you to type a custom name and select a party size (Light Party 4, Full Party 8, Alliance 24).

## 5. RSVP System

Once an event is posted, three buttons appear below the embed:

| Button | Status | Description |
|---|---|---|
| 🟩 **Accept** | `accepted` | Opens the role/job selection flow (Tank, Healer, DPS, Allrounder) |
| 🟦 **Tentative** | `tentative` | Same role/job selection, shown under a separate "Tentative" section |
| 🟥 **Decline** | `declined` | No job selection — instantly records the decline |

### Key Behaviors
- **Changing your mind**: Clicking any button overwrites your previous status. A declined user can later rejoin.
- **Player count**: Only accepted and tentative users count towards `max_players`. Declined users do not.
- **Reminders**: Only accepted and tentative users receive the 10-minute reminder. Declined users are excluded.
- **Unique Jobs**: A declined user's job slot is freed up for others.
- **Admin Log**: Every click is logged with the corresponding color and details.
- **Auto-Cleanup**: Expired events (> 8h past start time) are automatically removed from the event channel and the database every hour. An admin log notification is sent for each cleaned event.

## 6. Log Channel Configuration (Optional — `/facadminlog`)

```
/facadminlog on #your-log-channel    → Enable
/facadminlog off                     → Disable
```

> ⚠️ **Warning:** This channel contains security-relevant logs. It should only be visible to administrators.

## 7. Backups & Updates

- **Auto-Backup**: The bot automatically backs up `planner.db` every 24 hours to the `backups/` folder (keeping the last 7 files).
- **Manual Backup & Update**: Run the update script in your host terminal to safely backup the database before pulling new updates.
  - Linux/Raspberry Pi: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Restore Procedure**: To restore from a backup, you must **first stop the bot**. Rename your selected backup file to `planner.db`, displacing the old one, and then start the bot again.

> [!IMPORTANT]  
> For security reasons, backups and restores must be done directly on the host file system/terminal. There are no Discord commands for these processes.

## 8. Complete Command Reference

### 👤 User Commands

| Command | Description |
|---|---|
| `/fccreate` | Start the interactive DM event creation flow |
| `/fcmylanguage` | Set your personal language for DMs and ephemeral messages |
| `/fctime` | Display current Eorzea Time and UTC server time |
| `/fchelp` | Show all available user commands |

### 🔧 Admin Commands (Administrator / Owner only)

| Command | Description |
|---|---|
| `/facsetup` | Interactive setup wizard (language, event channel, timezone) |
| `/factimezone set <tz>` | Change the server timezone |
| `/factimezone status` | Show system time, server time, and next ping |
| `/facadminlog on <#channel>` | Enable event logging in a channel |
| `/facadminlog off` | Disable event logging |
| `/facdutyupdate` | Manually trigger XIVAPI content sync |
| `/facadmin sync` | Force global slash command synchronization |
| `/facadmin cleanup` | Manually delete expired events (> 8h) |
| `/fachelp` | Show all available admin commands |

## 9. Legacy Support (Prefix `!`)

All commands are also available using the `!` prefix (e.g. `!fccreate`, `!facsetup`).

---

# Deutsch

## 1. Server-Konfiguration (`/facsetup`)

Bevor Events erstellt werden können, **muss** der Bot eingerichtet werden.  
Nutze den Befehl `/facsetup` in einem beliebigen Kanal. Der interaktive Wizard führt dich in dieser Reihenfolge:

1. **Sprachwahl**: Wähle die Standard-Sprache des Servers (`de`, `en`, `fr`, `ja`).
2. **Event-Kanal**: Wähle den Textkanal, in dem Event-Embeds gepostet werden.
3. **Zeitzone**: Stelle die Server-Zeitzone ein (z.B. `Europe/Berlin`).

## 2. Berechtigungen & Sicherheit

Standardmäßig haben **ausschließlich** Server-Administratoren und der Bot-Owner (definiert als `OWNER_ID` in der `.env`-Datei) Zugriff auf Admin-Befehle (`/facsetup`, `/facadminlog`, `/factimezone set`, `/facadmin`).

> **Tipp:** Administratoren können über die Discord-Integrationseinstellungen weiteren Rollen Zugriff gewähren:  
> *Servereinstellungen → Integrationen → Fat Cat Planner*

### Discord User-ID finden (für `OWNER_ID`)

1. **Entwicklermodus aktivieren**: Benutzereinstellungen → Erweitert → Entwicklermodus (An).
2. **Desktop**: Unten links auf das Profilbild klicken → *Nutzer-ID kopieren*.
3. **Mobile**: Unten rechts auf das Profil klicken → Eigenes Bild anklicken → `...` → *Nutzer-ID kopieren*.

## 3. Event-Erstellung Schritt für Schritt (`/fccreate`)

Die Event-Erstellung läuft über eine private **Direktnachricht (DM)** ab.

### Schritt 1 — Start
Tippe `/fccreate` in einem Server-Kanal. Der Bot meldet sich per DM.

### Schritt 2 — Inhalt suchen
Tippe den Namen des Inhalts ein (z.B. „Episch", „Dawntrail", „Extremus"). Der Bot durchsucht seine XIVAPI-Datenbank und zeigt ein Dropdown-Menü.

### Schritt 3 — Zeit eingeben
Der Bot versteht viele intuitive Formate:

| Funktion | Beispiele | Beschreibung |
|---|---|---|
| Nur Uhrzeit | `18:00` oder `18.00` | Ist die Zeit vorbei, wird automatisch morgen geplant |
| Mit Trennzeichen | `15.30` oder `15,30` | Punkte/Kommata werden zu `15:30` konvertiert |
| Datum & Uhrzeit | `21.02.2026 18:00` oder `21/02 18:00` | Slashes, Bindestriche, Kommata unterstützt |
| Relatives Datum | `21.02. 18:00` | Ohne Jahr → aktuelles Jahr |
| US/JP-Format | `2026.02.21 18:00` | `YYYY.MM.DD` unterstützt |

### Schritt 4 — Dauer
Der Bot fragt, wie lange das Event dauert:
- **Eine Zahl eintippen** (z.B. `2` für 2 Stunden, `1.5` für 90 Minuten).
- **Den „Offenes Ende"-Button drücken**, wenn das Event kein festes Ende hat.

Die Endzeit wird automatisch berechnet und im Embed als „Von / Bis" angezeigt.

### Schritt 5 — Freitext (Optional)
Der Bot fragt nach einer optionalen Notiz:
- **Einen beliebigen Text eintippen** (z.B. „Bringt Essen mit! Loot: Need/Greed").
- **Den „Überspringen"-Button drücken**, um das Feld leer zu lassen.

### Schritt 6 — Unique Jobs
Du wirst gefragt, ob **Unique Jobs** erzwungen werden sollen. Wenn aktiviert, können sich keine zwei Spieler mit dem gleichen Job anmelden.

## 4. Manuelle Event-Erstellung

Falls der Inhalt nicht existiert (z.B. „Glamour-Wettbewerb", „Schatzkarten"):

Tippe in **Schritt 2** einfach `manuell` oder `manual`. Der Bot bittet dich dann um einen freien Titel und die Gruppengröße (Leichter Trupp 4, Voller Trupp 8, Allianz 24).

## 5. RSVP-System

Sobald ein Event gepostet wird, erscheinen drei Buttons:

| Button | Status | Beschreibung |
|---|---|---|
| 🟩 **Zusage** | `accepted` | Öffnet den Rollen-/Job-Auswahl-Flow (Tank, Heiler, DPS, Allrounder) |
| 🟦 **Vielleicht** | `tentative` | Gleicher Flow, aber separater „Vielleicht"-Bereich im Embed |
| 🟥 **Absage** | `declined` | Keine Job-Auswahl — sofortige Absage |

### Wichtige Verhaltensregeln
- **Meinung ändern**: Ein Klick auf einen Button überschreibt den vorherigen Status. Ein abgesagter User kann jederzeit wieder beitreten.
- **Spieleranzahl**: Nur Zusagen und Vielleicht zählen gegen `max_players`. Absagen nicht.
- **Erinnerungen**: Nur Zusagen und Vielleicht erhalten den 10-Minuten-Ping. Absagen werden nicht gepingt.
- **Unique Jobs**: Der Job-Slot eines abgesagten Users wird für andere freigegeben.
- **Admin-Log**: Jeder Klick wird mit entsprechender Farbe und Details geloggt.
- **Auto-Cleanup**: Abgelaufene Events (> 8h nach Startzeit) werden stündlich automatisch aus dem Event-Kanal und der Datenbank entfernt. Für jedes bereinigte Event wird ein Admin-Log gesendet.

## 6. Log-Kanal (Optional — `/facadminlog`)

```
/facadminlog on #dein-log-kanal     → Aktivieren
/facadminlog off                    → Deaktivieren
```

> ⚠️ **Warnung:** Dieser Kanal enthält sicherheitsrelevante Logs. Nur für Administratoren sichtbar machen!

## 7. Backups & Updates

- **Auto-Backup**: Der Bot sichert die `planner.db` automatisch alle 24 Stunden in den `backups/`-Ordner (und behält die letzten 7 Tage).
- **Manuelles Backup & Update**: Führe zur sicheren Aktualisierung das entsprechende Skript im Host-Terminal aus. Es erstellt automatisch ein Backup, bevor es aktualisiert.
  - Linux/Raspberry Pi: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Wiederherstellung (Restore)**: Um ein Backup wiederherzustellen, **stoppe zuerst den Bot**. Benenne die gewünschte Backup-Datei dann innerhalb deines Server-Verzeichnisses in `planner.db` um und starte den Bot neu.

> [!IMPORTANT]  
> Aus Sicherheitsgründen gibt es für Backup und Restore keine Discord-Befehle mehr. Führe diese Vorgänge immer direkt im Host-Terminal aus.

## 8. Vollständige Befehlsreferenz

### 👤 User-Befehle

| Befehl | Beschreibung |
|---|---|
| `/fccreate` | Startet den interaktiven DM-Event-Flow |
| `/fcmylanguage` | Persönliche Sprache einstellen |
| `/fctime` | Eorzea-Zeit und UTC-Serverzeit anzeigen |
| `/fchelp` | Alle User-Befehle anzeigen |

### 🔧 Admin-Befehle (Administrator / Owner)

| Befehl | Beschreibung |
|---|---|
| `/facsetup` | Interaktiver Setup-Wizard |
| `/factimezone set <tz>` | Server-Zeitzone ändern |
| `/factimezone status` | Systemzeit, Serverzeit, nächsten Ping anzeigen |
| `/facadminlog on <#kanal>` | Event-Logging aktivieren |
| `/facadminlog off` | Event-Logging deaktivieren |
| `/facdutyupdate` | XIVAPI Content-Sync manuell starten |
| `/facadmin sync` | Globale Slash-Command-Synchronisation erzwingen |
| `/facadmin cleanup` | Abgelaufene Events (> 8h) löschen |
| `/fachelp` | Alle Admin-Befehle anzeigen |

## 9. Legacy Support (Präfix `!`)

Alle Befehle sind auch über den Präfix `!` aufrufbar (z.B. `!fccreate`, `!facsetup`).

---

# Français

## 1. Configuration du serveur (`/facsetup`)

Avant de créer des événements, vous **devez** configurer le bot.  
Utilisez `/facsetup` dans n'importe quel canal. L'assistant interactif se déroule dans cet ordre :

1. **Langue** : Sélectionnez la langue par défaut (`de`, `en`, `fr`, `ja`).
2. **Canal d'événements** : Choisissez le canal où les embeds seront publiés.
3. **Fuseau horaire** : Définissez le fuseau horaire du serveur (ex. `Europe/Paris`).

## 2. Autorisations & Sécurité

Par défaut, **seuls** les Administrateurs et le Propriétaire du Bot (`OWNER_ID` dans `.env`) ont accès aux commandes admin (`/facsetup`, `/facadminlog`, `/factimezone set`, `/facadmin`).

> **Astuce :** Les administrateurs peuvent accorder l'accès via les paramètres d'intégration Discord :  
> *Paramètres du serveur → Intégrations → Fat Cat Planner*

### Trouver votre ID utilisateur Discord (pour `OWNER_ID`)

1. **Activer le mode développeur** : Paramètres → Avancés → Mode développeur (Activé).
2. **Bureau** : Photo de profil (en bas à gauche) → *Copier l'identifiant utilisateur*.
3. **Mobile** : Profil (en bas à droite) → Avatar → `...` → *Copier l'identifiant utilisateur*.

## 3. Création d'événement étape par étape (`/fccreate`)

La création se fait via un flux en **Message Privé (MP)**.

### Étape 1 — Démarrage
Tapez `/fccreate` dans un canal. Le bot vous contacte par MP.

### Étape 2 — Rechercher le contenu
Tapez le nom de l'activité (ex. « Sadique », « Fatal », « Dawntrail »). Le bot affiche un menu déroulant.

### Étape 3 — Saisir l'heure

| Fonction | Exemples | Description |
|---|---|---|
| Heure seule | `18:00` ou `18.00` | Si déjà passée, planification pour demain |
| Séparateurs | `15.30` ou `15,30` | Convertis en `15:30` |
| Date & heure | `21.02.2026 18:00` ou `21/02 18:00` | Slashs, tirets, virgules supportés |
| Date relative | `21.02. 18:00` | Sans année → année en cours |
| Format US/JP | `2026.02.21 18:00` | `AAAA.MM.JJ` supporté |

### Étape 4 — Durée
Le bot demande la durée :
- **Saisir un nombre** (ex. `2` pour 2 heures, `1.5` pour 90 minutes).
- **Bouton « Durée libre »** si l'événement n'a pas de fin fixe.

### Étape 5 — Texte libre (Optionnel)
- **Saisir un texte** (ex. « Apportez de la nourriture ! Règles de butin : Besoin/Cupidité »).
- **Bouton « Passer »** pour laisser vide.

### Étape 6 — Jobs uniques
Le bot demande si les **Jobs uniques** doivent être imposés (pas de doublon de job).

## 4. Création manuelle

Si le contenu n'est pas dans l'Outil de mission :

Lors de l'**Étape 2**, tapez `manuel` ou `manual`. Saisissez un nom libre et choisissez la taille (Équipe légère 4, Équipe complète 8, Alliance 24).

## 5. Système RSVP

Trois boutons apparaissent sous l'embed :

| Bouton | Statut | Description |
|---|---|---|
| 🟩 **Accepter** | `accepted` | Sélection rôle/job (Tank, Healer, DPS, Allrounder) |
| 🟦 **Peut-être** | `tentative` | Même sélection, section « Peut-être » séparée |
| 🟥 **Décliner** | `declined` | Pas de sélection, déclin immédiat |

### Comportements clés
- **Changer d'avis** : Chaque clic écrase le statut précédent. Un utilisateur ayant décliné peut rejoindre plus tard.
- **Nombre de joueurs** : Seuls acceptations et « peut-être » comptent dans la limite.
- **Rappels** : Seuls les participants actifs reçoivent le rappel 10 minutes avant.
- **Jobs uniques** : Le slot d'un déclin est libéré pour d'autres.
- **Log admin** : Chaque clic est journalisé avec couleur et détails.
- **Nettoyage automatique** : Les événements expirés (> 8h après l'heure de début) sont automatiquement supprimés du canal et de la base de données toutes les heures. Une notification de log admin est envoyée pour chaque événement nettoyé.

## 6. Canal de log (Optionnel — `/facadminlog`)

```
/facadminlog on #votre-canal-log    → Activer
/facadminlog off                    → Désactiver
```

> ⚠️ **Attention :** Ce canal contient des logs de sécurité. Visible uniquement par les administrateurs !

## 7. Sauvegardes & Mises à jour

- **Auto-Backup**: Le bot sauvegarde automatiquement `planner.db` toutes les 24 heures dans le dossier `backups/` (conserve les 7 derniers fichiers).
- **Sauvegarde manuelle & Mise à jour**: Exécutez le script de mise à jour dans votre terminal hôte pour sauvegarder en toute sécurité la base de données avant la mise à jour.
  - Linux/Raspberry Pi: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **Procédure de restauration**: Pour restaurer, vous devez **d'abord arrêter le bot**. Renommez votre fichier de sauvegarde sélectionné en `planner.db`, en remplaçant l'ancien, puis redémarrez le bot.

> [!IMPORTANT]  
> Pour des raisons de sécurité, les sauvegardes et restaurations doivent être effectuées directement sur le terminal hôte. Il n'y a pas de commandes Discord pour ces processus.

## 8. Référence complète des commandes

### 👤 Commandes utilisateur

| Commande | Description |
|---|---|
| `/fccreate` | Démarrer le flux de création en MP |
| `/fcmylanguage` | Définir votre langue personnelle |
| `/fctime` | Afficher l'heure éorzéenne et UTC |
| `/fchelp` | Afficher toutes les commandes utilisateur |

### 🔧 Commandes administrateur (Administrateur / Propriétaire)

| Commande | Description |
|---|---|
| `/facsetup` | Assistant de configuration interactif |
| `/factimezone set <fh>` | Modifier le fuseau horaire |
| `/factimezone status` | Afficher l'heure système, serveur et prochain ping |
| `/facadminlog on <#canal>` | Activer la journalisation |
| `/facadminlog off` | Désactiver la journalisation |
| `/facdutyupdate` | Déclencher la synchronisation XIVAPI |
| `/facadmin sync` | Forcer la synchronisation des commandes |
| `/facadmin cleanup` | Supprimer les événements expirés (> 8h) |
| `/fachelp` | Afficher toutes les commandes administrateur |

## 9. Prise en charge des anciens préfixes (`!`)

Toutes les commandes fonctionnent avec le préfixe `!` (ex. `!fccreate`, `!facsetup`).

---

# 日本語

## 1. サーバー設定 (`/facsetup`)

イベントを作成する前に、ボットの設定が**必須**です。  
任意のチャンネルで `/facsetup` を実行してください。ウィザードが以下の順序で進みます：

1. **言語選択**: サーバーのデフォルト言語（`de`, `en`, `fr`, `ja`）。
2. **イベントチャンネル**: イベントEmbedが投稿されるチャンネルを選択。
3. **タイムゾーン**: サーバーのタイムゾーンを設定（例: `Asia/Tokyo`）。

## 2. 権限とセキュリティ

デフォルトでは、サーバー管理者とボットオーナー（`.env` の `OWNER_ID`）**のみ**が管理コマンドを実行できます（`/facsetup`, `/facadminlog`, `/factimezone set`, `/facadmin`）。

> **ヒント:** 管理者はDiscordの連携設定から他のロールにアクセス権を付与できます：  
> *サーバー設定 → 連携 → Fat Cat Planner*

### Discord ユーザーIDの確認方法（`OWNER_ID` 用）

1. **開発者モードを有効化**: ユーザー設定 → 詳細設定 → 開発者モード（オン）。
2. **デスクトップ**: 左下のプロフィール画像をクリック → *ユーザーIDをコピー*。
3. **モバイル**: 右下のプロフィール → アバターをタップ → `...` → *ユーザーIDをコピー*。

## 3. イベント作成ステップ詳細 (`/fccreate`)

**ダイレクトメッセージ（DM）**によるインタラクティブフローです。

### ステップ 1 — 開始
サーバーチャンネルで `/fccreate` を入力。ボットからDMが届きます。

### ステップ 2 — コンテンツ検索
コンテンツ名を入力（例: 「零式」、「Dawntrail」、「絶」）。ドロップダウンメニューが表示されます。

### ステップ 3 — 時刻入力

| 機能 | 例 | 説明 |
|---|---|---|
| 時間のみ | `18:00` または `18.00` | 過ぎた場合、自動的に翌日に設定 |
| 区切り文字 | `15.30` または `15,30` | 自動変換 `15:30` |
| 日時指定 | `21.02.2026 18:00` または `21/02 18:00` | スラッシュ、ハイフン、カンマ対応 |
| 年省略 | `21.02. 18:00` | 年なし → 今年 |
| US/JPフォーマット | `2026.02.21 18:00` | `YYYY.MM.DD` 完全対応 |

### ステップ 4 — 所要時間
ボットが所要時間を尋ねます：
- **数字を入力**（例: `2` で2時間、`1.5` で90分）。
- **「オープンエンド」ボタン** — 終了時刻が未定の場合。

終了時刻は自動計算され、Embedに「開始 / 終了」形式で表示されます。

### ステップ 5 — フリーテキスト（任意）
- **任意のテキストを入力**（例: 「食べ物持参！ロット方式：Need/Greed」）。
- **「スキップ」ボタン** — 空にする場合。

### ステップ 6 — ユニークジョブ
**ユニークジョブ**を有効にするか尋ねられます。有効にすると同じジョブでの重複登録が防止されます。

## 4. マニュアルイベント作成

コンテンツファインダーにない場合（例: 「地図PT」、「ミラプリコンテスト」）：

**ステップ 2** で `マニュアル` または `manual` と入力。自由な名前とグループサイズ（ライトパーティ4、フルパーティ8、アライアンス24）を選択。

## 5. RSVPシステム

イベント投稿後、Embedの下に3つのボタンが表示されます：

| ボタン | ステータス | 説明 |
|---|---|---|
| 🟩 **参加** | `accepted` | ロール/ジョブ選択フロー（タンク、ヒーラー、DPS、オールラウンダー） |
| 🟦 **未定** | `tentative` | 同じフロー、「未定」セクションに別途表示 |
| 🟥 **辞退** | `declined` | ジョブ選択なし、即座に辞退を記録 |

### 主な動作
- **変更可能**: 任意のボタンクリックで前のステータスが上書き。辞退後も復帰可能。
- **プレイヤー数**: 参加と未定のみが`max_players`にカウント。辞退は含まれません。
- **リマインダー**: 参加と未定のみが10分前通知を受信。辞退は除外。
- **ユニークジョブ**: 辞退したユーザーのジョブスロットは開放されます。
- **管理ログ**: すべてのクリックが対応する色と詳細で記録。
- **自動クリーンアップ**: 期限切れのイベント（開始時刻から8時間以上経過）は毎時自動的にイベントチャンネルとデータベースから削除されます。各クリーンアップについて管理ログ通知が送信されます。

## 6. ログチャンネル設定（任意 — `/facadminlog`）

```
/facadminlog on #ログチャンネル     → 有効化
/facadminlog off                   → 無効化
```

> ⚠️ **警告:** セキュリティ関連のログが含まれます。管理者のみが閲覧できるようにしてください。

## 7. バックアップとアップデート

- **自動バックアップ**: ボットは24時間ごとに `planner.db` を `backups/` フォルダに自動バックアップします（過去7日分を保持）。
- **手動バックアップとアップデート**: 新しい更新を取得する前にデータベースをバックアップするには、ホストターミナルで更新スクリプトを実行します。
  - Linux/Raspberry Pi: `./update_bot.sh`
  - Windows: `update_bot.bat`
- **復元 (Restore)**: バックアップから復元するには、**必ずボットを停止し**、バックアップファイルを `planner.db` に名前変更してからボットを再起動してください。

> [!IMPORTANT]  
> セキュリティのため、バックアップと復元はホストのファイルシステム上で直接行う必要があります。これらのプロセスのためのDiscordコマンドはありません。

## 8. コマンドリファレンス一覧

### 👤 ユーザーコマンド

| コマンド | 説明 |
|---|---|
| `/fccreate` | インタラクティブDMイベント作成フローを開始 |
| `/fcmylanguage` | 個人言語を設定 |
| `/fctime` | エオルゼア時間とUTCサーバー時間を表示 |
| `/fchelp` | 全ユーザーコマンドを表示 |

### 🔧 管理者コマンド（管理者 / オーナー限定）

| コマンド | 説明 |
|---|---|
| `/facsetup` | インタラクティブセットアップウィザード |
| `/factimezone set <tz>` | タイムゾーンを変更 |
| `/factimezone status` | システム時間、サーバー時間、次のピングを表示 |
| `/facadminlog on <#チャンネル>` | イベントログを有効化 |
| `/facadminlog off` | イベントログを無効化 |
| `/facdutyupdate` | XIVAPI同期を手動トリガー |
| `/facadmin sync` | スラッシュコマンド同期を強制実行 |
| `/facadmin cleanup` | 期限切れイベント（8時間以上）を削除 |
| `/fachelp` | 全管理者コマンドを表示 |

## 9. レガシーサポート（プレフィックス `!`）

すべてのコマンドは `!` プレフィックスでも利用可能です（例: `!fccreate`, `!facsetup`）。
