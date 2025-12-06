"""Generación de textos y del informe TXT final."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def generar_resumen_no_tecnico(
    estado_general: Dict[str, Any],
    anomalias_7dias: Dict[str, Any],
) -> str:
    """Genera un resumen para usuario no técnico.

    Usa un tono cercano pero profesional, con un esquema tipo
    semáforo (OK/AVISO/CRÍTICO) y referencias a las áreas que
    parecen más problemáticas.

    Args:
        estado_general (dict): Estado global y por áreas.
        anomalias_7dias (dict): Resultado de analizar_anomalias_7dias().

    Returns:
        str: Texto en formato plano para la sección de usuario
        no técnico.
    """
    lineas: list[str] = []

    lineas.append("=== RESUMEN PARA USUARIO NO TÉCNICO ===")
    lineas.append("")

    estado_global = estado_general.get("global", "OK")
    lineas.append(f"Estado general de tu equipo: {estado_global}")
    lineas.append("")

    # Mapeamos estados a símbolos simples.
    simbolos = {
        "OK": "[OK]     ",
        "AVISO": "[AVISO]  ",
        "CRITICO": "[CRÍTICO]",
    }

    def _format_estado(nombre: str, valor: str) -> str:
        simbolo = simbolos.get(valor, "[?]")
        return f"  {simbolo} {nombre}: {valor}"

    lineas.append("Estado por áreas:")
    lineas.append(
        _format_estado("Memoria", estado_general.get("memoria", "OK"))
    )
    lineas.append(
        _format_estado("Disco", estado_general.get("disco", "OK"))
    )
    lineas.append(
        _format_estado("Registros de eventos", estado_general.get("logs", "OK"))
    )
    lineas.append("")

    lineas.append("Lo que hemos visto en los últimos 7 días:")
    lineas.append(f"  - {anomalias_7dias.get('descripcion_breve', '').strip()}")
    lineas.append("")

    lineas.append("Recomendaciones básicas:")
    if estado_global == "OK":
        lineas.append(
            "  - Tu equipo parece estar en buen estado. Si funciona "
            "fluido, no tienes que preocuparte por nada urgente."
        )
    elif estado_global == "AVISO":
        lineas.append(
            "  - Hemos visto algunos avisos. No es una emergencia, pero "
            "conviene que un técnico revise el informe con calma."
        )
    else:  # CRITICO
        lineas.append(
            "  - Hay indicadores críticos. Es MUY recomendable que un "
            "técnico revise este informe y actúe cuanto antes."
        )

    lineas.append(
        "  - Si notas que el ordenador va muy lento, se congela o se "
        "reinicia solo, coméntaselo a la persona que te ayuda con "
        "informática y enséñale este informe."
    )
    lineas.append("")

    return "\n".join(lineas)


def generar_detalle_tecnico(
    datos_crudos: Dict[str, Any],
    estado_general: Dict[str, Any],
    anomalias_7dias: Dict[str, Any],
) -> str:
    """Genera la sección de detalle técnico del informe.

    Incluye estructuras completas, listas de procesos, detalle de
    almacenamiento, interfaces de red y resumen de logs de los últimos
    7 días.

    Args:
        datos_crudos (dict): Información completa recopilada.
        estado_general (dict): Estado general calculado.
        anomalias_7dias (dict): Resultado de analizar_anomalias_7dias().

    Returns:
        str: Texto en formato plano para la sección de usuario técnico.
    """
    lineas: list[str] = []

    lineas.append("=== DETALLE TÉCNICO ===")
    lineas.append("")

    lineas.append(">> ESTADO GENERAL")
    lineas.append(repr(estado_general))
    lineas.append("")

    lineas.append(">> RESUMEN ANOMALÍAS ÚLTIMOS 7 DÍAS")
    lineas.append(repr(anomalias_7dias))
    lineas.append("")

    lineas.append(">> HARDWARE")
    lineas.append(repr(datos_crudos.get("hardware", {})))
    lineas.append("")

    lineas.append(">> SISTEMA")
    lineas.append(repr(datos_crudos.get("sistema", {})))
    lineas.append("")

    lineas.append(">> PROCESOS (TOP MEMORIA)")
    lineas.append(repr(datos_crudos.get("procesos", [])))
    lineas.append("")

    lineas.append(">> ALMACENAMIENTO")
    lineas.append(repr(datos_crudos.get("almacenamiento", {})))
    lineas.append("")

    lineas.append(">> RED")
    lineas.append(repr(datos_crudos.get("red", {})))
    lineas.append("")

    lineas.append(">> LOGS (ÚLTIMOS 7 DÍAS)")
    lineas.append(repr(datos_crudos.get("logs", {})))
    lineas.append("")

    return "\n".join(lineas)


def generar_informe_txt(
    ruta_escritorio: str,
    resumen_no_tecnico: str,
    detalle_tecnico: str,
    metadatos: Dict[str, Any],
) -> str:
    """Genera el informe de diagnóstico en formato texto plano.

    Crea un archivo en el Escritorio con una estructura formada por:
        - Portada y metadatos.
        - Sección de usuario no técnico.
        - Sección de detalle técnico.

    Args:
        ruta_escritorio (str): Ruta al directorio del Escritorio.
        resumen_no_tecnico (str): Texto para la sección de usuario no
            técnico.
        detalle_tecnico (str): Texto para la sección de usuario
            técnico.
        metadatos (dict): Información adicional, como datos de SO y
            si se ha ejecutado con privilegios elevados.

    Returns:
        str: Ruta completa del archivo de informe generado.

    Raises:
        OSError: Si ocurre algún problema al escribir el archivo.
    """
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"diagnostico_pc_profundo_{fecha}.txt"
    ruta_completa = Path(ruta_escritorio) / nombre_archivo

    lineas: list[str] = []
    lineas.append("########################################")
    lineas.append("#  INFORME DE DIAGNÓSTICO PC PROFUNDO  #")
    lineas.append("########################################")
    lineas.append("")
    lineas.append(
        f"Fecha de generación: "
        f"{datetime.now().isoformat(timespec='seconds')}"
    )
    lineas.append(f"Sistema operativo: {metadatos.get('os_info')}")
    lineas.append(f"Privilegios elevados: {metadatos.get('es_admin')}")
    lineas.append("")
    lineas.append(resumen_no_tecnico)
    lineas.append("")
    lineas.append(detalle_tecnico)

    contenido = "\n".join(lineas)
    ruta_completa.write_text(contenido, encoding="utf-8")

    return str(ruta_completa)
