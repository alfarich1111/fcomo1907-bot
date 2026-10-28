@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Claude Cloud uchun alohida Telegram seansi yaratiladi (telefon raqam + kod so'raladi).
echo Tayyor bo'lgach seans matni buferga (clipboard) nusxalanadi - uni claude.ai dagi TG_SESSION maydoniga Ctrl+V bilan qo'ying.
echo.
.venv\Scripts\python.exe tg.py export-session
echo.
for /f "usebackq delims=" %%v in (`.venv\Scripts\python.exe -c "import json;print(json.load(open('config.json'))['api_id'])"`) do echo TG_API_ID   = %%v
for /f "usebackq delims=" %%v in (`.venv\Scripts\python.exe -c "import json;print(json.load(open('config.json'))['api_hash'])"`) do echo TG_API_HASH = %%v
echo (bu ikkisini ham claude.ai dagi muhit sozlamalariga yozing)
pause
