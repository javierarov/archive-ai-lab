import os
import time
from pathlib import Path
from typing import Callable, Any

import requests
from dotenv import load_dotenv

from consumir_gemini import armar_peticion, extraer_texto


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=RUTA_ENV)

MODELO = "gemini-3.5-flash-lite"

URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODELO}:generateContent"
)

HEADERS = {
    "Content-Type": "application/json"
}


# ============================================================
# 2. CLASES DE ERRORES
# ============================================================

class ErrorAutenticacion(ValueError):
    """Error de credenciales o permisos."""


class ErrorTemporal(TimeoutError):
    """Error temporal que permite realizar reintentos."""


# ============================================================
# 3. CLASIFICACIÓN DE ERRORES HTTP
# ============================================================

def clasificar_error(codigo_http: int) -> None:
    """
    Clasifica una respuesta HTTP.

    401 y 403: errores de autenticación.
    429 y determinados 5XX: errores temporales.
    Otros códigos 4XX: errores no recuperables.
    """

    if codigo_http in (401, 403):
        raise ErrorAutenticacion(
            f"Credencial inválida o sin permiso. HTTP {codigo_http}"
        )

    if codigo_http == 429 or 500 <= codigo_http <= 599:
        raise ErrorTemporal(
            f"Error temporal del proveedor. HTTP {codigo_http}"
        )

    if codigo_http >= 400:
        raise ValueError(
            f"Error HTTP no recuperable: {codigo_http}"
        )


# ============================================================
# 4. ENVÍO DE PETICIONES
# ============================================================

def enviar_peticion(cuerpo: dict) -> dict:
    """
    Envía una solicitud a Gemini.

    Clasifica los errores HTTP y devuelve
    la respuesta como diccionario.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ErrorAutenticacion(
            "No se encontró GEMINI_API_KEY en el archivo .env."
        )

    headers = {
        **HEADERS,
        "x-goog-api-key": api_key
    }

    try:
        respuesta = requests.post(
            URL,
            headers=headers,
            json=cuerpo,
            timeout=30
        )

    except (
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ) as error:
        raise ErrorTemporal(
            "No fue posible completar la conexión con Gemini."
        ) from error

    clasificar_error(respuesta.status_code)

    return respuesta.json()


# ============================================================
# 5. MECANISMO DE REINTENTOS
# ============================================================

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: float = 2,
    espera_maxima: float = 10
) -> Any:
    """
    Ejecuta una operación con backoff exponencial
    y un límite máximo de espera.

    Solo reintenta errores temporales.
    """

    if intentos < 1:
        raise ValueError(
            "El número de intentos debe ser mayor o igual a 1."
        )

    if espera_segundos < 0:
        raise ValueError(
            "El tiempo de espera no puede ser negativo."
        )

    if espera_maxima < 0:
        raise ValueError(
            "La espera máxima no puede ser negativa."
        )

    for intento in range(1, intentos + 1):
        try:
            return funcion()

        except (TimeoutError, ErrorTemporal):
            if intento == intentos:
                raise

            tiempo_espera = min(
                espera_segundos * (2 ** (intento - 1)),
                espera_maxima
            )

            print(
                f"Intento {intento} de {intentos} falló. "
                f"Reintentando en {tiempo_espera} segundos..."
            )

            time.sleep(tiempo_espera)


# ============================================================
# 6. INTERFAZ PÚBLICA
# ============================================================

def consultar_modelo(
    pregunta: str,
    intentos: int = 3,
    espera_segundos: float = 2
) -> dict:
    """
    Consulta Gemini y devuelve los metadatos
    documentales extraídos.

    Coordina la preparación de la petición,
    el envío, los reintentos y la extracción.
    """

    cuerpo = armar_peticion(pregunta)

    try:
        respuesta = con_reintento(
            funcion=lambda: enviar_peticion(cuerpo),
            intentos=intentos,
            espera_segundos=espera_segundos
        )

    except TimeoutError as error:
        raise RuntimeError(
            "El servicio no respondió tras varios intentos. "
            "Intenta nuevamente más tarde."
        ) from error

    # Registrar el consumo de la consulta exitosa
    registrar_costo(respuesta)

    # Extraer y devolver los metadatos
    return extraer_texto(respuesta)

# ============================================================
# 7. REGISTRO DE CONSUMO Y COSTOS
# ============================================================

HISTORIAL_COSTOS = []


def registrar_costo(
    respuesta: dict,
    precio_entrada: float = 0.10,
    precio_salida: float = 0.40
) -> dict:
    """
    Registra tokens y calcula un costo estimado.

    Los precios son valores de ejemplo en USD
    por millón de tokens, no tarifas oficiales.

    No representa necesariamente el importe facturado.
    """

    uso = respuesta.get("usageMetadata", {})

    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)

    tokens_totales = uso.get(
        "totalTokenCount",
        tokens_entrada + tokens_salida
    )

    costo_entrada = (
        tokens_entrada / 1_000_000
    ) * precio_entrada

    costo_salida = (
        tokens_salida / 1_000_000
    ) * precio_salida

    costo_estimado = costo_entrada + costo_salida

    registro = {
        "tokens_entrada": tokens_entrada,
        "tokens_salida": tokens_salida,
        "tokens_totales": tokens_totales,
        "costo_estimado_usd": round(costo_estimado, 8)
    }

    HISTORIAL_COSTOS.append(registro)

    return registro
