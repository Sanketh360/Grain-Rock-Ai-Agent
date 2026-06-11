@echo off
title Grain Rock Launcher
color 0A

echo.
echo  ======================================
echo    GRAIN ROCK - Starting Up...
echo  ======================================
echo.

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found!
    echo  Please install Python from python.org
    pause
    exit /b 1
)

:: Go to correct GrainRock folder on D drive
cd /d "D:\GrainRock"

:: Check if virtual environment exists
if not exist "grainrock-env\Scripts\activate.bat" (
    echo  ERROR: Virtual environment not found!
    echo  Looking in: D:\GrainRock\grainrock-env
    echo  Please make sure you created it here.
    pause
    exit /b 1
)

:: Activate virtual environment
call grainrock-env\Scripts\activate.bat

:: Launch Grain Rock
echo  Launching Grain Rock...
echo.
python main.py

:: If python exits with error
if errorlevel 1 (
    echo.
    echo  Grain Rock closed with an error.
    pause
)