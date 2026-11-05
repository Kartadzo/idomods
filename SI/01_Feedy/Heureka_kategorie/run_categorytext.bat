@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Skladanie bloku CATEGORYTEXT dla feedu Heureka z raportow app.py.
rem Skrypt pyta o pliki wejsciowe (gdy jest tylko jeden kandydat, bierze go sam):
rem   raport_idosell_<lang>.csv, raport_google_<lang>.csv,
rem   povinne nazvy <lang> - *.csv, arkusz feedu *.xml
rem
rem Wyjscie: heureka_categorytext.xslt oraz blok HEUREKA-MAP wstawiony
rem do arkusza feedu (kopia zapasowa arkusza ladzie obok jako *.xml.bak).
rem
rem Najpierw uruchom run.bat - to on wytwarza raporty, ktore czyta ten skrypt.

where python >nul 2>nul
if errorlevel 1 (
  echo BLAD: nie znaleziono polecenia "python" w PATH.
  echo Zainstaluj Pythona 3.8+ albo uruchom skrypt z pelna sciezka do python.exe
  echo.
  pause
  exit /b 1
)

python build_categorytext.py

echo.
pause
