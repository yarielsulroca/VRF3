from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import date, datetime
import pandas as pd


@dataclass
class Invoice:
    fecha: Optional[date] = None
    tipo_comprobante: str = ""
    numero_comprobante: str = ""
    proveedor: str = ""
    cuit: str = ""
    factura_c: float = 0.0
    factura_a: float = 0.0
    iva_105_alt: float = 0.0
    neto_gravado: float = 0.0
    neto_no_gravado: float = 0.0
    exento: float = 0.0
    iva_21: float = 0.0
    iva_105: float = 0.0
    iva_27: float = 0.0
    percepcion_iva: float = 0.0
    percepcion_iibb: float = 0.0
    retenciones: float = 0.0
    total: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def iva_total(self) -> float:
        return self.iva_21 + self.iva_105 + self.iva_105_alt + self.iva_27

    @property
    def neto_total(self) -> float:
        return self.neto_gravado + self.neto_no_gravado + self.exento

    @property
    def percepciones_total(self) -> float:
        return self.percepcion_iva + self.percepcion_iibb

    def get_field(self, key: str):
        if key == "fecha":
            return self.fecha.strftime("%d/%m/%Y") if self.fecha else ""
        return getattr(self, key, "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fecha": self.get_field("fecha"),
            "tipo_comprobante": self.tipo_comprobante,
            "numero_comprobante": self.numero_comprobante,
            "proveedor": self.proveedor,
            "cuit": self.cuit,
            "factura_c": self.factura_c,
            "factura_a": self.factura_a,
            "iva_105_alt": self.iva_105_alt,
            "neto_gravado": self.neto_gravado,
            "neto_no_gravado": self.neto_no_gravado,
            "exento": self.exento,
            "iva_21": self.iva_21,
            "iva_105": self.iva_105,
            "iva_27": self.iva_27,
            "percepcion_iva": self.percepcion_iva,
            "percepcion_iibb": self.percepcion_iibb,
            "retenciones": self.retenciones,
            "total": self.total,
        }

    @classmethod
    def from_series(cls, row: pd.Series, col_map: Dict[str, str]) -> "Invoice":
        def get_val(key: str) -> float:
            col = col_map.get(key)
            if col and col in row.index:
                val = row[col]
                if pd.isna(val):
                    return 0.0
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0.0
            return 0.0

        def get_str(key: str) -> str:
            col = col_map.get(key)
            if col and col in row.index:
                val = row[col]
                if pd.isna(val):
                    return ""
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                return str(val).strip()
            return ""

        def get_date(key: str) -> Optional[date]:
            col = col_map.get(key)
            if col and col in row.index:
                val = row[col]
                if pd.isna(val):
                    return None
                if isinstance(val, (pd.Timestamp, datetime)):
                    return val.date()
                if isinstance(val, date):
                    return val
                try:
                    return pd.to_datetime(val, dayfirst=True).date()
                except Exception:
                    return None
            return None

        factura_c = get_val("factura_c")
        factura_a = get_val("factura_a")
        iva_105_alt = get_val("iva_105_alt")

        tipo_comprobante = get_str("tipo_comprobante")
        if not tipo_comprobante:
            if factura_a < 0 or factura_c < 0:
                tipo_comprobante = "NC"
            elif factura_c > 0:
                tipo_comprobante = "C"
            elif factura_a > 0:
                tipo_comprobante = "A"

        # Factura C (monotributo) no discrimina IVA: no es neto gravado
        neto_gravado = get_val("neto_gravado")
        if neto_gravado == 0:
            neto_gravado = factura_a

        return cls(
            fecha=get_date("fecha"),
            tipo_comprobante=tipo_comprobante,
            numero_comprobante=get_str("numero_comprobante"),
            proveedor=get_str("proveedor"),
            cuit=get_str("cuit"),
            factura_c=factura_c,
            factura_a=factura_a,
            iva_105_alt=iva_105_alt,
            neto_gravado=neto_gravado,
            neto_no_gravado=get_val("neto_no_gravado"),
            exento=get_val("exento"),
            iva_21=get_val("iva_21"),
            iva_105=get_val("iva_105"),
            iva_27=get_val("iva_27"),
            percepcion_iva=get_val("percepcion_iva"),
            percepcion_iibb=get_val("percepcion_iibb"),
            retenciones=get_val("retenciones"),
            total=get_val("total"),
            raw_data=row.to_dict(),
        )


@dataclass
class TaxSummary:
    total_facturas: int = 0
    factura_c: float = 0.0
    factura_a: float = 0.0
    iva_105_alt: float = 0.0
    neto_gravado: float = 0.0
    neto_no_gravado: float = 0.0
    exento: float = 0.0
    iva_21: float = 0.0
    iva_105: float = 0.0
    iva_27: float = 0.0
    iva_total: float = 0.0
    percepcion_iva: float = 0.0
    percepcion_iibb: float = 0.0
    percepciones_total: float = 0.0
    retenciones: float = 0.0
    total: float = 0.0

    @property
    def neto_total(self) -> float:
        return self.neto_gravado + self.neto_no_gravado + self.exento

    def to_dict(self) -> Dict[str, float]:
        return {
            "total_facturas": self.total_facturas,
            "factura_c": self.factura_c,
            "factura_a": self.factura_a,
            "iva_105_alt": self.iva_105_alt,
            "neto_gravado": self.neto_gravado,
            "neto_no_gravado": self.neto_no_gravado,
            "exento": self.exento,
            "neto_total": self.neto_total,
            "iva_21": self.iva_21,
            "iva_105": self.iva_105,
            "iva_27": self.iva_27,
            "iva_total": self.iva_total,
            "percepcion_iva": self.percepcion_iva,
            "percepcion_iibb": self.percepcion_iibb,
            "percepciones_total": self.percepciones_total,
            "retenciones": self.retenciones,
            "total": self.total,
        }

    @classmethod
    def from_invoices(cls, invoices: list["Invoice"]) -> "TaxSummary":
        """Agrega importes tal como vienen del libro (Excel). No aplica fórmulas de alícuota."""
        summary = cls()
        for inv in invoices:
            summary.total_facturas += 1
            summary.factura_c += inv.factura_c
            summary.factura_a += inv.factura_a
            summary.iva_105_alt += inv.iva_105_alt
            summary.neto_gravado += inv.neto_gravado
            summary.neto_no_gravado += inv.neto_no_gravado
            summary.exento += inv.exento
            summary.iva_21 += inv.iva_21
            summary.iva_105 += inv.iva_105
            summary.iva_27 += inv.iva_27
            summary.percepcion_iva += inv.percepcion_iva
            summary.percepcion_iibb += inv.percepcion_iibb
            summary.retenciones += inv.retenciones
            summary.total += inv.total
        # IVA total = suma de las columnas de IVA del libro (0.21 / 0.105 / 10.5 / 0.27), no neto × alícuota
        summary.iva_total = summary.iva_21 + summary.iva_105 + summary.iva_105_alt + summary.iva_27
        summary.percepciones_total = summary.percepcion_iva + summary.percepcion_iibb
        return summary