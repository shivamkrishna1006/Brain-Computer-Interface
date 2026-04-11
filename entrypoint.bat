@echo off
REM Entrypoint script for BCI Interface deployment on Windows
REM This script sets up the environment and runs the BCI application

setlocal enabledelayexpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "VENV_DIR=%PROJECT_ROOT%venv"
set "CONFIG_FILE=%PROJECT_ROOT%config.yaml"
set "ENV_FILE=%PROJECT_ROOT%.env"

REM Colors (using Windows API would be complex, so we'll skip colors on Windows)
color 0F

echo.
echo ============================================================
echo   BCI Interface - Windows Deployment Script
echo ============================================================
echo.

REM Check Python installation
call :check_python

REM Handle commands
if "%1%"=="" goto show_help
if "%1%"=="install" goto install_deps
if "%1%"=="train" goto train
if "%1%"=="evaluate" goto evaluate
if "%1%"=="realtime" goto realtime
if "%1%"=="shell" goto shell
if "%1%"=="verify" goto verify
if "%1%"=="help" goto show_help
if "%1%"=="--help" goto show_help
if "%1%"=="-h" goto show_help

echo Error: Unknown command: %1%
goto show_help

:check_python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7 or higher.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found
goto :eof

:create_venv
if exist "%VENV_DIR%" (
    echo [WARNING] Virtual environment already exists
    set /p response="Do you want to recreate it? (y/n): "
    if /i "%response%"=="y" (
        rmdir /s /q "%VENV_DIR%"
    ) else (
        goto :eof
    )
)
echo Creating virtual environment...
python -m venv "%VENV_DIR%"
echo [OK] Virtual environment created at %VENV_DIR%
goto :eof

:activate_venv
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    echo [OK] Virtual environment activated
) else (
    echo [ERROR] Could not find virtual environment activation script
    exit /b 1
)
goto :eof

:install_deps
echo.
echo ============================================================
echo   Installing Dependencies
echo ============================================================
echo.
call :create_venv
call :activate_venv

if not exist "%PROJECT_ROOT%requirements.txt" (
    echo [ERROR] requirements.txt not found
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo Installing packages...
pip install -r "%PROJECT_ROOT%requirements.txt"
echo [OK] Dependencies installed

if not exist "%ENV_FILE%" (
    if exist "%ENV_FILE%.example" (
        copy "%ENV_FILE%.example" "%ENV_FILE%"
        echo [OK] Environment file created from template
        echo [WARNING] Please update .env with your configuration
    )
)

call :verify_installation
echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo BCI Interface is ready to use.
echo Type: entrypoint.bat --help    for more information
echo Type: entrypoint.bat train     to train a model
goto :eof

:verify_installation
echo.
echo Verifying installation...
python -c "import tensorflow; print('TensorFlow:', tensorflow.__version__)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] TensorFlow import successful
) else (
    echo [ERROR] TensorFlow import failed
    exit /b 1
)

python -c "import numpy; print('NumPy:', numpy.__version__)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] NumPy import successful
) else (
    echo [ERROR] NumPy import failed
    exit /b 1
)

python -c "import mne; print('MNE:', mne.__version__)" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MNE import successful
) else (
    echo [ERROR] MNE import failed
    exit /b 1
)
goto :eof

:train
call :activate_venv
if exist "%ENV_FILE%" (
    REM Load environment variables from .env if needed
)
shift
python "%PROJECT_ROOT%main.py" train %*
goto :eof

:evaluate
call :activate_venv
shift
python "%PROJECT_ROOT%main.py" evaluate %*
goto :eof

:realtime
call :activate_venv
shift
python "%PROJECT_ROOT%main.py" realtime %*
goto :eof

:shell
call :activate_venv
python
goto :eof

:verify
call :activate_venv
call :verify_installation
echo Installation verification complete!
goto :eof

:show_help
echo.
echo Available commands:
echo   entrypoint.bat install    - Install dependencies
echo   entrypoint.bat train      - Train the BCI model
echo   entrypoint.bat evaluate   - Evaluate a trained model
echo   entrypoint.bat realtime   - Run in real-time mode
echo   entrypoint.bat shell      - Start Python shell
echo   entrypoint.bat verify     - Verify installation
echo   entrypoint.bat help       - Show this help message
echo.
echo Examples:
echo   entrypoint.bat install
echo   entrypoint.bat train
echo   entrypoint.bat evaluate --model bci_model
echo   entrypoint.bat realtime --model bci_model
echo.
echo For more information, see README.md
echo.
goto :eof

endlocal
