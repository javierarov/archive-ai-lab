
import pytest
from pydantic import ValidationError

from src.herramientas_bloque22 import (
    ArgumentosBusquedaDocumental,
    buscar_documentos_filtrados,
)


def test_busqueda_con_filtro_de_soporte():
    resultado = buscar_documentos_filtrados.invoke({
        "consulta": "patrimonio",
        "tipo_soporte": "Audio digital",
        "limite_resultados": 2,
    })

    assert "DOC-003" in resultado
    assert "Audio digital" in resultado
    assert "DOC-002" not in resultado


def test_busqueda_con_unicode():
    resultado = buscar_documentos_filtrados.invoke({
        "consulta": "conservaci\u00f3n",
    })

    assert "DOC-001" in resultado


def test_busqueda_sin_coincidencias():
    resultado = buscar_documentos_filtrados.invoke({
        "consulta": "astronomia",
    })

    assert "No se encontraron documentos" in resultado


def test_limite_inferior_invalido():
    with pytest.raises(ValidationError):
        ArgumentosBusquedaDocumental(
            consulta="patrimonio",
            limite_resultados=0,
        )


def test_limite_superior_invalido():
    with pytest.raises(ValidationError):
        ArgumentosBusquedaDocumental(
            consulta="patrimonio",
            limite_resultados=21,
        )


def test_consulta_vacia_invalida():
    with pytest.raises(ValidationError):
        ArgumentosBusquedaDocumental(
            consulta="",
        )


def test_argumentos_predeterminados():
    argumentos = ArgumentosBusquedaDocumental(
        consulta="patrimonio",
    )

    assert argumentos.tipo_soporte == "todos"
    assert argumentos.limite_resultados == 5
