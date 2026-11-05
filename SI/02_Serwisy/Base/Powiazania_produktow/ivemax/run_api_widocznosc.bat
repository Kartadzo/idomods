@echo off
chcp 65001 >nul
cd /d "%~dp0"
python api_widocznosc.py %*
pause
