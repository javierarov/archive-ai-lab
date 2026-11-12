
from collections import Counter

from src.corpus_bloque24 import (
    construir_corpus,
    fragmentar_corpus,
)


def test_corpus_contiene_cinco_documentos():
    corpus = construir_corpus()

    assert len(corpus) == 5


def test_identificadores_unicos():
    corpus = construir_corpus()

    identificadores = [
        documento.metadata["id"]
        for documento in corpus
    ]

    assert len(identificadores) == len(set(identificadores))


def test_documentos_tienen_metadatos():
    corpus = construir_corpus()

    for documento in corpus:
        assert documento.metadata["id"]
        assert documento.metadata["titulo"]
        assert documento.metadata["tema"]
        assert documento.metadata["origen"]


def test_fragmentacion_genera_chunks():
    corpus = construir_corpus()
    fragmentos = fragmentar_corpus(corpus)

    assert len(fragmentos) >= len(corpus)
    assert all(fragmento.page_content.strip() for fragmento in fragmentos)


def test_fragmentos_conservan_procedencia():
    corpus = construir_corpus()
    fragmentos = fragmentar_corpus(corpus)

    originales = {
        documento.metadata["id"]
        for documento in corpus
    }

    recuperados = {
        fragmento.metadata["id"]
        for fragmento in fragmentos
    }

    assert recuperados == originales


def test_todos_los_documentos_tienen_fragmentos():
    fragmentos = fragmentar_corpus(construir_corpus())

    conteo = Counter(
        fragmento.metadata["id"]
        for fragmento in fragmentos
    )

    assert len(conteo) == 5
    assert all(cantidad >= 1 for cantidad in conteo.values())


def test_fragmentos_respetan_tamano():
    fragmentos = fragmentar_corpus(construir_corpus())

    assert all(
        len(fragmento.page_content) <= 200
        for fragmento in fragmentos
    )
