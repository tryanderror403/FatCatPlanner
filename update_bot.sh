#!/bin/bash
# update_bot.sh
# Skript für manuelles Backup der Datenbank und Update des Bots (Linux/Raspberry Pi)

echo "Starte Update-Prozess..."

# Stelle sicher, dass der backups-Ordner existiert
mkdir -p backups

# Alte Backups bereinigen (> 90 Tage)
echo "Bereinige alte Backups..."
find backups/ -name "planner_update_backup_*" -mtime +90 -delete

DB_FILE="planner.db"

if [ -f "$DB_FILE" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M")
    BACKUP_FILE="backups/planner_update_backup_${TIMESTAMP}.db"
    
    cp "$DB_FILE" "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Datenbank-Backup erfolgreich: $BACKUP_FILE"
    else
        echo "Fehler beim Erstellen des Backups!"
        exit 1
    fi
else
    echo "Keine planner.db gefunden, überspringe Backup."
fi

# Hier das eigentliche Update ausführen
echo "Ziehe neueste Updates..."
git pull origin main

echo "Baue und starte Docker-Container neu..."
docker compose up -d --build

echo "Update-Prozess abgeschlossen."
