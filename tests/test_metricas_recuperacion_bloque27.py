
import pytest

from src.metricas_recuperacion_bloque27 import (
    precision_at_k,
    recall_at_k,
    calcular_f1,
    promediar,
    evaluar_caso,
)


def test_precision_parcial():
    recuperados = ["doc1", "doc2", "doc3"]
    relevantes = {"doc2"}

    assert precision_at_k(recuperados, relevantes) == pytest.approx(1 / 3)


def test_precision_perfecta():
    recuperados = ["doc1", "doc2"]
    relevantes = {"doc1", "doc2"}

    assert precision_at_k(recuperados, relevantes) == 1.0


def test_precision_sin_resultados():
    assert precision_at_k([], {"doc1"}) == 0.0


def test_precision_sin_aciertos():
    assert precision_at_k(["doc2"], {"doc1"}) == 0.0


def test_recall_parcial():
    recuperados = ["doc1", "doc3"]
    relevantes = {"doc1", "doc2"}

    assert recall_at_k(recuperados, relevantes) == 0.5


def test_recall_perfecto():
    recuperados = ["doc1", "doc2"]
    relevantes = {"doc1", "doc2"}

    assert recall_at_k(recuperados, relevantes) == 1.0


def test_recall_sin_aciertos():
    assert recall_at_k(["doc3"], {"doc1"}) == 0.0


def test_recall_sin_documentos_relevantes():
    assert recall_at_k(["doc1"], set()) is None


def test_recall_sin_resultados():
    assert recall_at_k([], {"doc1"}) == 0.0


def test_f1_equilibrado():
    assert calcular_f1(0.5, 0.5) == 0.5


def test_f1_parcial():
    assert calcular_f1(1 / 3, 0.5) == pytest.approx(0.4)


def test_f1_sin_aciertos():
    assert calcular_f1(0.0, 0.0) == 0.0


def test_f1_sin_recall_definido():
    assert calcular_f1(0.0, None) is None


def test_promedio_ignora_none():
    assert promediar([1.0, 0.5, None]) == 0.75


def test_promedio_lista_vacia():
    assert promediar([]) == 0.0


def test_evaluar_caso():
    resultado = evaluar_caso(
        ["bloque24-003", "bloque24-001", "bloque24-005"],
        {"bloque24-003", "bloque24-004"},
    )

    assert resultado["precision"] == pytest.approx(1 / 3)
    assert resultado["recall"] == 0.5
    assert resultado["f1"] == pytest.approx(0.4)


def test_evaluar_caso_sin_respuesta():
    resultado = evaluar_caso(
        ["bloque24-003", "bloque24-005"],
        set(),
    )

    assert resultado["precision"] == 0.0
    assert resultado["recall"] is None
    assert resultado["f1"] is None
