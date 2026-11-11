
import json
from datetime import datetime, timezone
from pathlib import Path


def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
    archivo="resultados/trazas_agente_bloque23.jsonl",
) -> None:
    """Guarda la ejecución del agente como una línea JSON."""

    ruta = Path(archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)

    acciones = []

    for accion, observacion in resultado.get(
        "intermediate_steps", []
    ):
        acciones.append({
            "herramienta": accion.tool,
            "argumentos": accion.tool_input,
            "observacion": str(observacion),
        })

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": acciones,
        "respuesta_final": str(resultado.get("output", "")),
    }

    with ruta.open("a", encoding="utf-8") as archivo_salida:
        archivo_salida.write(
            json.dumps(registro, ensure_ascii=False) + "\n"
        )


def detectar_repeticiones(
    archivo="resultados/trazas_agente_bloque23.jsonl",
):
    """Detecta herramientas llamadas consecutivamente."""

    ruta = Path(archivo)

    if not ruta.exists():
        return []

    alertas = []

    with ruta.open("r", encoding="utf-8") as entrada:
        for numero_linea, linea in enumerate(entrada, start=1):
            if not linea.strip():
                continue

            registro = json.loads(linea)

            herramientas = [
                accion["herramienta"]
                for accion in registro.get("acciones", [])
            ]

            for indice in range(1, len(herramientas)):
                if herramientas[indice] == herramientas[indice - 1]:
                    alertas.append({
                        "linea": numero_linea,
                        "session_id": registro.get("session_id"),
                        "herramienta": herramientas[indice],
                    })
                    break

    return alertas
