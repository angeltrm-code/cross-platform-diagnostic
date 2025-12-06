"""Recopilación de información de sistema para Windows 10+."""

from __future__ import annotations

import subprocess
from datetime import datetime, timedelta
from typing import Any, Dict, List

import psutil


def recopilar_hw_windows(es_admin: bool) -> Dict[str, Any]:
    """Recopila información de hardware en Windows.

    Incluye datos como modelo de CPU, número de núcleos, frecuencia
    estimada y memoria instalada.

    Args:
        es_admin (bool): Indica si se ejecuta con privilegios
            elevados. Actualmente no se usa, pero se mantiene para
            compatibilidad futura.

    Returns:
        dict: Información de hardware.
    """
    cpu_freq = psutil.cpu_freq()
    mem = psutil.virtual_memory()

    return {
        "cpu": {
            "model": _obtener_cpu_model_windows(),
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


def _obtener_cpu_model_windows() -> str | None:
    """Intenta obtener el modelo de CPU usando wmic.

    Returns:
        str | None: Modelo de CPU o None si no se puede obtener.
    """
    try:
        resultado = subprocess.run(
            ["wmic", "cpu", "get", "Name"],
            capture_output=True,
            text=True,
            check=False,
        )
        lineas = [
            l.strip() for l in resultado.stdout.splitlines() if l.strip()
        ]
        if len(lineas) >= 2:
            return lineas[1]
    except Exception:
        return None
    return None


def recopilar_sistema_windows(es_admin: bool) -> Dict[str, Any]:
    """Recopila información del sistema operativo en Windows.

    Incluye edición de Windows, versión y tiempo de actividad.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de sistema.
    """
    boot_ts = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_ts)
    uptime = datetime.now() - boot_time

    return {
        "edicion": _obtener_edicion_windows(),
        "version_completa": _obtener_version_windows(),
        "boot_time": boot_time.isoformat(timespec="seconds"),
        "uptime_horas": round(uptime.total_seconds() / 3600, 1),
    }


def _obtener_edicion_windows() -> str | None:
    """Devuelve una descripción básica de la edición de Windows."""
    try:
        resultado = subprocess.run(
            ["wmic", "os", "get", "Caption"],
            capture_output=True,
            text=True,
            check=False,
        )
        lineas = [
            l.strip() for l in resultado.stdout.splitlines() if l.strip()
        ]
        if len(lineas) >= 2:
            return lineas[1]
    except Exception:
        return None
    return None


def _obtener_version_windows() -> str:
    """Devuelve la versión de Windows usando platform."""
    import platform

    return f"{platform.system()} {platform.release()} ({platform.version()})"


def recopilar_procesos_windows(es_admin: bool) -> List[Dict[str, Any]]:
    """Recopila información de procesos en Windows.

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

    # Limitamos a los 20 procesos más pesados para el informe.
    return procesos_ordenados[:20]


def recopilar_almacenamiento_windows(es_admin: bool) -> Dict[str, Any]:
    """Recopila información de almacenamiento en Windows.

    Incluye unidades lógicas, capacidad total, usada y libre.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados.

    Returns:
        dict: Información de almacenamiento.
    """
    volumenes = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue

        volumenes.append(
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

    return {"volumenes": volumenes}


def recopilar_red_windows(es_admin: bool) -> Dict[str, Any]:
    """Recopila información básica de red en Windows.

    Incluye adaptadores, direcciones IP y estado.

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


def recopilar_logs_windows_7dias(es_admin: bool) -> Dict[str, Any]:
    """Recopila eventos y logs relevantes de los últimos 7 días en Windows.

    Utiliza la herramienta wevtutil si está disponible para consultar
    el registro de eventos de Sistema y Aplicación, filtrando los
    eventos de los últimos 7 días y clasificándolos por severidad.

    Args:
        es_admin (bool): Indica si el proceso tiene privilegios
            elevados. Algunos registros podrían requerir permisos de
            administrador.

    Returns:
        dict: Información de logs con listas de "errores", "avisos" e
        "informacion". Cada entrada es una cadena de texto resumida.
    """
    errores: list[str] = []
    avisos: list[str] = []
    info: list[str] = []

    # Ventana de 7 días en milisegundos (para la consulta XPATH).
    # 7 días * 24 horas * 3600 s * 1000 ms.
    siete_dias_ms = 7 * 24 * 3600 * 1000

    comandos = [
        [
            "wevtutil",
            "qe",
            "System",
            "/q:*[System[TimeCreated[timediff(@SystemTime) <= "
            f"{siete_dias_ms}"
            "]]]",
            "/f:text",
            "/c:200",
        ],
        [
            "wevtutil",
            "qe",
            "Application",
            "/q:*[System[TimeCreated[timediff(@SystemTime) <= "
            f"{siete_dias_ms}"
            "]]]",
            "/f:text",
            "/c:200",
        ],
    ]

    for cmd in comandos:
        try:
            resultado = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                errors="ignore",
            )
        except FileNotFoundError:
            # wevtutil no disponible (por ejemplo en ediciones muy
            # limitadas).
            continue

        texto = resultado.stdout.lower()
        for linea in texto.splitlines():
            linea_strip = linea.strip()
            if not linea_strip:
                continue
            if "error" in linea_strip:
                errores.append(linea_strip[:200])
            elif "warn" in linea_strip or "advert" in linea_strip:
                avisos.append(linea_strip[:200])
            else:
                info.append(linea_strip[:200])

    return {
        "errores": errores,
        "avisos": avisos,
        "informacion": info,
    }
