@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem Worktree zadan z /zadanie (Domino\.worktrees\<temat>).
rem Po dwukliku: menu (lista, utworz, usun).
rem Skrot dla Claude'a:
rem   run_worktree.bat utworz <temat>
rem   run_worktree.bat lista
rem   run_worktree.bat usun <temat>
rem Plik celowo bez polskich znakow - cmd zle je czyta w plikach .bat.

where python >nul 2>nul
if errorlevel 1 (
  echo BLAD: nie znaleziono polecenia "python" w PATH.
  pause
  exit /b 1
)

python worktree_zadania.py %*
set KOD=%errorlevel%
if "%~1"=="" pause
exit /b %KOD%
