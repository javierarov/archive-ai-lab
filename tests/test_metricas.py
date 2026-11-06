import sys
from pathlib import Path

RUTA_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(RUTA_SRC))

from metricas import calcular_metricas


def test_coincidencia_perfecta():
    referencia = ["museo", "de", "historia", "natural"]
    respuesta = ["museo", "de", "historia", "natural"]

    resultado = calcular_metricas(referencia, respuesta)

    assert resultado["precision"] == 1.0
    assert resultado["cobertura"] == 1.0
    assert resultado["f1"] == 1.0


def test_coincidencia_parcial():
    referencia = ["museo", "de", "historia", "natural"]
    respuesta = ["museo", "historia"]

    resultado = calcular_metricas(referencia, respuesta)

    assert resultado["precision"] == 1.0
    assert resultado["cobertura"] == 0.5
    assert resultado["f1"] == 0.6667


def test_sin_coincidencias():
    referencia = ["biblioteca", "nacional"]
    respuesta = ["universidad", "regional"]

    resultado = calcular_metricas(referencia, respuesta)

    assert resultado["precision"] == 0.0
    assert resultado["cobertura"] == 0.0
    assert resultado["f1"] == 0.0


def test_respuesta_vacia():
    referencia = ["museo", "nacional"]
    respuesta = []

    resultado = calcular_metricas(referencia, respuesta)

    assert resultado["precision"] == 0.0
    assert resultado["cobertura"] == 0.0
    assert resultado["f1"] == 0.0


def test_palabras_repetidas():
    referencia = ["de", "de", "chile"]
    respuesta = ["de", "chile"]

    resultado = calcular_metricas(referencia, respuesta)

    assert resultado["precision"] == 1.0
    assert resultado["cobertura"] == 0.6667
    assert resultado["f1"] == 0.8