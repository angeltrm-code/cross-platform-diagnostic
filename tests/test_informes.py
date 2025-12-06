"""Tests para la generación de textos de informe."""

from src.informes import generar_resumen_no_tecnico


def test_generar_resumen_no_tecnico_incluye_estado_global():
    estado = {"global": "AVISO", "memoria": "OK", "disco": "AVISO", "logs": "OK"}
    anomalias = {"descripcion_breve": "Se han detectado algunos errores."}
    texto = generar_resumen_no_tecnico(estado, anomalias)
    assert "Estado general de tu equipo: AVISO" in texto
    assert "Se han detectado algunos errores." in texto
