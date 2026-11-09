@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Porownanie sterownika XSLT z panelu IdoSell (schowek) z plikiem lokalnym w xslt/.
rem Po dwukliku: klient -> plik -> schowek -> folder na diff -> podmiana [T/n].
rem
rem Opcje (wszystkie opcjonalne):
rem   --lokalny ^<sciezka^>        plik lokalny sterownika
rem   --panel ^<sciezka^>          tekst z panelu z pliku zamiast schowka
rem   --folder-zadania ^<sciezka^> gdzie zapisac porownanie_*.diff
rem   --zastap / --bez-zmian     podmiana bez pytania / tylko porownanie
rem   --html                     dodatkowo podglad roznic w HTML

where python >nul 2>nul
if errorlevel 1 (
  echo BLAD: nie znaleziono polecenia "python" w PATH.
  echo Zainstaluj Pythona 3.8+ albo uruchom skrypt z pelna sciezka do python.exe
  echo.
  pause
  exit /b 1
)

python porownaj_sterownik.py %*

echo.
pause
