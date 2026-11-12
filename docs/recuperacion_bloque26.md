# Bloque 26: Recuperación semántica y citas documentales

**Proyecto:** Archive AI Lab

**Unidad:** 2.5, fundamentos de RAG

## 1. Objetivo

Implementar recuperación semántica sobre un índice vectorial persistente, conservando los metadatos de procedencia y construyendo un prompt dinámico que incorpore referencias documentales numeradas.

## 2. Infraestructura reutilizada

Se reutilizó el índice construido en el Bloque 24:

- Base vectorial: Chroma.
- Colección: `archive_ai_bloque24`.
- Modelo de embeddings: `models/gemini-embedding-001`.
- Documentos originales: 5.
- Fragmentos indexados: 10.

No fue necesario reconstruir el índice.

## 3. Funcionalidades implementadas

Se desarrolló `src/recuperacion_bloque26.py` con las siguientes funciones:

- `verificar_indice()`: comprueba la disponibilidad del índice local.
- `recuperar_fragmentos()`: utiliza un retriever de Chroma para obtener fragmentos semánticamente similares.
- `formatear_contexto()`: genera referencias numeradas y conserva la procedencia.
- `construir_prompt()`: combina pregunta, contexto e instrucciones de citación.

El sistema utiliza `k=3` como cantidad predeterminada de fragmentos recuperados.

## 4. Sistema de citas

Cada fragmento recuperado recibe una referencia numérica.

Ejemplo:

`[1] RAG-002 | Conservación preventiva`

El número identifica la posición del fragmento en la recuperación y `RAG-002` identifica el documento original.

La numeración permite asociar el contexto enviado al modelo con un diccionario de fuentes.

## 5. Pruebas de recuperación real

### Consulta 1

**Pregunta:** ¿Cómo evitar el deterioro de documentos?

Resultados:

1. RAG-002 · Conservación preventiva.
2. RAG-002 · Conservación preventiva.
3. RAG-001 · Descripción archivística.

El documento pertinente apareció en las dos primeras posiciones.

### Consulta 2

**Pregunta:** ¿Cómo registrar cambios y responsabilidades documentales?

Resultados:

1. RAG-005 · Trazabilidad y gobernanza de información.
2. RAG-005 · Trazabilidad y gobernanza de información.
3. RAG-004 · Clasificación y recuperación documental.

El documento pertinente apareció en las dos primeras posiciones.

## 6. Prueba con información ausente

**Pregunta:** ¿Cuál es el presupuesto anual del Archivo Nacional para 2027?

Resultados:

1. RAG-003 · Preservación audiovisual.
2. RAG-002 · Conservación preventiva.
3. RAG-003 · Preservación audiovisual.

Ninguno de los fragmentos contiene información presupuestaria.

Esto demuestra que la recuperación por similitud vectorial devuelve los resultados más próximos, aunque no existan documentos suficientes para responder.

El prompt incorpora instrucciones para reconocer la ausencia de información, pero todavía no existe un filtro automático de relevancia.

## 7. Pruebas automatizadas

Se incorporaron diez pruebas en:

`tests/test_recuperacion_bloque26.py`

Las pruebas comprueban:

- Numeración consecutiva.
- Conservación de metadatos.
- Correspondencia de las citas.
- Manejo de fragmentos incompletos.
- Validación de preguntas.
- Construcción del prompt.
- Recuperación simulada sin llamadas a Gemini.

**Resultado general:** 96 pruebas aprobadas.

## 8. Limitaciones

- La recuperación utiliza similitud vectorial, sin aplicar todavía un umbral de relevancia.
- Los resultados pueden incluir distintos fragmentos de un mismo documento.
- Algunos fragmentos comienzan a mitad de una oración debido a la estrategia de chunking.
- La generación de respuestas con un LLM no forma parte de esta implementación.
- Las instrucciones del prompt no garantizan por sí solas respuestas fundamentadas.
- La relevancia de los resultados se evaluó manualmente en tres consultas de demostración.

## 9. Conclusión

Se implementó un mecanismo de recuperación semántica con Chroma y Gemini Embeddings que permite localizar fragmentos documentales, conservar su procedencia y construir prompts dinámicos con citas numeradas.

Los resultados muestran recuperación pertinente en las dos consultas con respuesta disponible y evidencian la necesidad de incorporar evaluación de relevancia cuando el corpus no contiene información suficiente.

Este desarrollo prepara Archive AI Lab para las siguientes etapas de RAG y generación fundamentada.