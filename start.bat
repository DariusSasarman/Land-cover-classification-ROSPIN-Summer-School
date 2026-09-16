setlocal

rem from repo root
cd webserver\frontend
call npm install
call npm run build

cd ..\backend
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
fastapi dev app\main.py
