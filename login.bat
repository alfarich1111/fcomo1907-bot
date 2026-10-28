@echo off
cd /d "%~dp0"
if not exist config.json (
  copy config.example.json config.json >nul
  echo config.json yaratildi. Unga api_id va api_hash ni yozing, saqlang, keyin login.bat ni qayta ishga tushiring.
  notepad config.json
  pause
  exit /b
)
.venv\Scripts\python.exe tg.py login
pause
