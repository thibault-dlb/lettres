@echo off
rem Double-clic pour lancer le logiciel (Windows). Trouve Python, propose de l'installer si besoin.
cd /d "%~dp0"

py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3 lancer.py %*
    goto :fin
)

python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    python lancer.py %*
    goto :fin
)

echo Python est introuvable sur cet ordinateur.
set /p REPONSE=Installer Python automatiquement avec winget ? (O/N) :
if /i "%REPONSE%"=="O" (
    winget install -e --id Python.Python.3.12
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 (
        py -3 lancer.py %*
        goto :fin
    )
    echo.
    echo Python est installe. Ferme cette fenetre puis relance lancer.bat.
) else (
    echo.
    echo Installe Python depuis https://www.python.org/downloads/ puis relance lancer.bat.
    echo Pense a cocher "Add python.exe to PATH" pendant l'installation.
)
pause
exit /b 1

:fin
if errorlevel 1 pause
