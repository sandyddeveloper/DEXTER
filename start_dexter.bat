@echo off
chcp 65001 > nul
title DEXTER OS - INITIALIZING SYSTEMS
color 0f
cls

cd /d "%~dp0"
:: Use the venv python to launch the system
".\venv\Scripts\python.exe" -m src.main
pause
