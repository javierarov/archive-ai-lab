
import json
from pathlib import Path

from src.dataset_tipologias_bloque29 import (
    TIPOLOGIAS,
)


RAIZ = Path(__file__).resolve().parents[1]

RUTA_BENCHMARK = (
    RAIZ / "resultados"
    / "benchmark_citd_bloque30.json"
)

RUTA_RESULTADO = (
    RAIZ / "resultados"
    / "metricas_clasificacion_bloque30.json"
)

CLASES = list(TIPOLOGIAS)

SIN_PREDICCION = "sin_prediccion"


def division_segura(numerador, denominador):

    if denominador == 0:
        return 0.0

    return numerador / denominador


def construir_matriz_confusion(
    reales,
    predichas,
    clases,
):

    if len(reales) != len(predichas):
        raise ValueError(
            "Las listas deben tener igual longitud."
        )

    columnas = list(clases) + [SIN_PREDICCION]

    matriz = {
        real: {
            predicha: 0
            for predicha in columnas
        }
        for real in clases
    }

    for real, predicha in zip(
        reales,
        predichas,
    ):

        if real not in clases:
            raise ValueError(
                f"Clase real desconocida: {real}"
            )

        if predicha not in clases:
            predicha = SIN_PREDICCION

        matriz[real][predicha] += 1

    return matriz


def calcular_metricas_clase(
    matriz,
    clase,
):

    tp = matriz[clase][clase]

    fp = sum(
        matriz[real][clase]
        for real in matriz
        if real != clase
    )

    fn = sum(
        cantidad
        for predicha, cantidad
        in matriz[clase].items()
        if predicha != clase
    )

    total = sum(
        sum(fila.values())
        for fila in matriz.values()
    )

    tn = total - tp - fp - fn

    precision = division_segura(
        tp,
        tp + fp,
    )

    recall = division_segura(
        tp,
        tp + fn,
    )

    f1 = division_segura(
        2 * precision * recall,
        precision + recall,
    )

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "support": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def calcular_metricas_globales(
    reales,
    predichas,
    clases,
):

    if not reales:
        raise ValueError(
            "No existen casos para evaluar."
        )

    matriz = construir_matriz_confusion(
        reales,
        predichas,
        clases,
    )

    por_clase = {
        clase: calcular_metricas_clase(
            matriz,
            clase,
        )
        for clase in clases
    }

    total = len(reales)

    aciertos = sum(
        matriz[clase][clase]
        for clase in clases
    )

    macro_avg = {}

    weighted_avg = {}

    for campo in (
        "precision",
        "recall",
        "f1_score",
    ):

        macro_avg[campo] = division_segura(
            sum(
                metricas[campo]
                for metricas
                in por_clase.values()
            ),
            len(clases),
        )

        weighted_avg[campo] = division_segura(
            sum(
                metricas[campo]
                * metricas["support"]
                for metricas
                in por_clase.values()
            ),
            total,
        )

    return {
        "total": total,
        "aciertos": aciertos,
        "accuracy": division_segura(
            aciertos,
            total,
        ),
        "sin_prediccion": sum(
            fila[SIN_PREDICCION]
            for fila in matriz.values()
        ),
        "macro_avg": macro_avg,
        "weighted_avg": weighted_avg,
        "por_clase": por_clase,
        "matriz_confusion": matriz,
    }


def evaluar_experimento(
    registros,
    modalidad,
):

    reales = [
        registro["tipologia_esperada"]
        for registro in registros
    ]

    predichas = [
        registro[modalidad][
            "tipologia_predicha"
        ]
        for registro in registros
    ]

    return calcular_metricas_globales(
        reales,
        predichas,
        CLASES,
    )


def mostrar_matriz(matriz):

    columnas = CLASES + [SIN_PREDICCION]

    abreviaturas = [
        "CAR",
        "ACT",
        "DEC",
        "INF",
        "MEM",
        "N/A",
    ]

    print("\nMATRIZ DE CONFUSION")

    print(
        f"{'REAL / PRED':<16}"
        + "".join(
            f"{nombre:>7}"
            for nombre in abreviaturas
        )
    )

    for real, fila in matriz.items():

        print(
            f"{real:<16}"
            + "".join(
                f"{fila[columna]:>7}"
                for columna in columnas
            )
        )


def mostrar_metricas(resultado):

    print(
        f"\nAccuracy: "
        f"{resultado['accuracy']:.2%}"
    )

    print(
        f"Aciertos: "
        f"{resultado['aciertos']}/"
        f"{resultado['total']}"
    )

    print(
        "Sin prediccion:",
        resultado["sin_prediccion"],
    )

    print("\nMETRICAS POR TIPOLOGIA")

    print(
        f"{'Tipologia':<15}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1-score':>12}"
        f"{'Support':>10}"
    )

    for clase, datos in (
        resultado["por_clase"].items()
    ):

        print(
            f"{clase:<15}"
            f"{datos['precision']:>12.2%}"
            f"{datos['recall']:>12.2%}"
            f"{datos['f1_score']:>12.2%}"
            f"{datos['support']:>10}"
        )

    print("\nPROMEDIOS MACRO")

    for nombre, valor in (
        resultado["macro_avg"].items()
    ):
        print(f" - {nombre}: {valor:.2%}")

    print("\nPROMEDIOS PONDERADOS")

    for nombre, valor in (
        resultado["weighted_avg"].items()
    ):
        print(f" - {nombre}: {valor:.2%}")

    mostrar_matriz(
        resultado["matriz_confusion"]
    )


def main():

    benchmark = json.loads(
        RUTA_BENCHMARK.read_text(
            encoding="utf-8"
        )
    )

    experimentos = benchmark["experimentos"]

    if set(experimentos) != {"A", "B", "C", "D"}:
        raise ValueError(
            "El benchmark esta incompleto."
        )

    print("BLOQUE 30: METRICAS DE CLASIFICACION")
    print("=" * 65)

    print("Modelo:", benchmark["modelo"])

    reporte = {
        "bloque": 30,
        "proyecto": "Archive AI Lab",
        "modulo": "CITD",
        "modelo": benchmark["modelo"],
        "clases": CLASES,
        "fuente": RUTA_BENCHMARK.name,
        "nuevas_consultas": 0,
        "entrenamiento_ejecutado": False,
        "costo_api_externa_usd": 0.0,
        "experimentos": {},
    }

    for codigo, experimento in (
        experimentos.items()
    ):

        nombre = experimento[
            "configuracion"
        ]["nombre"]

        print("\n" + "=" * 65)

        print(
            f"EXPERIMENTO {codigo}: {nombre}"
        )

        reporte["experimentos"][codigo] = {
            "nombre": nombre,
        }

        for modalidad in (
            "evaluacion_estricta",
            "evaluacion_recuperada",
        ):

            resultado = evaluar_experimento(
                experimento["registros"],
                modalidad,
            )

            reporte["experimentos"][codigo][
                modalidad
            ] = resultado

            if modalidad == "evaluacion_recuperada":

                print("\nEVALUACION RECUPERADA")

                mostrar_metricas(resultado)

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

    print("\n" + "=" * 65)
    print("RESUMEN COMPARATIVO")

    print(
        f"{'Exp.':<8}"
        f"{'Accuracy':>12}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1 macro':>12}"
    )

    for codigo, experimento in (
        reporte["experimentos"].items()
    ):

        datos = experimento[
            "evaluacion_recuperada"
        ]

        macro = datos["macro_avg"]

        print(
            f"{codigo:<8}"
            f"{datos['accuracy']:>12.2%}"
            f"{macro['precision']:>12.2%}"
            f"{macro['recall']:>12.2%}"
            f"{macro['f1_score']:>12.2%}"
        )

    print("\nReporte:", RUTA_RESULTADO)

    print("\nMETRICAS CALCULADAS CORRECTAMENTE")
    print("SIN NUEVAS CONSULTAS AL MODELO")


if __name__ == "__main__":
    main()
