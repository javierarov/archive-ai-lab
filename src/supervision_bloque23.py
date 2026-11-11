
from datetime import datetime, timezone

from src.agente_con_herramientas import INVENTARIO


# Registro temporal de decisiones de supervisión
REGISTRO_APROBACIONES = []


def registrar_decision(
    identificador: str,
    aprobado: bool,
    motivo: str,
) -> None:
    """Registra una decisión humana sobre una operación sensible."""

    REGISTRO_APROBACIONES.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "herramienta": "simular_eliminacion_documental",
        "identificador": identificador,
        "aprobado": aprobado,
        "motivo": motivo,
    })


def simular_eliminacion_documental(
    identificador: str,
    aprobacion_humana: bool = False,
) -> str:
    """Simula una eliminación documental solo con aprobación humana.

    Esta función no modifica ni elimina registros del inventario.
    El argumento aprobacion_humana representa una decisión humana
    proporcionada externamente, nunca una decisión del agente.
    """

    codigo = identificador.strip().upper()

    if codigo not in INVENTARIO:
        return f"No existe el documento {codigo}."

    if aprobacion_humana is not True:
        registrar_decision(
            codigo,
            aprobado=False,
            motivo="Sin aprobación humana explícita",
        )

        return (
            f"Operación rechazada para {codigo}. "
            "Se requiere aprobación humana explícita."
        )

    registrar_decision(
        codigo,
        aprobado=True,
        motivo="Aprobación humana registrada",
    )

    return (
        f"Simulación autorizada para {codigo}. "
        "No se ha eliminado ni modificado ningún documento."
    )
