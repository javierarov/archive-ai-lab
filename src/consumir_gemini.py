
# Archive AI Lab
# Unidad 1.3 - Bloque 5
# Primera solicitud a Gemini desde Python

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

import time

import json

def armar_peticion(texto):

    if not isinstance(texto, str):
        raise ValueError("El texto debe ser una cadena.")

    texto = texto.strip()

    if not texto:
        raise ValueError("El texto no puede estar vacío.")

    instrucciones = (
        "Eres un asistente especializado en extracción de metadatos documentales. "
        "Identifica únicamente la institución y la ciudad mencionadas explícitamente. "
        "No agregues información que no aparezca en el texto. "
        "Si falta algún dato, utiliza null. "
        "Devuelve exclusivamente un objeto JSON válido."
    )

    return {
        "systemInstruction": {
            "parts": [
                {"text": instrucciones}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": texto}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "institucion": {"type": "STRING", "nullable": True},
                    "ciudad": {"type": "STRING", "nullable": True}
                },
                "required": ["institucion", "ciudad"]
            }
        }
    }






def enviar_peticion(url, headers, datos):
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


def extraer_texto(resultado):
    try:
        texto = resultado["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "La respuesta de Gemini no tiene el formato esperado."
        ) from error

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Gemini devolvió un texto vacío o inválido.")

    try:
        datos = json.loads(texto)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini no devolvió un JSON válido."
        ) from error

    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")

    campos_esperados = {"institucion", "ciudad"}

    if set(datos.keys()) != campos_esperados:
        raise ValueError(
            "La respuesta JSON no contiene exactamente los campos esperados."
        )

    for campo in campos_esperados:
        valor = datos[campo]

        if valor is not None and not isinstance(valor, str):
            raise ValueError(
                f"El campo '{campo}' debe ser texto o null."
            )

    return datos

def calcular_costo(uso, precio_entrada, precio_salida):
    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)

    costo_entrada = (tokens_entrada / 1_000_000) * precio_entrada
    costo_salida = (tokens_salida / 1_000_000) * precio_salida

    return costo_entrada + costo_salida


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
        datos = armar_peticion(
        "El Museo de Historia Natural inauguró "
        "una exposición en Santiago de Chile."

)


       
    
       # PASO 7: Enviar la solicitud y medir latencia

        inicio = time.perf_counter()

        respuesta = enviar_peticion(url, headers, datos)

        fin = time.perf_counter()

        latencia = fin - inicio

        print(f"Latencia de la solicitud: {latencia:.2f} segundos")

        if respuesta is None:
            print("El análisis no pudo completarse.")
            return
      

        
        # PASO 8: Procesar la respuesta
        try:
            resultado = respuesta.json()
            datos_extraidos = extraer_texto(resultado)
            uso = resultado.get("usageMetadata", {})

            print("Tokens de entrada:", uso.get("promptTokenCount", "No disponible"))
            print("Tokens de salida:", uso.get("candidatesTokenCount", "No disponible"))
            print("Tokens de razonamiento:", uso.get("thoughtsTokenCount", 0))
            print("Tokens totales:", uso.get("totalTokenCount", "No disponible"))

            print("Respuesta estructurada de Gemini:")
            print(json.dumps(datos_extraidos, ensure_ascii=False, indent=4))

        except ValueError as error:
            print("ERROR al procesar la respuesta:")
            print(error)

            
            # Tarifas hipotéticas para practicar
            precio_entrada = 0.10
            precio_salida = 0.40

            costo = calcular_costo(
                uso,
                precio_entrada,
                precio_salida
            )

            print(f"Costo estimado: US$ {costo:.8f}")



        

if __name__ == "__main__":
    main()