# VRF2 - Libro Compras

Aplicación de escritorio Windows para visualizar y analizar libros de compras (Excel) con foco en **IVA**.

## Inicio Rápido

### Opción A: Desarrollo (con Python instalado)
```bash
cd VRF2
python run.py
```
- Primera ejecución: crea `.venv`, instala dependencias, abre la app
- Ejecuciones posteriores: usa `.venv` existente

### Opción B: Ejecutable Standalone (sin Python)
```bash
python build.py
# Genera: dist/VRF2_Libro_Compras.exe
```
- Incluye Python + dependencias + Excel embebido
- Distribuible a cualquier Windows 10/11

### Opción C: Windows Doble-Click
- Doble-click en `run.bat` (auto-instala si es primera vez)

## Funcionalidades

| Característica | Descripción |
|---|---|
| **Excel como BD** | Lee `.xlsx` directo en cada apertura (sin BD intermedia) |
| **Carga async** | Chunked 5k filas + barra de progreso |
| **Tabla virtualizada** | ttk.Treeview - maneja 50k+ filas fluidamente |
| **Filtros tiempo real** | Búsqueda global + tipo factura (A/B/C/M/E) + fecha desde/hasta |
| **Cards IVA** | 10 cards: IVA TOTAL (principal), 21%, 10.5%, 27%, Netos, Percepciones, Retenciones, Total |
| **Ordenamiento** | Click en header de columna (toggle asc/desc) |
| **Auto-recarga** | Watchdog detecta cambios en el Excel y recarga solo |
| **Tema oscuro** | CustomTkinter "blue" theme, Segoe UI |
| **Formato AR** | Moneda `$ XX.XXX,XX` |

## Estructura de Datos Esperada (Libro Compras AR)

El `config.py` mapea automáticamente estas columnas (aliases flexibles):

| Campo Interno | Columnas Excel Reconocidas |
|---|---|
| `fecha` | Fecha, FECHA, Fecha Emision |
| `tipo_comprobante` | Tipo Comprobante, Tipo, Factura Tipo |
| `numero_comprobante` | Nro Comprobante, Número, Nro Factura |
| `proveedor` | Proveedor, Razon Social, Nombre |
| `cuit` | CUIT, CUIT Proveedor |
| `neto_gravado` | Neto Gravado, Base Imponible, Neto 21% |
| `neto_no_gravado` | Neto No Gravado, No Gravado |
| `exento` | Exento |
| `iva_21` | IVA 21%, IVA 21 |
| `iva_105` | IVA 10.5%, IVA 10,5% |
| `iva_27` | IVA 27% |
| `percepcion_iva` | Percepcion IVA, Perc. IVA |
| `percepcion_iibb` | Percepcion IIBB, Perc. IIBB |
| `retenciones` | Retenciones |
| `total` | Total, Importe Total, Monto Total |

> **Si tu Excel tiene otras columnas**: edita `src/config.py` → `COLUMN_MAP` agregando tus nombres exactos.

## Requisitos

- Windows 10/11
- Python 3.10+ (solo para desarrollo/build)
- Libro IVA Compras en Excel `.xlsx` (se elige al abrir la app con "Abrir Excel...")

## Build Standalone

```bash
python build.py
# Output: dist/VRF2_Libro_Compras.exe (~60-80 MB)
```

Incluye:
- Python 3.10+ runtime
- Todas las dependencias (pandas, customtkinter, etc.)
- El archivo Excel embebido (`.docs/`)
- Version info + icono (si existe `assets/icon.ico`)

## Personalizar Icono

```bash
# Opción 1: Generar automático (requiere pillow)
pip install pillow
python assets/generate_icon.py

# Opción 2: Poner tu propio icon.ico en assets/
# Debe ser .ico multi-resolución (16..256px)
```

## Arquitectura

```
src/
├── main.py                 # Entry point, MainWindow
├── install_deps.py         # Instalador GUI primera vez
├── config.py               # COLUMN_MAP, APP_CONFIG
├── models/invoice.py       # Invoice, TaxSummary (dataclasses)
├── services/excel_processor.py  # ExcelProcessor, TaxCalculator
└── ui/
    ├── data_table.py       # Treeview virtualizado + sort
    ├── filter_panel.py     # Search + tipo + fecha
    └── tax_cards.py        # Grid 10 cards responsivo
```

## Licencia

Uso interno VRF2.