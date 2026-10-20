import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional
import threading
import queue

from src.config import DOCS_DIR, APP_CONFIG
from src.services.excel_processor import ExcelProcessor, TaxCalculator
from src.ui.data_table import DataTable
from src.ui.filter_panel import FilterPanel
from src.ui.tax_cards import TaxSummaryCards
from src.models.invoice import Invoice


ctk.set_appearance_mode(APP_CONFIG["theme"])
ctk.set_default_color_theme(APP_CONFIG["color_theme"])


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_CONFIG["app_name"])
        self.geometry(f"{APP_CONFIG['window_size'][0]}x{APP_CONFIG['window_size'][1]}")
        self.minsize(*APP_CONFIG["min_window_size"])
        self.after(0, lambda: self.state("zoomed"))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.processor = ExcelProcessor()
        self.calculator = TaxCalculator()
        self._invoices: list[Invoice] = []
        self._excel_path: Optional[Path] = None
        self._load_queue = queue.Queue()
        self._loading = False
        self._loading_new_file = False

        self._create_layout()
        self._setup_menu()
        self._show_empty_state()

        self.after(100, self._check_load_queue)

    # --- layout ---

    def _create_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.header = self._create_header()
        self.header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 6))
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.filter_panel = FilterPanel(self.main_frame, on_filter_change=self._on_filter_change)
        self.cards = TaxSummaryCards(self.main_frame)
        self.table = DataTable(self.main_frame, on_row_select=self._on_row_select)
        self.empty_state = self._create_empty_state()

        self.footer = ctk.CTkFrame(self, height=1, fg_color="transparent")
        self.footer.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        self.footer.grid_columnconfigure(0, weight=1)

        self.status_bar = ctk.CTkLabel(
            self.footer,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
            anchor="w",
        )
        self.status_bar.grid(row=0, column=0, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.footer, width=260)
        self.progress_bar.set(0)

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text=APP_CONFIG["app_name"],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("blue", "#4fc3f7"),
        ).grid(row=0, column=0, padx=8, pady=8, sticky="w")

        self.file_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray65"),
            anchor="w",
        )
        self.file_label.grid(row=0, column=1, padx=8, pady=8, sticky="w")

        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=8, pady=8, sticky="e")

        self.reload_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Recargar",
            width=120,
            height=34,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            state="disabled",
            command=self._load_excel_async,
        )
        self.reload_btn.pack(side="right", padx=4)

        self.open_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Abrir Excel...",
            width=140,
            height=34,
            command=self._open_file_dialog,
        )
        self.open_btn.pack(side="right", padx=4)

        return header

    def _create_empty_state(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_frame, fg_color=("gray92", "gray16"), corner_radius=12)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(frame, text="📄", font=ctk.CTkFont(size=48)).grid(row=1, column=0, pady=(0, 8))
        ctk.CTkLabel(
            frame,
            text="Seleccioná el Libro IVA Compras del mes",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=2, column=0, pady=(0, 6))
        ctk.CTkLabel(
            frame,
            text="Archivo Excel (.xlsx) con la estructura habitual: FECHA, NUMERO, DETALLE, 0.21, TOTAL...",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray60"),
        ).grid(row=3, column=0, pady=(0, 18))

        self.empty_open_btn = ctk.CTkButton(
            frame,
            text="📂 Seleccionar Excel",
            width=220,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._open_file_dialog,
        )
        self.empty_open_btn.grid(row=4, column=0)
        return frame

    def _show_empty_state(self):
        self.filter_panel.grid_remove()
        self.cards.grid_remove()
        self.table.grid_remove()
        self.main_frame.grid_rowconfigure(2, weight=0, minsize=0)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.file_label.configure(text="")
        self.status_bar.configure(text="Sin archivo cargado")

    def _show_data_view(self):
        self.empty_state.grid_remove()
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=1, minsize=260)
        self.filter_panel.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.cards.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self.table.grid(row=2, column=0, sticky="nsew")

    def _setup_menu(self):
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Control-o>", lambda e: self._open_file_dialog())
        self.bind("<Control-r>", lambda e: self._load_excel_async())
        self.bind("<Escape>", lambda e: self.filter_panel.clear_filters())

    # --- carga ---

    def _open_file_dialog(self):
        if self._loading:
            return
        if self._excel_path is not None:
            initial_dir = self._excel_path.parent
        elif DOCS_DIR.exists():
            initial_dir = DOCS_DIR
        else:
            initial_dir = Path.home() / "Documents"

        file_path = filedialog.askopenfilename(
            title="Seleccionar Libro IVA Compras",
            initialdir=str(initial_dir),
            filetypes=[("Excel", "*.xlsx *.xlsm"), ("Todos los archivos", "*.*")],
        )
        if file_path:
            self._loading_new_file = True
            self._load_excel_async(Path(file_path))

    def _load_excel_async(self, path: Optional[Path] = None):
        path = path or self._excel_path
        if self._loading or path is None:
            return

        self._loading = True
        self.open_btn.configure(state="disabled")
        self.empty_open_btn.configure(state="disabled")
        self.reload_btn.configure(state="disabled", text="⏳ Cargando...")
        self.status_bar.configure(text=f"Cargando {path.name}...")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=(8, 0), sticky="e")

        def load_worker():
            try:
                def progress(current, total):
                    self._load_queue.put(("progress", current, total))

                invoices, _ = self.processor.load(path, progress)
                self._load_queue.put(("success", path, invoices, list(self.processor.missing_money_columns)))
            except Exception as e:
                self._load_queue.put(("error", path, str(e)))

        threading.Thread(target=load_worker, daemon=True).start()

    def _check_load_queue(self):
        try:
            while True:
                msg = self._load_queue.get_nowait()
                if msg[0] == "progress":
                    current, total = msg[1], msg[2]
                    self.progress_bar.set(min(current / total, 1.0) if total else 0)
                    self.status_bar.configure(text=f"Cargando... {current:,}/{total:,}".replace(",", "."))
                elif msg[0] == "success":
                    self._on_load_success(msg[1], msg[2], msg[3])
                elif msg[0] == "error":
                    self._on_load_error(msg[1], msg[2])
                elif msg[0] == "file_changed":
                    self.status_bar.configure(text="📁 Excel modificado - Recargando...")
                    self.after(500, self._load_excel_async)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_load_queue)

    def _finish_loading(self):
        self._loading = False
        self._loading_new_file = False
        self.progress_bar.grid_remove()
        self.open_btn.configure(state="normal")
        self.empty_open_btn.configure(state="normal")
        self.reload_btn.configure(
            state="normal" if self._excel_path else "disabled",
            text="🔄 Recargar",
        )

    def _on_load_success(self, path: Path, invoices: list[Invoice], missing_columns: list[str]):
        is_new_file = self._loading_new_file or path != self._excel_path
        self._excel_path = path
        self._invoices = invoices
        self._finish_loading()

        self.filter_panel.set_tipo_options(
            sorted(set(inv.tipo_comprobante for inv in invoices if inv.tipo_comprobante))
        )
        self.filter_panel.set_detalle_options(sorted(set(inv.proveedor for inv in invoices if inv.proveedor)))
        self.table.set_invoices(invoices)
        self._show_data_view()
        self.file_label.configure(text=f"📄 {path.name}")

        if is_new_file:
            self.filter_panel.clear_filters()
        else:
            self._on_filter_change(self.filter_panel.get_filters())
        self.status_bar.configure(
            text=f"Cargadas {len(invoices):,} facturas desde {path.name}".replace(",", ".")
        )

        self.processor.start_watcher(lambda: self._load_queue.put(("file_changed",)))

        if missing_columns and is_new_file:
            messagebox.showwarning(
                "Columnas no encontradas",
                f"En {path.name} no se encontraron estas columnas de importes:\n\n"
                f"{', '.join(missing_columns)}\n\n"
                "Se muestran en $ 0,00. Revisá los encabezados del Excel si deberían tener datos.",
            )

    def _on_load_error(self, path: Path, error: str):
        self._finish_loading()
        if self._excel_path is None:
            self._show_empty_state()
        else:
            self.status_bar.configure(text=f"Error al cargar {path.name}; se mantiene {self._excel_path.name}")
        messagebox.showerror("Error", f"No se pudo cargar {path.name}:\n{error}")

    # --- interacción ---

    def _on_filter_change(self, filters: dict):
        if not self._invoices:
            return
        self.table.apply_filters(filters)
        filtered = self.table.get_filtered_invoices()
        self.cards.update_summary(self.calculator.calculate(filtered))
        self.status_bar.configure(
            text=f"Mostrando {len(filtered):,} de {len(self._invoices):,} facturas".replace(",", ".")
        )

    def _on_row_select(self, invoice: Invoice):
        self.status_bar.configure(
            text=f"Seleccionada: {invoice.tipo_comprobante} {invoice.numero_comprobante} - {invoice.proveedor[:50]}"
        )

    def _on_close(self):
        self.processor.stop_watcher()
        self.destroy()


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
