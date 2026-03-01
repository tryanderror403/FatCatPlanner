#!/bin/bash
read -p '⚠️  Alle Testdaten löschen? (y/n): ' confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Abbruch."
    exit 0
fi

echo "Lösche Dateien und Ordner..."
rm -f .env planner.db
rm -rf .venv/ logs/
find . -type d -name '__pycache__' -exec rm -rf {} +

echo "✅ Bereinigung abgeschlossen. Der Ordner ist nun im Werkszustand."
