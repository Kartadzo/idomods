@echo off
chcp 65001 >nul
cd /d "%~dp0"
python api_kod_producenta.py %*
pause
