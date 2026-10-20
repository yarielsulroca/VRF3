#!/usr/bin/env python3
"""
Build script para crear ejecutable standalone con PyInstaller
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / ".venv"
SPEC_FILE = BASE_DIR / "build.spec"

def main():
    if not VENV_DIR.exists():
        print("Entorno virtual no encontrado. Ejecuta run.py primero.")
        sys.exit(1)

    python_exe = VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "python"
    pyinstaller = VENV_DIR / "Scripts" / "pyinstaller.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "pyinstaller"

    if not pyinstaller.exists():
        print("Instalando PyInstaller...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "pyinstaller"], check=True)

    if not SPEC_FILE.exists():
        print(f"Spec file no encontrado: {SPEC_FILE}")
        sys.exit(1)

    print("Construyendo ejecutable...")
    result = subprocess.run([str(pyinstaller), str(SPEC_FILE), "--clean"])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()