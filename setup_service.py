import os
import pathlib
import getpass

def main():
    base_dir = pathlib.Path(__file__).parent.resolve()
    bot_script = base_dir / "fatcat.py"
    
    if os.name == 'nt':
        venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = base_dir / ".venv" / "bin" / "python3"
        
    current_user = getpass.getuser()
    
    if not venv_python.exists():
        print(f"⚠️ Warnung: Das Programm python in der .venv ({venv_python}) existiert (noch) nicht.")
        print("   Bitte starte zuerst das Setup über run_bot.sh oder run_bot.bat")
        
    service_content = f"""[Unit]
Description=Fat Cat Planner Discord Bot
After=network.target

[Service]
Type=simple
User={current_user}
WorkingDirectory={base_dir}
ExecStart={venv_python} {bot_script}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = base_dir / "fatcat.service"
    service_file.write_text(service_content, encoding="utf-8")
    
    print(f"✅ Datei {service_file} erfolgreich erstellt!")
    print("\nZur Installation auf Linux (Systemd) führe Folgendes aus:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable fatcat.service")
    print("   sudo systemctl start fatcat.service")

if __name__ == "__main__":
    main()
