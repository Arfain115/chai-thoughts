@echo off
title chai review
cd /d "%~dp0"
python chai_review.py
if errorlevel 1 (
    echo.
    echo  python failed to run. is Python installed and on PATH?
    pause
)
