from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)


def crear_ruta(nombre, llamadas):
    """Crea una ruta simulada y registra su ejecución."""

    def ejecutar(datos):
        llamadas.append(nombre)
        return f"respuesta de {nombre}"

    return RunnableLambda(ejecutar)


def ejecutar_ruta(categoria):
    """Ejecuta el flujo sin llamar a Gemini."""

    llamadas = []

    clasificador = RunnableLambda(
        lambda datos: categoria
    )

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificador,
        cadena_queja=crear_ruta("queja", llamadas),
        cadena_sugerencia=crear_ruta("sugerencia", llamadas),
        cadena_pregunta=crear_ruta("pregunta", llamadas),
    )

    resultado = cadena.invoke({
        "mensaje": "Consulta sobre acceso a documentos"
    })

    return resultado, llamadas


def test_enrutamiento_queja():
    resultado, llamadas = ejecutar_ruta("queja")

    assert resultado == "respuesta de queja"
    assert llamadas == ["queja"]


def test_enrutamiento_sugerencia():
    resultado, llamadas = ejecutar_ruta("sugerencia")

    assert resultado == "respuesta de sugerencia"
    assert llamadas == ["sugerencia"]


def test_enrutamiento_pregunta():
    resultado, llamadas = ejecutar_ruta("pregunta")

    assert resultado == "respuesta de pregunta"
    assert llamadas == ["pregunta"]


def test_enrutamiento_categoria_desconocida():
    resultado, llamadas = ejecutar_ruta("categoria_desconocida")

    assert resultado == "respuesta de pregunta"
    assert llamadas == ["pregunta"]


def test_normalizacion_clasificacion():
    """Comprueba la limpieza de espacios y mayúsculas."""

    modelo_simulado = RunnableLambda(
        lambda prompt: AIMessage(content="  QUEJA \n")
    )

    clasificador = construir_paso_clasificacion(
        modelo_simulado
    )

    resultado = clasificador.invoke({
        "mensaje": "No puedo acceder al documento."
    })

    assert resultado == "queja"