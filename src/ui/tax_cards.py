import customtkinter as ctk
from typing import Dict, List
from src.models.invoice import TaxSummary
from src.config import APP_CONFIG, LIBRO_SCHEMA, LibroColumnDef


def format_money(value: float) -> str:
    return (
        f"{APP_CONFIG['currency_symbol']} {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


class TaxCard(ctk.CTkFrame):
    def __init__(self, master, title: str, is_main: bool = False, as_count: bool = False, **kwargs):
        # height=1: CTkFrame mide 200 px por defecto; así se ajusta al contenido
        super().__init__(master, height=1, fg_color=("gray90", "gray20"), corner_radius=10, **kwargs)
        self._as_count = as_count
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12 if is_main else 11, weight="bold"),
            text_color=("gray35", "gray65"),
            anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")

        self.value_label = ctk.CTkLabel(
            self,
            text=self._format(0),
            font=ctk.CTkFont(size=22 if is_main else 15, weight="bold"),
            text_color=("#1565c0", "#4fc3f7") if is_main else ("gray15", "gray90"),
            anchor="w",
        )
        self.value_label.grid(row=1, column=0, padx=12, pady=(0, 2), sticky="ew")

        self.detail_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=("gray40", "gray60"),
            anchor="w",
        )
        self.detail_label.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

    def _format(self, value: float) -> str:
        if self._as_count:
            return f"{int(value):,}".replace(",", ".")
        return format_money(value)

    def update_value(self, value: float, detail: str = ""):
        self.value_label.configure(text=self._format(value))
        self.detail_label.configure(text=detail)


class TaxSummaryCards(ctk.CTkFrame):
    """Totales por columna del Excel (Σ de lo importado, según filtros)."""

    COLUMNS = 6

    def __init__(self, master, **kwargs):
        super().__init__(master, height=1, fg_color="transparent", **kwargs)
        for col in range(self.COLUMNS):
            self.grid_columnconfigure(col, weight=1, uniform="cards")

        sum_columns: List[LibroColumnDef] = [c for c in LIBRO_SCHEMA if c.get("sum")]
        self._iva_columns = [c for c in sum_columns if c.get("iva")]
        self._total_column = next((c for c in sum_columns if c.get("main")), None)
        self._other_columns = [c for c in sum_columns if not c.get("main") and not c.get("iva")]

        self.cards: Dict[str, TaxCard] = {}
        self._build()

    def _place(self, key: str, card: TaxCard, row: int, col: int, colspan: int = 1):
        card.grid(row=row, column=col, columnspan=colspan, padx=4, pady=4, sticky="nsew")
        self.cards[key] = card

    def _build(self):
        iva_title = "IVA (Σ " + " + ".join(c["label"] for c in self._iva_columns) + ")"
        total_title = self._total_column["label"] if self._total_column else "TOTAL"

        self._place("iva_total", TaxCard(self, iva_title, is_main=True), row=0, col=0, colspan=2)
        self._place("total", TaxCard(self, total_title, is_main=True), row=0, col=2, colspan=2)
        self._place(
            "total_facturas",
            TaxCard(self, "Comprobantes", is_main=True, as_count=True),
            row=0,
            col=4,
            colspan=2,
        )

        for idx, col_def in enumerate(self._other_columns):
            row = 1 + idx // self.COLUMNS
            col = idx % self.COLUMNS
            self._place(col_def["key"], TaxCard(self, col_def["label"]), row=row, col=col)

    def update_summary(self, summary: TaxSummary):
        data = summary.to_dict()

        iva_detail = "   ".join(
            f"{c['label']}: {format_money(float(data.get(c['key'], 0)))}" for c in self._iva_columns
        )
        self.cards["iva_total"].update_value(float(data.get("iva_total", 0)), iva_detail)
        self.cards["total"].update_value(float(data.get("total", 0)), "Σ columna TOTAL del Excel")
        self.cards["total_facturas"].update_value(float(data.get("total_facturas", 0)), "Filas sumadas")

        for col_def in self._other_columns:
            key = col_def["key"]
            self.cards[key].update_value(float(data.get(key, 0)))
