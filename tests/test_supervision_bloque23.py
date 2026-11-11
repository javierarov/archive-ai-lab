
import pytest

from src.agente_con_herramientas import INVENTARIO
from src.supervision_bloque23 import (
    REGISTRO_APROBACIONES,
    simular_eliminacion_documental,
)


@pytest.fixture(autouse=True)
def limpiar_registro():
    """Evita que las pruebas compartan decisiones anteriores."""
    REGISTRO_APROBACIONES.clear()
    yield
    REGISTRO_APROBACIONES.clear()


def test_rechazo_sin_aprobacion():
    resultado = simular_eliminacion_documental(
        identificador="DOC-003",
        aprobacion_humana=False,
    )

    assert "rechazada" in resultado.lower()
    assert REGISTRO_APROBACIONES[-1]["aprobado"] is False


def test_rechazo_por_defecto():
    resultado = simular_eliminacion_documental(
        identificador="DOC-003",
    )

    assert "rechazada" in resultado.lower()
    assert REGISTRO_APROBACIONES[-1]["aprobado"] is False


def test_simulacion_con_aprobacion():
    resultado = simular_eliminacion_documental(
        identificador="DOC-003",
        aprobacion_humana=True,
    )

    assert "Simulación autorizada" in resultado
    assert REGISTRO_APROBACIONES[-1]["aprobado"] is True


def test_no_modifica_el_inventario():
    inventario_original = {
        codigo: datos.copy()
        for codigo, datos in INVENTARIO.items()
    }

    simular_eliminacion_documental(
        identificador="DOC-003",
        aprobacion_humana=True,
    )

    assert INVENTARIO == inventario_original
    assert "DOC-003" in INVENTARIO
