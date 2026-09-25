@echo off
cd /d "%~dp0"
py -3 cci_to_cia_gui.py
if errorlevel 1 pause
