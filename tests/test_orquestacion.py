
import logging

from langchain_core.runnables import RunnableLambda

from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_cadena_queja_segura,
    procesar_mensaje_seguro,
)


def provocar_fallo(entrada):
    """Simula un error de conexión con Gemini."""
    raise ConnectionError("Error de red simulado")


def test_queja_usa_fallback_ante_fallo():
    """La ruta de quejas debe devolver una respuesta alternativa."""

    cadena_queja = RunnableLambda(provocar_fallo)
    cadena_segura = construir_cadena_queja_segura(cadena_queja)

    resultado = cadena_segura.invoke({
        "mensaje": "No puedo acceder al catálogo digital."
    })

    assert isinstance(resultado, str)
    assert "identificador del documento" in resultado.lower()


def test_enrutamiento_queja_con_fallback():
    """Comprueba el fallback dentro del enrutamiento completo."""

    clasificador = RunnableLambda(lambda entrada: "queja")

    cadena_queja = construir_cadena_queja_segura(
        RunnableLambda(provocar_fallo)
    )

    flujo = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador,
        cadena_queja=cadena_queja,
        cadena_sugerencia=RunnableLambda(
            lambda entrada: "respuesta de sugerencia"
        ),
        cadena_pregunta=RunnableLambda(
            lambda entrada: "respuesta de pregunta"
        ),
    )

    resultado = procesar_mensaje_seguro(
        flujo,
        "No puedo recuperar un documento."
    )

    assert "identificador del documento" in resultado.lower()


def test_fallo_clasificacion_no_detiene_flujo(caplog):
    """Un fallo del clasificador debe entregar una respuesta segura."""

    clasificador = RunnableLambda(provocar_fallo)

    flujo = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador,
        cadena_queja=RunnableLambda(
            lambda entrada: "respuesta de queja"
        ),
        cadena_sugerencia=RunnableLambda(
            lambda entrada: "respuesta de sugerencia"
        ),
        cadena_pregunta=RunnableLambda(
            lambda entrada: "respuesta de pregunta"
        ),
    )

    with caplog.at_level(logging.ERROR):
        resultado = procesar_mensaje_seguro(
            flujo,
            "Mensaje documental de prueba"
        )

    assert "no pudimos procesar" in resultado.lower()
    assert any(
        "Error no controlado" in registro.message
        for registro in caplog.records
    )


def test_flujo_normal_no_activa_fallback():
    """Un flujo exitoso debe conservar la respuesta principal."""

    clasificador = RunnableLambda(lambda entrada: "queja")

    cadena_queja = construir_cadena_queja_segura(
        RunnableLambda(
            lambda entrada: "respuesta normal de queja"
        )
    )

    flujo = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador,
        cadena_queja=cadena_queja,
    )

    resultado = procesar_mensaje_seguro(
        flujo,
        "Tengo un problema con el catálogo."
    )

    assert resultado == "respuesta normal de queja"
