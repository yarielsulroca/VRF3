import sys
import subprocess
import os
import venv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import ctypes


BASE_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = BASE_DIR / ".venv"
REQUIREMENTS = BASE_DIR / "requirements.txt"
VC_REDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
VC_REDIST_PATH = BASE_DIR / "vc_redist.x64.exe"


class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VRF2 - Instalador de dependencias")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        self.center_window()

        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Preparando...")

        self.setup_ui()
        self.root.after(100, self.start_installation)

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 250
        y = (self.root.winfo_screenheight() // 2) - 150
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="VRF2 - Libro Compras", font=("Segoe UI", 16, "bold")).pack(pady=(0, 8))
        ttk.Label(frame, text="Instalando dependencias por primera vez...", font=("Segoe UI", 10)).pack(pady=(0, 20))

        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 9)).pack()

        self.detail_text = tk.Text(frame, height=6, width=55, font=("Consolas", 8), state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=scroll.set)

        self.btn_frame = ttk.Frame(frame)
        self.btn_frame.pack(fill=tk.X, pady=(15, 0))

        self.close_btn = ttk.Button(self.btn_frame, text="Cerrar", command=self.root.quit, state=tk.DISABLED)
        self.close_btn.pack(side=tk.RIGHT)

        self.retry_btn = ttk.Button(self.btn_frame, text="Reintentar", command=self.start_installation, state=tk.DISABLED)
        self.retry_btn.pack(side=tk.RIGHT, padx=5)

    def log(self, msg: str):
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.insert(tk.END, msg + "\n")
        self.detail_text.see(tk.END)
        self.detail_text.configure(state=tk.DISABLED)

    def update_progress(self, pct: float, status: str):
        self.progress_var.set(pct)
        self.status_var.set(status)
        self.root.update_idletasks()

    def start_installation(self):
        self.retry_btn.configure(state=tk.DISABLED)
        self.close_btn.configure(state=tk.DISABLED)
        self.progress_var.set(0)
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.configure(state=tk.DISABLED)

        threading.Thread(target=self.run_installation, daemon=True).start()

    def run_installation(self):
        try:
            self.update_progress(5, "Verificando Python...")
            self.log(f"Python: {sys.version}")

            if not self.is_admin():
                self.log("⚠ Ejecutando sin permisos de administrador. VC++ Redist podría fallar.")

            self.update_progress(10, "Creando entorno virtual...")
            self.create_venv()

            self.update_progress(30, "Actualizando pip...")
            self.run_pip(["install", "--upgrade", "pip"])

            self.update_progress(40, "Instalando dependencias Python...")
            self.install_requirements()

            self.update_progress(80, "Verificando Visual C++ Redistributable...")
            self.install_vc_redist()

            self.update_progress(95, "Creando accesos directos...")
            self.create_shortcuts()

            self.update_progress(100, "¡Instalación completada!")
            self.log("✅ Todo listo. Puede ejecutar la aplicación.")
            self.root.after(0, self.on_success)

        except Exception as e:
            self.log(f"❌ Error: {e}")
            self.root.after(0, lambda: self.on_error(str(e)))

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_venv(self):
        if VENV_DIR.exists():
            self.log("Entorno virtual ya existe, omitiendo...")
            return
        venv.create(VENV_DIR, with_pip=True)
        self.log("✅ Entorno virtual creado")

    def get_python(self):
        if sys.platform == "win32":
            return str(VENV_DIR / "Scripts" / "python.exe")
        return str(VENV_DIR / "bin" / "python")

    def run_pip(self, args):
        python = self.get_python()
        cmd = [python, "-m", "pip"] + args
        self.log(f"$ {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(f"pip falló: {detail}")
        if result.stdout:
            self.log(result.stdout.strip())

    def install_requirements(self):
        if not REQUIREMENTS.exists():
            raise FileNotFoundError("requirements.txt no encontrado")

        with open(REQUIREMENTS) as f:
            pkgs = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        for i, pkg in enumerate(pkgs):
            pct = 40 + int((i / len(pkgs)) * 40)
            self.update_progress(pct, f"Instalando {pkg}...")
            self.run_pip(["install", pkg])
            self.log(f"✅ {pkg}")

    def install_vc_redist(self):
        try:
            import ctypes
            ctypes.windll.msvcrt
            self.log("✅ VC++ Redist ya disponible")
            return
        except:
            pass

        if not VC_REDIST_PATH.exists():
            self.log("Descargando VC++ Redistributable...")
            self.download_file(VC_REDIST_URL, VC_REDIST_PATH)

        self.log("Instalando VC++ Redistributable (requiere admin)...")
        result = subprocess.run(
            [str(VC_REDIST_PATH), "/install", "/quiet", "/norestart"],
            capture_output=True, timeout=300
        )
        if result.returncode in (0, 3010, 1638):
            self.log("✅ VC++ Redist instalado")
        else:
            self.log(f"⚠ VC++ Redist: código {result.returncode} (puede requerir instalación manual)")

    def download_file(self, url, dest):
        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                pct = min(100, (block_num * block_size * 100) // total_size)
                self.update_progress(80 + pct // 5, f"Descargando VC++ Redist... {pct}%")

        urllib.request.urlretrieve(url, dest, reporthook)

    def create_shortcuts(self):
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            start_menu = winshell.start_menu()

            python_exe = self.get_python()
            icon = BASE_DIR / "assets" / "icon.ico"

            for folder, name in [(desktop, "VRF2 Libro Compras"), (start_menu / "Programs", "VRF2 Libro Compras")]:
                shortcut_path = Path(folder) / f"{name}.lnk"
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = python_exe
                shortcut.Arguments = "-m src.main"
                shortcut.WorkingDirectory = str(BASE_DIR)
                if icon.exists():
                    shortcut.IconLocation = str(icon)
                shortcut.save()
                self.log(f"✅ Acceso directo: {shortcut_path}")

        except ImportError:
            self.log("⚠ winshell/pywin32 no disponible, omitiendo accesos directos")
        except Exception as e:
            self.log(f"⚠ Error creando accesos directos: {e}")

    def on_success(self):
        self.close_btn.configure(state=tk.NORMAL)
        messagebox.showinfo("Éxito", "Instalación completada.\n\nAhora puede ejecutar la aplicación desde el acceso directo en el Escritorio o Menú Inicio.")

    def on_error(self, error: str):
        self.retry_btn.configure(state=tk.NORMAL)
        self.close_btn.configure(state=tk.NORMAL)
        messagebox.showerror("Error", f"Falló la instalación:\n{error}\n\nPuede reintentar o instalar manualmente.")

    def run(self):
        self.root.mainloop()


def main():
    if VENV_DIR.exists() and (BASE_DIR / "src" / "main.py").exists():
        python_exe = VENV_DIR / "Scripts" / "python.exe" if sys.platform == "win32" else VENV_DIR / "bin" / "python"
        if python_exe.exists():
            os.chdir(BASE_DIR)
            os.execv(str(python_exe), [str(python_exe), "-m", "src.main"])

    app = InstallerGUI()
    app.run()


if __name__ == "__main__":
    main()