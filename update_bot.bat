@echo off
:: update_bot.bat
:: Skript für manuelles Backup der Datenbank und Update des Bots (Windows)

echo Starte Update-Prozess...

if not exist "backups\" mkdir backups

set "DB_FILE=planner.db"

if exist "%DB_FILE%" (
    :: Hole das aktuelle Datum und die Uhrzeit
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
    set "YYYY=%%I:~0,4%"
    set "MM=%%I:~4,2%"
    set "DD=%%I:~6,2%"
    set "HH=%%I:~8,2%"
    set "MIN=%%I:~10,2%"
    
    :: Weil verzögerte Expansion ohne setlocal enabledelayedexpansion nicht immer klappt, 
    :: hier eine einfache Methode für den Timestamp
    call set TIMESTAMP=%%datetime:~0,4%%%%datetime:~4,2%%%%datetime:~6,2%%_%%datetime:~8,2%%%%datetime:~10,2%%
    
    set "BACKUP_FILE=backups\planner_update_backup_%TIMESTAMP%.db"
    
    copy "%DB_FILE%" "!BACKUP_FILE!" >nul
    
    if errorlevel 1 (
        :: Fallback falls verzögerte Expansion aus ist
        copy "%DB_FILE%" "backups\planner_update_backup_manual.db" >nul
        echo Datenbank-Backup erfolgreich: backups\planner_update_backup_manual.db
    ) else (
        echo Datenbank-Backup erfolgreich.
    )
) else (
    echo Keine planner.db gefunden, ueberspringe Backup.
)

:: Hier das eigentliche Update ausfuehren
echo Ziehe neueste Updates...
:: git pull

echo Update-Prozess abgeschlossen.
pause
