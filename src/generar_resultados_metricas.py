import json
from pathlib import Path

from metricas import calcular_metricas


RUTA_ENTRADA = Path("resultados/evaluacion_bloque15.json")
RUTA_SALIDA = Path("resultados/resultados_metricas.json")


def generar_resultados():
    casos = json.loads(
        RUTA_ENTRADA.read_text(encoding="utf-8")
    )

    resultados = []

    for caso in casos:
        if "respuesta_modelo" not in caso:
            raise ValueError(
                f"El caso {caso['id']} no tiene respuesta de Gemini."
            )

        metricas = calcular_metricas(
            caso["tokens_referencia"],
            caso["tokens_respuesta"]
        )

        resultado = {
            "id": caso["id"],
            "entrada": caso["entrada"],
            "referencia": caso["referencia"],
            "respuesta_modelo": caso["respuesta_modelo"],
            "coincidencia_cruda": caso["coincidencia_cruda"],
            "coincidencia_procesada": caso["coincidencia_procesada"],
            "precision": metricas["precision"],
            "cobertura": metricas["cobertura"],
            "f1": metricas["f1"]
        }

        resultados.append(resultado)

    resultados.sort(key=lambda caso: caso["id"])

    assert len(resultados) == 20
    assert [caso["id"] for caso in resultados] == list(range(1, 21))

    RUTA_SALIDA.parent.mkdir(exist_ok=True)

    RUTA_SALIDA.write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("RESULTADOS GENERADOS CORRECTAMENTE")
    print("Total de casos:", len(resultados))

    print("\nRESUMEN DE METRICAS")

    for caso in resultados:
        print(
            f"Caso {caso['id']:02d} | "
            f"Precision: {caso['precision']:.4f} | "
            f"Cobertura: {caso['cobertura']:.4f} | "
            f"F1: {caso['f1']:.4f}"
        )

    promedio_f1 = sum(
        caso["f1"] for caso in resultados
    ) / len(resultados)

    print("\nF1 promedio:", round(promedio_f1, 4))

    print("\nArchivo generado:", RUTA_SALIDA)


if __name__ == "__main__":
    generar_resultados()
    