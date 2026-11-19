
TECNICAS = (
    "RAG",
    "Fine-tuning completo",
    "PEFT",
)


CRITERIOS = {
    "informacion_cambia_seguido": {
        "RAG": 3,
        "Fine-tuning completo": 0,
        "PEFT": 0,
    },
    "problema_de_formato_o_tono": {
        "RAG": 0,
        "Fine-tuning completo": 1,
        "PEFT": 2,
    },
    "dataset_grande_y_de_calidad": {
        "RAG": 0,
        "Fine-tuning completo": 2,
        "PEFT": 1,
    },
    "presupuesto_limitado_o_iterar_rapido": {
        "RAG": 2,
        "Fine-tuning completo": 0,
        "PEFT": 1,
    },
    "necesita_multiples_variantes": {
        "RAG": 0,
        "Fine-tuning completo": 0,
        "PEFT": 2,
    },
}


CASO_1 = {
    "informacion_cambia_seguido": True,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": False,
    "presupuesto_limitado_o_iterar_rapido": True,
    "necesita_multiples_variantes": False,
}


CASO_2 = {
    "informacion_cambia_seguido": False,
    "problema_de_formato_o_tono": True,
    "dataset_grande_y_de_calidad": True,
    "presupuesto_limitado_o_iterar_rapido": False,
    "necesita_multiples_variantes": False,
}


def validar_respuestas(respuestas):

    if not isinstance(respuestas, dict):
        raise TypeError(
            "Las respuestas deben ser un diccionario."
        )

    faltantes = set(CRITERIOS) - set(respuestas)

    adicionales = set(respuestas) - set(CRITERIOS)

    if faltantes:
        raise ValueError(
            f"Criterios faltantes: {sorted(faltantes)}"
        )

    if adicionales:
        raise ValueError(
            f"Criterios desconocidos: {sorted(adicionales)}"
        )

    for clave, valor in respuestas.items():

        if type(valor) is not bool:
            raise ValueError(
                f"{clave}: debe ser True o False."
            )


def recomendar_estrategia(respuestas):

    validar_respuestas(respuestas)

    puntos = {
        tecnica: 0
        for tecnica in TECNICAS
    }

    for criterio, respuesta in respuestas.items():

        if respuesta:

            for tecnica, valor in (
                CRITERIOS[criterio].items()
            ):

                puntos[tecnica] += valor

    maximo = max(puntos.values())

    ganadoras = [
        tecnica
        for tecnica, valor in puntos.items()
        if valor == maximo
    ]

    return puntos, ganadoras


def analizar_sensibilidad(respuestas):

    puntos_base, ganadoras_base = (
        recomendar_estrategia(respuestas)
    )

    resultados = []

    for criterio in CRITERIOS:

        variante = dict(respuestas)

        variante[criterio] = (
            not variante[criterio]
        )

        puntos, ganadoras = (
            recomendar_estrategia(variante)
        )

        resultados.append({
            "criterio": criterio,
            "valor_original": respuestas[criterio],
            "valor_alternativo": variante[criterio],
            "puntos_originales": puntos_base.copy(),
            "puntos_alternativos": puntos,
            "ganadoras": ganadoras,
            "cambia_resultado": (
                set(ganadoras)
                != set(ganadoras_base)
            ),
        })

    return resultados


def mostrar_resultado(nombre, respuestas):

    puntos, ganadoras = (
        recomendar_estrategia(respuestas)
    )

    print(f"\n{nombre}")
    print("-" * 55)

    for tecnica, valor in puntos.items():
        print(f"{tecnica}: {valor} puntos")

    if max(puntos.values()) == 0:

        print("Sin evidencia favorable.")
        print("Se requiere analisis adicional.")

    elif len(ganadoras) > 1:

        print("EMPATE:", ", ".join(ganadoras))

    else:

        print("Candidata:", ganadoras[0])


def mostrar_sensibilidad(respuestas):

    resultados = analizar_sensibilidad(
        respuestas
    )

    cambios = 0

    for resultado in resultados:

        estado = (
            "CAMBIA"
            if resultado["cambia_resultado"]
            else "IGUAL"
        )

        if resultado["cambia_resultado"]:
            cambios += 1

        print(
            f"\n{resultado['criterio']}"
        )

        print(
            f" {resultado['valor_original']}"
            f" -> {resultado['valor_alternativo']}"
        )

        print(
            " Candidatas:",
            ", ".join(resultado["ganadoras"]),
        )

        print(" Resultado:", estado)

    print(
        f"\nCriterios sensibles: "
        f"{cambios}/{len(resultados)}"
    )


def main():

    print("BLOQUE 30: MOTOR DE DECISION")
    print("=" * 55)

    print("\nPASO 1: CASO CON GANADOR CLARO")

    mostrar_resultado(
        "Caso 1: bot de atencion al cliente",
        CASO_1,
    )

    print("\nPASO 2: CASO CON EMPATE")

    mostrar_resultado(
        "Caso 2: clasificador de errores",
        CASO_2,
    )

    print("\nPASO 3: ANALISIS DE SENSIBILIDAD")

    mostrar_sensibilidad(CASO_2)

    print("\nPASO 4: CASO SIN CRITERIOS FAVORABLES")

    respuestas_vacias = {
        criterio: False
        for criterio in CRITERIOS
    }

    mostrar_resultado(
        "Caso sin evidencia favorable",
        respuestas_vacias,
    )

    print("\n" + "=" * 55)
    print("MOTOR DE DECISION EJECUTADO")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()
