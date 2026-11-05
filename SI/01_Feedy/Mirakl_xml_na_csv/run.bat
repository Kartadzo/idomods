@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "%~dp0mirakl_xml_na_csv.py"
if errorlevel 9009 (
  echo.
  echo Nie znaleziono Pythona w PATH. Zainstaluj Python 3.8+ lub uruchom recznie.
  pause
)
