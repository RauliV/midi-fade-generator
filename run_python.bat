@echo off
REM Wrapper script to run Python with correct environment on Windows
REM This script tries different Python options to ensure midiutil is available

set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%valot_python_backend.py

REM List of Python commands to try, in order of preference
set PYTHON_COMMANDS=python python3 py "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"

for %%p in (%PYTHON_COMMANDS%) do (
    where %%p >nul 2>&1
    if not errorlevel 1 (
        %%p -c "import midiutil" >nul 2>&1
        if not errorlevel 1 (
            echo Using Python: %%p >&2
            %%p "%PYTHON_SCRIPT%" %*
            exit /b %errorlevel%
        ) else (
            echo Python %%p found but midiutil not available >&2
        )
    ) else (
        echo Python command %%p not found >&2
    )
)

echo Error: No suitable Python with midiutil found >&2
echo Please install midiutil with: pip install midiutil >&2
exit /b 1