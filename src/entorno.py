"""Detección de sistema operativo, privilegios y Escritorio."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict


def detectar_sistema_operativo() -> Dict[str, Any]:
    """Detecta el sistema operativo y devuelve información básica.

    Determina si el sistema es Windows o Linux e incluye detalles como
    versión, y nombre de distribución cuando sea posible (por ejemplo
    KDE Neon Plasma 6 en Linux).

    Returns:
        dict: Diccionario con información del sistema operativo:
            - familia (str): "windows" o "linux".
            - nombre (str): Nombre del sistema (por ejemplo "Windows").
            - version (str): Versión legible (por ejemplo "10").
            - distro (str | None): Nombre de distribución en Linux
              (por ejemplo "KDE neon"), None en Windows.

    Raises:
        RuntimeError: Si el sistema operativo no está soportado.
    """
    system = platform.system().lower()

    if system == "windows":
        return {
            "familia": "windows",
            "nombre": platform.system(),
            "version": platform.release(),
            "distro": None,
        }

    if system == "linux":
        distro = _detectar_distro_linux()
        return {
            "familia": "linux",
            "nombre": platform.system(),
            "version": platform.release(),
            "distro": distro,
        }

    raise RuntimeError(f"Sistema operativo no soportado: {system!r}")


def _detectar_distro_linux() -> str | None:
    """Intenta detectar la distribución Linux a partir de /etc/os-release.

    Returns:
        str | None: Nombre de distribución, o None si no se puede
        detectar.
    """
    os_release = Path("/etc/os-release")
    if not os_release.is_file():
        return None

    contenido = os_release.read_text(encoding="utf-8", errors="ignore")
    nombre = None
    for linea in contenido.splitlines():
        if linea.startswith("PRETTY_NAME=") or linea.startswith("NAME="):
            _, valor = linea.split("=", 1)
            nombre = valor.strip().strip('"').strip("'")
            break

    return nombre


def tiene_privilegios_elevados(os_info: Dict[str, Any]) -> bool:
    """Comprueba si el proceso se ejecuta con privilegios elevados.

    En Windows se considera privilegios elevados cuando el proceso
    se ejecuta como administrador. En Linux, cuando el UID efectivo
    es 0 (root).

    Args:
        os_info (dict): Información del sistema operativo.

    Returns:
        bool: True si se detectan privilegios elevados, False en caso
        contrario.
    """
    familia = os_info.get("familia")

    if familia == "linux":
        # En Linux, UID 0 = root.
        return os.geteuid() == 0

    if familia == "windows":
        # Intento de detección con ctypes; si falla, asumimos False.
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    return False


def obtener_ruta_escritorio(os_info: Dict[str, Any]) -> str:
    """Obtiene la ruta del Escritorio del usuario.

    La ruta al Escritorio depende del sistema operativo y de la
    configuración del usuario.

    Args:
        os_info (dict): Información del sistema operativo.

    Returns:
        str: Ruta absoluta al directorio del Escritorio.

    Raises:
        FileNotFoundError: Si no se consigue localizar un Escritorio
            válido.
    """
    home = Path.home()
    posibles_nombres = ["Desktop", "Escritorio"]

    for nombre in posibles_nombres:
        candidato = home / nombre
        if candidato.is_dir():
            return str(candidato)

    # Fallback: en algunos entornos, XDG_DESKTOP_DIR se define vía
    # archivos de configuración; si no encontramos, lanzamos error.
    raise FileNotFoundError("No se ha encontrado un Escritorio válido.")
