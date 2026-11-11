from langchain_core.language_models.fake import FakeListLLM

from src.cadena_tres_pasos import construir_cadena


def test_cadena_tres_pasos():
    """
    Comprueba que LangChain ejecuta correctamente
    una cadena de tres pasos con un modelo simulado.
    """

    modelo_simulado = FakeListLLM(
        responses=[
            # Respuesta simulada del paso 1
            "Institución: Archivo Nacional. "
            "Lugar: Santiago. "
            "Actividad: recepción de documentos históricos.",

            # Respuesta simulada del paso 2
            "El Archivo Nacional recibió documentos "
            "históricos en Santiago.",

            # Respuesta simulada del paso 3
            "El Archivo Nacional recibió documentos "
            "históricos en Santiago."
        ]
    )

    cadena = construir_cadena(modelo_simulado)

    resultado = cadena.invoke({
        "texto": (
            "El Archivo Nacional recibió documentos "
            "históricos en Santiago."
        )
    })

    assert isinstance(resultado, str)

    assert resultado == (
        "El Archivo Nacional recibió documentos "
        "históricos en Santiago."
    )