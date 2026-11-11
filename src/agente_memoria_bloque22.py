
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import (
    RunnableWithMessageHistory,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

from src.agente_con_herramientas import (
    consultar_metadatos,
    obtener_texto_respuesta,
)
from src.herramientas_bloque22 import (
    buscar_documentos_filtrados,
)


def normalizar_resultado(resultado):
    """Normaliza la respuesta para guardarla en el historial."""
    resultado_normalizado = dict(resultado)

    resultado_normalizado["output"] = obtener_texto_respuesta(
        resultado["output"]
    )

    return resultado_normalizado


def construir_agente_con_memoria(modelo):
    """Construye un agente con herramientas e historial por sesión."""

    herramientas = [
        buscar_documentos_filtrados,
        consultar_metadatos,
    ]

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente de consulta archivística. "
            "Trabajas exclusivamente con un inventario ficticio. "
            "Utiliza las herramientas disponibles para buscar "
            "documentos y consultar metadatos. "
            "Recuerda los documentos mencionados anteriormente "
            "dentro de la conversación. "
            "Si el usuario pregunta por 'ese documento', "
            "identifica el registro mencionado en el historial. "
            "Si se mencionaron varios registros y no está claro "
            "a cuál se refiere, solicita una aclaración. "
            "No inventes documentos ni metadatos."
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{entrada}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agente = create_tool_calling_agent(
        modelo,
        herramientas,
        prompt,
    )

    ejecutor = AgentExecutor(
        agent=agente,
        tools=herramientas,
        return_intermediate_steps=True,
        verbose=False,
        max_iterations=5,
    )

    # Normalizamos la respuesta antes de que sea guardada en memoria.
    # Conservamos intermediate_steps para verificar las herramientas.
    ejecutor_normalizado = ejecutor | RunnableLambda(
        normalizar_resultado
    )

    historiales = {}

    def obtener_historial(session_id):
        if session_id not in historiales:
            historiales[session_id] = InMemoryChatMessageHistory()

        return historiales[session_id]

    agente_con_memoria = RunnableWithMessageHistory(
        ejecutor_normalizado,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )

    return agente_con_memoria, historiales


def consultar(agente, mensaje, session_id):
    """Ejecuta una consulta utilizando una sesión específica."""

    resultado = agente.invoke(
        {"entrada": mensaje},
        config={
            "configurable": {
                "session_id": session_id,
            }
        },
    )

    print(f"\nSESION: {session_id}")
    print(f"CONSULTA: {mensaje}")
    print("RESPUESTA:")
    print(obtener_texto_respuesta(resultado["output"]))

    print("HERRAMIENTAS:")
    for accion, _ in resultado["intermediate_steps"]:
        print(f"- {accion.tool}")

    return resultado


def main():
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        timeout=30,
        max_retries=0,
    )

    agente, historiales = construir_agente_con_memoria(modelo)

    # Primera consulta: identificamos un documento específico.
    consultar(
        agente,
        "Busca el documento DOC-003 sobre patrimonio audiovisual.",
        "sesion-a",
    )

    # Segunda consulta: comprobamos si recuerda el documento.
    consultar(
        agente,
        "¿Cuál es la fecha de ese documento?",
        "sesion-a",
    )

    # Tercera consulta: verificamos una sesión independiente.
    consultar(
        agente,
        "¿De qué documento estábamos hablando?",
        "sesion-b",
    )

    print("\nMENSAJES POR SESION:")
    for identificador, historial in historiales.items():
        print(
            identificador,
            len(historial.messages),
            "mensajes",
        )


if __name__ == "__main__":
    main()
