import json
from pathlib import Path

RUTA_METRICAS = Path("resultados/resultados_metricas.json")
RUTA_REVISION = Path("resultados/revision_manual.json")

CASOS_SELECCIONADOS = [1, 2, 6, 10, 12, 13, 17, 18, 19, 20]

OBSERVACIONES = {
    1: "La ciudad fue abreviada de Santiago de Chile a Santiago.",
    2: "La respuesta coincide exactamente con la referencia.",
    6: "Se extrajo Santiago desde el nombre Biblioteca de Santiago.",
    10: "La respuesta coincide exactamente con la referencia.",
    12: "Se extrajo Concepción desde el nombre de la institución.",
    13: "Se separó Valparaíso del nombre Biblioteca Municipal de Valparaíso.",
    17: "Se agruparon dos instituciones en un único campo.",
    18: "Se seleccionó Chillán pese a existir dos ciudades mencionadas.",
    19: "La respuesta coincide exactamente con la referencia.",
    20: "La respuesta contiene correctamente dos valores nulos, pero F1 es cero."
}


def preparar_revision():
    resultados = json.loads(
        RUTA_METRICAS.read_text(encoding="utf-8")
    )

    revisiones = []

    for caso in resultados:
        if caso["id"] not in CASOS_SELECCIONADOS:
            continue

        revision = {
            "id": caso["id"],
            "entrada": caso["entrada"],
            "referencia": caso["referencia"],
            "respuesta_modelo": caso["respuesta_modelo"],
            "f1": caso["f1"],
            "revision_humana": {
                "correccion_factual": None,
                "completitud": None,
                "contradiccion": None,
                "observaciones": OBSERVACIONES[caso["id"]],
                "estado": "pendiente"
            }
        }

        revisiones.append(revision)

    assert len(revisiones) == 10

    RUTA_REVISION.parent.mkdir(exist_ok=True)

    RUTA_REVISION.write_text(
        json.dumps(revisiones, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("ARCHIVO DE REVISION PREPARADO")
    print("Casos seleccionados:", len(revisiones))
    print("Archivo:", RUTA_REVISION)
    print("Estado: pendiente de validacion humana")


if __name__ == "__main__":
    preparar_revision()
    