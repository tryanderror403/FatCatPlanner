#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  Fat Cat Planner – Systemd Service Installer
#  Installiert den Bot als dauerhaften Hintergrunddienst.
# ═══════════════════════════════════════════════════════════════
set -e

# ── Farben ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🐱 Fat Cat Planner – Service Installer${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

# ── Root-Check ──
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Bitte als Root ausführen: sudo bash install_service.sh${NC}"
    exit 1
fi

# ── Aktuelles Verzeichnis ermitteln ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/fatcat.service"

if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}✗ fatcat.service nicht gefunden in: $SCRIPT_DIR${NC}"
    exit 1
fi

# ── Benutzer ermitteln ──
REAL_USER="${SUDO_USER:-$(whoami)}"
echo -e "${YELLOW}► Erkannter Benutzer: ${NC}$REAL_USER"
echo -e "${YELLOW}► Installationsverzeichnis: ${NC}$SCRIPT_DIR"
echo ""

# ── Service-Datei anpassen ──
echo -e "${YELLOW}► Passe fatcat.service an...${NC}"
TEMP_SERVICE="/tmp/fatcat.service.tmp"
sed \
    -e "s|User=pi|User=$REAL_USER|g" \
    -e "s|/path/to/FatCatPlanner|$SCRIPT_DIR|g" \
    "$SERVICE_FILE" > "$TEMP_SERVICE"

# ── Kopieren & Aktivieren ──
echo -e "${YELLOW}► Kopiere nach /etc/systemd/system/...${NC}"
cp "$TEMP_SERVICE" /etc/systemd/system/fatcat.service
rm -f "$TEMP_SERVICE"

echo -e "${YELLOW}► Lade Systemd Daemon neu...${NC}"
systemctl daemon-reload

echo -e "${YELLOW}► Aktiviere und starte fatcat.service...${NC}"
systemctl enable --now fatcat.service

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Fat Cat Planner läuft als Systemdienst!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo "  Nützliche Befehle:"
echo "    Status:    sudo systemctl status fatcat"
echo "    Logs:      sudo journalctl -u fatcat -f"
echo "    Stoppen:   sudo systemctl stop fatcat"
echo "    Neustart:  sudo systemctl restart fatcat"
echo "    Entfernen: sudo systemctl disable --now fatcat"
echo ""
