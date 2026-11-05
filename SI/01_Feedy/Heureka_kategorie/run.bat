@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Mapowanie kategorii na kategorie Heureka (Heureka.cz / Heureka.sk).
rem Skrypt zadaje trzy pytania: plik Heureki, zrodlo kategorii, plik zrodlowy.
rem
rem Opcje (wszystkie opcjonalne):
rem   --zrodlo google ^| idosell   pomija pytanie o zrodlo kategorii
rem   --auto                      bez pytan; bierze pierwszy pasujacy plik
rem   --tylko-pewne               do XSLT trafiaja wylacznie dopasowania fuzzy_high
rem   --z-wezlami                 do XSLT trafiaja takze wezly posrednie drzewa
rem
rem Wyjscie: raport_<zrodlo>_<lang>.csv oraz <zrodlo>_to_heureka_<lang>.xslt

where python >nul 2>nul
if errorlevel 1 (
  echo BLAD: nie znaleziono polecenia "python" w PATH.
  echo Zainstaluj Pythona 3.8+ albo uruchom skrypt z pelna sciezka do python.exe
  echo.
  pause
  exit /b 1
)

python app.py %*

echo.
pause
