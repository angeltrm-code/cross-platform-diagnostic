"""Tests para el análisis de estado y anomalías."""

from src.analisis import evaluar_estado_general, analizar_anomalias_7dias


def test_analizar_anomalias_7dias_sin_logs_da_mensaje_tranquilo():
    datos_crudos = {"logs": {"errores": [], "avisos": []}}
    resultado = analizar_anomalias_7dias(datos_crudos)
    assert resultado["errores_graves"] == 0
    assert "No se han detectado" in resultado["descripcion_breve"]


def test_evaluar_estado_general_clasifica_memoria_disco_logs():
    datos_crudos = {
        "hardware": {"memoria": {"porcentaje_uso": 50}},
        "almacenamiento": {"volumenes": [
            {"mountpoint": "C:\\", "porcentaje_uso": 50},
        ]},
        "logs": {"errores": [], "avisos": []},
    }
    estado = evaluar_estado_general(datos_crudos)
    assert estado["memoria"] == "OK"
    assert estado["disco"] == "OK"
    assert estado["logs"] == "OK"
    assert estado["global"] == "OK"
