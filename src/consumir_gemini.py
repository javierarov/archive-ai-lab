
# Archive AI Lab
# Unidad 1.3 - Bloque 5
# Primera solicitud a Gemini desde Python

import os
from pathlib import Path

import requests
from dotenv import load_dotenv



def preparar_solicitud(texto):
    datos = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Identifica la institución y ciudad: "
                            + texto
                        )
                    }
                ]
            }
        ]
    }

    return datos



def consultar_gemini(url, headers, datos):
    respuesta = requests.post(
        url,
        headers=headers,
        json=datos,
        timeout=30
    )

    return respuesta


def extraer_respuesta(resultado):
    texto = resultado["candidates"][0]["content"]["parts"][0]["text"]

    return texto


# Función principal

def main():
    # PASO 1: Localizar el archivo .env
    carpeta_proyecto = Path(__file__).resolve().parent.parent
    archivo_env = carpeta_proyecto / ".env"

    # PASO 2: Cargar las variables
    load_dotenv(dotenv_path=archivo_env)

    # PASO 3: Obtener nuestra clave
    api_key = os.getenv("GEMINI_API_KEY")

    print("¿Existe .env?", archivo_env.is_file())
    print("¿Python encontró la clave?", bool(api_key))

    if not api_key or api_key == "tu_clave_real":
        print("ERROR: Configura GEMINI_API_KEY en .env")

    else:
        # PASO 4: Definir el modelo
        url = (
            "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash-lite:generateContent"
        )

        # PASO 5: Preparar los encabezados
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }

        # PASO 6: Preparar el contenido
        datos = preparar_solicitud(
            "El Museo de Historia Natural inauguró "
            "una exposición en Santiago de Chile."
        )

        
        # PASO 7: Enviar la solicitud
        respuesta = consultar_gemini(url, headers, datos)

        print("Estado HTTP:", respuesta.status_code)

        # PASO 8: Procesar la respuesta
        resultado = respuesta.json()

        if respuesta.status_code == 200:
            texto = extraer_respuesta(resultado)
            print("Respuesta de Gemini:")
            print(texto)
        else:
            print("Error de la API:")
            print(resultado.get("error", {}).get("message", "Error desconocido"))
        

if __name__ == "__main__":
    main()
