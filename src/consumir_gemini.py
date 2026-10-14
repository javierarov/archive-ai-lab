
# Archive AI Lab
# Unidad 1.3 - Bloque 5
# Primera solicitud a Gemini desde Python

import os
from pathlib import Path

import requests
from dotenv import load_dotenv



def preparar_solicitud(texto):
    
    if not isinstance(texto, str):
        raise ValueError("El contenido debe ser un texto.")

    if not texto.strip():
        raise ValueError("El texto no puede estar vacío.")

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
    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=datos,
            timeout=30
        )

        respuesta.raise_for_status()

        return respuesta

    except requests.exceptions.Timeout:
        print("ERROR: Gemini tardó demasiado en responder.")
        return None

    except requests.exceptions.ConnectionError:
        print("ERROR: No se pudo establecer conexión con Gemini.")
        return None

    except requests.exceptions.HTTPError as error:
        print("ERROR HTTP:", error)
        return None




def extraer_respuesta(resultado):
    try:
        texto = resultado["candidates"][0]["content"]["parts"][0]["text"]

        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("Gemini devolvió un texto vacío o inválido.")

        return texto

    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "La respuesta de Gemini no tiene el formato esperado."
        ) from error


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

        if respuesta is None:
            print("El análisis no pudo completarse.")
            return

        print("Estado HTTP:", respuesta.status_code)

      

        
        # PASO 8: Procesar la respuesta
        try:
            resultado = respuesta.json()
            texto = extraer_respuesta(resultado)

            print("Respuesta de Gemini:")
            print(texto)

        except ValueError as error:
            print("ERROR al procesar la respuesta:")
            print(error)


        

if __name__ == "__main__":
    main()
