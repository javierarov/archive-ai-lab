# Bloque 29: Personalización de modelos aplicada a la archivística

## Clasificador Inteligente de Tipologías Documentales (CITD)

**Proyecto:** Archive AI Lab  
**Autora:** Javiera Rojas Vergara  
**Fecha:** 19 de noviembre de 2026  
**Versión:** 1.0.0  
**Estado:** Prototipo experimental en modalidad dry run.

## 1. Contexto

Este laboratorio forma parte de la Unidad 2.6 de la Especialización en Inteligencia Artificial Avanzada para Roles Emergentes de Skillnest.

El desarrollo explora técnicas de personalización de modelos de lenguaje y su aplicación a procesos de clasificación documental, integrando conocimientos de archivística, calidad de datos e inteligencia artificial.

## 2. Objetivo

Diseñar, construir y validar un dataset especializado en tipologías documentales, preparando una configuración de entrenamiento mediante Parameter-Efficient Fine-Tuning (PEFT).

El propósito es establecer una base reproducible para futuros experimentos de clasificación automática de documentos.

## 3. Fundamentos teóricos

- **RAG:** incorporación de conocimiento externo durante la inferencia.
- **Fine-tuning:** ajuste de los parámetros de un modelo mediante entrenamiento adicional.
- **PEFT:** personalización eficiente mediante el entrenamiento de un subconjunto reducido de parámetros.
- **Soft-prompting:** optimización de representaciones vectoriales incorporadas a la entrada del modelo.

Se seleccionó PEFT mediante adaptadores como técnica experimental de personalización.

## 4. Construcción del dataset

Se construyeron 50 ejemplos sintéticos de textos documentales, distribuidos uniformemente en cinco tipologías.

| Tipología | Total | Entrenamiento | Evaluación |
|---|---:|---:|---:|
| Carta | 10 | 8 | 2 |
| Acta | 10 | 8 | 2 |
| Decreto | 10 | 8 | 2 |
| Informe | 10 | 8 | 2 |
| Memorando | 10 | 8 | 2 |
| **Total** | **50** | **40** | **10** |

La división se realizó mediante una estrategia estratificada 80/20, utilizando una semilla aleatoria fija de 42.

Los ejemplos son ficticios y no contienen datos institucionales confidenciales.

## 5. Gobernanza y calidad de datos

Se implementaron los siguientes controles:

- Integridad y completitud de registros.
- Unicidad de identificadores.
- Detección de textos duplicados.
- Validación de estructuras JSON.
- Consistencia entre tipologías y categorías.
- Balance de clases.
- Detección de duplicados entre entrenamiento y evaluación.
- Cobertura y reproducibilidad del dataset.

### Resultados de auditoría

| Indicador | Resultado |
|---|---:|
| Registros válidos | 50/50 |
| Problemas estructurales | 0 |
| Identificadores compartidos | 0 |
| Textos duplicados entre conjuntos | 0 |
| Razón de balance | 1:1 |
| Cobertura del dataset | 100% |
| Reproducibilidad | Validada |

## 6. Configuración PEFT

| Parámetro | Valor |
|---|---|
| Nombre propuesto | citd-archive-ai-lab-v1 |
| Modo | TUNING_MODE_PEFT_ADAPTER |
| Adaptador | ADAPTER_SIZE_FOUR |
| Épocas | 5 |
| Ejemplos de entrenamiento | 40 |
| Exposiciones teóricas a ejemplos | 200 |
| SDK google-genai | 3.0.0 |
| Modalidad | Dry run |

La configuración fue construida y serializada localmente mediante el SDK de Google.

No se ejecutó un trabajo real de entrenamiento ni se realizaron solicitudes a Gemini.

## 7. Arquitectura del desarrollo

El flujo experimental comprende las siguientes etapas:

1. Definición de tipologías documentales.
2. Construcción del dataset sintético.
3. División estratificada.
4. Auditoría de calidad.
5. Conversión al formato TuningExample.
6. Preparación de la configuración PEFT.
7. Generación de evidencia JSON.
8. Pruebas automatizadas.

## 8. Pruebas automatizadas

| Componente | Pruebas aprobadas |
|---|---:|
| Construcción del dataset | 5/5 |
| Validación de calidad | 7/7 |
| Separación de conjuntos | 4/4 |
| Configuración PEFT | 4/4 |
| **Total** | **20/20** |

Resultados de integración:

- Pruebas acumuladas del repositorio: 149.
- Pruebas fallidas: 0.
- Advertencias: 17.
- Tiempo de ejecución de nuevas pruebas: 0,57 segundos.
- Tiempo de ejecución total: 4,79 segundos.
- Costo de API: USD 0.

## 9. Reproducibilidad

Desde la raíz del repositorio, ejecutar en orden:

`python -m src.dataset_tipologias_bloque29`

`python -m src.validar_dataset_bloque29`

`python -m src.personalizacion_bloque29`

`python -m pytest tests/test_dataset_tipologias_bloque29.py -v`

`python -m pytest -q`

## 10. Limitaciones

- Dataset sintético de tamaño reducido.
- Ausencia de documentos reales para validación externa.
- Posible similitud semántica entre ejemplos.
- Clasificación limitada a cinco tipologías.
- Categorías descriptivas diseñadas para este experimento.
- Modelo base pendiente de selección.
- Disponibilidad del servicio remoto de entrenamiento no verificada.
- Ausencia de un modelo efectivamente entrenado.
- Ausencia de métricas de rendimiento predictivo.

Las pruebas aprobadas corresponden a la calidad del software y de la preparación estructural de los datos, no a la precisión de un modelo de clasificación.

## 11. Trabajo futuro

- Ampliación del corpus documental.
- Incorporación de documentos históricos de acceso público.
- Revisión archivística de las etiquetas.
- Incorporación de tipologías adicionales.
- Evaluación de modelos locales con LoRA y PEFT.
- Comparación experimental entre prompting, RAG y PEFT.
- Evaluación mediante accuracy, precision, recall, F1-score y matriz de confusión.
- Exploración de una posible integración futura con MAVIA LAB.

## 12. Conclusión

El laboratorio establece una base técnica reproducible para investigar la personalización de modelos de inteligencia artificial en el ámbito archivístico.

La incorporación de controles de calidad, separación de datos y pruebas automatizadas permite vincular la gestión de información con principios de ingeniería de datos, gobernanza y Machine Learning.

Repositorio: https://github.com/javierarov/archive-ai-lab