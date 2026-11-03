import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Permite importar cliente.py desde la carpeta src
RUTA_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(RUTA_SRC))

from cliente import (
    clasificar_error,
    con_reintento,
    enviar_peticion,
    registrar_costo,
    consultar_modelo,
    HISTORIAL_COSTOS,
    ErrorAutenticacion,
    ErrorTemporal,
)

# ============================================================
# 1. RESPUESTAS EXITOSAS
# ============================================================

def test_respuesta_exitosa():
    assert clasificar_error(200) is None


# ============================================================
# 2. ERRORES DE AUTENTICACION
# ============================================================

@pytest.mark.parametrize("codigo", [401, 403])
def test_error_autenticacion(codigo):
    with pytest.raises(ErrorAutenticacion):
        clasificar_error(codigo)


# ============================================================
# 3. ERRORES TEMPORALES
# ============================================================

@pytest.mark.parametrize("codigo", [429, 500, 502, 503, 504])
def test_error_temporal(codigo):
    with pytest.raises(ErrorTemporal):
        clasificar_error(codigo)


# ============================================================
# 4. ERRORES NO RECUPERABLES
# ============================================================

@pytest.mark.parametrize("codigo", [400, 404, 422])
def test_error_no_recuperable(codigo):
    with pytest.raises(ValueError) as error:
        clasificar_error(codigo)

    assert type(error.value) is ValueError



    # ============================================================
# 5. PRUEBAS DEL MECANISMO DE REINTENTOS
# ============================================================

def test_reintento_exitoso(monkeypatch):
    """Comprueba que una operación se recupera de un error temporal."""

    intentos_realizados = 0
    esperas = []

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: esperas.append(segundos)
    )

    def operacion():
        nonlocal intentos_realizados
        intentos_realizados += 1

        if intentos_realizados < 3:
            raise ErrorTemporal("Error 503 simulado")

        return "OK"

    resultado = con_reintento(
        funcion=operacion,
        intentos=3,
        espera_segundos=2
    )

    assert resultado == "OK"
    assert intentos_realizados == 3
    assert esperas == [2, 4]


def test_reintentos_agotados(monkeypatch):
    """Comprueba que se informa el error tras agotar los intentos."""

    intentos_realizados = 0

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: None
    )

    def operacion():
        nonlocal intentos_realizados
        intentos_realizados += 1
        raise ErrorTemporal("Servicio no disponible")

    with pytest.raises(ErrorTemporal):
        con_reintento(
            funcion=operacion,
            intentos=3,
            espera_segundos=1
        )

    assert intentos_realizados == 3


def test_error_autenticacion_sin_reintento(monkeypatch):
    """Comprueba que un error de autenticación no se reintenta."""

    intentos_realizados = 0
    esperas = []

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: esperas.append(segundos)
    )

    def operacion():
        nonlocal intentos_realizados
        intentos_realizados += 1
        raise ErrorAutenticacion("Credenciales inválidas")

    with pytest.raises(ErrorAutenticacion):
        con_reintento(
            funcion=operacion,
            intentos=3,
            espera_segundos=2
        )

    assert intentos_realizados == 1
    assert esperas == []


def test_limite_maximo_espera(monkeypatch):
    """Comprueba que el backoff respeta el límite máximo."""

    intentos_realizados = 0
    esperas = []

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: esperas.append(segundos)
    )

    def operacion():
        nonlocal intentos_realizados
        intentos_realizados += 1

        if intentos_realizados < 6:
            raise ErrorTemporal("Error temporal")

        return "OK"

    resultado = con_reintento(
        funcion=operacion,
        intentos=6,
        espera_segundos=2,
        espera_maxima=10
    )

    assert resultado == "OK"
    assert intentos_realizados == 6
    assert esperas == [2, 4, 8, 10, 10]


def test_numero_intentos_invalido():
    """Comprueba que no se admiten cero intentos."""

    with pytest.raises(ValueError):
        con_reintento(
            funcion=lambda: "OK",
            intentos=0
        )



        # ============================================================
# 6. PRUEBAS DE ENVIO HTTP
# ============================================================

def test_enviar_peticion_exitosa(monkeypatch):
    """Comprueba una respuesta HTTP 200."""

    monkeypatch.setenv("GEMINI_API_KEY", "clave_simulada")

    respuesta = Mock()
    respuesta.status_code = 200
    respuesta.json.return_value = {"resultado": "OK"}

    solicitud = Mock(return_value=respuesta)

    monkeypatch.setattr(
        "cliente.requests.post",
        solicitud
    )

    resultado = enviar_peticion({"texto": "Prueba"})

    assert resultado == {"resultado": "OK"}
    assert solicitud.call_count == 1

    argumentos = solicitud.call_args.kwargs

    assert argumentos["json"] == {"texto": "Prueba"}
    assert argumentos["timeout"] == 30
    assert argumentos["headers"]["x-goog-api-key"] == "clave_simulada"


@pytest.mark.parametrize("codigo", [401, 403])
def test_enviar_peticion_autenticacion(monkeypatch, codigo):
    """Comprueba errores de credenciales y permisos."""

    monkeypatch.setenv("GEMINI_API_KEY", "clave_simulada")

    respuesta = Mock()
    respuesta.status_code = codigo

    monkeypatch.setattr(
        "cliente.requests.post",
        Mock(return_value=respuesta)
    )

    with pytest.raises(ErrorAutenticacion):
        enviar_peticion({"texto": "Prueba"})


@pytest.mark.parametrize("codigo", [429, 503])
def test_enviar_peticion_error_temporal(monkeypatch, codigo):
    """Comprueba errores temporales del proveedor."""

    monkeypatch.setenv("GEMINI_API_KEY", "clave_simulada")

    respuesta = Mock()
    respuesta.status_code = codigo

    monkeypatch.setattr(
        "cliente.requests.post",
        Mock(return_value=respuesta)
    )

    with pytest.raises(ErrorTemporal):
        enviar_peticion({"texto": "Prueba"})


def test_enviar_peticion_sin_api_key(monkeypatch):
    """Comprueba que no se envían solicitudes sin credenciales."""

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    solicitud = Mock()

    monkeypatch.setattr(
        "cliente.requests.post",
        solicitud
    )

    with pytest.raises(ErrorAutenticacion):
        enviar_peticion({"texto": "Prueba"})

    solicitud.assert_not_called()



    # ============================================================
# 7. PRUEBAS DEL REGISTRO DE COSTOS
# ============================================================

def test_registrar_costo_exitoso():
    """Comprueba el registro de tokens y costo estimado."""

    HISTORIAL_COSTOS.clear()

    respuesta = {
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 500,
            "totalTokenCount": 1500
        }
    }

    registro = registrar_costo(respuesta)

    assert registro["tokens_entrada"] == 1000
    assert registro["tokens_salida"] == 500
    assert registro["tokens_totales"] == 1500
    assert registro["costo_estimado_usd"] == 0.0003
    assert len(HISTORIAL_COSTOS) == 1


def test_registrar_costo_sin_metadata():
    """Comprueba una respuesta sin información de consumo."""

    HISTORIAL_COSTOS.clear()

    registro = registrar_costo({})

    assert registro["tokens_entrada"] == 0
    assert registro["tokens_salida"] == 0
    assert registro["tokens_totales"] == 0
    assert registro["costo_estimado_usd"] == 0


def test_registrar_costo_acumulado():
    """Comprueba el registro de múltiples operaciones."""

    HISTORIAL_COSTOS.clear()

    respuesta = {
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 500,
            "totalTokenCount": 1500
        }
    }

    registrar_costo(respuesta)
    registrar_costo(respuesta)

    assert len(HISTORIAL_COSTOS) == 2

    costo_total = sum(
        registro["costo_estimado_usd"]
        for registro in HISTORIAL_COSTOS
    )

    assert round(costo_total, 8) == 0.0006


def test_registrar_costo_precios_personalizados():
    """Comprueba el cálculo con precios configurables."""

    HISTORIAL_COSTOS.clear()

    respuesta = {
        "usageMetadata": {
            "promptTokenCount": 1000000,
            "candidatesTokenCount": 1000000,
            "totalTokenCount": 2000000
        }
    }

    registro = registrar_costo(
        respuesta,
        precio_entrada=0.20,
        precio_salida=0.80
    )

    assert registro["costo_estimado_usd"] == 1.0



    # ============================================================
# 8. PRUEBAS DE INTEGRACION DE CONSULTAR_MODELO
# ============================================================

def crear_respuesta_simulada():
    """Genera una respuesta ficticia con el formato de Gemini."""

    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "institucion": "Museo de Historia Natural",
                                "ciudad": "Santiago de Chile"
                            })
                        }
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 1000,
            "candidatesTokenCount": 500,
            "totalTokenCount": 1500
        }
    }


def test_consultar_modelo_exitoso(monkeypatch):
    """Comprueba la extracción y el registro de costos."""

    HISTORIAL_COSTOS.clear()

    monkeypatch.setattr(
        "cliente.enviar_peticion",
        lambda cuerpo: crear_respuesta_simulada()
    )

    resultado = consultar_modelo(
        "El Museo de Historia Natural está en Santiago de Chile."
    )

    assert resultado == {
        "institucion": "Museo de Historia Natural",
        "ciudad": "Santiago de Chile"
    }

    assert len(HISTORIAL_COSTOS) == 1
    assert HISTORIAL_COSTOS[0]["tokens_totales"] == 1500


def test_consultar_modelo_reintento_exitoso(monkeypatch):
    """Comprueba que una consulta se recupera de un error temporal."""

    contador = 0
    esperas = []

    HISTORIAL_COSTOS.clear()

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: esperas.append(segundos)
    )

    def envio_simulado(cuerpo):
        nonlocal contador
        contador += 1

        if contador == 1:
            raise ErrorTemporal("HTTP 503 simulado")

        return crear_respuesta_simulada()

    monkeypatch.setattr(
        "cliente.enviar_peticion",
        envio_simulado
    )

    resultado = consultar_modelo(
        "El Museo de Historia Natural está en Santiago.",
        intentos=3,
        espera_segundos=2
    )

    assert contador == 2
    assert esperas == [2]
    assert resultado["institucion"] == "Museo de Historia Natural"
    assert len(HISTORIAL_COSTOS) == 1


def test_consultar_modelo_error_autenticacion(monkeypatch):
    """Comprueba que los errores de autenticación no se reintentan."""

    contador = 0

    HISTORIAL_COSTOS.clear()

    def envio_simulado(cuerpo):
        nonlocal contador
        contador += 1
        raise ErrorAutenticacion("API Key inválida")

    monkeypatch.setattr(
        "cliente.enviar_peticion",
        envio_simulado
    )

    with pytest.raises(ErrorAutenticacion):
        consultar_modelo(
            "Texto de prueba",
            intentos=3
        )

    assert contador == 1
    assert len(HISTORIAL_COSTOS) == 0


def test_consultar_modelo_reintentos_agotados(monkeypatch):
    """Comprueba el comportamiento cuando fallan todos los intentos."""

    contador = 0
    esperas = []

    monkeypatch.setattr(
        "cliente.time.sleep",
        lambda segundos: esperas.append(segundos)
    )

    def envio_simulado(cuerpo):
        nonlocal contador
        contador += 1
        raise ErrorTemporal("Servicio no disponible")

    monkeypatch.setattr(
        "cliente.enviar_peticion",
        envio_simulado
    )

    with pytest.raises(
        RuntimeError,
        match="El servicio no respondió"
    ):
        consultar_modelo(
            "Texto de prueba",
            intentos=3,
            espera_segundos=2
        )

    assert contador == 3
    assert esperas == [2, 4]