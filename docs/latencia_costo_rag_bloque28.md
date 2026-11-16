# Bloque 28: Evaluación de latencia y costo del flujo RAG

**Proyecto:** Archive AI Lab  
**Actividad:** Core, Unidad 2.5: Fundamentos de RAG  
**Fecha:** 16 de noviembre de 2026

## 1. Objetivo

Medir la latencia y el consumo de tokens de un flujo completo de Retrieval-Augmented Generation (RAG), identificar las etapas de mayor duración y comparar el comportamiento de diferentes configuraciones de recuperación.

## 2. Infraestructura utilizada

- **Base vectorial:** Chroma, persistente en disco.
- **Colección:** `archive_ai_bloque24`.
- **Corpus:** 5 documentos ficticios distribuidos en 10 fragmentos.
- **Modelo de embeddings:** `models/gemini-embedding-001`.
- **Modelo generativo:** `gemini-3.5-flash-lite`.
- **Lenguaje:** Python.

Se reutilizó el índice existente del Bloque 24 sin reconstruir los embeddings almacenados.

## 3. Metodología

Para cada pregunta se midieron las siguientes operaciones:

1. Generación del embedding de la pregunta.
2. Búsqueda de fragmentos relevantes mediante Chroma.
3. Generación de una respuesta utilizando el contexto recuperado.
4. Medición de la duración total del flujo.

Los tiempos se midieron con `time.perf_counter()` y se expresaron en milisegundos.

El consumo de tokens se obtuvo de `usage_metadata` de las respuestas del modelo generativo.

Se ejecutaron tres preguntas diferentes con `k=3` y se repitió la primera con `k=6`.

## 4. Resultados por consulta

| Consulta | k | Tiempo total (ms) | Tokens |
|---|---:|---:|---:|
| Metadatos descriptivos | 3 | 2.887,95 | 263 |
| Conservación preventiva | 3 | 2.155,56 | 242 |
| Gobernanza de información | 3 | 3.626,60 | 265 |
| Metadatos descriptivos | 6 | 2.600,92 | 420 |

**Resultados acumulados:**

- Consultas completadas: 4.
- Tiempo promedio: 2.817,76 ms.
- Tokens totales: 1.190.
- Costo estimado de generación: US$0,0005902.

## 5. Comparación de k=3 y k=6

Se ejecutó la misma pregunta sobre metadatos descriptivos con ambas configuraciones.

| Indicador | k=3 | k=6 |
|---|---:|---:|
| Fragmentos recuperados | 3 | 6 |
| Tokens de entrada | 232 | 389 |
| Tokens de salida | 31 | 31 |
| Embedding (ms) | 1.122,15 | 375,77 |
| Búsqueda (ms) | 1,91 | 2,38 |
| Generación (ms) | 1.696,49 | 2.148,16 |
| Tiempo total (ms) | 2.887,95 | 2.600,92 |
| Costo estimado de generación (USD) | 0,0001471 | 0,0001942 |

Al aumentar de tres a seis fragmentos:

- Los tokens de entrada aumentaron un 67,7 %.
- Los tokens totales aumentaron un 59,7 %.
- El costo estimado de generación aumentó aproximadamente un 32 %.
- El tiempo de generación aumentó aproximadamente un 26,6 %.
- El tiempo total disminuyó en esta ejecución debido principalmente a la menor latencia del embedding.

Ambas configuraciones produjeron respuestas equivalentes para la pregunta evaluada.

## 6. Análisis

Las operaciones remotas con Gemini concentraron la mayor parte de la latencia.

Las búsquedas locales en Chroma tardaron aproximadamente dos milisegundos por consulta, mientras que los embeddings y la generación requirieron cientos o miles de milisegundos.

La comparación mostró que aumentar k incrementa la cantidad de contexto enviado al modelo y el consumo de tokens.

No obstante, una ejecución por configuración no permite concluir que k=6 sea sistemáticamente más rápido o más lento.

Los resultados del Bloque 27 también indicaron que k=3 era suficiente para recuperar los fragmentos etiquetados como relevantes del conjunto de evaluación.

Por tanto, k=3 se mantiene como configuración inicial para este corpus experimental.

## 7. Costos y limitaciones

El costo monetario se estimó usando tarifas de referencia configuradas en el script:

- Entrada: US$0,30 por millón de tokens.
- Salida: US$2,50 por millón de tokens.

Estas cifras no representan necesariamente cargos reales de la cuenta.

La estimación no incluye embeddings y no constituye una medición completa de facturación.

Otras limitaciones:

- Corpus de solo diez fragmentos.
- Cuatro ejecuciones completas.
- Una sola repetición de la pregunta comparativa para cada configuración.
- Variabilidad de red y tiempos del servicio.
- No se realizó una evaluación automática de la calidad factual de las respuestas.
- El modelo generativo utiliza parámetros de muestreo fijos, por lo que ignora `temperature`.

## 8. Evidencia

**Código:** `registro_rag.py`

**Registros:** `registros_latencia_costo.jsonl`

El archivo JSONL contiene una línea por ejecución, con fecha, pregunta, configuración, identificadores recuperados, tiempos y consumo de tokens.

La integridad de las cuatro ejecuciones se verificó mediante una auditoría local sin llamadas adicionales a Gemini.

## 9. Conclusión

Se implementó y evaluó un flujo RAG completo con medición diferenciada de embedding, recuperación y generación.

El experimento permitió identificar las etapas de mayor latencia y comprobar que recuperar más fragmentos incrementa el consumo de tokens y el costo estimado de generación.

La evidencia obtenida constituye una base para futuras optimizaciones de rendimiento y costo en sistemas de recuperación documental.