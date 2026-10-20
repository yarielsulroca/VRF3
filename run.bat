@echo off
REM VRF2 - Launcher para desarrollo
REM Ejecuta la app desde el entorno virtual

cd /d "%~dp0"

if not exist ".venv" (
    echo Entorno virtual no encontrado.
    echo Ejecutando instalador...
    python src\install_deps.py
    if errorlevel 1 (
        echo Error en la instalacion.
        pause
        exit /b 1
    )
)

echo Iniciando VRF2 - Libro Compras...
.venv\Scripts\python.exe -m src.main

if errorlevel 1 (
    echo.
    echo La aplicacion termino con errores.
    pause
)