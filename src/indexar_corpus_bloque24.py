
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.corpus_bloque24 import (
    construir_corpus,
    fragmentar_corpus,
)


RUTA_INDICE = Path("vectorstore/bloque24")
NOMBRE_COLECCION = "archive_ai_bloque24"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"


def construir_embeddings():
    """Prepara el modelo de embeddings de Gemini."""

    load_dotenv(dotenv_path=Path.cwd() / ".env")

    if not os.getenv("GEMINI_API_KEY") and not os.getenv(
        "GOOGLE_API_KEY"
    ):
        raise RuntimeError(
            "No se encontro una clave de Gemini en el entorno."
        )

    return GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS
    )


def indexar_corpus():
    """Indexa el corpus una vez y reutiliza el indice existente."""

    documentos = construir_corpus()
    fragmentos = fragmentar_corpus(documentos)

    print(f"DOCUMENTOS: {len(documentos)}", flush=True)
    print(f"FRAGMENTOS: {len(fragmentos)}", flush=True)

    if not fragmentos:
        raise RuntimeError("El corpus no contiene fragmentos.")

    # Si ya hay archivos, revisamos el indice sin recrearlo.
    if RUTA_INDICE.exists() and any(RUTA_INDICE.iterdir()):
        embeddings = construir_embeddings()

        indice = Chroma(
            collection_name=NOMBRE_COLECCION,
            embedding_function=embeddings,
            persist_directory=str(RUTA_INDICE),
        )

        cantidad = indice._collection.count()

        if cantidad != len(fragmentos):
            raise RuntimeError(
                f"El indice contiene {cantidad} fragmentos, "
                f"pero se esperaban {len(fragmentos)}. "
                "No se modificara automaticamente."
            )

        print("INDICE EXISTENTE REUTILIZADO")
        print(f"VECTORES GUARDADOS: {cantidad}")
        return

    embeddings = construir_embeddings()

    print("GENERANDO EMBEDDINGS REALES...", flush=True)

    identificadores = [
        f"bloque24-{indice:03d}"
        for indice in range(1, len(fragmentos) + 1)
    ]

    indice = Chroma.from_documents(
        documents=fragmentos,
        embedding=embeddings,
        ids=identificadores,
        collection_name=NOMBRE_COLECCION,
        persist_directory=str(RUTA_INDICE),
    )

    cantidad = indice._collection.count()

    print("INDEXACION FINALIZADA")
    print(f"VECTORES GUARDADOS: {cantidad}")
    print(f"CARPETA: {RUTA_INDICE}")

    if cantidad != len(fragmentos):
        raise RuntimeError(
            "El numero de vectores no coincide con los fragmentos."
        )


if __name__ == "__main__":
    indexar_corpus()
