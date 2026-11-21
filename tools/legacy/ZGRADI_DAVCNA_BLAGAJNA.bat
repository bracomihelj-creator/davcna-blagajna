@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo  Gradnja DavcnaBlagajna.exe (PyInstaller)
echo ============================================
echo.

where py >nul 2>&1
if errorlevel 1 (
  echo NAPAKA: Python launcher "py" ni na PATH.
  pause
  exit /b 1
)

py -3.10 -m pip install -q --upgrade pip
py -3.10 -m pip install -q pyinstaller openpyxl selenium

if not exist "dist" mkdir "dist"

echo.
echo PyInstaller ...
py -3.10 -m PyInstaller DavcnaBlagajna.spec --noconfirm
if errorlevel 1 (
  echo.
  echo NAPAKA: gradnja ni uspela.
  pause
  exit /b 1
)

if not exist "dist\DavcnaBlagajna.exe" (
  echo NAPAKA: dist\DavcnaBlagajna.exe ni bil ustvarjen.
  pause
  exit /b 1
)

if not exist "dist\PREBERI_ME.txt" echo Opozorilo: dist\PREBERI_ME.txt manjka
if not exist "dist\ZAZENI_DavcnaBlagajna.bat" echo Opozorilo: dist\ZAZENI_DavcnaBlagajna.bat manjka
if not exist "dist\blagajna_minimax_settings.json" (
  echo Ustvarjam predlogo blagajna_minimax_settings.json ...
  copy /Y "blagajna_minimax_settings.example.json" "dist\blagajna_minimax_settings.json" >nul 2>&1
)

echo.
echo Koncano. Distribucija v mapi:
echo   %CD%\dist
echo.
dir /b dist
echo.
pause
exit /b 0
