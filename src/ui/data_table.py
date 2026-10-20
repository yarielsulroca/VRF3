import customtkinter as ctk
import tkinter.ttk as ttk
from typing import List, Callable, Optional
from datetime import date
from src.models.invoice import Invoice
from src.config import APP_CONFIG, LIBRO_SCHEMA

# Columna extra para filtrar (no está en el Excel, se deduce de Fact. A / C)
TIPO_COLUMN = ("tipo_comprobante", "Tipo", 56)

COLUMN_WIDTHS = {
    "fecha": 100,
    "numero_comprobante": 90,
    "proveedor": 220,
    "cuit": 110,
    "factura_c": 100,
    "factura_a": 100,
    "iva_21": 95,
    "iva_105": 95,
    "iva_27": 95,
    "iva_105_alt": 95,
    "neto_no_gravado": 90,
    "percepcion_iva": 90,
    "percepcion_iibb": 90,
    "total": 110,
}


class DataTable(ctk.CTkFrame):
    def __init__(self, master, on_row_select: Optional[Callable] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color=("white", "gray10"))
        self.on_row_select = on_row_select

        self._all_invoices: List[Invoice] = []
        self._filtered_invoices: List[Invoice] = []
        self._sort_column: Optional[str] = None
        self._sort_reverse = False
        self._columns: List[tuple] = []

        self._create_widgets()
        self._apply_schema_columns()
        self._layout_widgets()

    def _schema_columns(self) -> List[tuple]:
        cols = []
        for item in LIBRO_SCHEMA:
            key = item["key"]
            label = item["label"]
            width = COLUMN_WIDTHS.get(key, 100 if item.get("kind") == "money" else 90)
            cols.append((key, label, width))
        cols.append(TIPO_COLUMN)
        return cols

    def _apply_schema_columns(self):
        self._columns = self._schema_columns()
        columns = [c[0] for c in self._columns]
        self.tree.configure(columns=columns)
        for col_id, col_name, col_width in self._columns:
            self.tree.heading(col_id, text=col_name, command=lambda c=col_id: self._on_header_click(c))
            anchor = "w" if col_id in ("proveedor", "numero_comprobante", "cuit") else "e"
            self.tree.column(col_id, width=col_width, minwidth=60, anchor=anchor)

    def _create_widgets(self):
        self.tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        columns = [c[0] for c in self._schema_columns()]
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#1e1e1e" if APP_CONFIG["theme"] == "dark" else "white",
            foreground="white" if APP_CONFIG["theme"] == "dark" else "black",
            fieldbackground="#1e1e1e" if APP_CONFIG["theme"] == "dark" else "white",
            borderwidth=0,
            font=("Segoe UI", 10),
            rowheight=28,
        )
        style.configure(
            "Treeview.Heading",
            background="#2d2d2d" if APP_CONFIG["theme"] == "dark" else "#f0f0f0",
            foreground="white" if APP_CONFIG["theme"] == "dark" else "black",
            font=("Segoe UI", 10, "bold"),
            borderwidth=1,
        )
        style.map(
            "Treeview",
            background=[("selected", "#3d7abd")],
            foreground=[("selected", "white")],
        )

        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        self.row_count_label = ctk.CTkLabel(
            self,
            text="0 facturas",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        )

    def _layout_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")

        self.row_count_label.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="w")

    def set_invoices(self, invoices: List[Invoice]):
        self._all_invoices = invoices
        self._filtered_invoices = invoices.copy()
        self._refresh()

    def apply_filters(self, filters: dict):
        search = filters.get("search", "")
        detalle = filters.get("detalle")
        tipo = filters.get("tipo_comprobante")
        fecha_desde = filters.get("fecha_desde")
        fecha_hasta = filters.get("fecha_hasta")

        self._filtered_invoices = []
        for inv in self._all_invoices:
            if search:
                search_fields = [
                    inv.proveedor.lower(),
                    inv.numero_comprobante.lower(),
                    inv.cuit.lower(),
                    inv.tipo_comprobante.lower(),
                ]
                if not any(search in field for field in search_fields):
                    continue

            if detalle and detalle not in inv.proveedor.lower():
                continue

            if tipo and inv.tipo_comprobante != tipo:
                continue

            if fecha_desde and inv.fecha and inv.fecha < fecha_desde:
                continue

            if fecha_hasta and inv.fecha and inv.fecha > fecha_hasta:
                continue

            self._filtered_invoices.append(inv)

        if self._sort_column:
            self._sort_filtered()

        self._refresh()

    def _cell_value(self, inv: Invoice, key: str) -> str:
        if key == "tipo_comprobante":
            return inv.tipo_comprobante
        val = inv.get_field(key)
        if isinstance(val, date):
            return val.strftime("%d/%m/%Y")
        if key == "fecha":
            return str(val)
        if isinstance(val, (int, float)):
            return self._fmt(float(val))
        return str(val) if val is not None else ""

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())

        for inv in self._filtered_invoices:
            values = [self._cell_value(inv, col_id) for col_id, _, _ in self._columns]
            self.tree.insert("", "end", values=values, tags=(inv.tipo_comprobante,))

        self.tree.tag_configure("A", background="#1a3a5c")
        self.tree.tag_configure("B", background="#1a5c3a")
        self.tree.tag_configure("C", background="#5c1a3a")
        self.tree.tag_configure("M", background="#3a1a5c")
        self.tree.tag_configure("E", background="#5c3a1a")

        self.row_count_label.configure(text=f"{len(self._filtered_invoices):,} facturas".replace(",", "."))

    def _fmt(self, value: float) -> str:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _on_header_click(self, column: str):
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False
        self._sort_filtered()
        self._refresh()

    def _sort_filtered(self):
        if not self._sort_column:
            return

        def sort_key(inv: Invoice):
            val = inv.get_field(self._sort_column)
            if self._sort_column == "tipo_comprobante":
                val = inv.tipo_comprobante
            if isinstance(val, (int, float)):
                return val
            return str(val or "")

        self._filtered_invoices.sort(key=sort_key, reverse=self._sort_reverse)

    def _on_select(self, event):
        selection = self.tree.selection()
        if selection and self.on_row_select:
            idx = self.tree.index(selection[0])
            if idx < len(self._filtered_invoices):
                self.on_row_select(self._filtered_invoices[idx])

    def _on_double_click(self, event):
        pass

    def get_filtered_invoices(self) -> List[Invoice]:
        return self._filtered_invoices

    def get_selected_invoice(self) -> Optional[Invoice]:
        selection = self.tree.selection()
        if selection:
            idx = self.tree.index(selection[0])
            if idx < len(self._filtered_invoices):
                return self._filtered_invoices[idx]
        return None
