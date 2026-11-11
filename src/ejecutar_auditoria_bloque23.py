
import json
from pathlib import Path
from types import SimpleNamespace

from src.supervision_bloque23 import (
    REGISTRO_APROBACIONES,
    simular_eliminacion_documental,
)
from src.trazas_bloque23 import (
    registrar_traza,
    detectar_repeticiones,
)


RUTA_TRAZAS = Path("resultados/auditoria_bloque23.jsonl")


def main():
    # Se utiliza un archivo de demostración independiente.
    # No se sobrescriben las trazas de otras actividades.
    RUTA_TRAZAS.parent.mkdir(parents=True, exist_ok=True)

    accion_consulta = SimpleNamespace(
        tool="consultar_metadatos",
        tool_input={"identificador": "DOC-003"},
    )

    resultado_consulta = {
        "output": "DOC-003: Entrevista sobre patrimonio audiovisual.",
        "intermediate_steps": [
            (
                accion_consulta,
                "Fecha: 2022-11-04. Soporte: Audio digital.",
            )
        ],
    }

    registrar_traza(
        session_id="auditoria-23",
        entrada="Consultar metadatos de DOC-003",
        resultado=resultado_consulta,
        archivo=RUTA_TRAZAS,
    )

    resultado_sensible = simular_eliminacion_documental(
        identificador="DOC-003",
        aprobacion_humana=False,
    )

    # Incorporamos la decisión de supervisión al registro de auditoría.
    decision = REGISTRO_APROBACIONES[-1]

    accion_supervision = SimpleNamespace(
        tool="simular_eliminacion_documental",
        tool_input={
            "identificador": "DOC-003",
            "aprobacion_humana": False,
        },
    )

    registrar_traza(
        session_id="auditoria-23",
        entrada="Solicitud simulada de eliminación de DOC-003",
        resultado={
            "output": resultado_sensible,
            "intermediate_steps": [
                (
                    accion_supervision,
                    json.dumps(decision, ensure_ascii=False),
                )
            ],
        },
        archivo=RUTA_TRAZAS,
    )

    print("RESULTADO DE SUPERVISION:")
    print(resultado_sensible)

    print("\nDECISION REGISTRADA:")
    print(json.dumps(decision, ensure_ascii=False, indent=2))

    print("\nALERTAS:")
    print(detectar_repeticiones(RUTA_TRAZAS))

    print("\nARCHIVO:")
    print(RUTA_TRAZAS)


if __name__ == "__main__":
    main()
