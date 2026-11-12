
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def construir_corpus():
    """Crea un corpus archivístico ficticio de cinco documentos."""

    registros = [
        {
            "id": "RAG-001",
            "titulo": "Descripción archivística",
            "tema": "metadatos",
            "contenido": (
                "La descripción archivística permite identificar, "
                "contextualizar y recuperar documentos mediante "
                "información estructurada. Los metadatos descriptivos "
                "incluyen título, fecha, productor y alcance del contenido. "
                "La calidad de estos datos mejora la recuperación "
                "y facilita el acceso a los fondos documentales."
            ),
        },
        {
            "id": "RAG-002",
            "titulo": "Conservación preventiva",
            "tema": "conservacion",
            "contenido": (
                "La conservación preventiva reúne medidas destinadas "
                "a disminuir el deterioro de los documentos. "
                "Incluye controlar la temperatura y humedad, "
                "utilizar materiales de almacenamiento adecuados "
                "y reducir la exposición a agentes de daño. "
                "Estas acciones favorecen la preservación a largo plazo."
            ),
        },
        {
            "id": "RAG-003",
            "titulo": "Preservación audiovisual",
            "tema": "audiovisual",
            "contenido": (
                "Los archivos audiovisuales requieren estrategias "
                "de preservación específicas para soportes físicos "
                "y formatos digitales. La digitalización permite "
                "generar copias de acceso, pero no reemplaza "
                "la gestión de integridad, los controles de calidad "
                "ni la planificación de migraciones tecnológicas."
            ),
        },
        {
            "id": "RAG-004",
            "titulo": "Clasificación y recuperación documental",
            "tema": "recuperacion",
            "contenido": (
                "La clasificación documental organiza los registros "
                "de acuerdo con sus funciones, series y contextos "
                "de producción. Los instrumentos de descripción "
                "facilitan encontrar información relevante. "
                "Una estrategia de recuperación debe considerar "
                "vocabularios controlados y necesidades de consulta."
            ),
        },
        {
            "id": "RAG-005",
            "titulo": "Trazabilidad y gobernanza de información",
            "tema": "gobernanza",
            "contenido": (
                "La trazabilidad documental permite registrar "
                "las acciones realizadas sobre un documento. "
                "Una política de gobernanza establece responsabilidades, "
                "controles de acceso y criterios para gestionar "
                "el ciclo de vida de la información. "
                "Los registros de auditoría ayudan a revisar cambios "
                "y demostrar el cumplimiento de procedimientos."
            ),
        },
    ]

    return [
        Document(
            page_content=registro["contenido"],
            metadata={
                "id": registro["id"],
                "titulo": registro["titulo"],
                "tema": registro["tema"],
                "origen": "corpus_ficticio_bloque24",
            },
        )
        for registro in registros
    ]


def fragmentar_corpus(documentos):
    """Divide los documentos conservando sus metadatos."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=30,
    )

    return splitter.split_documents(documentos)


if __name__ == "__main__":
    corpus = construir_corpus()
    fragmentos = fragmentar_corpus(corpus)

    print(f"DOCUMENTOS: {len(corpus)}")
    print(f"FRAGMENTOS: {len(fragmentos)}")

    for numero, fragmento in enumerate(fragmentos, start=1):
        print(
            f"\nFRAGMENTO {numero} "
            f"({fragmento.metadata['id']})"
        )
        print(fragmento.page_content)
