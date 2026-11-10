@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Historia zmian sterownikow XSLT w panelu IdoSell.
rem Po dwukliku: menu (odbiornik dla Claude in Chrome, porownanie zrzutow,
rem kontrola przed zamknieciem projektu, lista zrzutow).
rem
rem Polecenia (skrot dla Claude'a), np.:
rem   run_historia.bat odbiornik
rem   run_historia.bat zloz --klient ezebra --sesja ^<sesja^>
rem   run_historia.bat kontrola --klient ezebra
rem Pelna lista: python historia.py -h

where python >nul 2>nul
if errorlevel 1 (
  echo BLAD: nie znaleziono polecenia "python" w PATH.
  echo Zainstaluj Pythona 3.8+ albo uruchom skrypt z pelna sciezka do python.exe
  echo.
  pause
  exit /b 1
)

python historia.py %*

echo.
pause
