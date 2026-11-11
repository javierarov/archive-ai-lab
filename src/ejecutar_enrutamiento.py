
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.enrutamiento import construir_cadena


RUTA_RESULTADOS = Path("resultados/enrutamiento_bloque19.json")


def guardar_resultados(resultados):
    RUTA_RESULTADOS.parent.mkdir(exist_ok=True)

    RUTA_RESULTADOS.write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def main():
    load_dotenv(dotenv_path=Path.cwd() / ".env")

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        timeout=30,
        max_retries=0,
    )

    cadena = construir_cadena(modelo)

    mensajes = [
        {
            "tipo": "pregunta",
            "mensaje": (
                "¿Cómo puedo solicitar acceso a documentos "
                "históricos digitalizados?"
            ),
        },
        {
            "tipo": "queja",
            "mensaje": (
                "No puedo recuperar un documento desde "
                "el catálogo digital."
            ),
        },
        {
            "tipo": "sugerencia",
            "mensaje": (
                "Sería útil incorporar filtros por fecha "
                "e institución en el buscador."
            ),
        },
    ]

    if RUTA_RESULTADOS.exists():
        resultados = json.loads(
            RUTA_RESULTADOS.read_text(encoding="utf-8")
        )
    else:
        resultados = []

    completados = {
        item["tipo"]
        for item in resultados
        if item.get("estado") == "exitoso"
    }

    print("ARCHIVE AI LAB - BLOQUE 19", flush=True)

    for caso in mensajes:
        tipo = caso["tipo"]
        mensaje = caso["mensaje"]

        if tipo in completados:
            print(f"\nOMITIENDO {tipo}: ya completado")
            continue

        print(f"\nPROBANDO: {tipo.upper()}", flush=True)

        try:
            respuesta = cadena.invoke({
                "mensaje": mensaje
            })

            nuevo_resultado = {
                "tipo": tipo,
                "mensaje": mensaje,
                "respuesta": respuesta,
                "estado": "exitoso"
            }

            resultados = [
                item
                for item in resultados
                if item["tipo"] != tipo
            ]

            resultados.append(nuevo_resultado)
            guardar_resultados(resultados)

            print("RESPUESTA:", respuesta, flush=True)

        except Exception as error:
            print(
                f"ERROR: {type(error).__name__}: {error}",
                flush=True
            )
            print(
                "Ejecucion detenida. "
                "Los resultados anteriores permanecen guardados."
            )
            break

    print("\nEJECUCION FINALIZADA")


if __name__ == "__main__":
    main()
