from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def construir_cadena(modelo):
    """
    Construye una cadena LangChain de tres pasos:

    1. Extraer información documental.
    2. Generar una descripción archivística.
    3. Revisar la descripción generada.

    No ejecuta el modelo hasta llamar a invoke().
    """

    # PASO 1: Extraer información relevante
    plantilla_extraccion = PromptTemplate.from_template(
        "Analiza el siguiente texto documental y extrae "
        "los hechos, instituciones, personas, lugares y fechas "
        "que aparezcan explícitamente. "
        "No inventes información.\n\n"
        "Texto:\n{texto}"
    )

    # PASO 2: Crear una descripción archivística
    plantilla_descripcion = PromptTemplate.from_template(
        "A partir de la siguiente información extraída, "
        "redacta una descripción archivística breve, "
        "clara y objetiva. "
        "No agregues datos que no estén presentes.\n\n"
        "Información:\n{informacion}"
    )

    # PASO 3: Revisar la descripción
    plantilla_revision = PromptTemplate.from_template(
        "Revisa la siguiente descripción archivística. "
        "Corrige problemas de claridad, redacción o coherencia. "
        "No agregues información nueva. "
        "Devuelve únicamente la descripción revisada.\n\n"
        "Descripción:\n{descripcion}"
    )

    # Conectar los tres pasos
    cadena = (
        plantilla_extraccion
        | modelo
        | StrOutputParser()
        | (lambda informacion: {"informacion": informacion})
        | plantilla_descripcion
        | modelo
        | StrOutputParser()
        | (lambda descripcion: {"descripcion": descripcion})
        | plantilla_revision
        | modelo
        | StrOutputParser()
    )

    return cadena