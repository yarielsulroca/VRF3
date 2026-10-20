# Plan de Trabajo - APP Escritorio Windows Python

## Objetivo
Construir una aplicación de escritorio Windows en Python que use el archivo Excel **directamente como base de datos/repositorio de datos** (sin BD intermedia). La app lee el `.xlsx` en cada apertura, construye la tabla dinámica en memoria y calcula totales de impuestos (foco en IVA) sobre los datos filtrados.

---

## Fase 1: Análisis y Preparación (Día 1) ✅ COMPLETADA

### 1.1 Análisis del Excel
- [x] Estructura documentada en `config.py` (COLUMN_MAP con aliases típicos Libro Compras AR)
- [x] Columnas mapeadas: fecha, tipo_comprobante, numero_comprobante, proveedor, cuit, neto_gravado, neto_no_gravado, exento, iva_21, iva_105, iva_27, percepcion_iva, percepcion_iibb, retenciones, total

### 1.2 Definir Stack Tecnológico
- [x] Python 3.10+
- [x] UI: CustomTkinter (moderno, nativo Windows)
- [x] Excel: pandas + openpyxl
- [x] Packaging: PyInstaller
- [x] Dependency installer: script personalizado + requirements.txt

---

## Fase 2: Instalador de Dependencias (Día 1-2) ✅ COMPLETADA

### 2.1 Crear Instalador Primera Ejecución
- [x] Script `src/install_deps.py` con GUI tkinter:
  - Verifica Python instalado
  - Crea entorno virtual (.venv)
  - Instala requirements.txt con progreso
  - Descarga e instala Visual C++ Redistributable (si falta)
  - Crea accesos directos en Escritorio y Menú Inicio (winshell + pywin32)
- [x] GUI con barra de progreso, log detallado, reintentos
- [x] Launcher `run.py` / `run.bat` que auto-ejectua instalador si no existe .venv

---

## Fase 3: App Principal - Núcleo (Día 2-3) ✅ COMPLETADA

### 3.1 Estructura Base
- [x] `src/main.py` - Punto de entrada con MainWindow
- [x] `src/config.py` - Configuración completa (rutas, COLUMN_MAP, APP_CONFIG, find_column)
- [x] `src/models/invoice.py` - Invoice, TaxSummary dataclasses con propiedades calculadas
- [x] `src/services/excel_processor.py` - ExcelProcessor, TaxCalculator
- [x] `src/ui/` - Componentes: data_table.py, filter_panel.py, tax_cards.py

### 3.2 Procesador de Excel (Excel = Base de Datos) ✅
- [x] **Lectura directa** del `.xlsx` en cada inicio (sin BD intermedia)
- [x] Carga asíncrona chunked con barra de progreso (pandas `read_excel` + `chunksize=5000`)
- [x] Validación de columnas requeridas al abrir
- [x] Normalización on-the-fly: fechas (múltiples formatos), números, tipos factura, alias de columnas
- [x] Índices en memoria para filtros rápidos (lista filtrada in-memory)
- [x] Detección automática de columnas via COLUMN_MAP (fuzzy matching)
- [x] Watcher con watchdog: recarga automática si el archivo cambia en disco (polling mtime)

---

## Fase 4: UI - Tabla Dinámica (Día 3-4) ✅ COMPLETADA

### 4.1 Ventana Principal
- [x] Header con título, botón recargar, botón abrir otro archivo
- [x] Botones ventana nativos (minimizar/cerrar via tk)
- [x] Barra de progreso durante importación asíncrona

### 4.2 Tabla de Datos (`src/ui/data_table.py`)
- [x] ttk.Treeview virtualizado (solo renderiza visible)
- [x] Columnas autoajustables con anchos predefinidos
- [x] Ordenamiento por columna (click en header, toggle asc/desc)
- [x] Búsqueda global con debounce (300ms) en filter_panel
- [x] Scroll vertical/horizontal nativo

### 4.3 Filtros Específicos (`src/ui/filter_panel.py`)
- [x] Búsqueda global (proveedor, nro factura, CUIT, tipo)
- [x] Filtro por tipo factura (ComboBox: A, B, C, M, E, NC, ND)
- [x] Filtro por fecha (desde/hasta con parsing flexible DD/MM/YYYY)
- [x] Botón limpiar filtros
- [x] Actualización en tiempo real de tabla y cards

---

## Fase 5: Cards de Totales / Impuestos (Día 4) ✅ COMPLETADA

### 5.1 Calculadora de Impuestos (`src/services/excel_processor.py::TaxCalculator`)
- [x] Suma total de importes
- [x] Desglose IVA (21%, 10.5%, 27%)
- [x] Otros impuestos (percepciones IVA, IIBB, retenciones)
- [x] Neto gravado, neto no gravado, exento
- [x] Agrupación por tipo factura y por mes (métodos extra)

### 5.2 Cards Visuales (`src/ui/tax_cards.py`)
- [x] Grid responsivo 4 columnas (TaxSummaryCards)
- [x] Card principal: **IVA TOTAL** (destacada, azul, tamaño grande)
- [x] Cards secundarias: IVA 21%, IVA 10.5%, IVA 27%, Neto Gravado, Neto No Gravado, Exento, Percepciones, Retenciones, TOTAL GENERAL
- [x] Actualización en tiempo real al filtrar (conectado a FilterPanel)
- [x] Formato moneda argentina ($ XX.XXX,XX)

---

## Fase 6: Estilizado Moderno (Día 5) ✅ COMPLETADA (Base)

### 6.1 Tema Visual
- [x] Modo oscuro por defecto (configurable en APP_CONFIG)
- [x] Paleta profesional (azules/grises CustomTkinter theme "blue")
- [x] Tipografía sistema (Segoe UI via CustomTkinter)
- [x] Espaciado consistente (padding 8/12/16px)
- [x] Treeview estilizado para tema oscuro (ttk.Style personalizado)

### 6.2 Componentes Pulidos
- [x] Tabla: filas con tags por tipo factura (colores sutiles A/B/C/M/E)
- [x] Inputs: placeholder, focus via CustomTkinter
- [x] Botones: primary/secondary (fg_color/hover_color)
- [x] Scrollbars nativos
- [ ] Tooltips en headers de columna (pendiente)

---

## Fase 7: Empaquetado y Testing (Día 5-6) 🟡 EN PROGRESO

### 7.1 Build Executable
- [x] `build.spec` configurado (onefile, windowed, icon, version_info, datas)
- [x] `version_info.txt` con metadatos Windows
- [x] `build.py` script de construcción
- [ ] Icono `.ico` real en `assets/icon.ico` (placeholder: generar o proveer)
- [ ] Test build: `python build.py` → `dist/VRF2_Libro_Compras.exe`

### 7.2 Testing
- [ ] Probar con archivo Excel original (requiere Python instalado)
- [ ] Probar con archivos vacíos/inválidos
- [ ] Verificar memoria con 10k+ filas
- [ ] Testing en Windows 10/11 limpio (instalador + app)

---

## Entregables Finales

```
VRF2/
├── .docs/
│   ├── Precondiciones.md
│   └── LIBRO COMPRAS SEPTIEMBRE-26.xlsx
├── .skills/
│   ├── desktop-app-builder.md
│   └── WORK_PLAN.md
├── src/
│   ├── main.py
│   ├── install_deps.py
│   ├── config.py
│   ├── models/
│   ├── services/
│   └── ui/
├── requirements.txt
├── build.spec (PyInstaller)
├── assets/
│   └── icon.ico
└── dist/
    └── VRF2_Compras.exe (instalable)
```

---

## Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Excel estructura cambia | Media | Alto | Configuración de columnas en config.py |
| Rendimiento 50k+ filas | Media | Medio | Virtualización, carga chunked |
| DLLs faltantes en Windows limpio | Alta | Alto | Instalador verifica VC++ Redist |
| Encoding Excel (latin-1/utf-8) | Media | Medio | Detección automática encoding |

---

## Próximos Pasos Inmediatos (Para vos, en tu máquina con Python)

1. **Instalar Python 3.10+** (si no está) → https://python.org/downloads
2. **Clonar/abrir carpeta** `VRF2` en terminal
3. **Ejecutar launcher**: `python run.py` (auto-crea .venv, instala deps, abre app)
   - O doble-click `run.bat` en Windows
4. **Verificar carga del Excel** - La app leerá `.docs/LIBRO COMPRAS SEPTIEMBRE-26.xlsx`
5. **Ajustar COLUMN_MAP** en `src/config.py` si las columnas no coinciden exactamente
6. **Generar icono** - Crear `assets/icon.ico` (256x256) o usar uno propio
7. **Build ejecutable**: `python build.py` → genera `dist/VRF2_Libro_Compras.exe`
8. **Distribuir** - El `.exe` es standalone (incluye Python + deps + Excel embebido)