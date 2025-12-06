#!/usr/bin/env python3
"""Punto de entrada del diagnóstico de PC profundo.

Orquesta el flujo completo:
    - Detección de sistema operativo y privilegios.
    - Recopilación de información pasiva profunda (HW, SO, procesos,
      almacenamiento, red, logs últimos 7 días).
    - Análisis de estado general (OK/AVISO/CRÍTICO).
    - Análisis de anomalías de la última semana.
    - Generación de informe TX en el Escritorio.
    - Mensajes de progreso en la CLI para que el usuario vea que el
      diagnóstico sigue ejecutándose.
"""

from src.entorno import detectar_sistema_operativo, tiene_privilegios_elevados
from src.entorno import obtener_ruta_escritorio
from src.diag_windows import (
    recopilar_hw_windows,
    recopilar_sistema_windows,
    recopilar_procesos_windows,
    recopilar_almacenamiento_windows,
    recopilar_red_windows,
    recopilar_logs_windows_7dias,
)
from src.diag_linux import (
    recopilar_hw_linux,
    recopilar_sistema_linux,
    recopilar_procesos_linux,
    recopilar_almacenamiento_linux,
    recopilar_red_linux,
    recopilar_logs_linux_7dias,
)
from src.analisis import evaluar_estado_general, analizar_anomalias_7dias
from src.informes import (
    generar_resumen_no_tecnico,
    generar_detalle_tecnico,
    generar_informe_txt,
)
from src.progreso import mostrar_progreso


def recopilar_datos_sistema(os_info: dict, es_admin: bool) -> dict:
    """Recopila información pasiva profunda del sistema (Windows/Linux).

    Args:
        os_info (dict): Información básica del sistema operativo.
        es_admin (bool): True si se ejecuta con privilegios elevados.

    Returns:
        dict: Diccionario con claves "hardware", "sistema", "procesos",
        "almacenamiento", "red" y "logs".
    """
    familia = os_info.get("familia")

    if familia == "windows":
        return {
            "hardware": recopilar_hw_windows(es_admin),
            "sistema": recopilar_sistema_windows(es_admin),
            "procesos": recopilar_procesos_windows(es_admin),
            "almacenamiento": recopilar_almacenamiento_windows(es_admin),
            "red": recopilar_red_windows(es_admin),
            "logs": recopilar_logs_windows_7dias(es_admin),
        }

    if familia == "linux":
        return {
            "hardware": recopilar_hw_linux(es_admin),
            "sistema": recopilar_sistema_linux(es_admin),
            "procesos": recopilar_procesos_linux(es_admin),
            "almacenamiento": recopilar_almacenamiento_linux(es_admin),
            "red": recopilar_red_linux(es_admin),
            "logs": recopilar_logs_linux_7dias(es_admin),
        }

    raise RuntimeError(f"Sistema operativo no soportado: {familia!r}")


def main() -> None:
    """Orquesta el diagnóstico completo y genera el informe en el Escritorio.

    Flujo:
        1) Detecta sistema operativo y versión.
        2) Comprueba privilegios elevados.
        3) Recopila información pasiva profunda.
        4) Evalúa estado general.
        5) Analiza anomalías de los últimos 7 días.
        6) Genera resumen no técnico y detalle técnico.
        7) Escribe informe TXT en el Escritorio.
        8) Muestra progreso por pasos en la CLI.

    Raises:
        RuntimeError: Si el sistema operativo no está soportado.
    """
    total_pasos = 7
    paso = 1

    mostrar_progreso(paso, total_pasos, "Detectando sistema operativo...")
    os_info = detectar_sistema_operativo()

    paso += 1
    mostrar_progreso(paso, total_pasos, "Comprobando privilegios...")
    es_admin = tiene_privilegios_elevados(os_info)

    paso += 1
    mostrar_progreso(
        paso,
        total_pasos,
        "Recopilando información profunda del sistema...",
    )
    datos_crudos = recopilar_datos_sistema(os_info, es_admin)

    paso += 1
    mostrar_progreso(paso, total_pasos, "Evaluando estado general...")
    estado_general = evaluar_estado_general(datos_crudos)

    paso += 1
    mostrar_progreso(
        paso,
        total_pasos,
        "Analizando anomalías de los últimos 7 días...",
    )
    anomalias_7dias = analizar_anomalias_7dias(datos_crudos)

    paso += 1
    mostrar_progreso(
        paso,
        total_pasos,
        "Preparando resumen para usuario no técnico...",
    )
    resumen_no_tecnico = generar_resumen_no_tecnico(
        estado_general,
        anomalias_7dias,
    )

    paso += 1
    mostrar_progreso(
        paso,
        total_pasos,
        "Preparando detalle técnico e informe final...",
    )
    detalle_tecnico = generar_detalle_tecnico(
        datos_crudos,
        estado_general,
        anomalias_7dias,
    )

    ruta_escritorio = obtener_ruta_escritorio(os_info)
    metadatos = {
        "os_info": os_info,
        "es_admin": es_admin,
    }

    ruta_informe = generar_informe_txt(
        ruta_escritorio,
        resumen_no_tecnico,
        detalle_tecnico,
        metadatos,
    )

    print()
    print("Diagnóstico completado.")
    print(f"Informe generado en: {ruta_informe}")


if __name__ == "__main__":
    main()
