
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)


# Inventario ficticio para pruebas del Bloque 21
INVENTARIO = {
    "DOC-001": {
        "titulo": "Manual de conservación documental",
        "institucion": "Archivo de Demostración",
        "fecha": "2024-03-15",
        "soporte": "Documento digital",
        "descripcion": (
            "Manual sobre técnicas de conservación preventiva "
            "para colecciones documentales."
        ),
    },
    "DOC-002": {
        "titulo": "Registro de exposición fotográfica",
        "institucion": "Centro Cultural de Demostración",
        "fecha": "2023-08-10",
        "soporte": "Fotografía digital",
        "descripcion": (
            "Registro de una exposición sobre patrimonio "
            "fotográfico regional."
        ),
    },
    "DOC-003": {
        "titulo": "Entrevista sobre patrimonio audiovisual",
        "institucion": "Archivo de Demostración",
        "fecha": "2022-11-04",
        "soporte": "Audio digital",
        "descripcion": (
            "Entrevista sobre preservación y acceso "
            "a colecciones audiovisuales."
        ),
    },
}


@tool
def buscar_documentos(consulta: str) -> str:
    """Busca registros del inventario por título o descripción.
    Úsala cuando el usuario necesite encontrar documentos por tema
    y todavía no conozca su identificador.
    """
    palabras = consulta.lower().split()
    coincidencias = []

    for identificador, registro in INVENTARIO.items():
        texto = (
            registro["titulo"] + " " + registro["descripcion"]
        ).lower()

        if any(palabra in texto for palabra in palabras):
            coincidencias.append(
                f"{identificador}: {registro['titulo']}"
            )

    if not coincidencias:
        return "No se encontraron documentos para esa consulta."

    return "\n".join(coincidencias)


@tool
def consultar_metadatos(identificador: str) -> str:
    """Consulta los metadatos de un documento mediante su identificador.
    Úsala cuando el usuario indique un código documental, como DOC-003,
    y solicite información sobre fecha, soporte o institución.
    """
    codigo = identificador.strip().upper()
    registro = INVENTARIO.get(codigo)

    if registro is None:
        return f"No existe un documento con el identificador {codigo}."

    return (
        f"Identificador: {codigo}\n"
        f"Título: {registro['titulo']}\n"
        f"Institución: {registro['institucion']}\n"
        f"Fecha: {registro['fecha']}\n"
        f"Soporte: {registro['soporte']}\n"
        f"Descripción: {registro['descripcion']}"
    )


def construir_agente(modelo):
    """Construye el agente y habilita la traza de herramientas."""

    herramientas = [
        buscar_documentos,
        consultar_metadatos,
    ]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de consulta archivística. "
            "Dispones de dos herramientas para consultar un inventario "
            "documental ficticio de demostración. "
            "Utiliza buscar_documentos cuando te soliciten localizar "
            "registros del inventario por tema. "
            "Utiliza consultar_metadatos cuando necesites recuperar "
            "información de un registro mediante su identificador. "
            "Si el usuario hace una pregunta conceptual general, "
            "como qué es la conservación preventiva, responde "
            "directamente sin utilizar herramientas. "
            "No inventes registros ni metadatos. "
            "Distingue claramente entre información del inventario "
            "y explicaciones generales."
        ),
        ("human", "{entrada}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo,
        herramientas,
        prompt,
    )

    return AgentExecutor(
        agent=agente,
        tools=herramientas,
        return_intermediate_steps=True,
        verbose=False,
        max_iterations=5,
    )


def main():
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        timeout=30,
        max_retries=0,
    )

    agente = construir_agente(modelo)

    consultas = [
        "Busca documentos sobre conservación documental.",
        "¿Cuál es la fecha y el soporte del documento DOC-003?",
    ]

    for consulta in consultas:
        print(f"\nCONSULTA: {consulta}", flush=True)

        resultado = agente.invoke({"entrada": consulta})

        print("\nRESPUESTA:")
        print(obtener_texto_respuesta(resultado["output"]))

        print("\nHERRAMIENTAS UTILIZADAS:")
        for accion, observacion in resultado["intermediate_steps"]:
            print(f"- {accion.tool}")
            print(f"  Observación: {observacion}")



def obtener_texto_respuesta(contenido):
    """Extrae el texto visible de la respuesta del agente."""

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        return "\n".join(
            bloque["text"]
            for bloque in contenido
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
        )

    return str(contenido)

if __name__ == "__main__":
    main()
