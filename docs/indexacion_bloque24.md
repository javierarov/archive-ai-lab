# Bloque 24: Indexación vectorial de un corpus archivístico

**Proyecto:** Archive AI Lab
**Unidad:** 2.5, fundamentos de RAG
**Actividad:** Construcción y persistencia de un índice vectorial con Gemini y Chroma

## 1. Objetivo

Construir un índice vectorial persistente a partir de un corpus documental archivístico, aplicando fragmentación de textos y generación de embeddings.

El propósito es preparar una base de conocimiento que posteriormente pueda utilizarse en sistemas de recuperación semántica y generación aumentada por recuperación (RAG).

## 2. Corpus documental

Se construyó un corpus ficticio compuesto por cinco documentos relacionados con la gestión archivística.

| Identificador | Título |
|---|---|
| RAG-001 | Descripción archivística |
| RAG-002 | Conservación preventiva |
| RAG-003 | Preservación audiovisual |
| RAG-004 | Clasificación y recuperación documental |
| RAG-005 | Trazabilidad y gobernanza de información |

Cada documento contiene texto original y metadatos de identificación, título, tema y origen.

**Archivo:** `src/corpus_bloque24.py`

## 3. Estrategia de fragmentación

Se utilizó `RecursiveCharacterTextSplitter`, de LangChain, con la siguiente configuración:

- Tamaño máximo: 200 caracteres.
- Solapamiento: 30 caracteres.
- Conservación de metadatos originales.

**Resultados observados:**

- Documentos procesados: 5.
- Fragmentos generados: 10.
- Fragmentos por documento: 2.

La fragmentación conserva información de procedencia, permitiendo relacionar cada fragmento con su documento original.

El solapamiento busca reducir la pérdida de contexto entre fragmentos consecutivos.

## 4. Generación de embeddings

Se utilizó el modelo `models/gemini-embedding-001` mediante `GoogleGenerativeAIEmbeddings`.

Los embeddings fueron generados mediante llamadas reales a la API de Gemini.

La indexación se ejecutó una vez sobre los diez fragmentos del corpus.

**Archivo:** `src/indexar_corpus_bloque24.py`

## 5. Almacenamiento vectorial

Se utilizó Chroma como base de datos vectorial con persistencia local.

**Configuración:**

- Colección: `archive_ai_bloque24`.
- Directorio: `vectorstore/bloque24`.
- Fragmentos almacenados: 10.
- Identificadores: `bloque24-001` a `bloque24-010`.

La carpeta `vectorstore/` está excluida de Git mediante `.gitignore`.

## 6. Verificación de persistencia

Tras finalizar la primera indexación, se ejecutó nuevamente el programa.

El sistema informó:

**INDICE EXISTENTE REUTILIZADO**
**VECTORES GUARDADOS: 10**

Posteriormente, se abrió la colección mediante `chromadb.PersistentClient` y se recuperaron directamente los documentos y metadatos almacenados.

La consulta devolvió los diez registros esperados, asociados a los cinco documentos originales.

Estas operaciones se realizaron sin generar nuevamente los embeddings.

## 7. Pruebas automatizadas

Se incorporaron pruebas para validar el corpus, la fragmentación, la procedencia documental y la persistencia del índice.

**Archivos de pruebas:**

- `tests/test_corpus_bloque24.py`
- `tests/test_indexacion_bloque24.py`

Las pruebas de persistencia utilizan embeddings deterministas de prueba y un directorio temporal, evitando dependencias de servicios externos.

**Resultado de la suite completa:**

86 pruebas aprobadas.

Se observaron 17 advertencias de deprecación procedentes de dependencias de LangSmith, Chroma y LangChain. No impidieron superar las pruebas.

## 8. Reproducibilidad

Para instalar las dependencias:

`python -m pip install -r requirements.txt`

Para revisar la fragmentación:

`python -m src.corpus_bloque24`

Para realizar la indexación:

`python -m src.indexar_corpus_bloque24`

Para ejecutar las pruebas:

`python -m pytest -q`

La indexación real requiere configurar una clave de API válida mediante variables de entorno.

La primera indexación puede consumir cuota o generar costos de Gemini.

Una instalación nueva debe construir su propio índice local, ya que los archivos generados por Chroma no se incluyen en el repositorio.

## 9. Limitaciones

Este bloque implementa la preparación e indexación del corpus, pero todavía no desarrolla un flujo RAG completo de consulta y generación de respuestas.

La reutilización del índice comprueba la cantidad de registros almacenados, pero no detecta modificaciones del contenido original si se mantiene el mismo número de fragmentos.

Las pruebas automatizadas utilizan vectores ficticios para validar el almacenamiento y la persistencia, no la calidad semántica de los embeddings.

La generación de embeddings reales y la persistencia local fueron comprobadas mediante ejecuciones manuales.

## 10. Conclusión

Se construyó y validó un índice vectorial persistente a partir de cinco documentos archivísticos.

La implementación permite fragmentar documentos, conservar sus metadatos, generar embeddings reales con Gemini, almacenar diez vectores en Chroma y reutilizar el índice sin reindexaciones innecesarias.

Este desarrollo constituye la base técnica para incorporar recuperación semántica y sistemas RAG en las siguientes etapas de Archive AI Lab.
