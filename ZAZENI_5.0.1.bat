@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3.10 DavcnaBlagajna.pyw
if errorlevel 1 (
  echo.
  echo Zagon 5.0.1 ni uspel. Preveri Python 3.10 in pywebview.
  pause
)
