
from collections import Counter
import hashlib

import pytest
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from src.corpus_bloque24 import (
    construir_corpus,
    fragmentar_corpus,
)
from src.indexar_corpus_bloque24 import NOMBRE_COLECCION


class EmbeddingsDePrueba(Embeddings):
    """Genera vectores deterministas sin usar servicios externos."""

    def embed_documents(self, texts):
        return [self.embed_query(texto) for texto in texts]

    def embed_query(self, text):
        digest = hashlib.sha256(
            text.encode("utf-8")
        ).digest()

        return [
            byte / 255.0
            for byte in digest[:16]
        ]


@pytest.fixture
def coleccion_temporal(tmp_path):
    """Crea y reabre un índice Chroma aislado para cada prueba."""

    ruta = tmp_path / "chroma_bloque24"
    fragmentos = fragmentar_corpus(construir_corpus())

    identificadores = [
        f"bloque24-{numero:03d}"
        for numero in range(1, len(fragmentos) + 1)
    ]

    Chroma.from_documents(
        documents=fragmentos,
        embedding=EmbeddingsDePrueba(),
        ids=identificadores,
        collection_name=NOMBRE_COLECCION,
        persist_directory=str(ruta),
    )

    indice_reabierto = Chroma(
        collection_name=NOMBRE_COLECCION,
        embedding_function=EmbeddingsDePrueba(),
        persist_directory=str(ruta),
    )

    return indice_reabierto._collection


def test_indice_tiene_diez_vectores(coleccion_temporal):
    assert coleccion_temporal.count() == 10


def test_vectores_conservan_metadatos(coleccion_temporal):
    datos = coleccion_temporal.get(
        include=["metadatas"]
    )

    for metadata in datos["metadatas"]:
        assert metadata["id"]
        assert metadata["titulo"]
        assert metadata["tema"]
        assert metadata["origen"]


def test_todos_los_documentos_estan_indexados(
    coleccion_temporal,
):
    datos = coleccion_temporal.get(
        include=["metadatas"]
    )

    conteo = Counter(
        metadata["id"]
        for metadata in datos["metadatas"]
    )

    assert len(conteo) == 5
    assert all(
        cantidad == 2
        for cantidad in conteo.values()
    )


def test_fragmentos_tienen_contenido(coleccion_temporal):
    datos = coleccion_temporal.get(
        include=["documents"]
    )

    assert len(datos["documents"]) == 10
    assert all(
        contenido.strip()
        for contenido in datos["documents"]
    )


def test_indice_se_puede_reabrir(
    coleccion_temporal,
):
    assert coleccion_temporal.count() == 10

    datos = coleccion_temporal.get(
        include=["embeddings"]
    )

    assert len(datos["ids"]) == 10
    assert datos["embeddings"] is not None
    assert len(datos["embeddings"]) == 10
