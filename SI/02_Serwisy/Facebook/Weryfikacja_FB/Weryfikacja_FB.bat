@echo off
setlocal
rem Weryfikacja integracji IdoSell - Meta Ads (skill /weryfikacja-fb).
rem Dwuklik: pyta o link do zadania ClickUp i uruchamia Claude Code w tym folderze.
rem Wymaga: Claude Code (polecenie "claude") i wlaczonego Claude in Chrome (/chrome).
rem Plik celowo bez polskich znakow - cmd zle je czyta w plikach .bat.

cd /d "%~dp0"

set "LINK=%~1"
if "%LINK%"=="" (
    echo.
    echo  Weryfikacja integracji z Meta Ads
    echo  ---------------------------------
    set /p "LINK=Wklej link do zadania ClickUp: "
)
if "%LINK%"=="" (
    echo Nie podano linku. Koniec.
    pause
    exit /b 1
)

claude "/weryfikacja-fb %LINK%"

endlocal
