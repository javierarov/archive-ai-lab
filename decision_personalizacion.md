# Decisión fundamentada de personalización de modelos

**Proyecto:** Archive AI Lab  
**Módulo:** Clasificador Inteligente de Tipologías Documentales (CITD)  
**Autora:** Javiera Rojas Vergara  
**Fecha:** 19 de noviembre de 2026  
**Actividad Core:** Bloque 30  
**Versión:** 2.0

## 1. El problema

El CITD busca automatizar la identificación de tipologías documentales mediante modelos de lenguaje, generando resultados estructurados en JSON que puedan integrarse con sistemas de gestión documental.

El alcance experimental comprende cinco tipologías: carta, acta, decreto, informe y memorando.

Se busca determinar si es necesario personalizar los parámetros de un modelo o si es posible resolver el problema mediante estrategias de prompting y generación estructurada.

## 2. Resultado del método de decisión

### 2.1. Evaluación inicial

Se aplicó el método de cinco criterios propuesto por Skillnest mediante un algoritmo implementado en Python.

| Criterio | Respuesta | Fundamento |
|---|---|---|
| Información cambiante | False | Las cinco tipologías son relativamente estables dentro del alcance experimental. |
| Problemas de formato o tono | True | 20 de 20 respuestas originales incumplieron el formato solicitado. |
| Dataset grande y de calidad | False | Se dispone de 50 ejemplos sintéticos frente al objetivo orientativo de 200. |
| Presupuesto limitado o iteración rápida | True | Se prioriza la experimentación local de bajo costo. |
| Múltiples variantes | False | El alcance actual contempla un único clasificador. |

Puntajes iniciales:

- RAG: 2 puntos.
- Fine-tuning completo: 1 punto.
- PEFT: 3 puntos.

La estrategia inicialmente seleccionada fue PEFT.

### 2.2. Validación experimental

Se diseñó un benchmark utilizando el modelo Qwen 2.5 de 1.5B parámetros, ejecutado localmente mediante Ollama.

Se evaluaron 20 documentos sintéticos adicionales, distribuidos uniformemente entre las cinco tipologías. Se utilizaron cuatro configuraciones, obteniendo un total de 80 respuestas experimentales.

| Indicador | Zero-shot | Few-shot | Zero-shot + Schema | Few-shot + Schema |
|---|---:|---:|---:|---:|
| JSON válido estricto | 0% | 100% | 100% | 100% |
| Esquema válido estricto | 0% | 100% | 100% | 100% |
| Accuracy recuperada | 45% | 65% | 40% | 65% |
| Precision macro | 60,62% | 60,83% | 56,97% | 60,83% |
| Recall macro | 45% | 65% | 40% | 65% |
| F1 macro | 40,84% | 60,29% | 37,33% | 60,29% |
| Consistencia de categorías recuperada | 45% | 100% | 70% | 100% |
| Respuesta completamente correcta estricta | 0% | 65% | 35% | 65% |
| Latencia promedio | 3,06 s | 2,92 s | 2,90 s | 2,79 s |

La evaluación estricta considera las respuestas originales del modelo. La evaluación recuperada elimina únicamente los delimitadores Markdown antes de interpretar el JSON.

Los resultados demuestran que, dentro de la muestra evaluada, la incorporación de ejemplos permite resolver los incumplimientos estructurales y mejorar la clasificación sin modificar los parámetros del modelo.

### 2.3. Análisis de sensibilidad

Se modificó individualmente cada criterio del escenario inicial.

| Criterio modificado | Nueva técnica candidata | Cambio |
|---|---|---|
| Información cambiante | RAG | Sí |
| Problemas de formato o tono | RAG | Sí |
| Dataset grande y de calidad | PEFT | No |
| Presupuesto limitado | PEFT | No |
| Múltiples variantes | PEFT | No |

Dos de los cinco criterios modifican la técnica inicialmente recomendada.

### 2.4. Reevaluación de la estrategia

Los experimentos Few-shot y Few-shot + JSON Schema eliminaron los 20 incumplimientos de formato observados inicialmente.

Por lo tanto, para estas configuraciones y dentro de la muestra experimental, el criterio de problemas de formato puede establecerse como False.

Los nuevos puntajes son:

- RAG: 2 puntos.
- Fine-tuning completo: 0 puntos.
- PEFT: 1 punto.

RAG obtiene la mayor puntuación bajo estas condiciones. Sin embargo, el método de decisión no incorpora el prompting como una alternativa independiente.

## 3. Técnica elegida y por qué

Entre las tres técnicas evaluadas mediante el método de Skillnest, se selecciona RAG como alternativa prioritaria para una futura incorporación de conocimiento archivístico externo. Su implementación quedará condicionada a que exista una necesidad efectiva de recuperación de información.

Para el problema inmediato de clasificación documental, se selecciona Few-shot prompting combinado con JSON Schema como estrategia de implementación experimental.

Esta decisión se fundamenta en los siguientes resultados:

- 100% de cumplimiento estructural en los 20 casos evaluados.
- Accuracy del 65%.
- F1 macro del 60,29%.
- Consistencia de categorías del 100%.
- Latencia promedio observada de 2,79 segundos.
- Ausencia de costos de API externa.
- Ausencia de requerimientos de entrenamiento adicional.

Aunque Few-shot sin JSON Schema obtuvo las mismas predicciones, se prioriza la configuración con generación restringida para disponer de un control explícito sobre la estructura de salida.

Se posterga PEFT hasta disponer de un dataset más representativo y evidencia de que las estrategias de prompting no permiten alcanzar los objetivos de calidad establecidos.

El fine-tuning completo se descarta para esta etapa debido al tamaño del dataset y a sus mayores requerimientos potenciales de recursos.

La configuración seleccionada no se considera apta para producción sin validaciones adicionales. Particularmente, el modelo no identificó correctamente ninguna de las cuatro actas evaluadas y mantiene una tendencia a predecir la categoría memorando.

## 4. Qué necesitaría para ejecutarla

### 4.1. Recursos disponibles

- Modelo local Qwen 2.5 de 1.5B parámetros.
- Ollama.
- Python.
- Dataset inicial de 50 ejemplos sintéticos.
- Conjunto experimental adicional de 20 documentos.
- Motor de decisión tecnológica MEEP.
- Benchmark comparativo de cuatro configuraciones.
- Motor de métricas de clasificación.
- Evidencias experimentales en formato JSON.

### 4.2. Recursos para una futura personalización

En caso de retomar PEFT, se plantea alcanzar un corpus inicial de 200 ejemplos etiquetados.

| Recurso | Cantidad |
|---|---:|
| Ejemplos disponibles en el dataset inicial | 50 |
| Ejemplos adicionales requeridos | 150 |
| Objetivo experimental | 200 |
| Horas adicionales estimadas | 13,5 |
| Costo humano adicional estimado | $202.500 CLP |
| Costo humano total estimado | $270.000 CLP |

La estimación utiliza una tarifa hipotética de $15.000 CLP por hora, cinco minutos de etiquetado por documento y una segunda revisión de dos minutos para el 20% de los registros.

Los valores no incluyen infraestructura, electricidad ni cómputo de entrenamiento.

### 4.3. Próximas etapas

- Incorporar documentos reales de acceso público.
- Revisar los criterios archivísticos de identificación documental.
- Mejorar la clasificación de actas.
- Evaluar modelos locales de diferentes tamaños.
- Utilizar un nuevo corpus de evaluación independiente.
- Comparar los resultados con un modelo personalizado mediante PEFT.
- Mantener la revisión humana de las clasificaciones.

### 4.4. Limitaciones

El estudio se realizó con un único modelo, una muestra sintética reducida y una ejecución por configuración. Los mismos documentos se utilizaron para comparar las cuatro estrategias.

Los resultados son exploratorios y no permiten generalizar el rendimiento a colecciones documentales reales. Las diferencias de latencia tampoco permiten establecer conclusiones definitivas sobre eficiencia computacional.

No se ejecutó ningún entrenamiento real ni se utilizaron APIs externas de inteligencia artificial.

### Evidencias del proyecto

- resultados/evaluacion_estrategia_bloque30.json
- resultados/evaluacion_modelo_local_bloque30.json
- resultados/benchmark_citd_bloque30.json
- resultados/metricas_clasificacion_bloque30.json

**Repositorio:** https://github.com/javierarov/archive-ai-lab