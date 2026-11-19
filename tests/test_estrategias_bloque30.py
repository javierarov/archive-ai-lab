
import pytest

from src.comparar_estrategias_bloque30 import (
    CRITERIOS,
    CASO_1,
    CASO_2,
    recomendar_estrategia,
    analizar_sensibilidad,
)

from src.evaluar_estrategia_bloque30 import (
    estimar_costos,
    evaluar_citd,
)


def respuestas_base():
    return {
        criterio: False
        for criterio in CRITERIOS
    }


# ==========================================
# ALGORITMO DE DECISION
# ==========================================


def test_caso_uno_rag():

    puntos, candidatas = recomendar_estrategia(
        CASO_1
    )

    assert puntos == {
        "RAG": 5,
        "Fine-tuning completo": 1,
        "PEFT": 3,
    }

    assert candidatas == ["RAG"]


def test_caso_dos_empate():

    puntos, candidatas = recomendar_estrategia(
        CASO_2
    )

    assert puntos == {
        "RAG": 0,
        "Fine-tuning completo": 3,
        "PEFT": 3,
    }

    assert set(candidatas) == {
        "Fine-tuning completo",
        "PEFT",
    }


def test_sin_criterios_favorables():

    puntos, candidatas = recomendar_estrategia(
        respuestas_base()
    )

    assert all(
        valor == 0
        for valor in puntos.values()
    )

    assert len(candidatas) == 3


def test_informacion_cambiante():

    respuestas = respuestas_base()

    respuestas["informacion_cambia_seguido"] = True

    puntos, candidatas = recomendar_estrategia(
        respuestas
    )

    assert puntos["RAG"] == 3
    assert candidatas == ["RAG"]


def test_multiples_variantes():

    respuestas = respuestas_base()

    respuestas["necesita_multiples_variantes"] = True

    puntos, candidatas = recomendar_estrategia(
        respuestas
    )

    assert puntos["PEFT"] == 2
    assert candidatas == ["PEFT"]


def test_todos_los_criterios():

    respuestas = {
        criterio: True
        for criterio in CRITERIOS
    }

    puntos, candidatas = recomendar_estrategia(
        respuestas
    )

    assert puntos == {
        "RAG": 5,
        "Fine-tuning completo": 3,
        "PEFT": 6,
    }

    assert candidatas == ["PEFT"]


# ==========================================
# VALIDACION DE ENTRADAS
# ==========================================


def test_rechazar_lista():

    with pytest.raises(TypeError):

        recomendar_estrategia([])


def test_detectar_criterio_faltante():

    respuestas = respuestas_base()

    del respuestas["informacion_cambia_seguido"]

    with pytest.raises(ValueError):

        recomendar_estrategia(respuestas)


def test_detectar_criterio_desconocido():

    respuestas = respuestas_base()

    respuestas["criterio_inventado"] = True

    with pytest.raises(ValueError):

        recomendar_estrategia(respuestas)


def test_rechazar_texto_como_booleano():

    respuestas = respuestas_base()

    respuestas["informacion_cambia_seguido"] = "si"

    with pytest.raises(ValueError):

        recomendar_estrategia(respuestas)


def test_rechazar_none():

    respuestas = respuestas_base()

    respuestas["informacion_cambia_seguido"] = None

    with pytest.raises(ValueError):

        recomendar_estrategia(respuestas)


# ==========================================
# ANALISIS DE SENSIBILIDAD
# ==========================================


def test_cantidad_variaciones():

    resultados = analizar_sensibilidad(
        CASO_2
    )

    assert len(resultados) == 5


def test_sensibilidad_caso_dos():

    resultados = analizar_sensibilidad(
        CASO_2
    )

    assert all(
        resultado["cambia_resultado"]
        for resultado in resultados
    )


def test_no_modificar_respuestas_originales():

    respuestas = CASO_2.copy()

    original = respuestas.copy()

    analizar_sensibilidad(respuestas)

    assert respuestas == original


def test_inversion_individual():

    resultados = analizar_sensibilidad(
        CASO_2
    )

    for resultado in resultados:

        assert resultado["valor_alternativo"] == (
            not resultado["valor_original"]
        )


# ==========================================
# ESTIMACION DE COSTOS
# ==========================================


def test_costo_50_ejemplos():

    resultado = estimar_costos(50)

    assert resultado["horas_totales"] == 4.5

    assert resultado["costo_estimado_clp"] == 67500


def test_costo_200_ejemplos():

    resultado = estimar_costos(200)

    assert resultado["horas_totales"] == 18

    assert resultado["costo_estimado_clp"] == 270000


def test_costo_ampliacion():

    resultado = estimar_costos(150)

    assert resultado["horas_totales"] == 13.5

    assert resultado["costo_estimado_clp"] == 202500


# ==========================================
# EVALUACION DEL CITD
# ==========================================


def test_evaluacion_citd_provisional():

    reporte = evaluar_citd()

    assert reporte["estado_decision"] == "provisional"

    assert reporte["puntos"] == {
        "RAG": 2,
        "Fine-tuning completo": 1,
        "PEFT": 3,
    }

    assert reporte["candidatas"] == ["PEFT"]

    assert reporte["dataset"]["ejemplos_actuales"] == 50

    assert reporte["dataset"]["ejemplos_faltantes"] == 150

    assert reporte["llamadas_api"] == 0

    assert reporte["entrenamiento_ejecutado"] is False


def test_sensibilidad_citd():

    reporte = evaluar_citd()

    sensibles = {
        resultado["criterio"]
        for resultado in reporte["sensibilidad"]
        if resultado["cambia_resultado"]
    }

    assert sensibles == {
        "informacion_cambia_seguido",
        "problema_de_formato_o_tono",
    }

    alternativo = reporte[
        "escenario_sin_problema_de_formato"
    ]

    assert alternativo["candidatas"] == ["RAG"]
