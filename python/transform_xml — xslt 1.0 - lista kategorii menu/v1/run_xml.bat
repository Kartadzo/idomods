@echo off
setlocal

echo -----------------------------------------
echo   Sprawdzanie środowiska Python...
echo -----------------------------------------

:: Sprawdzenie czy Python jest dostępny
python --version >nul 2>&1
if errorlevel 1 (
    echo BLAD: Python nie jest zainstalowany lub nie jest w PATH.
    echo Zainstaluj Python 3.x i sproboj ponownie.
    pause
    exit /b
)

echo Python wykryty.

echo -----------------------------------------
echo   Sprawdzanie wymaganych bibliotek...
echo -----------------------------------------

python -c "import lxml" 2>nul
if errorlevel 1 (
    echo Instalowanie brakujacej biblioteki: lxml
    pip install lxml
)

python -c "import tqdm" 2>nul
if errorlevel 1 (
    echo Instalowanie brakujacej biblioteki: tqdm
    pip install tqdm
)

echo Wszystkie wymagane biblioteki sa zainstalowane.

echo -----------------------------------------
echo   Uruchamianie aplikacji...
echo   Poprawny wynik zapisany będzie w pliku output.xml
echo -----------------------------------------

python app_xml_to_xml.py

echo -----------------------------------------
echo   Działanie aplikacji zakonczone.
echo -----------------------------------------

pause
