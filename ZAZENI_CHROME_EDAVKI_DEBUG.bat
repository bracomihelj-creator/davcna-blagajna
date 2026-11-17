@echo off

setlocal EnableExtensions

cd /d "%~dp0"



set "PORT=9222"



echo === Chrome eDavki + debug port %PORT% ===

echo.

echo NOVO (pomembno):

echo   - Tvoj OBICAJNI Chrome (Gmail, ...) LAHKO ostane odprt.

echo   - Odpre se LOČENO okno z profilom BlagajnaFURS\ChromeEdavki.

echo   - Enkrat se prijavi v eDavke s certifikatom v tem oknu.

echo   - Debug port 9222 deluje v tem profilu (privzeti profil pogosto NE).

echo.

echo Ce port ze deluje, skripta ne naredi nic.

echo Za popolni restart eDavki Chrome: python _start_chrome_edavki_debug.py --restart

echo.

pause



python "%~dp0_start_chrome_edavki_debug.py" --port %PORT% --wait-sec 60

set "RC=%ERRORLEVEL%"



if %RC% NEQ 0 (

  echo.

  echo Diagnostika: python "%~dp0_check_chrome_debug.py"

  echo.

  pause

  exit /b %RC%

)



echo.

echo Pripravljeno. Pusti eDavki Chrome okno odprto.

echo.

echo Preverba (v NASLOVNO vrstico eDavki Chrome okna, ne obicajnega):

echo   http://127.0.0.1:%PORT%/json/version

echo   (NE samo http://127.0.0.1 — brez :%PORT% vedno ERR_CONNECTION_REFUSED)

pause

exit /b 0

