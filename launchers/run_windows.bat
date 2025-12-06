@echo off
REM Lanzador sencillo para Windows (CMD).
REM Asume que Python está en el PATH.

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"
python "%SCRIPT_DIR%\main.py"
pause
