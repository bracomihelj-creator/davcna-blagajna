@echo off
setlocal
cd /d "%~dp0"

rem Davčna Blagajna 3.0* — firme iz SQL EvidencaFirm (dbo.Clients)
rem DDV zavezanec / Ni zavezanec = stolpec OddajaDdv iz tega seznama
rem Stara 2.2.29 (Excel): ZAZENI_DavcnaBlagajna_2.2.29_ARHIV.bat
rem Konzola/napake: ZAZENI_DavcnaBlagajna_PY.bat

if defined TCL_LIBRARY (
  if not exist "%TCL_LIBRARY%" set "TCL_LIBRARY="
)
if defined TK_LIBRARY (
  if not exist "%TK_LIBRARY%" set "TK_LIBRARY="
)
echo %TCL_LIBRARY% | find /I "_MEI" >nul && set "TCL_LIBRARY="
echo %TK_LIBRARY% | find /I "_MEI" >nul && set "TK_LIBRARY="

where pyw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pyw -3.10 "%~dp0DavcnaBlagajna.pyw"
  endlocal
  exit /b 0
)

where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pythonw "%~dp0DavcnaBlagajna.pyw"
  endlocal
  exit /b 0
)

echo NAPAKA: pyw/pythonw ni v PATH.
echo Namesti Python ali zaženi ZAZENI_DavcnaBlagajna_PY.bat (s konzolo).
pause
endlocal
exit /b 1
