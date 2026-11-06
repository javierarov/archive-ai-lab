import json
from pathlib import Path

RUTA = Path("resultados/revision_manual.json")

CALIFICACIONES = {
    1: ("si", "parcial", "no"),
    2: ("si", "si", "no"),
    6: ("si", "no", "no"),
    10: ("si", "si", "no"),
    12: ("si", "no", "no"),
    13: ("parcial", "no", "no"),
    17: ("parcial", "no", "no"),
    18: ("si", "no", "no"),
    19: ("si", "si", "no"),
    20: ("si", "si", "no"),
}


def validar_revision():
    revisiones = json.loads(
        RUTA.read_text(encoding="utf-8")
    )

    ids = [caso["id"] for caso in revisiones]

    assert len(revisiones) == 10
    assert len(set(ids)) == 10
    assert set(ids) == set(CALIFICACIONES)

    for caso in revisiones:
        id_caso = caso["id"]

        factual, completitud, contradiccion = (
            CALIFICACIONES[id_caso]
        )

        caso["revision_humana"].update({
            "correccion_factual": factual,
            "completitud": completitud,
            "contradiccion": contradiccion,
            "estado": "validado",
        })

    # Respaldo antes de modificar el archivo.
    respaldo = RUTA.with_name(
        "revision_manual_antes_validacion.json"
    )

    respaldo.write_text(
        RUTA.read_text(encoding="utf-8"),
        encoding="utf-8"
    )

    RUTA.write_text(
        json.dumps(
            revisiones,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("REVISION HUMANA VALIDADA")
    print("Casos revisados:", len(revisiones))
    print("Archivo actualizado:", RUTA)

    print("\nRESUMEN:")
    for caso in revisiones:
        revision = caso["revision_humana"]

        print(
            f"Caso {caso['id']:02d} | "
            f"Factual: {revision['correccion_factual']} | "
            f"Completitud: {revision['completitud']} | "
            f"Contradiccion: {revision['contradiccion']}"
        )


if __name__ == "__main__":
    validar_revision()