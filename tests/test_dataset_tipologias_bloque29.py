
import json
from copy import deepcopy

from google.genai import types

from src.dataset_tipologias_bloque29 import (
    TIPOLOGIAS,
    construir_dataset,
    dividir_dataset,
    obtener_balance,
)

from src.validar_dataset_bloque29 import (
    validar_dataset,
    comprobar_balance,
    detectar_contaminacion,
)

from src.personalizacion_bloque29 import (
    preparar_ejemplos,
    preparar_configuracion,
    construir_reporte,
)


# ==========================================
# CONSTRUCCION DEL DATASET
# ==========================================


def test_total_ejemplos():
    ejemplos = construir_dataset()

    assert len(ejemplos) == 50


def test_total_tipologias():
    assert len(TIPOLOGIAS) == 5


def test_balance_dataset_maestro():
    ejemplos = construir_dataset()
    balance = obtener_balance(ejemplos)

    assert all(
        cantidad == 10
        for cantidad in balance.values()
    )


def test_identificadores_unicos():
    ejemplos = construir_dataset()

    ids = [
        ejemplo["id"]
        for ejemplo in ejemplos
    ]

    assert len(ids) == len(set(ids))


def test_estructura_salida():
    ejemplos = construir_dataset()

    for ejemplo in ejemplos:

        salida = json.loads(
            ejemplo["output"]
        )

        assert set(salida) == {
            "tipologia",
            "categoria",
        }


# ==========================================
# VALIDACION DE CALIDAD
# ==========================================


def test_dataset_valido():
    ejemplos = construir_dataset()

    assert validar_dataset(ejemplos) == []


def test_detectar_entrada_vacia():
    ejemplos = construir_dataset()

    ejemplos[0]["text_input"] = ""

    problemas = validar_dataset(ejemplos)

    assert any(
        "text_input invalido" in problema
        for problema in problemas
    )


def test_detectar_id_duplicado():
    ejemplos = construir_dataset()

    ejemplos.append(
        deepcopy(ejemplos[0])
    )

    problemas = validar_dataset(ejemplos)

    assert any(
        "ID duplicado" in problema
        for problema in problemas
    )


def test_detectar_texto_duplicado():
    ejemplos = construir_dataset()

    ejemplos[1]["text_input"] = (
        ejemplos[0]["text_input"]
    )

    problemas = validar_dataset(ejemplos)

    assert any(
        "Texto duplicado" in problema
        for problema in problemas
    )


def test_detectar_json_invalido():
    ejemplos = construir_dataset()

    ejemplos[0]["output"] = "no es json"

    problemas = validar_dataset(ejemplos)

    assert any(
        "JSON de salida invalido" in problema
        for problema in problemas
    )


def test_detectar_tipologia_desconocida():
    ejemplos = construir_dataset()

    ejemplos[0]["output"] = json.dumps({
        "tipologia": "desconocida",
        "categoria": "Comunicacion",
    })

    problemas = validar_dataset(ejemplos)

    assert any(
        "tipologia desconocida" in problema
        for problema in problemas
    )


def test_detectar_categoria_inconsistente():
    ejemplos = construir_dataset()

    ejemplos[0]["output"] = json.dumps({
        "tipologia": "carta",
        "categoria": "Categoria incorrecta",
    })

    problemas = validar_dataset(ejemplos)

    assert any(
        "categoria inconsistente" in problema
        for problema in problemas
    )


# ==========================================
# SEPARACION DE CONJUNTOS
# ==========================================


def test_division_80_20():
    ejemplos = construir_dataset()

    train, evaluacion = dividir_dataset(
        ejemplos
    )

    assert len(train) == 40
    assert len(evaluacion) == 10


def test_division_estratificada():
    ejemplos = construir_dataset()

    train, evaluacion = dividir_dataset(
        ejemplos
    )

    assert comprobar_balance(train, 8)

    assert comprobar_balance(
        evaluacion,
        2,
    )


def test_ausencia_de_contaminacion():
    ejemplos = construir_dataset()

    train, evaluacion = dividir_dataset(
        ejemplos
    )

    resultado = detectar_contaminacion(
        train,
        evaluacion,
    )

    assert resultado["ids_compartidos"] == []
    assert resultado["textos_compartidos"] == []

    # Introducir una fuga de datos intencional.
    evaluacion_contaminada = evaluacion + [
        deepcopy(train[0])
    ]

    resultado = detectar_contaminacion(
        train,
        evaluacion_contaminada,
    )

    assert train[0]["id"] in resultado[
        "ids_compartidos"
    ]

    assert resultado["textos_compartidos"]


def test_division_reproducible():
    ejemplos = construir_dataset()

    primera = dividir_dataset(ejemplos)
    segunda = dividir_dataset(ejemplos)

    assert primera == segunda


# ==========================================
# CONFIGURACION PEFT
# ==========================================


def test_conversion_tuning_examples():
    ejemplos = construir_dataset()

    train, _ = dividir_dataset(ejemplos)

    resultado = preparar_ejemplos(train)

    assert len(resultado) == 40

    assert all(
        isinstance(e, types.TuningExample)
        for e in resultado
    )

    for original, convertido in zip(
        train,
        resultado,
    ):
        assert convertido.text_input == (
            original["text_input"]
        )

        assert convertido.output == (
            original["output"]
        )


def test_modo_peft():
    config = preparar_configuracion()

    assert config.tuning_mode == (
        types.TuningMode.TUNING_MODE_PEFT_ADAPTER
    )


def test_hiperparametros():
    config = preparar_configuracion()

    assert config.epoch_count == 5

    assert config.adapter_size == (
        types.AdapterSize.ADAPTER_SIZE_FOUR
    )

    assert config.tuned_model_display_name == (
        "citd-archive-ai-lab-v1"
    )


def test_reporte_dry_run():
    ejemplos = construir_dataset()

    train, evaluacion = dividir_dataset(
        ejemplos
    )

    dataset = types.TuningDataset(
        examples=preparar_ejemplos(train)
    )

    config = preparar_configuracion()

    reporte = construir_reporte(
        dataset,
        config,
        evaluacion,
    )

    assert reporte["modalidad"] == "dry_run"

    assert reporte[
        "entrenamiento_ejecutado"
    ] is False

    assert reporte[
        "modelo_entrenado_disponible"
    ] is False

    assert reporte["llamadas_api"] == 0
    assert reporte["costo_api_usd"] == 0.0

    assert reporte["dataset"][
        "entrenamiento"
    ] == 40

    assert reporte["dataset"][
        "evaluacion_reservada"
    ] == 10

    assert reporte[
        "exposiciones_teoricas_a_ejemplos"
    ] == 200
