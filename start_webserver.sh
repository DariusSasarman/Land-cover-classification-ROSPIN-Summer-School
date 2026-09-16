#!/usr/bin/env bash
set -e

# from repo root
cd webserver/frontend
npm install
npm run build

cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev app/main.py
