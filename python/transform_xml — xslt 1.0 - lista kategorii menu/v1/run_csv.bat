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
echo   Przetwarzanie pliku XML...
echo -----------------------------------------

python .\app_xml_to_csv.py

echo -----------------------------------------
echo   Przetwarzanie zakonczone.
echo   Wynik zapisano w pliku output.csv
echo -----------------------------------------

pause
