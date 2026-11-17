@echo off

setlocal EnableExtensions

cd /d "%~dp0"

set "PORT=9223"

echo === Chrome Minimax KIR/KPR + debug port %PORT% ===
echo.
echo NOVO (pomembno):
echo   - Tvoj OBICAJNI Chrome LAHKO ostane odprt.
echo   - eDavki Chrome (port 9222) LAHKO ostane odprt.
echo   - Odpre se LOČENO okno z profilom MinimaxBlagajna\ChromeMinimax.
echo   - Enkrat se prijavi v Minimax v tem oknu.
echo.
echo Ce port ze deluje, skripta ne naredi nic.
echo Za popolni restart: python _start_chrome_minimax_debug.py --restart
echo.
pause

python "%~dp0_start_chrome_minimax_debug.py" --port %PORT% --wait-sec 60
set "RC=%ERRORLEVEL%"

if %RC% NEQ 0 (
  echo.
  echo Diagnostika: python "%~dp0_check_chrome_debug.py"
  echo.
  pause
  exit /b %RC%
)

echo.
echo Pripravljeno. Pusti Minimax Chrome okno odprto.
echo.
echo Preverba (v NASLOVNO vrstico Minimax Chrome okna):
echo   http://127.0.0.1:%PORT%/json/version
echo.
pause
exit /b 0
