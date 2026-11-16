
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

RAIZ = Path(__file__).resolve().parent
INDICE = RAIZ / "vectorstore" / "bloque24"
REGISTRO = RAIZ / "registros_latencia_costo.jsonl"

COLECCION = "archive_ai_bloque24"
MODELO_EMBEDDING = "models/gemini-embedding-001"
MODELO_GENERATIVO = "gemini-3.5-flash-lite"

# Tarifas de referencia: nivel de pago estándar, USD / 1M tokens.
PRECIO_ENTRADA = 0.30
PRECIO_SALIDA = 2.50

PREGUNTAS = {
    1: "Que metadatos descriptivos permiten identificar un documento?",
    2: "Que condiciones ambientales deben controlarse para conservar documentos?",
    3: "Que responsabilidades establece la gobernanza de la informacion?",
}

PROMPT = """Eres un asistente de consulta archivistica.

Responde utilizando exclusivamente los fragmentos siguientes.
Cita cada afirmacion factual con [1], [2], etc.
Si la informacion no alcanza, indicalo claramente.
No inventes informacion.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def verificar_entorno():
    if not INDICE.is_dir():
        raise FileNotFoundError(f"Indice no encontrado: {INDICE}")

    cliente = chromadb.PersistentClient(path=str(INDICE))
    coleccion = cliente.get_collection(COLECCION)

    if coleccion.count() != 10:
        raise RuntimeError(
            f"Se esperaban 10 fragmentos; hay {coleccion.count()}."
        )

    load_dotenv(RAIZ / ".env")
    clave = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not clave:
        raise RuntimeError("No se encontro la clave Gemini.")

    return coleccion


def formatear_contexto(ids, documentos, metadatos):
    partes = []

    for numero, (identificador, texto, metadata) in enumerate(
        zip(ids, documentos, metadatos),
        start=1,
    ):
        metadata = metadata or {}
        fuente = (
            metadata.get("fuente")
            or metadata.get("titulo")
            or metadata.get("source")
            or identificador
        )

        partes.append(
            f"[{numero}] Fuente: {fuente}\n"
            f"ID: {identificador}\n"
            f"Contenido: {texto}"
        )

    return "\n\n".join(partes)


def calcular_costo_referencia(tokens):
    if not tokens:
        return None

    entrada = tokens.get("input_tokens")
    salida = tokens.get("output_tokens")

    if entrada is None or salida is None:
        return None

    return round(
        (
            entrada * PRECIO_ENTRADA
            + salida * PRECIO_SALIDA
        ) / 1_000_000,
        8,
    )


def registrar_consulta(pregunta, k, coleccion):
    if k not in (3, 6):
        raise ValueError("Para esta actividad usa k=3 o k=6.")

    tiempos = {}
    inicio_total = time.perf_counter()

    embedding_modelo = GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDING
    )

    inicio = time.perf_counter()
    vector = embedding_modelo.embed_query(pregunta)
    tiempos["embedding"] = round(
        (time.perf_counter() - inicio) * 1000, 2
    )

    inicio = time.perf_counter()
    resultado = coleccion.query(
        query_embeddings=[vector],
        n_results=k,
        include=["documents", "metadatas"],
    )
    tiempos["busqueda"] = round(
        (time.perf_counter() - inicio) * 1000, 2
    )

    ids = resultado["ids"][0]
    documentos = resultado["documents"][0]
    metadatos = resultado["metadatas"][0]

    contexto = formatear_contexto(
        ids, documentos, metadatos
    )
    mensaje = PROMPT.format(
        contexto=contexto,
        pregunta=pregunta,
    )

    modelo = ChatGoogleGenerativeAI(
        model=MODELO_GENERATIVO,
        temperature=0,
        max_retries=0,
    )

    inicio = time.perf_counter()
    respuesta = modelo.invoke(mensaje)
    tiempos["generacion"] = round(
        (time.perf_counter() - inicio) * 1000, 2
    )

    duracion = round(
        (time.perf_counter() - inicio_total) * 1000, 2
    )

    tokens = (
        dict(respuesta.usage_metadata)
        if respuesta.usage_metadata
        else None
    )

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "modelo_embedding": MODELO_EMBEDDING,
        "modelo_generativo": MODELO_GENERATIVO,
        "coleccion": COLECCION,
        "fragmentos_recuperados": len(ids),
        "ids_recuperados": ids,
        "tiempos_ms": tiempos,
        "tiempo_total_ms": duracion,
        "tokens": tokens,
        "costo_generacion_estimado_usd": (
            calcular_costo_referencia(tokens)
        ),
        "nota_costo": (
            "Estimacion de tarifa pagada estandar para "
            "generacion, no factura real. No incluye embeddings."
        ),
    }

    # Guardar inmediatamente cada consulta terminada.
    with REGISTRO.open("a", encoding="utf-8") as archivo:
        archivo.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )

    print("\nRESPUESTA:")
    print(respuesta.content)

    print("\nREGISTRO:")
    print(
        json.dumps(
            registro, indent=2, ensure_ascii=False
        )
    )
    print(f"\nGuardado en: {REGISTRO}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument(
        "--caso", type=int, choices=(1, 2, 3), default=1
    )
    parser.add_argument(
        "--k", type=int, choices=(3, 6), default=3
    )
    args = parser.parse_args()

    coleccion = verificar_entorno()

    print("BLOQUE 28: LATENCIA Y COSTO RAG")
    print("Vectores:", coleccion.count())
    print("Modelo generativo:", MODELO_GENERATIVO)

    if not args.run:
        print("MODO VERIFICACION")
        print("SIN LLAMADAS A GEMINI")
        return

    print("Pregunta:", PREGUNTAS[args.caso])
    print("k:", args.k)

    registrar_consulta(
        PREGUNTAS[args.caso],
        args.k,
        coleccion,
    )


if __name__ == "__main__":
    main()
