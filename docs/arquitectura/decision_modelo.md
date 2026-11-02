# Decisión de arquitectura: selección de modelo generativo

**Proyecto:** Archive AI Lab  
**Fecha:** 2 de noviembre de 2026  
**Actividad:** Bloque 9, comparación de modelos y costo por solicitud.

## 1. Objetivo

Seleccionar un modelo de inteligencia artificial apropiado para una miniaplicación Python destinada a extraer información de textos documentales mediante una API.

Se priorizan la precisión de la extracción, el costo, la latencia y la facilidad de integración.

## 2. Modelos evaluados

- **Gemini 3.5 Flash-Lite:** modelo orientado a tareas de extracción y procesamiento de información de bajo costo.
- **Gemini 3.6 Flash:** modelo diseñado para tareas generales y de mayor complejidad.

Ambos modelos se probaron mediante la API de Gemini utilizando la misma oración de ejemplo.

## 3. Resultados experimentales

| Indicador | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---|---|
| Primera latencia exitosa | 1,85 s | 3,91 s |
| Segunda ejecución | 5,44 s | Error HTTP 503 |
| Tokens de entrada (primera ejecución) | 21 | 21 |
| Tokens de salida (primera ejecución) | 42 | 42 |
| Tokens totales (primera ejecución) | 63 | 241 |
| Extracción de institución y ciudad | Exitosa | Exitosa |

En una ejecución posterior, Gemini 3.5 Flash-Lite registró 21 tokens de entrada, 44 de salida, 0 de razonamiento y 65 tokens totales.

## 4. Comparación económica

Tarifas oficiales de la API de Gemini, modalidad estándar de pago, consultadas el 2 de noviembre de 2026:

| Concepto | Gemini 3.5 Flash-Lite | Gemini 3.6 Flash |
|---|---|---|
| Entrada por millón de tokens | US$0,30 | US$0,75 |
| Salida por millón de tokens | US$2,50 | US$3,75 |

Los costos efectivos dependen del consumo, la modalidad de servicio y las condiciones de facturación.

Fuente: https://ai.google.dev/gemini-api/docs/pricing

## 5. Riesgos identificados

Los dos modelos añadieron una identificación institucional más específica que la expresada literalmente en el texto original.

Para aplicaciones documentales, esto constituye un riesgo de introducir información no verificada.

También se observó variación en la latencia y un error temporal HTTP 503.

Las pruebas son exploratorias y no permiten establecer conclusiones definitivas sobre rendimiento o disponibilidad.

## 6. Decisión de arquitectura

Se selecciona provisionalmente **Gemini 3.5 Flash-Lite** como modelo principal de Archive AI Lab.

La decisión se fundamenta en:

- Menores tarifas de entrada y salida.
- Resultados satisfactorios para la tarea básica de extracción.
- Integración funcional con el módulo Python existente.
- Posibilidad de registrar tokens, latencia y errores.

Gemini 3.6 Flash permanece como alternativa para evaluar tareas de mayor complejidad.

## 7. Próximas mejoras

Se propone ampliar las pruebas con distintos textos, registrar más mediciones de latencia e implementar instrucciones que reduzcan las inferencias no respaldadas por el contenido original.

También se incorporará una salida JSON estructurada, con validación de sus campos.

## 8. Conclusión

La selección de un modelo generativo debe justificarse según las necesidades concretas de la aplicación y no solamente por su capacidad general.

Para la versión actual de Archive AI Lab, Gemini 3.5 Flash-Lite presenta una relación preliminar favorable entre costo y funcionalidad.

La decisión deberá revisarse a medida que aumenten la complejidad de las tareas y el volumen de procesamiento.