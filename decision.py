
from pathlib import Path

from src.evaluar_estrategia_bloque30 import (
    evaluar_citd,
)


RAIZ = Path(__file__).resolve().parent

RUTA_DOCUMENTO = (
    RAIZ / "decision_personalizacion.md"
)


def generar_esqueleto_decision(
    problema,
    puntos,
    ganadoras,
):

    lineas = [
        "# Decision de personalizacion",
        "",
        "## 1. El problema",
        problema,
        "",
        "## 2. Resultado del metodo de decision",
    ]

    for tecnica, puntaje in sorted(
        puntos.items(),
        key=lambda elemento: -elemento[1],
    ):

        lineas.append(
            f"- {tecnica}: {puntaje} puntos"
        )

    lineas.append("")

    if max(puntos.values()) == 0:

        lineas.append(
            "**Sin evidencia favorable.**"
        )

    elif len(ganadoras) > 1:

        lineas.append(
            "**Empate entre: "
            + ", ".join(ganadoras)
            + "**"
        )

    else:

        lineas.append(
            f"**Candidata: {ganadoras[0]}**"
        )

    lineas.extend([
        "",
        "## 3. Tecnica elegida y por que",
        "[COMPLETAR: justificacion fundamentada]",
        "",
        "## 4. Que necesitarias para ejecutarla",
        "[COMPLETAR: datos, costos y recursos]",
        "",
    ])

    return "\n".join(lineas)


def main():

    reporte = evaluar_citd()

    problema = (
        "El CITD necesita clasificar documentos "
        "segun su tipologia y devolver resultados "
        "con una estructura JSON consistente."
    )

    documento = generar_esqueleto_decision(
        problema,
        reporte["puntos"],
        reporte["candidatas"],
    )

    print("BLOQUE 30: ACTIVIDAD CORE")
    print("=" * 55)

    print(documento)

    if RUTA_DOCUMENTO.exists():

        print(
            "El documento ya existe. "
            "No se sobrescribira."
        )

    else:

        RUTA_DOCUMENTO.write_text(
            documento,
            encoding="utf-8",
        )

        print("Documento generado:", RUTA_DOCUMENTO)

    print("\nSIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()

