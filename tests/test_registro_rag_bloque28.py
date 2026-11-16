
import pytest

from registro_rag import (
    calcular_costo_referencia,
    formatear_contexto,
    verificar_entorno,
    COLECCION,
    MODELO_GENERATIVO,
    MODELO_EMBEDDING,
)


def test_costo_primera_consulta():
    tokens = {
        "input_tokens": 232,
        "output_tokens": 31,
    }

    resultado = calcular_costo_referencia(tokens)

    assert resultado == pytest.approx(0.0001471)


def test_costo_consulta_k6():
    tokens = {
        "input_tokens": 389,
        "output_tokens": 31,
    }

    resultado = calcular_costo_referencia(tokens)

    assert resultado == pytest.approx(0.0001942)


def test_costo_sin_metadata():
    assert calcular_costo_referencia(None) is None


def test_costo_sin_tokens_de_salida():
    tokens = {"input_tokens": 200}

    assert calcular_costo_referencia(tokens) is None


def test_costo_cero_tokens():
    tokens = {
        "input_tokens": 0,
        "output_tokens": 0,
    }

    assert calcular_costo_referencia(tokens) == 0.0


def test_contexto_incluye_citas():
    contexto = formatear_contexto(
        ids=["bloque24-001", "bloque24-002"],
        documentos=[
            "La descripcion archivistica identifica documentos.",
            "Los metadatos facilitan la recuperacion.",
        ],
        metadatos=[
            {"fuente": "Descripcion archivistica"},
            {"fuente": "Descripcion archivistica"},
        ],
    )

    assert "[1]" in contexto
    assert "[2]" in contexto
    assert "bloque24-001" in contexto
    assert "bloque24-002" in contexto
    assert "Los metadatos facilitan la recuperacion." in contexto


def test_contexto_usa_id_si_falta_fuente():
    contexto = formatear_contexto(
        ids=["bloque24-003"],
        documentos=["Control de temperatura y humedad."],
        metadatos=[{}],
    )

    assert "Fuente: bloque24-003" in contexto


def test_contexto_sin_fragmentos():
    contexto = formatear_contexto(
        ids=[],
        documentos=[],
        metadatos=[],
    )

    assert contexto == ""


def test_configuracion_modelos():
    assert MODELO_GENERATIVO == "gemini-3.5-flash-lite"
    assert MODELO_EMBEDDING == "models/gemini-embedding-001"
    assert COLECCION == "archive_ai_bloque24"
