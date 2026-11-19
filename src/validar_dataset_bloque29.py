
import json
from collections import Counter

from src.dataset_tipologias_bloque29 import (
    RUTA_DATASET,
    TIPOLOGIAS,
    construir_dataset,
    dividir_dataset,
)


def cargar_jsonl(ruta):

    with ruta.open("r", encoding="utf-8") as archivo:

        return [
            json.loads(linea)
            for linea in archivo
            if linea.strip()
        ]


def normalizar_texto(texto):

    return " ".join(texto.casefold().split())


def validar_dataset(ejemplos):

    problemas = []
    ids_vistos = set()
    textos_vistos = set()

    for numero, ejemplo in enumerate(ejemplos, start=1):

        if not isinstance(ejemplo, dict):
            problemas.append(
                f"Registro {numero}: estructura invalida"
            )
            continue

        identificador = ejemplo.get("id")
        entrada = ejemplo.get("text_input")
        salida = ejemplo.get("output")

        for campo, valor in (
            ("id", identificador),
            ("text_input", entrada),
            ("output", salida),
        ):
            if not isinstance(valor, str) or not valor.strip():
                problemas.append(
                    f"Registro {numero}: campo {campo} invalido"
                )

        if isinstance(identificador, str):

            if identificador in ids_vistos:
                problemas.append(
                    f"ID duplicado: {identificador}"
                )

            ids_vistos.add(identificador)

        if isinstance(entrada, str):

            texto = normalizar_texto(entrada)

            if texto in textos_vistos:
                problemas.append(
                    f"Texto duplicado: {identificador}"
                )

            textos_vistos.add(texto)

        if not isinstance(salida, str):
            continue

        try:
            etiquetas = json.loads(salida)

        except json.JSONDecodeError:
            problemas.append(
                f"{identificador}: JSON de salida invalido"
            )
            continue

        if not isinstance(etiquetas, dict):
            problemas.append(
                f"{identificador}: salida no es un objeto JSON"
            )
            continue

        if set(etiquetas) != {"tipologia", "categoria"}:
            problemas.append(
                f"{identificador}: campos de salida invalidos"
            )
            continue

        tipologia = etiquetas["tipologia"]
        categoria = etiquetas["categoria"]

        if (
            not isinstance(tipologia, str)
            or tipologia not in TIPOLOGIAS
        ):
            problemas.append(
                f"{identificador}: tipologia desconocida"
            )
            continue

        if categoria != TIPOLOGIAS[tipologia]:
            problemas.append(
                f"{identificador}: categoria inconsistente"
            )

        if (
            isinstance(identificador, str)
            and not identificador.startswith(tipologia + "-")
        ):
            problemas.append(
                f"{identificador}: ID inconsistente con tipologia"
            )

    return problemas


def comprobar_balance(ejemplos, cantidad_esperada):

    balance = Counter(
        json.loads(ejemplo["output"])["tipologia"]
        for ejemplo in ejemplos
    )

    esperado = Counter({
        tipologia: cantidad_esperada
        for tipologia in TIPOLOGIAS
    })

    return balance == esperado


def detectar_contaminacion(entrenamiento, evaluacion):

    ids_train = {
        ejemplo["id"] for ejemplo in entrenamiento
    }

    ids_eval = {
        ejemplo["id"] for ejemplo in evaluacion
    }

    textos_train = {
        normalizar_texto(ejemplo["text_input"])
        for ejemplo in entrenamiento
    }

    textos_eval = {
        normalizar_texto(ejemplo["text_input"])
        for ejemplo in evaluacion
    }

    return {
        "ids_compartidos": sorted(ids_train & ids_eval),
        "textos_compartidos": sorted(
            textos_train & textos_eval
        ),
    }


def main():

    maestro = cargar_jsonl(
        RUTA_DATASET / "tipologias_documentales.jsonl"
    )

    entrenamiento = cargar_jsonl(
        RUTA_DATASET / "entrenamiento.jsonl"
    )

    evaluacion = cargar_jsonl(
        RUTA_DATASET / "evaluacion.jsonl"
    )

    print("BLOQUE 29: AUDITORIA DEL DATASET")
    print("=" * 55)

    print("\nPASO 1: INTEGRIDAD")

    assert len(maestro) == 50
    assert len(entrenamiento) == 40
    assert len(evaluacion) == 10

    print("Dataset maestro:", len(maestro))
    print("Entrenamiento:", len(entrenamiento))
    print("Evaluacion:", len(evaluacion))

    print("\nPASO 2: CALIDAD ESTRUCTURAL")

    for nombre, conjunto in (
        ("maestro", maestro),
        ("entrenamiento", entrenamiento),
        ("evaluacion", evaluacion),
    ):

        problemas = validar_dataset(conjunto)

        print(
            f"{nombre}: {len(problemas)} problemas"
        )

        for problema in problemas:
            print(" -", problema)

        assert not problemas

    print("\nPASO 3: BALANCE")

    assert comprobar_balance(maestro, 10)
    assert comprobar_balance(entrenamiento, 8)
    assert comprobar_balance(evaluacion, 2)

    print("Dataset maestro: 10 ejemplos por tipologia")
    print("Entrenamiento: 8 ejemplos por tipologia")
    print("Evaluacion: 2 ejemplos por tipologia")
    print("BALANCE VALIDADO")

    print("\nPASO 4: CONTAMINACION ENTRE CONJUNTOS")

    contaminacion = detectar_contaminacion(
        entrenamiento,
        evaluacion,
    )

    print(
        "IDs compartidos:",
        len(contaminacion["ids_compartidos"]),
    )

    print(
        "Textos compartidos:",
        len(contaminacion["textos_compartidos"]),
    )

    assert not contaminacion["ids_compartidos"]
    assert not contaminacion["textos_compartidos"]

    print("SIN DUPLICADOS ENTRE CONJUNTOS")

    print("\nPASO 5: COBERTURA DEL DATASET")

    registros_maestro = {
        e["id"]: e for e in maestro
    }

    registros_divididos = {
        e["id"]: e
        for e in entrenamiento + evaluacion
    }

    assert registros_maestro == registros_divididos

    print("Los 50 ejemplos se conservaron correctamente")

    print("\nPASO 6: REPRODUCIBILIDAD")

    maestro_esperado = construir_dataset()

    train_esperado, eval_esperada = dividir_dataset(
        maestro_esperado
    )

    assert maestro == maestro_esperado
    assert entrenamiento == train_esperado
    assert evaluacion == eval_esperada

    print("Dataset y division reproducibles")

    print("\n" + "=" * 55)
    print("AUDITORIA DEL DATASET SUPERADA")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()

