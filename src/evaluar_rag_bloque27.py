
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.casos_evaluacion_bloque27 import (
    CASOS_EVALUACION,
    validar_casos,
)
from src.metricas_recuperacion_bloque27 import (
    evaluar_caso,
    promediar,
)


RAIZ = Path(__file__).resolve().parents[1]
RUTA_INDICE = RAIZ / "vectorstore" / "bloque24"
RUTA_RESULTADOS = RAIZ / "resultados"
COLECCION = "archive_ai_bloque24"
MODELO = "models/gemini-embedding-001"


def abrir_coleccion():
    """Abre el índice sin generar embeddings."""

    if not RUTA_INDICE.is_dir():
        raise FileNotFoundError(
            f"No existe el índice: {RUTA_INDICE}"
        )

    cliente = chromadb.PersistentClient(
        path=str(RUTA_INDICE)
    )

    coleccion = cliente.get_collection(COLECCION)

    if coleccion.count() != 10:
        raise RuntimeError(
            "Se esperaban 10 fragmentos en Chroma."
        )

    validar_casos(set(coleccion.get()["ids"]))

    return coleccion


def evaluar_ranking(ids_recuperados, relevantes, k):
    """Calcula las métricas sobre los primeros k IDs."""

    return evaluar_caso(
        ids_recuperados[:k],
        relevantes,
    )


def imprimir_resultado(numero, pregunta, ids, m3, m5):
    print()
    print("=" * 65)
    print(f"CASO {numero}: {pregunta}")
    print("RANKING:", ids)

    for k, metricas in [(3, m3), (5, m5)]:
        recall = metricas["recall"]
        recall_txt = (
            "N/A" if recall is None else f"{recall:.3f}"
        )

        f1 = metricas["f1"]
        f1_txt = "N/A" if f1 is None else f"{f1:.3f}"

        print(
            f"k={k} | "
            f"Precisión={metricas['precision']:.3f} | "
            f"Recall={recall_txt} | "
            f"F1={f1_txt}"
        )


def ejecutar_evaluacion():
    coleccion = abrir_coleccion()

    load_dotenv(RAIZ / ".env")

    if not (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    ):
        raise RuntimeError(
            "Falta la clave de Gemini en el entorno."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=MODELO
    )

    resultados = []

    for numero, caso in enumerate(
        CASOS_EVALUACION,
        start=1,
    ):
        pregunta = caso["pregunta"]

        # Una sola llamada de embeddings por pregunta.
        vector_pregunta = embeddings.embed_query(pregunta)

        # Chroma devuelve IDs reales, no solo metadatos.
        busqueda = coleccion.query(
            query_embeddings=[vector_pregunta],
            n_results=5,
        )

        ids = busqueda["ids"][0]

        metricas_3 = evaluar_ranking(
            ids,
            caso["ids_relevantes"],
            k=3,
        )

        metricas_5 = evaluar_ranking(
            ids,
            caso["ids_relevantes"],
            k=5,
        )

        imprimir_resultado(
            numero,
            pregunta,
            ids,
            metricas_3,
            metricas_5,
        )

        resultados.append({
            "pregunta": pregunta,
            "ids_relevantes": sorted(
                caso["ids_relevantes"]
            ),
            "ids_recuperados": ids,
            "k3": metricas_3,
            "k5": metricas_5,
        })

    promedios = {}

    for clave, k in [("k3", 3), ("k5", 5)]:
        promedios[clave] = {
            "k": k,
            "precision": promediar(
                r[clave]["precision"]
                for r in resultados
            ),
            "recall": promediar(
                r[clave]["recall"]
                for r in resultados
            ),
            "f1": promediar(
                r[clave]["f1"]
                for r in resultados
            ),
        }

    reporte = {
        "fecha_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "modelo": MODELO,
        "coleccion": COLECCION,
        "fragmentos_indexados": coleccion.count(),
        "total_preguntas": len(CASOS_EVALUACION),
        "criterio_relevancia": (
            "Etiquetas manuales previas a la recuperación"
        ),
        "resultados": resultados,
        "promedios": promedios,
    }

    RUTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    archivo = (
        RUTA_RESULTADOS
        / "evaluacion_rag_bloque27.json"
    )

    if archivo.exists():
        raise FileExistsError(
            "Ya existe una evaluación guardada. "
            "No se sobrescribirá: " + str(archivo)
        )

    archivo.write_text(
        json.dumps(
            reporte,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 65)
    print("PROMEDIOS FINALES")

    for clave, valores in promedios.items():
        print(
            clave.upper(),
            "| Precisión:",
            round(valores["precision"], 3),
            "| Recall:",
            round(valores["recall"], 3),
            "| F1:",
            round(valores["f1"], 3),
        )

    print("\nRESULTADOS GUARDADOS EN:")
    print(archivo)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        action="store_true",
        help="Ejecuta las consultas reales a Gemini",
    )
    args = parser.parse_args()

    coleccion = abrir_coleccion()

    print("BLOQUE 27: EVALUACIÓN DE RAG")
    print("VECTORES:", coleccion.count())
    print("PREGUNTAS:", len(CASOS_EVALUACION))

    if not args.run:
        print("MODO VERIFICACIÓN LOCAL")
        print("NO SE REALIZARON LLAMADAS A GEMINI")
        print("Usa --run para ejecutar la evaluación.")
        return

    archivo = (
        RUTA_RESULTADOS
        / "evaluacion_rag_bloque27.json"
    )

    if archivo.exists():
        raise FileExistsError(
            "Ya existe el archivo de resultados. "
            "Se evita repetir la evaluación."
        )

    ejecutar_evaluacion()


if __name__ == "__main__":
    main()
