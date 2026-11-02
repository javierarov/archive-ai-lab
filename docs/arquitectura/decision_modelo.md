# Decisión de arquitectura: selección de modelo generativo

**Proyecto:** Archive AI Lab  
**Fecha:** 2 de noviembre de 2026  
**Actividad:** Bloque 9, comparación de modelos y costo por solicitud.

## 1. Objetivo

Seleccionar un modelo de inteligencia artificial apropiado para una miniaplicación Python destinada a extraer metadatos documentales mediante una API.

Los criterios de evaluación son:

- Precisión de la extracción.
- Costo de utilización.
- Latencia de respuesta.
- Facilidad de integración.
- Comportamiento frente a errores.

## 2. Modelos evaluados

Se compararon dos modelos disponibles mediante la API de Google Gemini:

**Gemini 3.5 Flash-Lite:** modelo optimizado para tareas de extracción, procesamiento documental y ejecución de bajo costo.

**Gemini 3.6 Flash:** modelo de propósito general, orientado a tareas de mayor complejidad.

Ambos fueron probados mediante solicitudes HTTP desde Python, utilizando el mismo texto de entrada y la misma instrucción de extracción.

## 3. Resultados experimentales

Las pruebas se realizaron el 2 de noviembre de 2026 utilizando Archive AI Lab.

| Indicador | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---|---|
| Primera latencia exitosa | 1,85 s | 3,91 s |
| Segunda ejecución | 5,44 s | Error HTTP 503 |
| Tokens de entrada (primera ejecución) | 21 | 21 |
| Tokens de salida (primera ejecución) | 42 | 42 |
| Tokens totales (primera ejecución) | 63 | 241 |
| Extracción de institución y ciudad | Exitosa | Exitosa |

En una ejecución posterior, Gemini 3.5 Flash-Lite registró:

- 21 tokens de entrada.
- 44 tokens de salida.
- 0 tokens de razonamiento.
- 65 tokens totales.

### Interpretación

Las mediciones muestran que ambos modelos consiguieron realizar la tarea básica de extracción.

Gemini 3.5 Flash-Lite presentó una menor latencia en la primera comparación y un menor consumo total de tokens.

Sin embargo, su latencia aumentó en una ejecución posterior, lo que evidencia variabilidad entre solicitudes.

Gemini 3.6 Flash registró 241 tokens totales, frente a 63 de Flash-Lite. La diferencia podría estar asociada al procesamiento interno del modelo, pero no se verificó su desglose mediante el campo de tokens de razonamiento.

La segunda ejecución de Gemini 3.6 Flash devolvió un error HTTP 503. Una única incidencia no permite establecer conclusiones sobre la disponibilidad general del servicio.

## 4. Comparación económica

Se utilizaron las tarifas oficiales publicadas para la modalidad estándar de pago de Google Gemini, vigentes al momento de realizar el análisis.

| Concepto | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---|---|
| Entrada por millón de tokens | US$0,30 | US$0,75 |
| Salida por millón de tokens, incluido razonamiento | US$2,50 | US$3,75 |

Fuente oficial: https://ai.google.dev/gemini-api/docs/pricing

### Consideraciones

Gemini 3.5 Flash-Lite presenta tarifas inferiores para tokens de entrada y salida.

Los datos de consumo fueron obtenidos de las respuestas de la API. Las tarifas corresponden a información publicada por el proveedor y no representan cargos efectivamente facturados.

Para Gemini 3.6 Flash, el desglose disponible no permite calcular con precisión el costo completo de la solicitud de 241 tokens.

La comparación económica respalda provisionalmente la selección de Flash-Lite para tareas simples de extracción documental.

## 5. Calidad de las respuestas y riesgos identificados

Durante las pruebas iniciales, ambos modelos añadieron una identificación institucional más específica que la expresada en el texto original.

Por ejemplo, el texto mencionaba «Museo de Historia Natural», mientras que las respuestas incorporaban «Museo Nacional de Historia Natural».

Para aplicaciones documentales, este comportamiento representa un riesgo de introducir información no verificada.

Por ello, se identificó la necesidad de utilizar instrucciones más restrictivas y validaciones de salida.

## 6. Decisión de arquitectura

Se selecciona **Gemini 3.5 Flash-Lite** como modelo principal de Archive AI Lab.

La decisión se fundamenta en:

- Menores tarifas publicadas de entrada y salida.
- Resultados satisfactorios en la extracción básica.
- Integración funcional con Python mediante solicitudes HTTP.
- Disponibilidad de métricas de consumo.
- Manejo de errores mediante excepciones controladas.

Gemini 3.6 Flash se mantiene como alternativa para futuras pruebas con tareas documentales de mayor complejidad.

Esta decisión es provisional y podrá revisarse según nuevos requisitos y mediciones.

## 7. Validación posterior: Bloque 10

Tras la comparación de modelos, se implementaron mejoras en Archive AI Lab:

- Prompt de sistema especializado en extracción de metadatos documentales.
- Separación de instrucciones del sistema y texto del usuario.
- Generación de respuestas JSON estructuradas.
- Validación de los campos `institucion` y `ciudad`.
- Uso de valores `null` cuando la información no aparece explícitamente.
- Control de respuestas con estructura o tipos de datos inválidos.

### Resultados del banco de pruebas

Se ejecutaron cinco casos utilizando Gemini 3.5 Flash-Lite.

| Caso | Objetivo | Resultado |
|---|---|---|
| 1 | Institución y ciudad explícitas | Aprobado |
| 2 | Institución sin ciudad | Aprobado |
| 3 | Ciudad sin institución | Aprobado |
| 4 | Información ausente | Aprobado |
| 5 | Evitar inferencias | Aprobado |

**Resultado:** 5 de 5 casos correctos en la muestra evaluada.

Estos resultados muestran que la combinación del modelo seleccionado, el prompt de sistema y el esquema JSON funcionó correctamente en las pruebas realizadas.

No obstante, una muestra de cinco textos breves no permite afirmar que el sistema tenga una precisión general del 100 %.

La documentación completa de estas pruebas se encuentra en `docs/banco_pruebas_prompts.md`.

## 8. Limitaciones

La evaluación presenta las siguientes limitaciones:

- Número reducido de pruebas comparativas.
- Variabilidad en los tiempos de respuesta.
- Una única incidencia HTTP 503.
- Ausencia de mediciones repetidas y sistemáticas para ambos modelos.
- Desglose incompleto de tokens de la prueba de Gemini 3.6 Flash.
- Evaluación de calidad limitada a textos breves.

Por lo tanto, los resultados deben interpretarse como una evaluación exploratoria y no como una comparación exhaustiva de rendimiento.

## 9. Próximas mejoras

Se propone:

- Ampliar el banco de pruebas con documentos más extensos.
- Evaluar entidades ambiguas y referencias institucionales complejas.
- Registrar múltiples ejecuciones por modelo.
- Calcular estadísticas de latencia.
- Mejorar el registro de tokens y costos estimados.
- Implementar pruebas automatizadas de validación.
- Evaluar la precisión mediante conjuntos de referencia revisados por humanos.

## 10. Conclusión

La selección de un modelo generativo debe responder a los requisitos concretos de una aplicación, considerando su costo, rendimiento, calidad y facilidad de integración.

Las pruebas realizadas permiten justificar provisionalmente la utilización de Gemini 3.5 Flash-Lite como modelo principal de Archive AI Lab.

Su integración con Python, junto con las mejoras posteriores de prompts y validación JSON, permitió construir una miniaplicación funcional para la extracción básica de metadatos documentales.

La arquitectura incorpora mecanismos de validación, manejo de errores y documentación técnica que facilitan su mantenimiento y evolución.

La decisión podrá revisarse en futuras etapas del proyecto, especialmente al aumentar la complejidad de los documentos y el volumen de procesamiento.