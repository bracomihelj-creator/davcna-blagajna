@echo off
setlocal
cd /d "%~dp0dist"
if not exist "DavcnaBlagajna.exe" (
  echo NAPAKA: DavcnaBlagajna.exe ni najden v podmapi "dist".
  echo Najprej zgradi EXE z ZGRADI_DAVCNA_BLAGAJNA.bat
  pause
  exit /b 1
)
if not exist "blagajna_minimax_settings.json" (
  if exist "..\blagajna_minimax_settings.json" (
    copy /Y "..\blagajna_minimax_settings.json" "blagajna_minimax_settings.json" >nul
  )
) else (
  findstr /C:"\"minimax_client_id\": \"\"" "blagajna_minimax_settings.json" >nul 2>&1
  if not errorlevel 1 (
    if exist "..\blagajna_minimax_settings.json" (
      copy /Y "..\blagajna_minimax_settings.json" "blagajna_minimax_settings.json" >nul
    )
  )
)
start "" "DavcnaBlagajna.exe"
endlocal
