from pathlib import Path
from typing import Dict, List, Optional, TypedDict


class LibroColumnDef(TypedDict, total=False):
    key: str
    label: str
    kind: str  # text | money
    sum: bool
    main: bool
    iva: bool

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / ".docs"
# Estructura del Libro IVA Compras VRF (misma fila de encabezados que el .xlsx)
LIBRO_SCHEMA: List[LibroColumnDef] = [
    {"key": "fecha", "label": "FECHA", "kind": "text"},
    {"key": "numero_comprobante", "label": "NUMERO", "kind": "text"},
    {"key": "proveedor", "label": "DETALLE", "kind": "text"},
    {"key": "cuit", "label": "C.U.I.T.", "kind": "text"},
    {"key": "factura_c", "label": 'FACTURA. "C"', "kind": "money", "sum": True},
    {"key": "factura_a", "label": 'FACTURA. "A"', "kind": "money", "sum": True},
    {"key": "iva_21", "label": "0.21", "kind": "money", "sum": True, "iva": True},
    {"key": "iva_105", "label": "0.105", "kind": "money", "sum": True, "iva": True},
    {"key": "iva_27", "label": "0.27", "kind": "money", "sum": True, "iva": True},
    # El libro carga el IVA 10,5% en la columna "10.5" (la columna 0.105 suele venir vacía)
    {"key": "iva_105_alt", "label": "10.5", "kind": "money", "sum": True, "iva": True},
    {"key": "neto_no_gravado", "label": "NO.G", "kind": "money", "sum": True},
    {"key": "percepcion_iva", "label": "P.IVA", "kind": "money", "sum": True},
    {"key": "percepcion_iibb", "label": "P.IB", "kind": "money", "sum": True},
    {"key": "total", "label": "TOTAL", "kind": "money", "sum": True, "main": True},
]

COLUMN_MAP: Dict[str, List[str]] = {
    "fecha": ["Fecha", "FECHA", "fecha", "Fecha Emision", "Fecha Emisión"],
    "tipo_comprobante": ["Tipo Comprobante", "TIPO COMPROBANTE", "Tipo", "Comprobante", "Factura Tipo"],
    "numero_comprobante": [
        "Nro Comprobante", "Nº Comprobante", "Numero", "Número", "Nro Factura", "Factura Nro",
        "Numero Factura", "Número Factura", "Nro", "Comprobante Nro",
    ],
    "proveedor": ["Proveedor", "Razon Social", "Razón Social", "Nombre", "Detalle"],
    "cuit": ["CUIT", "Cuit", "cuit", "CUIT Proveedor", "C.U.I.T.", "C.U.I.T"],
    "factura_c": ['FACTURA. "C"', 'FACTURA "C"', "FACTURA C"],
    "factura_a": ['FACTURA. "A"', 'FACTURA "A"', "FACTURA A"],
    "neto_gravado": ["Neto Gravado", "NETO GRAVADO", "Gravado", "Base Imponible", "Neto 21%", "Neto 10.5%"],
    "neto_no_gravado": ["Neto No Gravado", "NETO NO GRAVADO", "No Gravado", "NO.G"],
    "exento": ["Exento", "EXENTO"],
    # Las columnas de IVA se reconocen por el número del encabezado (ver NUMERIC_COLUMN_RATES)
    "percepcion_iva": ["Percepcion IVA", "Percepción IVA", "Perc. IVA", "Percepcion I.V.A.", "P.IVA"],
    "percepcion_iibb": ["Percepcion IIBB", "Percepción IIBB", "Perc. IIBB", "Percepcion Ingresos Brutos", "P.IB"],
    "retenciones": ["Retenciones", "RETENCIONES", "Retencion", "Retención"],
    "total": ["Total", "TOTAL", "Importe Total", "Importe", "Monto Total"],
}

REQUIRED_COLUMNS = ["fecha", "numero_comprobante", "total"]

# Encabezados de IVA según el número que contienen: "0.21", "IVA 0,21", "IVA 21%"...
# 0.105 y 10.5 son dos columnas distintas del libro; ambas son IVA 10,5%.
NUMERIC_COLUMN_RATES: Dict[str, tuple] = {
    "iva_21": (0.21, 21.0),
    "iva_105": (0.105,),
    "iva_27": (0.27, 27.0),
    "iva_105_alt": (10.5,),
}

HEADER_SCAN_MAX_ROWS = 40

TAX_COLUMNS = [
    "neto_gravado", "neto_no_gravado", "exento",
    "iva_21", "iva_105", "iva_27",
    "percepcion_iva", "percepcion_iibb", "retenciones"
]

FACTURA_TYPES = ["A", "B", "C", "M", "E", "NC", "ND"]

DATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]

APP_CONFIG = {
    "app_name": "VRF2 - Libro Compras",
    "version": "1.0.0",
    "window_size": (1400, 900),
    "min_window_size": (1000, 700),
    "theme": "dark",
    "color_theme": "blue",
    "chunk_size": 5000,
    "auto_reload_seconds": 5,
    "currency_symbol": "$",
    "currency_locale": "es_AR",
}

def column_label(col) -> str:
    if isinstance(col, float):
        return str(col).strip()
    if isinstance(col, int):
        return str(col)
    return str(col).strip()


def normalize_label(col) -> str:
    """'IVA 0,21' -> '0.21', 'NUMERO  FACTURA' -> 'numero factura', 'C.U.I.T.' -> 'c.u.i.t'."""
    text = column_label(col).lower()
    for token in ("iva", "%", '"', "'"):
        text = text.replace(token, " ")
    text = text.replace(",", ".")
    return " ".join(text.split()).strip(" .")


def header_number(col) -> Optional[float]:
    if isinstance(col, (int, float)):
        return float(col)
    try:
        return float(normalize_label(col))
    except ValueError:
        return None


def match_schema_column(df_columns: List, schema_item: LibroColumnDef, used: Optional[set] = None):
    key = schema_item["key"]
    used = used or set()
    candidates = [col for col in df_columns if col not in used]

    aliases = {normalize_label(schema_item["label"])}
    aliases.update(normalize_label(a) for a in COLUMN_MAP.get(key, []))
    if key not in NUMERIC_COLUMN_RATES:
        for col in candidates:
            if normalize_label(col) in aliases:
                return col
        return None

    for col in candidates:
        number = header_number(col)
        if number is not None and any(abs(number - rate) < 1e-9 for rate in NUMERIC_COLUMN_RATES[key]):
            return col
    return None


def find_column(df_columns: List, target: str):
    aliases = {normalize_label(a) for a in COLUMN_MAP.get(target, [])}
    for col in df_columns:
        if normalize_label(col) in aliases:
            return col
    return None