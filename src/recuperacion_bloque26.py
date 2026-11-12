
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]

RUTA_INDICE = RAIZ_PROYECTO / "vectorstore" / "bloque24"

COLECCION = "archive_ai_bloque24"

MODELO_EMBEDDINGS = "models/gemini-embedding-001"


PROMPT_TEMPLATE = """
Eres un asistente especializado en gestion documental y archivistica.

Responde la pregunta utilizando EXCLUSIVAMENTE la
informacion proporcionada en el contexto.

Instrucciones:

1. No inventes informacion.
2. Cita las fuentes utilizando numeros entre corchetes,
   por ejemplo [1] o [2].
3. No cites documentos que no aparecen en el contexto.
4. Si no existe informacion suficiente para responder,
   indicalo explicitamente.
5. Mantén un lenguaje claro y profesional.

CONTEXTO DOCUMENTAL:

{contexto}

PREGUNTA:

{pregunta}

RESPUESTA:
"""


def verificar_indice():
    """Comprueba el indice sin llamar a Gemini."""

    if not RUTA_INDICE.is_dir():
        raise FileNotFoundError(
            f"No existe el indice: {RUTA_INDICE}"
        )

    cliente = chromadb.PersistentClient(
        path=str(RUTA_INDICE)
    )

    coleccion = cliente.get_collection(COLECCION)

    cantidad = coleccion.count()

    if cantidad == 0:
        raise RuntimeError(
            "La coleccion vectorial esta vacia."
        )

    return cantidad


def recuperar_fragmentos(pregunta, k=3):
    """
    Recupera documentos relevantes mediante embeddings reales.

    Esta funcion SI realiza una llamada a Gemini
    para generar el embedding de la pregunta.
    """

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia.")

    if k < 1:
        raise ValueError("k debe ser mayor o igual a 1.")

    verificar_indice()

    load_dotenv(RAIZ_PROYECTO / ".env")

    if not (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    ):
        raise RuntimeError(
            "No se encontro la clave de Gemini."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS
    )

    vectorstore = Chroma(
        collection_name=COLECCION,
        persist_directory=str(RUTA_INDICE),
        embedding_function=embeddings,
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever.invoke(pregunta)


def formatear_contexto(fragmentos):
    """
    Convierte los fragmentos recuperados en
    contexto numerado y diccionario de citas.
    """

    lineas = []
    citas = {}

    for numero, documento in enumerate(
        fragmentos,
        start=1,
    ):
        metadata = documento.metadata

        identificador = metadata.get("id")
        titulo = metadata.get("titulo")

        if not identificador or not titulo:
            raise ValueError(
                "El fragmento no tiene metadatos "
                "suficientes para generar una cita."
            )

        fuente = f"{identificador} | {titulo}"

        lineas.append(
            f"[{numero}] {documento.page_content}"
        )

        citas[numero] = fuente

    contexto = "\n\n".join(lineas)

    return contexto, citas


def construir_prompt(pregunta, k=3):
    """
    Recupera fragmentos y construye un prompt
    con citas documentales.
    """

    if not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacia.")

    fragmentos = recuperar_fragmentos(
        pregunta=pregunta,
        k=k,
    )

    contexto, citas = formatear_contexto(
        fragmentos
    )

    prompt = PROMPT_TEMPLATE.format(
        contexto=contexto,
        pregunta=pregunta,
    )

    return prompt, citas


if __name__ == "__main__":
    print("BLOQUE 26: RECUPERACION SEMANTICA")
    print("VECTORES DISPONIBLES:", verificar_indice())
    print("MODULO PREPARADO PARA CONSULTAS")
    print("NO SE REALIZARON LLAMADAS A GEMINI")
