"""Análisis de estado general y anomalías de los últimos 7 días."""

from __future__ import annotations

from typing import Any, Dict


def evaluar_estado_general(datos_crudos: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa el estado general del sistema a partir de los datos crudos.

    Aplica reglas basadas en umbrales para clasificar memoria, disco y
    logs en categorías:
        - "OK"
        - "AVISO"
        - "CRITICO"

    Umbrales elegidos:
        - Memoria:
            - uso < 75%  -> OK
            - 75–90%     -> AVISO
            - > 90%      -> CRITICO
        - Disco (volumen principal / raíz):
            - uso < 85%  -> OK
            - 85–95%     -> AVISO
            - > 95%      -> CRITICO
        - Logs (últimos 7 días):
            - errores < 5        -> OK
            - 5–19 errores       -> AVISO
            - >= 20 errores      -> CRITICO

    El estado global se calcula como:
        - CRITICO si alguna área es CRITICO.
        - AVISO si no hay CRITICO pero sí algún AVISO.
        - OK en caso contrario.

    Args:
        datos_crudos (dict): Información recopilada del sistema.

    Returns:
        dict: Estado general, por ejemplo:
            {
                "memoria": "OK",
                "disco": "AVISO",
                "logs": "OK",
                "global": "AVISO",
            }
    """
    estado = {}

    # --- Memoria ---
    mem_info = (
        datos_crudos.get("hardware", {}).get("memoria", {})
    )
    mem_pct = mem_info.get("porcentaje_uso")
    estado["memoria"] = _clasificar_memoria(mem_pct)

    # --- Disco ---
    disco_pct = _obtener_porcentaje_uso_disco(datos_crudos)
    estado["disco"] = _clasificar_disco(disco_pct)

    # --- Logs ---
    logs = datos_crudos.get("logs", {})
    errores = len(logs.get("errores", []))
    estado["logs"] = _clasificar_logs(errores)

    # --- Global ---
    if "CRITICO" in estado.values():
        estado["global"] = "CRITICO"
    elif "AVISO" in estado.values():
        estado["global"] = "AVISO"
    else:
        estado["global"] = "OK"

    return estado


def _clasificar_memoria(porcentaje_uso: float | None) -> str:
    """Clasifica el estado de la memoria según el porcentaje de uso."""
    if porcentaje_uso is None:
        return "OK"

    if porcentaje_uso > 90:
        return "CRITICO"
    if porcentaje_uso >= 75:
        return "AVISO"
    return "OK"


def _obtener_porcentaje_uso_disco(datos_crudos: Dict[str, Any]) -> float | None:
    """Obtiene un porcentaje de uso de disco representativo.

    En Windows:
        - Usa la unidad con mountpoint más corto (típicamente C:\\).
    En Linux:
        - Usa el sistema de archivos con punto de montaje "/" si existe.

    Args:
        datos_crudos (dict): Datos crudos con información de
            almacenamiento.

    Returns:
        float | None: Porcentaje de uso, o None si no se puede
        determinar.
    """
    almacenamiento = datos_crudos.get("almacenamiento", {})

    # Intento Linux.
    sistemas_archivos = almacenamiento.get("sistemas_archivos")
    if sistemas_archivos:
        raiz = [
            s for s in sistemas_archivos if s.get("mountpoint") == "/"
        ]
        if raiz:
            return raiz[0].get("porcentaje_uso")
        # Fallback: el primero.
        return sistemas_archivos[0].get("porcentaje_uso")

    # Intento Windows.
    volumenes = almacenamiento.get("volumenes")
    if volumenes:
        # Sorteamos por longitud del mountpoint; el más corto suele
        # corresponder al sistema.
        ordenados = sorted(volumenes, key=lambda v: len(v["mountpoint"]))
        return ordenados[0].get("porcentaje_uso")

    return None


def _clasificar_disco(porcentaje_uso: float | None) -> str:
    """Clasifica el estado del disco según el porcentaje de uso."""
    if porcentaje_uso is None:
        return "OK"

    if porcentaje_uso > 95:
        return "CRITICO"
    if porcentaje_uso >= 85:
        return "AVISO"
    return "OK"


def _clasificar_logs(errores: int) -> str:
    """Clasifica el estado de logs según el número de errores."""
    if errores >= 20:
        return "CRITICO"
    if errores >= 5:
        return "AVISO"
    return "OK"


def analizar_anomalias_7dias(datos_crudos: Dict[str, Any]) -> Dict[str, Any]:
    """Analiza anomalías registradas en los últimos 7 días.

    Tiene en cuenta:
        - Número de errores y avisos en los logs.
        - Presencia de ciertas palabras clave relacionadas con disco,
          red, memoria o drivers, para orientar el posible origen de
          los problemas.

    Args:
        datos_crudos (dict): Información recopilada, que debe incluir
            la clave "logs".

    Returns:
        dict: Resumen de anomalías, por ejemplo:
            {
                "errores_graves": 12,
                "avisos_relevantes": 8,
                "area_sospechosa": ["disco", "red"],
                "descripcion_breve": "Se han detectado errores de disco..."
            }
    """
    logs = datos_crudos.get("logs", {})
    errores = logs.get("errores", [])
    avisos = logs.get("avisos", [])

    palabras_disco = ("disk", "nvme", "ntfs", "sata")
    palabras_red = ("network", "ethernet", "wifi", "wlan")
    palabras_mem = ("memory", "ram", "out of memory")
    palabras_driver = ("driver", "nvlddmkm", "gpu", "graphics")

    area_sospechosa: set[str] = set()

    for entrada in errores:
        low = entrada.lower()
        if any(p in low for p in palabras_disco):
            area_sospechosa.add("disco")
        if any(p in low for p in palabras_red):
            area_sospechosa.add("red")
        if any(p in low for p in palabras_mem):
            area_sospechosa.add("memoria")
        if any(p in low for p in palabras_driver):
            area_sospechosa.add("drivers")

    descripcion = "No se han detectado anomalías relevantes en la última semana."
    if errores or avisos:
        descripcion = (
            "En la última semana se han registrado eventos relevantes. "
            f"Errores: {len(errores)}, avisos: {len(avisos)}."
        )
        if area_sospechosa:
            descripcion += " Las áreas más sospechosas son: "
            descripcion += ", ".join(sorted(area_sospechosa)) + "."

    return {
        "errores_graves": len(errores),
        "avisos_relevantes": len(avisos),
        "area_sospechosa": sorted(area_sospechosa),
        "descripcion_breve": descripcion,
    }
