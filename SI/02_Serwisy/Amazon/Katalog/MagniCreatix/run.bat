@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "%~dp0..\amazon_szablon.py" "%~dp0."
echo.
pause
