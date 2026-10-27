@echo off
setlocal

echo -----------------------------------------
echo   Sprawdzanie srodowiska Python...
echo -----------------------------------------

:: Sprawdzenie czy Python jest dostepny
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

:: Sprawdz lxml
python -c "import lxml" 2>nul
if errorlevel 1 (
    echo Instalowanie brakujacej biblioteki: lxml
    pip install lxml
)

:: Sprawdz tqdm
python -c "import tqdm" 2>nul
if errorlevel 1 (
    echo Instalowanie brakujacej biblioteki: tqdm
    pip install tqdm
)

echo Wszystkie wymagane biblioteki sa zainstalowane.

echo -----------------------------------------
echo   Przetwarzanie pliku XML...
echo -----------------------------------------

python .\app_xml_to_xml.py
if errorlevel 1 (
    echo -----------------------------------------
    echo   Przerwano przetwarzanie aplikacji.
    echo -----------------------------------------
    pause
    exit /b
)

echo -----------------------------------------
echo   Przetwarzanie zakonczone.
echo   Wynik zapisano w pliku output.xml
echo -----------------------------------------

pause
