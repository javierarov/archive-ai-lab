
import json

import pytest

from src.evaluar_modelo_local_bloque30 import (
    evaluar_respuesta,
)

from src.benchmark_citd_bloque30 import (
    retirar_markdown,
    construir_registro,
    calcular_metricas,
    obtener_ejemplos_few_shot,
)

from src.metricas_clasificacion_bloque30 import (
    CLASES,
    SIN_PREDICCION,
    division_segura,
    construir_matriz_confusion,
    calcular_metricas_clase,
    calcular_metricas_globales,
)


RESPUESTA_VALIDA = json.dumps({
    "tipologia": "carta",
    "categoria": "Comunicacion",
})


# ==========================================
# VALIDACION DE RESPUESTAS
# ==========================================


def test_json_valido():

    resultado = evaluar_respuesta(
        RESPUESTA_VALIDA,
        "carta",
    )

    assert resultado["json_valido"] is True
    assert resultado["esquema_valido"] is True
    assert resultado["clasificacion_correcta"] is True
    assert resultado["categoria_consistente"] is True


def test_rechazar_markdown_estricto():

    respuesta = (
        "```json\n"
        + RESPUESTA_VALIDA
        + "\n```"
    )

    resultado = evaluar_respuesta(
        respuesta,
        "carta",
    )

    assert resultado["json_valido"] is False


def test_recuperar_json_markdown():

    respuesta = (
        "```json\n"
        + RESPUESTA_VALIDA
        + "\n```"
    )

    assert retirar_markdown(
        respuesta
    ) == RESPUESTA_VALIDA


def test_conservar_json_original():

    assert retirar_markdown(
        RESPUESTA_VALIDA
    ) == RESPUESTA_VALIDA


def test_categoria_inconsistente():

    respuesta = json.dumps({
        "tipologia": "informe",
        "categoria": "Comunicacion",
    })

    resultado = evaluar_respuesta(
        respuesta,
        "informe",
    )

    assert resultado["esquema_valido"] is True
    assert resultado["clasificacion_correcta"] is True
    assert resultado["categoria_consistente"] is False


def test_campos_adicionales():

    respuesta = json.dumps({
        "tipologia": "carta",
        "categoria": "Comunicacion",
        "campo_extra": "no permitido",
    })

    resultado = evaluar_respuesta(
        respuesta,
        "carta",
    )

    assert resultado["json_valido"] is True
    assert resultado["esquema_valido"] is False


def test_tipologia_desconocida():

    respuesta = json.dumps({
        "tipologia": "desconocida",
        "categoria": "Comunicacion",
    })

    resultado = evaluar_respuesta(
        respuesta,
        "carta",
    )

    assert resultado["esquema_valido"] is False


# ==========================================
# BENCHMARK
# ==========================================


def test_evaluacion_estricta_y_recuperada():

    respuesta = (
        "```json\n"
        + RESPUESTA_VALIDA
        + "\n```"
    )

    registro = construir_registro(
        1,
        "Documento ficticio",
        "carta",
        respuesta,
        100,
    )

    assert not registro[
        "evaluacion_estricta"
    ]["json_valido"]

    assert registro[
        "evaluacion_recuperada"
    ]["json_valido"]


def test_metricas_benchmark():

    registro = construir_registro(
        1,
        "Documento ficticio",
        "carta",
        RESPUESTA_VALIDA,
        100,
    )

    resultado = calcular_metricas(
        [registro]
    )

    estricta = resultado["metricas"][
        "evaluacion_estricta"
    ]

    assert estricta[
        "respuesta_correcta"
    ]["porcentaje"] == 100

    assert resultado[
        "incumplimientos_formato"
    ] == 0


def test_ejemplos_few_shot_balanceados():

    ejemplos = obtener_ejemplos_few_shot()

    assert len(ejemplos) == 5

    clases = {
        json.loads(e["output"])["tipologia"]
        for e in ejemplos
    }

    assert clases == set(CLASES)


# ==========================================
# METRICAS DE CLASIFICACION
# ==========================================


def test_division_segura():

    assert division_segura(3, 4) == 0.75

    assert division_segura(1, 0) == 0


def test_matriz_confusion():

    reales = [
        "carta",
        "carta",
        "acta",
    ]

    predichas = [
        "carta",
        "acta",
        "acta",
    ]

    matriz = construir_matriz_confusion(
        reales,
        predichas,
        CLASES,
    )

    assert matriz["carta"]["carta"] == 1

    assert matriz["carta"]["acta"] == 1

    assert matriz["acta"]["acta"] == 1


def test_matriz_sin_prediccion():

    matriz = construir_matriz_confusion(
        ["carta"],
        [None],
        CLASES,
    )

    assert matriz["carta"][
        SIN_PREDICCION
    ] == 1


def test_longitudes_incompatibles():

    with pytest.raises(ValueError):

        construir_matriz_confusion(
            ["carta"],
            [],
            CLASES,
        )


def test_clase_real_desconocida():

    with pytest.raises(ValueError):

        construir_matriz_confusion(
            ["desconocida"],
            ["carta"],
            CLASES,
        )


def test_metricas_memorando_experimento_d():

    reales = [
        tipo
        for tipo in CLASES
        for _ in range(4)
    ]

    predichas = [
        "carta",
        "carta",
        "carta",
        "memorando",

        "memorando",
        "informe",
        "memorando",
        "memorando",

        "decreto",
        "decreto",
        "memorando",
        "decreto",

        "informe",
        "informe",
        "informe",
        "informe",

        "memorando",
        "memorando",
        "informe",
        "memorando",
    ]

    matriz = construir_matriz_confusion(
        reales,
        predichas,
        CLASES,
    )

    resultado = calcular_metricas_clase(
        matriz,
        "memorando",
    )

    assert resultado["tp"] == 3
    assert resultado["fp"] == 5
    assert resultado["fn"] == 1
    assert resultado["tn"] == 11

    assert resultado["precision"] == 0.375
    assert resultado["recall"] == 0.75
    assert resultado["f1_score"] == 0.5


def test_clasificacion_perfecta():

    resultado = calcular_metricas_globales(
        CLASES,
        CLASES,
        CLASES,
    )

    assert resultado["accuracy"] == 1.0

    assert resultado["macro_avg"][
        "f1_score"
    ] == 1.0


def test_clasificacion_totalmente_incorrecta():

    resultado = calcular_metricas_globales(
        ["carta", "acta"],
        ["acta", "carta"],
        CLASES,
    )

    assert resultado["accuracy"] == 0.0

    assert resultado["macro_avg"][
        "f1_score"
    ] == 0.0


def test_macro_y_weighted_balanceados():

    resultado = calcular_metricas_globales(
        CLASES,
        ["memorando"] * 5,
        CLASES,
    )

    assert resultado["macro_avg"] == (
        resultado["weighted_avg"]
    )


def test_rechazar_evaluacion_vacia():

    with pytest.raises(ValueError):

        calcular_metricas_globales(
            [],
            [],
            CLASES,
        )
