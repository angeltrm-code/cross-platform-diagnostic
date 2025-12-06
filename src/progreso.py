"""Funciones auxiliares para mostrar progreso en la CLI."""

def mostrar_progreso(paso_actual: int, total_pasos: int, mensaje: str) -> None:
    """Muestra un mensaje de progreso simple en la CLI.

    Calcula el porcentaje completado en función del paso actual y el
    número total de pasos, y lo muestra junto con un mensaje
    descriptivo. El objetivo es que el usuario vea que el diagnóstico
    sigue ejecutándose y en qué parte del proceso se encuentra.

    Args:
        paso_actual (int): Número de paso actual (empezando en 1).
        total_pasos (int): Número total de pasos previstos.
        mensaje (str): Descripción breve de la tarea en curso.
    """
    if total_pasos <= 0:
        porcentaje = 0
    else:
        porcentaje = int((paso_actual / total_pasos) * 100)

    print(f"[{porcentaje:3d}%] {mensaje}")
