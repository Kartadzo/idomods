@echo off
setlocal
rem Diagnostyka IdoSell - Google Merchant Center (skill /weryfikacja-gmc).
rem Dwuklik: pyta o link do zadania ClickUp i uruchamia Claude Code w tym folderze.
rem Wymaga: Claude Code (polecenie "claude") i wlaczonego Claude in Chrome (/chrome).
rem Plik celowo bez polskich znakow - cmd zle je czyta w plikach .bat.

cd /d "%~dp0"

set "LINK=%~1"
if "%LINK%"=="" (
    echo.
    echo  Diagnostyka Google Merchant Center
    echo  ----------------------------------
    set /p "LINK=Wklej link do zadania ClickUp: "
)
if "%LINK%"=="" (
    echo Nie podano linku. Koniec.
    pause
    exit /b 1
)

claude "/weryfikacja-gmc %LINK%"

endlocal
