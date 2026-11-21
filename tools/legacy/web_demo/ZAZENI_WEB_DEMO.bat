@echo off
setlocal
cd /d "%~dp0"
echo Blagajna Web Demo — zaganjam streznik na http://127.0.0.1:8765
echo.
py -m pip install -q -r requirements.txt 2>nul
start "" "http://127.0.0.1:8765"
py app.py
endlocal
