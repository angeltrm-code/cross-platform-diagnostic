# cross-platform-diagnostic

Utilidad multiplataforma para diagnosticar y analizar PCs (Windows y Linux). Recopila información profunda de hardware, sistema, procesos, almacenamiento, red y eventos de los últimos 7 días, evalúa el estado general (OK/AVISO/CRÍTICO), detecta anomalías recientes y genera un informe de texto en el Escritorio con versión para usuario no técnico y detalle técnico.

## Características
- Detección de sistema operativo y privilegios elevados.
- Recopilación de datos pasivos en Windows 10+ y distribuciones Linux.
- Evaluación por áreas (memoria, disco, logs) y estado global.
- Análisis de anomalías en la última semana a partir de eventos del sistema.
- Informe TXT en el Escritorio con resumen y detalle técnico.
- Progreso por pasos en CLI para que el usuario vea el avance.

## Requisitos
- Python 3.10+.
- Dependencias: `psutil` (ver `requirements.txt`).
- Acceso a `journalctl` o `/var/log/syslog` en Linux para leer eventos; en Windows se usan consultas a los registros de eventos.

## Instalación rápida
```bash
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso
- Linux: `python main.py`
- Windows: `python main.py` (o usa los launchers en `launchers/` si quieres crear accesos directos: `run_windows.bat`, `run_windows_admin.ps1`, `run_linux.sh`).

El informe se guarda en tu Escritorio como `diagnostico_pc_profundo_<fecha>.txt`.

Guía paso a paso para usuarios no técnicos (Windows y Linux): `docs/guia_uso_diagnostico_pc_profundo.md`.

## Estructura principal
- `main.py`: orquesta el flujo completo y genera el informe.
- `src/entorno.py`: detección de OS, privilegios y ruta del Escritorio.
- `src/diag_windows.py` y `src/diag_linux.py`: recopilación de hardware, sistema, procesos, almacenamiento, red y logs por plataforma.
- `src/analisis.py`: reglas de salud y análisis de anomalías.
- `src/informes.py`: composición de texto y generación de informe.
- `src/progreso.py`: utilidades de progreso en CLI.
- `tests/`: casos de prueba básicos para análisis e informes.

## Créditos
Proyecto desarrollado por @angeltrm-code.
