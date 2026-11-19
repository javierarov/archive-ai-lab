
import json
from pathlib import Path

from google.genai import types

from src.dataset_tipologias_bloque29 import (
    RUTA_DATASET,
    SEMILLA,
    TIPOLOGIAS,
)

from src.validar_dataset_bloque29 import (
    cargar_jsonl,
    validar_dataset,
    comprobar_balance,
    detectar_contaminacion,
)


RAIZ = Path(__file__).resolve().parents[1]

RUTA_RESULTADOS = (
    RAIZ / "resultados"
    / "configuracion_peft_bloque29.json"
)

NOMBRE_MODELO = "citd-archive-ai-lab-v1"

EPOCHS = 5

ADAPTER_SIZE = types.AdapterSize.ADAPTER_SIZE_FOUR


def preparar_ejemplos(entrenamiento):

    problemas = validar_dataset(entrenamiento)

    if problemas:
        raise ValueError(
            f"Dataset invalido: {problemas}"
        )

    return [
        types.TuningExample(
            text_input=ejemplo["text_input"],
            output=ejemplo["output"],
        )
        for ejemplo in entrenamiento
    ]


def preparar_configuracion():

    return types.CreateTuningJobConfig(
        tuning_mode=(
            types.TuningMode.TUNING_MODE_PEFT_ADAPTER
        ),
        adapter_size=ADAPTER_SIZE,
        epoch_count=EPOCHS,
        tuned_model_display_name=NOMBRE_MODELO,
    )


def preparar_laboratorio():

    entrenamiento = cargar_jsonl(
        RUTA_DATASET / "entrenamiento.jsonl"
    )

    evaluacion = cargar_jsonl(
        RUTA_DATASET / "evaluacion.jsonl"
    )

    for conjunto in (entrenamiento, evaluacion):

        problemas = validar_dataset(conjunto)

        if problemas:
            raise ValueError(
                f"Dataset invalido: {problemas}"
            )

    if not comprobar_balance(entrenamiento, 8):
        raise ValueError(
            "Balance de entrenamiento incorrecto."
        )

    if not comprobar_balance(evaluacion, 2):
        raise ValueError(
            "Balance de evaluacion incorrecto."
        )

    contaminacion = detectar_contaminacion(
        entrenamiento,
        evaluacion,
    )

    if (
        contaminacion["ids_compartidos"]
        or contaminacion["textos_compartidos"]
    ):
        raise ValueError(
            "Contaminacion entre conjuntos."
        )

    ejemplos = preparar_ejemplos(entrenamiento)

    dataset = types.TuningDataset(
        examples=ejemplos
    )

    config = preparar_configuracion()

    return dataset, config, evaluacion


def construir_reporte(dataset, config, evaluacion):

    return {
        "bloque": 29,
        "proyecto": "Archive AI Lab",
        "modulo": "CITD",
        "nombre_modelo_propuesto": NOMBRE_MODELO,
        "modalidad": "dry_run",
        "modelo_base": None,
        "entrenamiento_ejecutado": False,
        "modelo_entrenado_disponible": False,
        "llamadas_api": 0,
        "costo_api_usd": 0.0,
        "datos_sinteticos": True,
        "dataset": {
            "total_ejemplos": (
                len(dataset.examples) + len(evaluacion)
            ),
            "entrenamiento": len(dataset.examples),
            "evaluacion_reservada": len(evaluacion),
            "tipologias": list(TIPOLOGIAS),
            "semilla": SEMILLA,
        },
        "configuracion_peft": config.model_dump(
            mode="json",
            exclude_none=True,
        ),
        "exposiciones_teoricas_a_ejemplos": (
            len(dataset.examples) * EPOCHS
        ),
        "limitaciones": [
            "Dataset sintetico de tamano reducido.",
            "No se ha realizado entrenamiento remoto.",
            "No existen metricas de clasificacion.",
            "Modelo base pendiente de seleccion.",
            "Disponibilidad del servicio de tuning no verificada.",
            "Compatible localmente con los tipos del SDK.",
        ],
    }


def guardar_reporte(reporte):

    RUTA_RESULTADOS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RUTA_RESULTADOS.write_text(
        json.dumps(
            reporte,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )


def main():

    print("BLOQUE 29: PERSONALIZACION DOCUMENTAL")
    print("=" * 55)

    dataset, config, evaluacion = preparar_laboratorio()

    print("\nPASO 1: DATASET PARA PEFT")

    print("Entrenamiento:", len(dataset.examples))
    print("Evaluacion reservada:", len(evaluacion))
    print("Tipologias:", len(TIPOLOGIAS))
    print("Dataset validado: True")

    print("\nPASO 2: CONFIGURACION")

    print("Nombre:", config.tuned_model_display_name)
    print("Modo:", config.tuning_mode)
    print("Adapter:", config.adapter_size)
    print("Epochs:", config.epoch_count)

    print("\nPASO 3: EJEMPLO DE ENTRENAMIENTO")

    ejemplo = dataset.examples[0]

    print("Entrada:", ejemplo.text_input)
    print("Salida:", ejemplo.output)

    print("\nPASO 4: CONFIGURACION SERIALIZADA")

    print(
        config.model_dump_json(
            indent=2,
            exclude_none=True,
        )
    )

    print("\nPASO 5: EVIDENCIA")

    reporte = construir_reporte(
        dataset,
        config,
        evaluacion,
    )

    guardar_reporte(reporte)

    print(
        "Exposiciones teoricas:",
        reporte["exposiciones_teoricas_a_ejemplos"],
    )

    print("Reporte guardado:", RUTA_RESULTADOS)

    print("\n" + "=" * 55)
    print("CONFIGURACION PEFT ARCHIVISTICA PREPARADA")
    print("NO SE EJECUTO ENTRENAMIENTO")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()
