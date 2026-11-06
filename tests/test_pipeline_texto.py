import sys
from pathlib import Path

import pytest

RUTA_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(RUTA_SRC))

from pipeline_texto import (
    limpiar_texto,
    tokenizar,
    procesar_texto,
    metadatos_a_texto
)


def test_limpiar_texto():
    texto = "  HOLA,   MUNDO!!!  "

    resultado = limpiar_texto(texto)

    assert resultado == "hola mundo"


def test_tokenizar():
    resultado = tokenizar("archivo audiovisual digital")

    assert resultado == ["archivo", "audiovisual", "digital"]


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El cielo, es AZUL!")

    assert resultado == ["el", "cielo", "es", "azul"]


def test_procesar_texto_vacio():
    resultado = procesar_texto("¡¡¡...!!!")

    assert resultado == []


def test_procesar_texto_unicode():
    texto = "\u00a1EL Museo est\u00e1 en SANTIAGO!"

    resultado = procesar_texto(texto)

    assert resultado == [
        "el", "museo", "est\u00e1", "en", "santiago"
    ]

def test_metadatos_a_texto():
    metadatos = {
        "institucion": "Museo de Historia Natural",
        "ciudad": "Santiago de Chile"
    }

    resultado = metadatos_a_texto(metadatos)

    assert resultado == (
        "Museo de Historia Natural Santiago de Chile"
    )


def test_metadatos_a_texto_con_null():
    metadatos = {
        "institucion": "Museo de Historia Natural",
        "ciudad": None
    }

    resultado = metadatos_a_texto(metadatos)

    assert resultado == "Museo de Historia Natural"