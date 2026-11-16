
import pytest

from src.evaluar_rag_bloque27 import evaluar_ranking


def test_ranking_k3_recupera_relevante():
    ranking = [
        "bloque24-001",
        "bloque24-002",
        "bloque24-007",
        "bloque24-008",
        "bloque24-009",
    ]

    resultado = evaluar_ranking(
        ranking,
        {"bloque24-001"},
        k=3,
    )

    assert resultado["precision"] == pytest.approx(1 / 3)
    assert resultado["recall"] == 1.0
    assert resultado["f1"] == pytest.approx(0.5)


def test_ranking_k5_reduce_precision():
    ranking = [
        "bloque24-001",
        "bloque24-002",
        "bloque24-007",
        "bloque24-008",
        "bloque24-009",
    ]

    resultado = evaluar_ranking(
        ranking,
        {"bloque24-001"},
        k=5,
    )

    assert resultado["precision"] == pytest.approx(0.2)
    assert resultado["recall"] == 1.0
    assert resultado["f1"] == pytest.approx(1 / 3)


def test_ranking_relevante_en_tercera_posicion():
    ranking = [
        "bloque24-005",
        "bloque24-004",
        "bloque24-006",
    ]

    resultado = evaluar_ranking(
        ranking,
        {"bloque24-006"},
        k=3,
    )

    assert resultado["precision"] == pytest.approx(1 / 3)
    assert resultado["recall"] == 1.0


def test_ranking_sin_aciertos():
    ranking = [
        "bloque24-001",
        "bloque24-002",
        "bloque24-003",
    ]

    resultado = evaluar_ranking(
        ranking,
        {"bloque24-010"},
        k=3,
    )

    assert resultado["precision"] == 0.0
    assert resultado["recall"] == 0.0
    assert resultado["f1"] == 0.0


def test_pregunta_sin_respuesta_documental():
    ranking = [
        "bloque24-005",
        "bloque24-004",
        "bloque24-006",
    ]

    resultado = evaluar_ranking(
        ranking,
        set(),
        k=3,
    )

    assert resultado["precision"] == 0.0
    assert resultado["recall"] is None
    assert resultado["f1"] is None


def test_ranking_respeta_limite_k():
    ranking = [
        "bloque24-001",
        "bloque24-002",
        "bloque24-003",
        "bloque24-004",
        "bloque24-005",
    ]

    relevantes = {"bloque24-005"}

    resultado_k3 = evaluar_ranking(
        ranking, relevantes, k=3
    )

    resultado_k5 = evaluar_ranking(
        ranking, relevantes, k=5
    )

    assert resultado_k3["recall"] == 0.0
    assert resultado_k5["recall"] == 1.0


def test_ranking_vacio():
    resultado = evaluar_ranking(
        [],
        {"bloque24-001"},
        k=3,
    )

    assert resultado["precision"] == 0.0
    assert resultado["recall"] == 0.0
    assert resultado["f1"] == 0.0
