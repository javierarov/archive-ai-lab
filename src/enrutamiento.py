import logging

from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough


def normalizar_categoria(texto: str) -> str:
    """Normaliza la respuesta de clasificación."""
    return texto.strip().lower().strip(" .!¡")


def construir_paso_clasificacion(modelo):
    """Clasifica un mensaje como pregunta, queja o sugerencia."""

    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje relacionado con "
        "servicios documentales o archivísticos.\n"
        "Responde usando exclusivamente una palabra: "
        "pregunta, queja o sugerencia.\n\n"
        "Mensaje:\n{mensaje}"
    )

    return (
        plantilla
        | modelo
        | StrOutputParser()
        | normalizar_categoria
    )


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """Construye un flujo con dos condiciones y una ruta por defecto."""

    cadena_queja = cadena_queja or RunnablePassthrough()
    cadena_sugerencia = cadena_sugerencia or RunnablePassthrough()
    cadena_pregunta = cadena_pregunta or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (
            lambda entrada: entrada["categoria"] == "queja",
            cadena_queja,
        ),
        (
            lambda entrada: entrada["categoria"] == "sugerencia",
            cadena_sugerencia,
        ),
        cadena_pregunta,
    )

    return (
        RunnablePassthrough.assign(
            categoria=paso_clasificacion
        )
        | bifurcacion
    )

def construir_cadena(modelo):
    """Construye el flujo completo utilizando Gemini."""

    paso_clasificacion = construir_paso_clasificacion(modelo)

    cadena_pregunta = (
        PromptTemplate.from_template(
            "Responde con claridad esta consulta sobre "
            "gestión documental. No inventes procedimientos "
            "ni características de servicios.\n\n"
            "Consulta:\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    cadena_queja = (
        PromptTemplate.from_template(
            "Responde de manera respetuosa y concisa a esta "
            "queja sobre un servicio documental. "
            "Reconoce el problema y sugiere pasos para investigarlo. "
            "Puedes solicitar el identificador del documento y "
            "el mensaje de error. "
            "No afirmes representar a una institución, "
            "no prometas intervenciones de equipos técnicos "
            "ni asegures que el problema será resuelto.\n\n"
            "Queja:\n{mensaje}"
        )


        | modelo
        | StrOutputParser()
    )

    cadena_queja = construir_cadena_queja_segura(cadena_queja)


    cadena_sugerencia = (
        PromptTemplate.from_template(
            "Responde de manera breve y profesional a esta "
            "sugerencia sobre servicios documentales. "
            "Agradece la propuesta y explica cómo podría "
            "evaluarse su viabilidad. "
            "No afirmes que ha sido aprobada, implementada "
            "o incorporada a una hoja de ruta. "
            "Responde exclusivamente en español, "
            "con redacción clara y sin caracteres extraños.\n\n"
            "Sugerencia:\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    return construir_cadena_con_enrutamiento(
        paso_clasificacion=paso_clasificacion,
        cadena_queja=cadena_queja,
        cadena_sugerencia=cadena_sugerencia,
        cadena_pregunta=cadena_pregunta,
    )




# BLOQUE 20: MANEJO DE ERRORES

logger = logging.getLogger(__name__)


RESPUESTA_ERROR_GENERAL = (
    "No pudimos procesar tu mensaje en este momento. "
    "Intenta nuevamente más tarde."
)


def construir_cadena_queja_segura(cadena_queja):
    """
    Protege la ruta de quejas con una respuesta alternativa
    cuando el procesamiento principal lanza una excepción.
    """

    respuesta_alternativa = RunnableLambda(
        lambda entrada: (
            "No fue posible procesar tu consulta en este momento. "
            "Puedes conservar el identificador del documento y "
            "el mensaje de error para intentar nuevamente o "
            "consultar los canales oficiales de soporte."
        )
    )

    return cadena_queja.with_fallbacks(
        [respuesta_alternativa]
    )


def procesar_mensaje_seguro(cadena, mensaje):
    """
    Ejecuta el flujo y captura errores no controlados.
    """

    try:
        return cadena.invoke({"mensaje": mensaje})

    except Exception:
        logger.exception(
            "Error no controlado durante el procesamiento del mensaje"
        )

        return RESPUESTA_ERROR_GENERAL
