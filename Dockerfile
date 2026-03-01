# ═══════════════════════════════════════════════════
#  Fat Cat Planner – Dockerfile
#  Optimiert für Raspberry Pi (ARM) & Desktop (x86)
# ═══════════════════════════════════════════════════

FROM python:3.11-slim

# Systemabhängigkeiten (für aiohttp / aiosqlite wheels)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Dependencies zuerst (Layer-Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Unbuffered Output für Docker Logs
ENV PYTHONUNBUFFERED=1

# Startbefehl
CMD ["python", "fatcat.py"]
