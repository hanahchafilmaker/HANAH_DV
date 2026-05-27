@echo off
title Thesis Tool Test Runner

echo ============================================
echo Thesis Tool - System Test
echo ============================================
echo.

echo [1/3] Running test_final.py ...
python test_final.py

if errorlevel 1 (
    echo.
    echo [ERROR] test_final.py failed
    pause
    exit /b
)

echo.
echo ============================================
echo [2/3] Running test_tkinter_fn_id.py ...
echo ============================================
echo.

python test_tkinter_fn_id.py

if errorlevel 1 (
    echo.
    echo [ERROR] test_tkinter_fn_id.py failed
    pause
    exit /b
)

echo.
echo ============================================
echo [3/3] Launching main_gui.py ...
echo ============================================
echo.

python main_gui.py

echo.
echo Program closed.
pause