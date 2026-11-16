# Bloque 27: Evaluación cuantitativa de recuperación RAG

**Proyecto:** Archive AI Lab

**Unidad:** 2.5, fundamentos de RAG

## 1. Objetivo

Evaluar cuantitativamente la calidad del recuperador semántico de Archive AI Lab mediante métricas de precisión, exhaustividad (recall) y F1, utilizando un conjunto de preguntas con etiquetas de relevancia definidas antes de la recuperación.

## 2. Corpus e infraestructura

Se reutilizó el índice vectorial construido en el Bloque 24:

- Base vectorial: Chroma.
- Colección: `archive_ai_bloque24`.
- Modelo: `models/gemini-embedding-001`.
- Documentos originales: 5.
- Fragmentos indexados: 10.

El índice existente se utilizó sin reconstruirlo.

## 3. Conjunto de evaluación

Se prepararon once preguntas:

- Diez preguntas relacionadas con contenidos disponibles en el corpus.
- Una pregunta sin información relevante disponible.

Cada pregunta respondible recibió una etiqueta de relevancia correspondiente al identificador de un fragmento.

Las etiquetas se establecieron antes de ejecutar el recuperador.

**Archivo:** `src/casos_evaluacion_bloque27.py`

Las etiquetas constituyen una primera referencia de evaluación y no una anotación exhaustiva de todos los fragmentos potencialmente relevantes.

## 4. Métricas utilizadas

### Precision@k

Proporción de fragmentos recuperados que pertenecen al conjunto de relevancia definido para la pregunta.

### Recall@k

Proporción de fragmentos relevantes recuperados respecto del total de fragmentos etiquetados como relevantes.

### F1

Media armónica de precisión y recall.

Para preguntas sin fragmentos relevantes etiquetados, recall y F1 se registran como no aplicables.

**Archivo:** `src/metricas_recuperacion_bloque27.py`

## 5. Procedimiento

Se generó un embedding por pregunta utilizando Gemini.

Cada embedding se consultó contra Chroma para recuperar cinco fragmentos ordenados por similitud.

Sobre el mismo ranking se calcularon las métricas para dos configuraciones:

- k=3.
- k=5.

Esta metodología permitió comparar las configuraciones sin duplicar las llamadas de embeddings.

**Archivo:** `src/evaluar_rag_bloque27.py`

## 6. Resultados

| Métrica | k=3 | k=5 |
|---|---:|---:|
| Precisión promedio | 0,303 | 0,182 |
| Recall promedio | 1,000 | 1,000 |
| F1 promedio | 0,500 | 0,333 |

Los promedios de precisión consideran las once preguntas.

Los promedios de recall y F1 excluyen la pregunta sin fragmentos relevantes.

De las diez preguntas respondibles, nueve recuperaron el fragmento etiquetado como relevante en primera posición.

En las diez preguntas respondibles, el fragmento etiquetado apareció entre los tres primeros resultados.

## 7. Interpretación

La configuración k=3 obtuvo mayor precisión y F1 que k=5, manteniendo el mismo recall.

Esto ocurrió porque los fragmentos etiquetados como relevantes ya estaban presentes entre los tres primeros resultados. Recuperar dos fragmentos adicionales aumentó la cantidad de resultados considerados irrelevantes según las etiquetas actuales.

Por lo tanto, k=3 se establece como configuración inicial recomendada para este corpus.

## 8. Consulta sin respuesta

La pregunta sobre el presupuesto anual del Archivo Nacional para 2027 no contaba con información relevante en el corpus.

Chroma recuperó fragmentos relacionados con preservación y conservación documental, pero ninguno permitía responder la pregunta.

Esto evidencia que recuperar los vecinos vectoriales más cercanos no equivale a determinar si existe evidencia suficiente.

La capacidad de abstención o rechazo automático todavía no fue evaluada mediante estas métricas.

## 9. Pruebas automatizadas

Se incorporaron pruebas para las fórmulas, los casos especiales y el uso de rankings con diferentes valores de k.

**Archivos:**

- `tests/test_metricas_recuperacion_bloque27.py`
- `tests/test_evaluar_rag_bloque27.py`

**Resultado de la suite completa:** 120 pruebas aprobadas.

## 10. Evidencia

El archivo `resultados/evaluacion_rag_bloque27.json` contiene:

- Fecha y hora de la evaluación.
- Modelo de embeddings.
- Colección utilizada.
- Preguntas.
- Identificadores relevantes.
- Rankings recuperados.
- Métricas individuales.
- Métricas promedio.

La evaluación fue auditada posteriormente sin nuevas llamadas a Gemini.

## 11. Limitaciones

- El corpus tiene solamente diez fragmentos.
- Las etiquetas incluyen un fragmento relevante por pregunta respondible.
- Algunos fragmentos adicionales podrían considerarse relevantes mediante una anotación más exhaustiva.
- El conjunto de preguntas está estrechamente relacionado con los documentos del corpus.
- Las métricas no evalúan directamente la calidad de respuestas generadas por un LLM.
- Las preguntas sin respuesta requieren mecanismos de evaluación diferentes de recall.
- Los resultados no representan necesariamente el desempeño en colecciones documentales de mayor escala.

## 12. Conclusión

Se implementó un sistema reproducible de evaluación cuantitativa de recuperación documental.

Las pruebas permitieron comparar k=3 y k=5, identificar el comportamiento del ranking y seleccionar una configuración inicial fundamentada en resultados.

Este desarrollo constituye una primera línea de base para mejorar las estrategias de recuperación semántica de Archive AI Lab.