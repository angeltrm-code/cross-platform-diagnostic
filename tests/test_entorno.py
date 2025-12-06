"""Tests básicos para el módulo entorno."""

from src.entorno import detectar_sistema_operativo, obtener_ruta_escritorio


def test_detectar_sistema_operativo_devuelve_campos_clave():
    os_info = detectar_sistema_operativo()
    assert "familia" in os_info
    assert os_info["familia"] in ("windows", "linux")
    assert "nombre" in os_info
    assert "version" in os_info


def test_obtener_ruta_escritorio_existe_o_lanza_error():
    os_info = detectar_sistema_operativo()
    try:
        ruta = obtener_ruta_escritorio(os_info)
        assert isinstance(ruta, str)
        assert ruta  # no cadena vacía
    except FileNotFoundError:
        # Aceptamos el caso extremo de no tener Escritorio.
        assert True
