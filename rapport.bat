@echo off
REM Rapport quotidien automatique (Windows) : appelle l'API et archive le rapport.
REM Peut être planifié avec le Planificateur de tâches Windows.
cd /d "%~dp0"
python rapport.py %1
if errorlevel 1 (
    echo Echec de la generation du rapport.
    exit /b 1
)
if not exist rapports mkdir rapports
move /y rapport_*.txt rapports\ >nul
echo Rapport archive dans le dossier rapports.