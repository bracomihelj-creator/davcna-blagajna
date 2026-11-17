@echo off
setlocal
cd /d "%~dp0"

rem Davčna Blagajna 3.0* — zagon S konzolo (za napake)
rem Brez konzole: Zagon_davcnaBlagajna_V3.bat

if defined TCL_LIBRARY (
  if not exist "%TCL_LIBRARY%" set "TCL_LIBRARY="
)
if defined TK_LIBRARY (
  if not exist "%TK_LIBRARY%" set "TK_LIBRARY="
)
echo %TCL_LIBRARY% | find /I "_MEI" >nul && set "TCL_LIBRARY="
echo %TK_LIBRARY% | find /I "_MEI" >nul && set "TK_LIBRARY="

py -3.10 "%~dp0DavcnaBlagajna_v2_1.py"
if errorlevel 1 (
  echo.
  echo Program se je koncal z napako.
  pause
)
endlocal
