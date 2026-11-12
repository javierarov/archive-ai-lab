
import pytest

from langchain_core.documents import Document

from src.recuperacion_bloque26 import (
    PROMPT_TEMPLATE,
    construir_prompt,
    formatear_contexto,
    recuperar_fragmentos,
)


@pytest.fixture
def documentos_prueba():
    """Documentos ficticios con metadatos archivisticos."""

    return [
        Document(
            page_content=(
                "La conservacion preventiva reduce "
                "el deterioro documental."
            ),
            metadata={
                "id": "RAG-002",
                "titulo": "Conservacion preventiva",
            },
        ),
        Document(
            page_content=(
                "La digitalizacion permite generar "
                "copias de acceso."
            ),
            metadata={
                "id": "RAG-003",
                "titulo": "Preservacion audiovisual",
            },
        ),
    ]


def test_contexto_numera_fragmentos(documentos_prueba):
    contexto, citas = formatear_contexto(documentos_prueba)

    assert "[1]" in contexto
    assert "[2]" in contexto
    assert len(citas) == 2


def test_citas_conservan_procedencia(documentos_prueba):
    _, citas = formatear_contexto(documentos_prueba)

    assert citas[1] == (
        "RAG-002 | Conservacion preventiva"
    )

    assert citas[2] == (
        "RAG-003 | Preservacion audiovisual"
    )


def test_citas_tienen_numeracion_consecutiva(
    documentos_prueba,
):
    _, citas = formatear_contexto(documentos_prueba)

    assert list(citas.keys()) == [1, 2]


def test_rechaza_fragmentos_sin_identificador():
    documentos = [
        Document(
            page_content="Documento sin identificador.",
            metadata={"titulo": "Sin identificador"},
        )
    ]

    with pytest.raises(ValueError):
        formatear_contexto(documentos)


def test_rechaza_fragmentos_sin_titulo():
    documentos = [
        Document(
            page_content="Documento sin titulo.",
            metadata={"id": "RAG-999"},
        )
    ]

    with pytest.raises(ValueError):
        formatear_contexto(documentos)


def test_prompt_exige_citas_y_limita_al_contexto():
    assert "EXCLUSIVAMENTE" in PROMPT_TEMPLATE
    assert "[1]" in PROMPT_TEMPLATE
    assert "informacion suficiente" in PROMPT_TEMPLATE


def test_construir_prompt_con_recuperacion_simulada(
    monkeypatch,
    documentos_prueba,
):
    def recuperar_simulado(pregunta, k=3):
        return documentos_prueba[:k]

    monkeypatch.setattr(
        "src.recuperacion_bloque26.recuperar_fragmentos",
        recuperar_simulado,
    )

    pregunta = "Como evitar el deterioro documental?"

    prompt, citas = construir_prompt(pregunta, k=2)

    assert pregunta in prompt
    assert "[1]" in prompt
    assert "[2]" in prompt
    assert len(citas) == 2


def test_recuperacion_rechaza_pregunta_vacia():
    with pytest.raises(ValueError):
        recuperar_fragmentos("")


def test_recuperacion_rechaza_k_invalido():
    with pytest.raises(ValueError):
        recuperar_fragmentos(
            "Como conservar documentos?",
            k=0,
        )


def test_construir_prompt_rechaza_pregunta_vacia():
    with pytest.raises(ValueError):
        construir_prompt("  ")
