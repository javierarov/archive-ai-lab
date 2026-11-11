
from src.agente_con_herramientas import (
    buscar_documentos,
    consultar_metadatos,
)


def test_buscar_documentos_encuentra_registro():
    resultado = buscar_documentos.invoke({
        "consulta": "conservación documental"
    })

    assert "DOC-001" in resultado
    assert "Manual de conservación documental" in resultado


def test_buscar_documentos_sin_resultados():
    resultado = buscar_documentos.invoke({
        "consulta": "astronomía"
    })

    assert "No se encontraron documentos" in resultado


def test_consultar_metadatos_registro_existente():
    resultado = consultar_metadatos.invoke({
        "identificador": "DOC-003"
    })

    assert "2022-11-04" in resultado
    assert "Audio digital" in resultado
    assert "Entrevista sobre patrimonio audiovisual" in resultado


def test_consultar_metadatos_registro_inexistente():
    resultado = consultar_metadatos.invoke({
        "identificador": "DOC-999"
    })

    assert "No existe un documento" in resultado
