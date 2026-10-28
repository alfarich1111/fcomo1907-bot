@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PATH=%PATH%;%ProgramFiles%\GitHub CLI;%ProgramFiles%\Git\cmd;%LOCALAPPDATA%\Programs\Git\cmd"

echo === 1/4  GitHub'ga kirish (brauzer ochiladi, "alfarich1111" bilan kiring) ===
gh auth status >nul 2>&1 || gh auth login --hostname github.com --git-protocol https --web
if errorlevel 1 goto fail

echo.
echo === 2/4  Ochiq (public) repozitoriy yaratish va kodni yuklash ===
gh repo view alfarich1111/fcomo1907-bot >nul 2>&1 || gh repo create alfarich1111/fcomo1907-bot --public --source . --remote origin
if errorlevel 1 goto fail
git push -u origin main
if errorlevel 1 goto fail

echo.
echo === 3/4  API kalitlarini GitHub Secrets'ga yozish (config.json dan) ===
for /f "usebackq delims=" %%v in (`.venv\Scripts\python.exe -c "import json;print(json.load(open('config.json'))['api_id'])"`) do set "TGID=%%v"
for /f "usebackq delims=" %%v in (`.venv\Scripts\python.exe -c "import json;print(json.load(open('config.json'))['api_hash'])"`) do set "TGHASH=%%v"
gh secret set TG_API_ID --body "%TGID%"
gh secret set TG_API_HASH --body "%TGHASH%"
set "TGID="
set "TGHASH="

echo.
echo === 4/4  GitHub uchun alohida Telegram seansi (telefon raqam + kod so'raladi) ===
.venv\Scripts\python.exe tg.py export-session --gh-secret
if errorlevel 1 goto fail

echo.
echo TAYYOR! Endi Claude'ga "github tayyor" deb yozing.
pause
exit /b

:fail
echo.
echo Xatolik bo'ldi. Ekrandagi yozuvni Claude'ga yuboring.
pause
