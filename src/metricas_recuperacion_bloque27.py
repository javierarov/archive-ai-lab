
def precision_at_k(ids_recuperados, ids_relevantes):
    """
    Calcula la precision de los fragmentos recuperados.

    Devuelve 0.0 si no se recupero ningun fragmento.
    """

    if not ids_recuperados:
        return 0.0

    relevantes = set(ids_relevantes)

    aciertos = sum(
        identificador in relevantes
        for identificador in ids_recuperados
    )

    return aciertos / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """
    Calcula la exhaustividad.

    Devuelve None cuando no existen fragmentos
    relevantes para la pregunta.
    """

    relevantes = set(ids_relevantes)

    if not relevantes:
        return None

    recuperados = set(ids_recuperados)

    aciertos = len(recuperados & relevantes)

    return aciertos / len(relevantes)


def calcular_f1(precision, recall):
    """
    Calcula la media armonica de precision y recall.
    """

    if recall is None:
        return None

    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
        / (precision + recall)
    )


def promediar(valores):
    """
    Promedia valores numericos e ignora None.
    """

    validos = [
        valor
        for valor in valores
        if valor is not None
    ]

    if not validos:
        return 0.0

    return sum(validos) / len(validos)


def evaluar_caso(ids_recuperados, ids_relevantes):
    """
    Calcula las metricas de una pregunta.
    """

    precision = precision_at_k(
        ids_recuperados,
        ids_relevantes,
    )

    recall = recall_at_k(
        ids_recuperados,
        ids_relevantes,
    )

    f1 = calcular_f1(precision, recall)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


if __name__ == "__main__":
    recuperados = [
        "bloque24-003",
        "bloque24-001",
        "bloque24-005",
    ]

    relevantes = {
        "bloque24-003",
        "bloque24-004",
    }

    resultado = evaluar_caso(
        recuperados,
        relevantes,
    )

    print("BLOQUE 27: METRICAS DE RECUPERACION")
    print("PRECISION:", round(resultado["precision"], 3))
    print("RECALL:", round(resultado["recall"], 3))
    print("F1:", round(resultado["f1"], 3))

    assert round(resultado["precision"], 3) == 0.333
    assert resultado["recall"] == 0.5
    assert round(resultado["f1"], 3) == 0.4

    print("METRICAS VALIDADAS CORRECTAMENTE")
