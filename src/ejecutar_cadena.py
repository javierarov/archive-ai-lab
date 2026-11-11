from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.cadena_tres_pasos import construir_cadena


def main():
    # Cargar la clave de Gemini desde .env
    load_dotenv()

    modelo = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    timeout=30,
    max_retries=0
)

    # Construir nuestra cadena de tres pasos
    cadena = construir_cadena(modelo)

    # Texto documental de prueba
    texto = (
        "El Archivo Nacional realizó una jornada de conservación "
        "documental en Santiago el 15 de octubre de 2025. "
        "Durante la actividad, especialistas presentaron técnicas "
        "para preservar documentos históricos y mejorar "
        "su acceso público."
    )

    print("INICIANDO CADENA LANGCHAIN")
    print("\nTEXTO ORIGINAL:")
    print(texto)

    # Ejecutar las tres etapas
    resultado = cadena.invoke({"texto": texto})

    print("\nDESCRIPCION ARCHIVISTICA FINAL:")
    print(resultado)

    print("\nCADENA EJECUTADA CORRECTAMENTE")


if __name__ == "__main__":
    main()
