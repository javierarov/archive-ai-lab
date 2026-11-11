
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from src.agente_con_herramientas import INVENTARIO


class ArgumentosBusquedaDocumental(BaseModel):
    """Argumentos para buscar registros documentales."""

    consulta: str = Field(
        min_length=1,
        description=(
            "Tema o palabras que se deben buscar "
            "en el título y descripción de los documentos."
        ),
    )

    tipo_soporte: str = Field(
        default="todos",
        description=(
            "Filtra por soporte documental. "
            "Usa 'todos' si no se solicita un tipo específico. "
            "Ejemplos: 'Audio digital', 'Fotografía digital' "
            "o 'Documento digital'."
        ),
    )

    limite_resultados: int = Field(
        default=5,
        ge=1,
        le=20,
        description=(
            "Número máximo de registros que se devolverán. "
            "Debe ser un número entero entre 1 y 20."
        ),
    )


@tool(
    "buscar_documentos_filtrados",
    args_schema=ArgumentosBusquedaDocumental,
)
def buscar_documentos_filtrados(
    consulta: str,
    tipo_soporte: str = "todos",
    limite_resultados: int = 5,
) -> str:
    """Busca registros del inventario documental por tema.

    Usa esta herramienta cuando el usuario quiera localizar
    documentos y necesite filtrar por soporte o limitar
    la cantidad de resultados.
    """
    palabras = consulta.lower().split()
    coincidencias = []

    for identificador, registro in INVENTARIO.items():
        texto = (
            registro["titulo"] + " " + registro["descripcion"]
        ).lower()

        coincide_tema = any(
            palabra in texto for palabra in palabras
        )

        coincide_soporte = (
            tipo_soporte.lower() == "todos"
            or registro["soporte"].lower()
            == tipo_soporte.lower()
        )

        if coincide_tema and coincide_soporte:
            coincidencias.append(
                f"{identificador}: {registro['titulo']} "
                f"({registro['soporte']})"
            )

    if not coincidencias:
        return "No se encontraron documentos para esos criterios."

    return "\n".join(
        coincidencias[:limite_resultados]
    )
