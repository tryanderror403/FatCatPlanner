#!/bin/bash
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing requirements..."
pip3 install -r requirements.txt

echo "Starting Fat Cat Planner..."
python3 fatcat.py
