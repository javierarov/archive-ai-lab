
import json
from pathlib import Path

from src.comparar_estrategias_bloque30 import (
    recomendar_estrategia,
    analizar_sensibilidad,
)

from src.dataset_tipologias_bloque29 import (
    RUTA_DATASET,
)

from src.validar_dataset_bloque29 import (
    cargar_jsonl,
    validar_dataset,
)


RAIZ = Path(__file__).resolve().parents[1]

RUTA_RESULTADO = (
    RAIZ / "resultados"
    / "evaluacion_estrategia_bloque30.json"
)


def estimar_costos(
    ejemplos,
    minutos=5,
    tarifa=15000,
    porcentaje_revision=0.20,
    minutos_revision=2,
):

    horas_base = ejemplos * minutos / 60

    horas_revision = (
        ejemplos
        * porcentaje_revision
        * minutos_revision
        / 60
    )

    horas_total = horas_base + horas_revision

    return {
        "ejemplos": ejemplos,
        "horas_etiquetado": round(horas_base, 2),
        "horas_revision": round(horas_revision, 2),
        "horas_totales": round(horas_total, 2),
        "costo_estimado_clp": round(
            horas_total * tarifa, 2
        ),
    }


def evaluar_citd():

    maestro = cargar_jsonl(
        RUTA_DATASET / "tipologias_documentales.jsonl"
    )

    problemas = validar_dataset(maestro)

    if problemas:
        raise ValueError(
            f"Dataset invalido: {problemas}"
        )

    respuestas = {
        "informacion_cambia_seguido": False,
        "problema_de_formato_o_tono": True,
        "dataset_grande_y_de_calidad": False,
        "presupuesto_limitado_o_iterar_rapido": True,
        "necesita_multiples_variantes": False,
    }

    evidencia = {
        "informacion_cambia_seguido": {
            "estado": "supuesto",
            "detalle": (
                "Cinco tipologias documentales "
                "relativamente estables."
            ),
        },
        "problema_de_formato_o_tono": {
            "estado": "hipotesis_no_medida",
            "detalle": (
                "Se busca consistencia JSON. "
                "Falta evaluar 20 respuestas reales."
            ),
        },
        "dataset_grande_y_de_calidad": {
            "estado": "verificado",
            "detalle": (
                f"{len(maestro)} ejemplos sinteticos. "
                "Umbral orientativo: 200 ejemplos. "
                "Calidad semantica pendiente."
            ),
        },
        "presupuesto_limitado_o_iterar_rapido": {
            "estado": "supuesto_de_planificacion",
            "detalle": (
                "Se prioriza experimentacion "
                "de bajo costo."
            ),
        },
        "necesita_multiples_variantes": {
            "estado": "alcance_actual",
            "detalle": (
                "Un unico clasificador documental."
            ),
        },
    }

    puntos, candidatas = recomendar_estrategia(
        respuestas
    )

    sensibilidad = analizar_sensibilidad(
        respuestas
    )

    alternativa = dict(respuestas)

    alternativa["problema_de_formato_o_tono"] = False

    puntos_alt, candidatas_alt = (
        recomendar_estrategia(alternativa)
    )

    objetivo = 200

    faltantes = max(
        0,
        objetivo - len(maestro),
    )

    reporte = {
        "bloque": 30,
        "proyecto": "Archive AI Lab",
        "modulo": "MEEP",
        "caso": "CITD",
        "estado_decision": "provisional",
        "respuestas": respuestas,
        "evidencia": evidencia,
        "puntos": puntos,
        "candidatas": candidatas,
        "sensibilidad": sensibilidad,
        "escenario_sin_problema_de_formato": {
            "respuestas": alternativa,
            "puntos": puntos_alt,
            "candidatas": candidatas_alt,
        },
        "dataset": {
            "ejemplos_actuales": len(maestro),
            "objetivo_orientativo": objetivo,
            "ejemplos_faltantes": faltantes,
        },
        "costos_hipoteticos": {
            "tarifa_hora_clp": 15000,
            "minutos_por_ejemplo": 5,
            "porcentaje_revision": 0.20,
            "minutos_revision": 2,
            "dataset_actual": estimar_costos(
                len(maestro)
            ),
            "dataset_objetivo": estimar_costos(
                objetivo
            ),
            "ampliacion": estimar_costos(
                faltantes
            ),
        },
        "entrenamiento_ejecutado": False,
        "llamadas_api": 0,
        "costo_api_usd": 0.0,
    }

    return reporte


def main():

    print("BLOQUE 30: EVALUACION DEL CITD")
    print("=" * 55)

    reporte = evaluar_citd()

    print("\nPASO 1: ESCENARIO INICIAL")

    for tecnica, puntos in reporte["puntos"].items():
        print(f"{tecnica}: {puntos} puntos")

    print(
        "Candidatas:",
        ", ".join(reporte["candidatas"]),
    )

    print("\nPASO 2: ANALISIS DE SENSIBILIDAD")

    for resultado in reporte["sensibilidad"]:

        print(
            resultado["criterio"],
            "->",
            resultado["ganadoras"],
            "|",
            "CAMBIA"
            if resultado["cambia_resultado"]
            else "IGUAL",
        )

    print("\nPASO 3: ESCENARIO ALTERNATIVO")

    alternativo = reporte[
        "escenario_sin_problema_de_formato"
    ]

    for tecnica, puntos in alternativo["puntos"].items():
        print(f"{tecnica}: {puntos} puntos")

    print(
        "Candidatas:",
        ", ".join(alternativo["candidatas"]),
    )

    print("\nPASO 4: RECURSOS NECESARIOS")

    datos = reporte["dataset"]

    ampliacion = reporte[
        "costos_hipoteticos"
    ]["ampliacion"]

    print("Ejemplos actuales:", datos["ejemplos_actuales"])
    print("Objetivo:", datos["objetivo_orientativo"])
    print("Ejemplos faltantes:", datos["ejemplos_faltantes"])

    print(
        "Horas adicionales:",
        ampliacion["horas_totales"],
    )

    print(
        "Costo adicional estimado:",
        f"CLP {ampliacion['costo_estimado_clp']:,.0f}",
    )

    RUTA_RESULTADO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RUTA_RESULTADO.write_text(
        json.dumps(
            reporte,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print("\nPASO 5: EVIDENCIA")

    print("Reporte:", RUTA_RESULTADO)

    print("\n" + "=" * 55)
    print("EVALUACION DE ESTRATEGIA FINALIZADA")
    print("DECISION PROVISIONAL")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()

