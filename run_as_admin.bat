@echo off
cd /d "%~dp0"
powershell -Command "Start-Process -FilePath 'python.exe' -ArgumentList 'ui_locator_gui.py' -Verb RunAs"