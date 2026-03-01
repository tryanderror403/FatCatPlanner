@echo off
set /p confirm="⚠️ Alle Testdaten loeschen? (y/n): "

if /i "%confirm%" NEQ "y" (
    echo Abbruch.
    exit /b
)

echo Loesche Dateien und Ordner...
del /f /q .env 2>nul
del /f /q planner.db 2>nul
rd /s /q .venv 2>nul
rd /s /q logs 2>nul

for /d /r . %%d in (__pycache__) do @(
    rd /s /q "%%d" 2>nul
)

echo ✅ Bereinigung abgeschlossen. Der Ordner ist nun im Werkszustand.
pause
