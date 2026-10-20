# Skill: Desktop App Builder (Python/Windows)

## Description
Skill for building Windows desktop applications in Python with modern UI, Excel data processing, and tax visualization capabilities.

## Capabilities
- Python desktop app development (Tkinter, CustomTkinter, PyQt, PySide)
- Windows installer/dependency management
- **Excel as database** - Direct read, no intermediate DB (pandas, openpyxl)
- Dynamic table UI with filtering/search (virtualized for 10k+ rows)
- Tax calculation and visualization (IVA focus) - computed on filtered data
- Modern UI styling with custom themes
- File watcher for auto-reload on Excel change

## Workflow
1. Analyze Excel structure and requirements
2. Design app architecture
3. Create dependency installer
4. Build main UI with data table
5. Implement filtering/search
6. Add tax summary cards
7. Apply modern styling
8. Test and package

## Tools
- Python 3.10+
- pandas, openpyxl for Excel
- CustomTkinter or PyQt6 for modern UI
- cx_Freeze or PyInstaller for packaging