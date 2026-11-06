from collections import Counter


def calcular_metricas(
    referencia_tokens: list[str],
    respuesta_tokens: list[str]
) -> dict:
    """
    Calcula precisión, cobertura y F1
    utilizando coincidencias de tokens.
    """

    referencia = Counter(referencia_tokens)
    respuesta = Counter(respuesta_tokens)

    coincidencias = sum(
        (referencia & respuesta).values()
    )

    total_referencia = sum(referencia.values())
    total_respuesta = sum(respuesta.values())

    precision = (
        coincidencias / total_respuesta
        if total_respuesta > 0
        else 0.0
    )

    cobertura = (
        coincidencias / total_referencia
        if total_referencia > 0
        else 0.0
    )

    f1 = (
        2 * precision * cobertura / (precision + cobertura)
        if precision + cobertura > 0
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "cobertura": round(cobertura, 4),
        "f1": round(f1, 4)
    }
