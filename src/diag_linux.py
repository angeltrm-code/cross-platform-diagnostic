"""Recopilación de información de sistema para Linux (incluyendo KDE Neon)."""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psutil


def recopilar_hw_linux(es_admin: bool) -> Dict[str, Any]:
    """Recopila información de hardware en Linux.

    Incluye modelo de CPU, núcleos y memoria.

    Args:
        es_admin (bool): Indica si se ejecuta con privilegios
            elevados.

    Returns:
        dict: Información de hardware.
    """
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()

    return {
        "cpu": {
            "model": _obtener_cpu_model_linux(),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "freq_mhz": cpu_freq.current if cpu_freq else None,
        },
        "memoria": {
            "total_gb": round(mem.total / (1024**3), 2),
            "usada_gb": round(mem.used / (1024**3), 2),
            "porcentaje_uso": mem.percent,
        },
    }


def _obtener_cpu_model_linux() -> str | None:
    """Intenta obtener el modelo de CPU desde /proc/cpuinfo."""
    try:
        contenido = Path("/proc/cpuinfo").read_text(
            encoding="utf-8", errors="ignore"
        )
        for linea in contenido.splitlines():
            if "model name" in linea.lower():
                _, valor = linea.split(":", 1)
                return valor.strip()
    except Exception:
        return None
    return None


def recopilar_sistema_linux(es_admin: bool) -> Dict[str, Any]:
    """Recopila información del sistema operativo en Linux.

    Incluye distribución, versión, kernel y tiempo de actividad.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de sistema.
    """
    distro = _obtener_distro_linux()
    kernel = _obtener_kernel_linux()

    boot_ts = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_ts)
    uptime = datetime.now() - boot_time

    return {
        "distro": distro,
        "kernel": kernel,
        "boot_time": boot_time.isoformat(timespec="seconds"),
        "uptime_horas": round(uptime.total_seconds() / 3600, 1),
    }


def _obtener_distro_linux() -> str | None:
    """Intenta obtener el nombre de la distribución Linux."""
    os_release = Path("/etc/os-release")
    if not os_release.is_file():
        return None

    contenido = os_release.read_text(encoding="utf-8", errors="ignore")
    for linea in contenido.splitlines():
        if linea.startswith("PRETTY_NAME="):
            _, valor = linea.split("=", 1)
            return valor.strip().strip('"').strip("'")
    return None


def _obtener_kernel_linux() -> str:
    """Devuelve la versión de kernel de Linux."""
    try:
        resultado = subprocess.run(
            ["uname", "-r"],
            capture_output=True,
            text=True,
            check=False,
        )
        return resultado.stdout.strip()
    except Exception:
        return "desconocido"


def recopilar_procesos_linux(es_admin: bool) -> List[Dict[str, Any]]:
    """Recopila información de procesos en Linux.

    Obtiene una lista de procesos ordenada por consumo de memoria
    descendente.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        list[dict]: Lista de procesos con nombre, PID, uso de CPU y
        memoria.
    """
    procesos = []
    for proc in psutil.process_iter(
        attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]
    ):
        info = proc.info
        procesos.append(
            {
                "pid": info.get("pid"),
                "nombre": info.get("name"),
                "usuario": info.get("username"),
                "cpu_percent": info.get("cpu_percent"),
                "mem_percent": round(info.get("memory_percent") or 0, 2),
            },
        )

    procesos_ordenados = sorted(
        procesos,
        key=lambda p: p["mem_percent"],
        reverse=True,
    )

    return procesos_ordenados[:20]


def recopilar_almacenamiento_linux(es_admin: bool) -> Dict[str, Any]:
    """Recopila información de almacenamiento en Linux.

    Incluye sistemas de archivos montados y su uso.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de almacenamiento.
    """
    sistemas_archivos = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue

        sistemas_archivos.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "usado_gb": round(usage.used / (1024**3), 2),
                "libre_gb": round(usage.free / (1024**3), 2),
                "porcentaje_uso": usage.percent,
            },
        )

    return {"sistemas_archivos": sistemas_archivos}


def recopilar_red_linux(es_admin: bool) -> Dict[str, Any]:
    """Recopila información básica de red en Linux.

    Incluye interfaces, direcciones IP y estado.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de red.
    """
    if_addrs = psutil.net_if_addrs()
    if_stats = psutil.net_if_stats()

    interfaces = []
    for nombre, addrs in if_addrs.items():
        estadistica = if_stats.get(nombre)
        ips = [
            a.address for a in addrs if hasattr(a, "address") and a.address
        ]
        interfaces.append(
            {
                "nombre": nombre,
                "ips": ips,
                "isup": getattr(estadistica, "isup", None),
                "velocidad_mbps": getattr(estadistica, "speed", None),
            },
        )

    return {"interfaces": interfaces}


def recopilar_logs_linux_7dias(es_admin: bool) -> Dict[str, Any]:
    """Recopila eventos y logs relevantes de los últimos 7 días en Linux.

    Intenta usar journalctl si está disponible; en caso contrario,
    recurre a ficheros de log tradicionales (/var/log/syslog) si
    existen. Clasifica las entradas por severidad aproximada.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de logs ("errores", "avisos", "informacion").
    """
    errores: list[str] = []
    avisos: list[str] = []
    info: list[str] = []

    # Primero intentamos con journalctl.
    try:
        resultado = subprocess.run(
            [
                "journalctl",
                "--since",
                "7 days ago",
                "--no-pager",
                "--output=short",
            ],
            capture_output=True,
            text=True,
            check=False,
            errors="ignore",
        )
        texto = resultado.stdout.lower()
        for linea in texto.splitlines():
            linea_strip = linea.strip()
            if not linea_strip:
                continue
            if "error" in linea_strip or "crit" in linea_strip:
                errores.append(linea_strip[:200])
            elif "warn" in linea_strip:
                avisos.append(linea_strip[:200])
            else:
                info.append(linea_strip[:200])
    except FileNotFoundError:
        # journalctl no disponible, intentamos /var/log/syslog.
        syslog = Path("/var/log/syslog")
        if syslog.is_file():
            contenido = syslog.read_text(encoding="utf-8", errors="ignore")
            for linea in contenido.splitlines()[-2000:]:
                linea_low = linea.lower()
                if "error" in linea_low or "crit" in linea_low:
                    errores.append(linea_low[:200])
                elif "warn" in linea_low:
                    avisos.append(linea_low[:200])
                else:
                    info.append(linea_low[:200])

    return {
        "errores": errores,
        "avisos": avisos,
        "informacion": info,
    }
