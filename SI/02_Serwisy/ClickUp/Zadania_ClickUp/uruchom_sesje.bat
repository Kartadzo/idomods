@echo off
setlocal
rem Otwiera nowe okno terminala z Claude Code w podanym folderze (skill /zadanie).
rem Uzycie: uruchom_sesje.bat "<folder>" "<prompt startowy>" ["<tytul okna>"]
rem Prompt bez polskich znakow - cmd zle je przekazuje. Szczegoly zadania sa w ANALIZA_*.md w folderze.
rem Test: set ZADANIE_KOMENDA=<inny program> podmienia "claude" (np. sonde zapisujaca argumenty).
rem Plik celowo bez polskich znakow - cmd zle je czyta w plikach .bat.

set "FOLDER=%~1"
set "PROMPT=%~2"
set "TYTUL=%~3"
if "%TYTUL%"=="" set "TYTUL=Claude - zadanie"
set "KOMENDA=claude"
if defined ZADANIE_KOMENDA set "KOMENDA=%ZADANIE_KOMENDA%"

if "%FOLDER%"=="" (
    echo Brak folderu. Uzycie: uruchom_sesje.bat "folder" "prompt" ["tytul"]
    exit /b 1
)
if not exist "%FOLDER%\" (
    echo Folder nie istnieje: %FOLDER%
    exit /b 1
)

start "%TYTUL%" /D "%FOLDER%" cmd /k "chcp 65001 >nul & "%KOMENDA%" "%PROMPT%""
endlocal
