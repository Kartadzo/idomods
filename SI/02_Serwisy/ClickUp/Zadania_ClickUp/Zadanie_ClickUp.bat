@echo off
setlocal
rem Analiza zadania ClickUp i start sesji realizujacej (skill /zadanie).
rem Dwuklik: pyta o link do zadania ClickUp i uruchamia Claude Code w folderze Domino.
rem Wymaga: Claude Code (polecenie "claude") i konektora ClickUp.
rem Plik celowo bez polskich znakow - cmd zle je czyta w plikach .bat.

cd /d "%~dp0..\..\..\.."

set "LINK=%~1"
if "%LINK%"=="" (
    echo.
    echo  Zadanie ClickUp - analiza i start realizacji
    echo  --------------------------------------------
    set /p "LINK=Wklej link do zadania ClickUp: "
)
if "%LINK%"=="" (
    echo Nie podano linku. Koniec.
    pause
    exit /b 1
)

claude "/zadanie %LINK%"

endlocal
