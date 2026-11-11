
import json
from types import SimpleNamespace

from src.trazas_bloque23 import (
    registrar_traza,
    detectar_repeticiones,
)


def crear_accion(nombre, argumentos=None):
    """Crea una acción simulada para probar las trazas."""
    return SimpleNamespace(
        tool=nombre,
        tool_input=argumentos or {},
    )


def test_registrar_traza_jsonl(tmp_path):
    ruta = tmp_path / "trazas.jsonl"

    resultado = {
        "output": "Documento DOC-003 encontrado.",
        "intermediate_steps": [
            (
                crear_accion(
                    "consultar_metadatos",
                    {"identificador": "DOC-003"},
                ),
                "Fecha: 2022-11-04",
            )
        ],
    }

    registrar_traza(
        session_id="sesion-prueba",
        entrada="Consulta DOC-003",
        resultado=resultado,
        archivo=ruta,
    )

    registros = [
        json.loads(linea)
        for linea in ruta.read_text(encoding="utf-8").splitlines()
    ]

    assert len(registros) == 1
    assert registros[0]["session_id"] == "sesion-prueba"
    assert registros[0]["acciones"][0]["herramienta"] == (
        "consultar_metadatos"
    )
    assert registros[0]["acciones"][0]["argumentos"] == {
        "identificador": "DOC-003"
    }


def test_registrar_varias_interacciones(tmp_path):
    ruta = tmp_path / "trazas.jsonl"

    for numero in range(2):
        registrar_traza(
            session_id="sesion-a",
            entrada=f"Consulta {numero}",
            resultado={
                "output": "Respuesta de prueba",
                "intermediate_steps": [],
            },
            archivo=ruta,
        )

    lineas = ruta.read_text(encoding="utf-8").splitlines()

    assert len(lineas) == 2


def test_detectar_repeticiones(tmp_path):
    ruta = tmp_path / "trazas.jsonl"

    accion = crear_accion(
        "consultar_metadatos",
        {"identificador": "DOC-003"},
    )

    registrar_traza(
        session_id="sesion-a",
        entrada="Consulta repetida",
        resultado={
            "output": "Respuesta de prueba",
            "intermediate_steps": [
                (accion, "Primera consulta"),
                (accion, "Segunda consulta"),
            ],
        },
        archivo=ruta,
    )

    alertas = detectar_repeticiones(ruta)

    assert len(alertas) == 1
    assert alertas[0]["herramienta"] == "consultar_metadatos"
    assert alertas[0]["session_id"] == "sesion-a"


def test_sin_alertas_cuando_no_hay_repeticiones(tmp_path):
    ruta = tmp_path / "trazas.jsonl"

    registrar_traza(
        session_id="sesion-a",
        entrada="Consulta normal",
        resultado={
            "output": "Respuesta de prueba",
            "intermediate_steps": [
                (
                    crear_accion("buscar_documentos_filtrados"),
                    "DOC-003",
                ),
                (
                    crear_accion("consultar_metadatos"),
                    "Fecha: 2022-11-04",
                ),
            ],
        },
        archivo=ruta,
    )

    assert detectar_repeticiones(ruta) == []


def test_archivo_inexistente(tmp_path):
    ruta = tmp_path / "archivo_inexistente.jsonl"

    assert detectar_repeticiones(ruta) == []
