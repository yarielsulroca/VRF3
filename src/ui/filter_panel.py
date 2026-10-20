import customtkinter as ctk
from datetime import date, datetime
from typing import Callable, Optional, List
from src.config import FACTURA_TYPES
from src.ui.autocomplete_combo import AutocompleteCombo


class FilterPanel(ctk.CTkFrame):
    def __init__(self, master, on_filter_change: Callable, **kwargs):
        super().__init__(master, height=1, **kwargs)
        self.configure(fg_color=("gray92", "gray16"), corner_radius=10)
        self.on_filter_change = on_filter_change
        self._debounce_timer = None

        self._create_widgets()
        self._layout_widgets()

    def _label(self, text: str) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray30", "gray70"),
            anchor="w",
        )

    def _create_widgets(self):
        self.search_label = self._label("Buscar (detalle, número, CUIT)")
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._debounced_filter)
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, height=32)

        self.detalle_label = self._label("Detalle (escribí o elegí)")
        self.detalle_var = ctk.StringVar(value="Todos")
        self.detalle_var.trace_add("write", self._debounced_filter)
        self.detalle_combo = AutocompleteCombo(
            self,
            variable=self.detalle_var,
            values=["Todos"],
            command=self._on_filter_change,
            width=240,
            height=32,
        )

        self.tipo_label = self._label("Tipo factura")
        self.tipo_var = ctk.StringVar(value="Todos")
        self.tipo_combo = ctk.CTkComboBox(
            self,
            values=["Todos"] + FACTURA_TYPES,
            variable=self.tipo_var,
            width=110,
            height=32,
            command=self._on_filter_change,
        )

        self.fecha_desde_label = self._label("Fecha desde (DD/MM/AAAA)")
        self.fecha_desde_var = ctk.StringVar()
        self.fecha_desde_var.trace_add("write", self._debounced_filter)
        self.fecha_desde_entry = ctk.CTkEntry(self, textvariable=self.fecha_desde_var, width=150, height=32)

        self.fecha_hasta_label = self._label("Fecha hasta (DD/MM/AAAA)")
        self.fecha_hasta_var = ctk.StringVar()
        self.fecha_hasta_var.trace_add("write", self._debounced_filter)
        self.fecha_hasta_entry = ctk.CTkEntry(self, textvariable=self.fecha_hasta_var, width=150, height=32)

        self.clear_btn = ctk.CTkButton(
            self,
            text="Limpiar filtros",
            width=120,
            height=32,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            command=self.clear_filters,
        )

    def _layout_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        labels = [
            self.search_label,
            self.detalle_label,
            self.tipo_label,
            self.fecha_desde_label,
            self.fecha_hasta_label,
        ]
        inputs = [
            self.search_entry,
            self.detalle_combo,
            self.tipo_combo,
            self.fecha_desde_entry,
            self.fecha_hasta_entry,
        ]
        for col, (label, widget) in enumerate(zip(labels, inputs)):
            padx = (12, 6) if col == 0 else 6
            label.grid(row=0, column=col, padx=padx, pady=(8, 0), sticky="w")
            widget.grid(row=1, column=col, padx=padx, pady=(2, 10), sticky="ew" if col == 0 else "w")
        self.clear_btn.grid(row=1, column=len(inputs), padx=(6, 12), pady=(2, 10), sticky="e")

    def _debounced_filter(self, *args):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(300, self._on_filter_change)

    def _on_filter_change(self, *args):
        self.on_filter_change(self.get_filters())

    def get_filters(self) -> dict:
        return {
            "search": self.search_var.get().strip().lower(),
            "detalle": self._detalle_filter(),
            "tipo_comprobante": self.tipo_var.get() if self.tipo_var.get() != "Todos" else None,
            "fecha_desde": self._parse_date(self.fecha_desde_var.get()),
            "fecha_hasta": self._parse_date(self.fecha_hasta_var.get()),
        }

    def _detalle_filter(self) -> Optional[str]:
        value = self.detalle_var.get().strip().lower()
        if not value or value == "todos":
            return None
        return value

    def _parse_date(self, date_str: str) -> Optional[date]:
        date_str = date_str.strip()
        if not date_str:
            return None
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def clear_filters(self):
        self.search_var.set("")
        self.detalle_var.set("Todos")
        self.tipo_var.set("Todos")
        self.fecha_desde_var.set("")
        self.fecha_hasta_var.set("")
        self.on_filter_change(self.get_filters())

    def set_tipo_options(self, tipos: List[str]):
        self.tipo_combo.configure(values=["Todos"] + sorted(tipos))

    def set_detalle_options(self, detalles: List[str]):
        self.detalle_combo.set_values(["Todos"] + sorted(detalles, key=str.lower))
