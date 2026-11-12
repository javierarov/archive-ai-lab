
from src.recuperacion_bloque26 import construir_prompt


PREGUNTAS = [
    "¿Cómo evitar el deterioro de documentos?",
    "¿Cómo registrar cambios y responsabilidades documentales?",
]


def main():
    print("=" * 60)
    print("BLOQUE 26: PRUEBAS REALES DE RECUPERACION SEMANTICA")
    print("=" * 60)

    for numero, pregunta in enumerate(PREGUNTAS, start=1):
        print()
        print(f"CONSULTA {numero}")
        print("PREGUNTA:", pregunta)

        prompt, citas = construir_prompt(
            pregunta=pregunta,
            k=3,
        )

        print()
        print("DOCUMENTOS RECUPERADOS:")

        for indice, fuente in citas.items():
            print(f"[{indice}] {fuente}")

        print()
        print("PROMPT GENERADO:")
        print(prompt)

        assert len(citas) == 3
        assert pregunta in prompt
        assert all(
            fuente.startswith("RAG-")
            for fuente in citas.values()
        )

        print()
        print("CONSULTA VALIDADA CORRECTAMENTE")

    print()
    print("=" * 60)
    print("DOS CONSULTAS SEMANTICAS COMPLETADAS")
    print("=" * 60)


if __name__ == "__main__":
    main()
