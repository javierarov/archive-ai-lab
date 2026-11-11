
import warnings

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory


def test_memoria_conserva_y_aisla_sesiones():
    historiales = {}

    def obtener_historial(session_id):
        if session_id not in historiales:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                historiales[session_id] = InMemoryChatMessageHistory()
        return historiales[session_id]

    def responder(entrada):
        historial = entrada["chat_history"]
        mensaje = entrada["entrada"]

        return {
            "output": AIMessage(
                content=f"Recibido: {mensaje}. "
                f"Mensajes previos: {len(historial)}"
            )
        }

    cadena = RunnableLambda(responder)

    agente_con_memoria = RunnableWithMessageHistory(
        cadena,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )

    configuracion_a = {
        "configurable": {"session_id": "sesion-a"}
    }

    configuracion_b = {
        "configurable": {"session_id": "sesion-b"}
    }

    agente_con_memoria.invoke(
        {"entrada": "Documento DOC-003"},
        config=configuracion_a,
    )

    segunda_respuesta = agente_con_memoria.invoke(
        {"entrada": "¿Cuál era el documento?"},
        config=configuracion_a,
    )

    respuesta_b = agente_con_memoria.invoke(
        {"entrada": "Hola"},
        config=configuracion_b,
    )

    assert len(historiales["sesion-a"].messages) == 4
    assert len(historiales["sesion-b"].messages) == 2

    assert "Mensajes previos: 2" in segunda_respuesta["output"].content
    assert "Mensajes previos: 0" in respuesta_b["output"].content
