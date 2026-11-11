
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from src.agente_memoria_bloque22 import (
    construir_agente_con_memoria,
)


class ModeloSimulado(BaseChatModel):
    """Modelo simulado que cuenta mensajes de usuario."""

    @property
    def _llm_type(self):
        return "modelo-simulado-memoria"

    def bind_tools(self, tools, **kwargs):
        """Permite construir el agente sin llamar a una API."""
        return self

    def _generate(
        self,
        messages,
        stop=None,
        run_manager=None,
        **kwargs,
    ):
        mensajes_usuario = [
            mensaje
            for mensaje in messages
            if isinstance(mensaje, HumanMessage)
        ]

        respuesta = AIMessage(
            content=(
                "Mensajes de usuario recibidos: "
                f"{len(mensajes_usuario)}"
            )
        )

        return ChatResult(
            generations=[
                ChatGeneration(message=respuesta)
            ]
        )


def test_agente_recibe_historial_por_sesion():
    modelo = ModeloSimulado()

    agente, historiales = construir_agente_con_memoria(modelo)

    sesion_a = {"configurable": {"session_id": "sesion-a"}}
    sesion_b = {"configurable": {"session_id": "sesion-b"}}

    primera = agente.invoke(
        {"entrada": "Documento DOC-003"},
        config=sesion_a,
    )

    segunda = agente.invoke(
        {"entrada": "¿Cuál era el documento?"},
        config=sesion_a,
    )

    independiente = agente.invoke(
        {"entrada": "Hola"},
        config=sesion_b,
    )

    assert "1" in primera["output"]
    assert "2" in segunda["output"]
    assert "1" in independiente["output"]

    assert len(historiales["sesion-a"].messages) == 4
    assert len(historiales["sesion-b"].messages) == 2
