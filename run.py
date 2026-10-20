#!/usr/bin/env python3
"""
VRF2 - Launcher para desarrollo
Ejecuta la app desde el entorno virtual
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / ".venv"
def main():
    if not VENV_DIR.exists():
        print("Entorno virtual no encontrado.")
        print("Ejecutando instalador...")
        result = subprocess.run([sys.executable, str(BASE_DIR / "src" / "install_deps.py")])
        if result.returncode != 0:
            print("Error en la instalación.")
            sys.exit(1)

    python_exe = VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "python"

    if not python_exe.exists():
        print(f"Python no encontrado en {python_exe}")
        sys.exit(1)

    print("Iniciando VRF2 - Libro Compras...")
    result = subprocess.run(
        [str(python_exe), "-m", "src.main"],
        cwd=str(BASE_DIR),
    )
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()