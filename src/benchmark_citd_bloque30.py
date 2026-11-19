
import json
import re
import time

from collections import Counter
from urllib.request import Request, urlopen

from src.evaluar_modelo_local_bloque30 import (
    RAIZ,
    MODELO,
    URL,
    CASOS,
    TIPOLOGIAS,
    construir_prompt,
    evaluar_respuesta,
)

from src.dataset_tipologias_bloque29 import (
    RUTA_DATASET,
)

from src.validar_dataset_bloque29 import (
    cargar_jsonl,
)


RUTA_BASELINE = (
    RAIZ / "resultados"
    / "evaluacion_modelo_local_bloque30.json"
)

RUTA_RESULTADO = (
    RAIZ / "resultados"
    / "benchmark_citd_bloque30.json"
)


EXPERIMENTOS = {
    "A": {
        "nombre": "Zero-shot",
        "few_shot": False,
        "json_restringido": False,
    },
    "B": {
        "nombre": "Few-shot",
        "few_shot": True,
        "json_restringido": False,
    },
    "C": {
        "nombre": "Zero-shot + JSON Schema",
        "few_shot": False,
        "json_restringido": True,
    },
    "D": {
        "nombre": "Few-shot + JSON Schema",
        "few_shot": True,
        "json_restringido": True,
    },
}


ESQUEMA_JSON = {
    "type": "object",
    "properties": {
        "tipologia": {
            "type": "string",
            "enum": list(TIPOLOGIAS),
        },
        "categoria": {
            "type": "string",
            "enum": list(TIPOLOGIAS.values()),
        },
    },
    "required": [
        "tipologia",
        "categoria",
    ],
    "additionalProperties": False,
}


def obtener_ejemplos_few_shot():

    entrenamiento = cargar_jsonl(
        RUTA_DATASET / "entrenamiento.jsonl"
    )

    seleccionados = {}

    for ejemplo in entrenamiento:

        salida = json.loads(ejemplo["output"])

        tipo = salida["tipologia"]

        if tipo not in seleccionados:
            seleccionados[tipo] = ejemplo

    if set(seleccionados) != set(TIPOLOGIAS):
        raise ValueError(
            "Faltan tipologias en los ejemplos."
        )

    return [
        seleccionados[tipo]
        for tipo in TIPOLOGIAS
    ]


def construir_prompt_few_shot(texto):

    ejemplos = obtener_ejemplos_few_shot()

    bloques = []

    for ejemplo in ejemplos:

        bloques.append(
            "Documento:\n"
            + ejemplo["text_input"]
            + "\nRespuesta:\n"
            + ejemplo["output"]
        )

    instrucciones = (
        "Estudia estos ejemplos de clasificacion "
        "documental antes de responder.\n\n"
        + "\n\n".join(bloques)
    )

    return (
        instrucciones
        + "\n\n"
        + construir_prompt(texto)
    )


def consultar_modelo(texto, configuracion):

    if configuracion["few_shot"]:

        prompt = construir_prompt_few_shot(
            texto
        )

    else:

        prompt = construir_prompt(texto)

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 42,
            "num_predict": 200,
        },
    }

    if configuracion["json_restringido"]:

        payload["format"] = ESQUEMA_JSON

    peticion = Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    inicio = time.perf_counter()

    with urlopen(peticion, timeout=180) as respuesta:
        resultado = json.load(respuesta)

    latencia = (
        time.perf_counter() - inicio
    ) * 1000

    return resultado["response"], latencia


def retirar_markdown(respuesta):

    texto = respuesta.strip()

    coincidencia = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```",
        texto,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if coincidencia:
        return coincidencia.group(1).strip()

    return texto


def construir_registro(
    numero,
    texto,
    esperada,
    respuesta,
    latencia,
):

    estricta = evaluar_respuesta(
        respuesta,
        esperada,
    )

    recuperada = evaluar_respuesta(
        retirar_markdown(respuesta),
        esperada,
    )

    return {
        "id": f"baseline-{numero:03d}",
        "texto": texto,
        "tipologia_esperada": esperada,
        "respuesta_original": respuesta,
        "latencia_ms": round(latencia, 2),
        "evaluacion_estricta": estricta,
        "evaluacion_recuperada": recuperada,
    }


def calcular_metricas(registros):

    total = len(registros)

    metricas = {}

    for modalidad in (
        "evaluacion_estricta",
        "evaluacion_recuperada",
    ):

        metricas[modalidad] = {}

        for campo in (
            "json_valido",
            "esquema_valido",
            "clasificacion_correcta",
            "categoria_consistente",
        ):

            cantidad = sum(
                r[modalidad][campo]
                for r in registros
            )

            metricas[modalidad][campo] = {
                "correctos": cantidad,
                "total": total,
                "porcentaje": round(
                    cantidad / total * 100,
                    2,
                ),
            }

        completos = sum(
            all(
                r[modalidad][campo]
                for campo in (
                    "esquema_valido",
                    "clasificacion_correcta",
                    "categoria_consistente",
                )
            )
            for r in registros
        )

        metricas[modalidad]["respuesta_correcta"] = {
            "correctos": completos,
            "total": total,
            "porcentaje": round(
                completos / total * 100,
                2,
            ),
        }

    predicciones = Counter(
        str(
            r["evaluacion_recuperada"][
                "tipologia_predicha"
            ]
        )
        for r in registros
    )

    incumplimientos = total - metricas[
        "evaluacion_estricta"
    ]["esquema_valido"]["correctos"]

    return {
        "metricas": metricas,
        "predicciones": dict(predicciones),
        "incumplimientos_formato": incumplimientos,
        "problema_de_formato_o_tono": (
            incumplimientos / total >= 0.15
        ),
        "latencia_promedio_ms": round(
            sum(r["latencia_ms"] for r in registros)
            / total,
            2,
        ),
    }


def recuperar_baseline():

    datos = json.loads(
        RUTA_BASELINE.read_text(
            encoding="utf-8"
        )
    )

    originales = datos["registros"]

    if datos["modelo"] != MODELO:
        raise ValueError("Modelo base diferente.")

    if len(originales) != len(CASOS):
        raise ValueError("Cantidad incorrecta de casos.")

    registros = []

    for numero, original in enumerate(
        originales,
        start=1,
    ):

        esperada, texto = CASOS[numero - 1]

        if (
            original["texto"] != texto
            or original["tipologia_esperada"] != esperada
        ):
            raise ValueError(
                "Los casos del baseline no coinciden."
            )

        registros.append(
            construir_registro(
                numero,
                original["texto"],
                original["tipologia_esperada"],
                original["respuesta_original"],
                original["latencia_ms"],
            )
        )

    return registros


def ejecutar_experimento(configuracion):

    registros = []

    for numero, (esperada, texto) in enumerate(
        CASOS,
        start=1,
    ):

        respuesta, latencia = consultar_modelo(
            texto,
            configuracion,
        )

        registro = construir_registro(
            numero,
            texto,
            esperada,
            respuesta,
            latencia,
        )

        registros.append(registro)

        print(
            f"Caso {numero:02d}/{len(CASOS)} | "
            f"Esperada: {esperada} | "
            "Predicha: "
            + str(
                registro["evaluacion_recuperada"][
                    "tipologia_predicha"
                ]
            ),
            flush=True,
        )

    return registros


def mostrar_resultado(resultado):

    for modalidad, metricas in (
        resultado["metricas"].items()
    ):

        print("\n" + modalidad.upper())

        for nombre, metrica in metricas.items():

            print(
                f"{nombre}: "
                f"{metrica['correctos']}/"
                f"{metrica['total']} "
                f"({metrica['porcentaje']}%)"
            )

    print(
        "\nPredicciones:",
        resultado["predicciones"],
    )

    print(
        "Incumplimientos de formato:",
        resultado["incumplimientos_formato"],
    )

    print(
        "Latencia promedio:",
        resultado["latencia_promedio_ms"],
        "ms",
    )


def main():

    print("BLOQUE 30: BENCHMARK COMPARATIVO CITD")
    print("=" * 60)

    print("Modelo:", MODELO)

    reporte = {
        "modelo": MODELO,
        "casos_por_experimento": len(CASOS),
        "llamadas_gemini": 0,
        "costo_api_externa_usd": 0.0,
        "entrenamiento_ejecutado": False,
        "experimentos": {},
    }

    for codigo, configuracion in (
        EXPERIMENTOS.items()
    ):

        print("\n" + "=" * 60)

        print(
            f"EXPERIMENTO {codigo}: "
            f"{configuracion['nombre']}"
        )

        if codigo == "A":

            registros = recuperar_baseline()

            print(
                "Reutilizando evidencia original."
            )

        else:

            registros = ejecutar_experimento(
                configuracion
            )

        resultado = calcular_metricas(registros)

        mostrar_resultado(resultado)

        reporte["experimentos"][codigo] = {
            "configuracion": configuracion,
            "registros": registros,
            **resultado,
        }

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

    print("\n" + "=" * 60)
    print("RESUMEN COMPARATIVO")

    for codigo, resultado in (
        reporte["experimentos"].items()
    ):

        estricta = resultado["metricas"][
            "evaluacion_estricta"
        ]

        recuperada = resultado["metricas"][
            "evaluacion_recuperada"
        ]

        print(
            f"{codigo} | "
            f"JSON: "
            f"{estricta['json_valido']['porcentaje']}% | "
            f"Accuracy recuperada: "
            f"{recuperada['clasificacion_correcta']['porcentaje']}% | "
            f"Respuesta correcta estricta: "
            f"{estricta['respuesta_correcta']['porcentaje']}%"
        )

    print("\nReporte:", RUTA_RESULTADO)

    print("BENCHMARK FINALIZADO")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()
