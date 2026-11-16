
"""
Conjunto de evaluación del Bloque 27.

Las etiquetas de relevancia se definen antes
de ejecutar el recuperador semántico.

Corpus: Archive AI Lab, Bloque 24.
"""

CASOS_EVALUACION = [
    {
        "pregunta": (
            "Que metadatos descriptivos permiten "
            "identificar un documento?"
        ),
        "ids_relevantes": {"bloque24-001"},
    },
    {
        "pregunta": (
            "Como facilitan los metadatos "
            "el acceso a los documentos?"
        ),
        "ids_relevantes": {"bloque24-002"},
    },
    {
        "pregunta": (
            "Que condiciones ambientales deben "
            "controlarse para conservar documentos?"
        ),
        "ids_relevantes": {"bloque24-003"},
    },
    {
        "pregunta": (
            "Como disminuir la exposicion "
            "de documentos a agentes de dano?"
        ),
        "ids_relevantes": {"bloque24-004"},
    },
    {
        "pregunta": (
            "Que aporta la digitalizacion "
            "de archivos audiovisuales?"
        ),
        "ids_relevantes": {"bloque24-005"},
    },
    {
        "pregunta": (
            "Que controles necesita la preservacion "
            "de archivos audiovisuales digitales?"
        ),
        "ids_relevantes": {"bloque24-006"},
    },
    {
        "pregunta": (
            "Como se organizan los documentos "
            "segun funciones y series?"
        ),
        "ids_relevantes": {"bloque24-007"},
    },
    {
        "pregunta": (
            "Para que sirven los vocabularios "
            "controlados en la recuperacion documental?"
        ),
        "ids_relevantes": {"bloque24-008"},
    },
    {
        "pregunta": (
            "Que responsabilidades establece "
            "la gobernanza de la informacion?"
        ),
        "ids_relevantes": {"bloque24-009"},
    },
    {
        "pregunta": (
            "Como se auditan los cambios "
            "realizados sobre los documentos?"
        ),
        "ids_relevantes": {"bloque24-010"},
    },
    {
        "pregunta": (
            "Cual es el presupuesto anual "
            "del Archivo Nacional para 2027?"
        ),
        "ids_relevantes": set(),
    },
]


def validar_casos(identificadores_disponibles):
    """Verifica la estructura y las etiquetas."""

    if not 8 <= len(CASOS_EVALUACION) <= 15:
        raise ValueError(
            "Se necesitan entre 8 y 15 preguntas."
        )

    preguntas = [
        caso["pregunta"]
        for caso in CASOS_EVALUACION
    ]

    if len(preguntas) != len(set(preguntas)):
        raise ValueError(
            "Existen preguntas duplicadas."
        )

    for caso in CASOS_EVALUACION:
        if not caso["pregunta"].strip():
            raise ValueError("Hay una pregunta vacia.")

        if not caso["ids_relevantes"].issubset(
            identificadores_disponibles
        ):
            raise ValueError(
                "Una etiqueta no existe en el indice: "
                + caso["pregunta"]
            )

    return True
