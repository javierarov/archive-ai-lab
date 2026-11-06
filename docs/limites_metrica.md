# Límites de la evaluación mediante métricas léxicas

**Proyecto:** Archive AI Lab  
**Actividad:** Bloque 17, evaluación automática y revisión humana  
**Muestra:** 20 respuestas reales de Gemini  
**Revisión humana:** 10 casos seleccionados

## 1. Qué mide

Archive AI Lab utiliza un pipeline de procesamiento de texto para comparar los metadatos extraídos por Gemini con referencias previamente definidas.

El sistema transforma los valores de los campos `institucion` y `ciudad` en texto, aplica limpieza y tokenización, y calcula tres métricas:

- **Precisión:** proporción de tokens de la respuesta que coinciden con la referencia.
- **Cobertura (recall):** proporción de tokens de la referencia que aparecen en la respuesta.
- **F1:** media armónica entre precisión y cobertura.

El cálculo considera la frecuencia de aparición de cada token.

Se evaluaron 20 respuestas reales del modelo. El F1 promedio obtenido fue **0,8807**.

Este resultado refleja coincidencia léxica y no debe interpretarse como una medida directa de exactitud factual, calidad semántica o cumplimiento de instrucciones.

Además, la comparación reúne los valores de ambos campos en una misma secuencia de tokens. Por ello, no comprueba de manera independiente si cada valor fue asignado al campo correcto.

## 2. Modos de falla conocidos

### 2.1. Respuestas correctas con F1 igual a cero

En el caso 20, el texto no mencionaba instituciones ni ciudades.

Tanto la referencia como Gemini devolvieron:

`{"institucion": null, "ciudad": null}`

Aunque la respuesta coincidió exactamente con lo esperado, el F1 fue 0,0000.

Esto ocurre porque el cálculo utiliza conjuntos de tokens vacíos y no contempla una regla especial para coincidencias entre respuestas completamente nulas.

Por tanto, un F1 de cero no siempre representa una extracción incorrecta.

### 2.2. Diferencias de denominación

En el caso 1, la referencia contenía «Santiago de Chile», mientras que Gemini devolvió «Santiago».

El resultado obtuvo F1 = 0,8333.

La respuesta conserva una identificación geográfica válida, pero no reproduce íntegramente la denominación esperada.

Esto demuestra que una diferencia textual puede producir una penalización incluso cuando existe una relación semántica clara.

### 2.3. Extracción de ubicaciones desde nombres institucionales

En los casos 6 y 12, Gemini identificó como ciudades términos que aparecían dentro de nombres de instituciones:

- Caso 6: «Biblioteca de Santiago».
- Caso 12: «Museo de Historia Natural de Concepción».

Las referencias establecidas para estos casos asignaban `null` al campo `ciudad`, porque no se indicaba una ubicación independiente del nombre institucional.

Gemini devolvió una ciudad en ambos casos.

Estos resultados muestran que la presencia literal de un término geográfico no garantiza que su extracción sea adecuada para la tarea.

### 2.4. Fragmentación de nombres institucionales

En el caso 13, la referencia esperaba «Biblioteca Municipal de Valparaíso» como institución y `null` como ciudad.

Gemini devolvió «Biblioteca Municipal» como institución y «Valparaíso» como ciudad.

El F1 obtenido fue 0,8571.

La coincidencia de tokens no permitió detectar completamente que el modelo había dividido una denominación institucional entre dos campos.

### 2.5. Ambigüedad por múltiples entidades

En el caso 17, el texto mencionaba la Biblioteca Nacional y el Archivo Nacional.

La referencia asignaba `null` al campo `institucion` debido a la presencia de dos instituciones, mientras que Gemini las agrupó en una única cadena.

El F1 obtenido fue 0,2857.

En el caso 18, el texto mencionaba actividades en Chillán y Concepción. La referencia asignaba `null` a `ciudad` porque existían dos localidades, pero Gemini seleccionó Chillán.

El F1 fue 0,8571.

Ambos casos muestran que el sistema necesita reglas explícitas para resolver menciones múltiples. También evidencian una limitación del esquema de salida, que solo admite una cadena de texto o un valor nulo por campo.

### 2.6. Limitaciones de infraestructura

Durante la recopilación de las respuestas se registraron errores temporales de disponibilidad del proveedor.

El sistema utilizó reintentos y mecanismos de conservación de resultados para recuperar las consultas pendientes sin repetir innecesariamente las respuestas exitosas.

Estos errores deben distinguirse de los errores de calidad del contenido: una consulta sin respuesta no permite evaluar la corrección factual del modelo.

## 3. Muestra revisada

Se seleccionaron diez casos para revisión humana, incluyendo respuestas con puntuaciones F1 altas, intermedias y bajas.

La evaluación consideró tres criterios:

- **Corrección factual:** respaldo de la información extraída en el texto original.
- **Completitud:** presencia de los datos requeridos según la rúbrica utilizada.
- **Contradicción:** existencia de información incompatible con el contenido original.

La revisión fue validada manualmente y quedó registrada en `resultados/revision_manual.json`.

### Resultados de la revisión

| Caso | F1 | Corrección factual | Completitud | Contradicción |
|---|---:|---|---|---|
| 1 | 0,8333 | Sí | Parcial | No |
| 2 | 1,0000 | Sí | Sí | No |
| 6 | 0,8571 | Sí | No | No |
| 10 | 1,0000 | Sí | Sí | No |
| 12 | 0,9231 | Sí | No | No |
| 13 | 0,8571 | Parcial | No | No |
| 17 | 0,2857 | Parcial | No | No |
| 18 | 0,8571 | Sí | No | No |
| 19 | 1,0000 | Sí | Sí | No |
| 20 | 0,0000 | Sí | Sí | No |

La revisión identificó ocho casos con corrección factual afirmativa y dos con corrección parcial.

En completitud, cuatro casos fueron calificados como completos, uno como parcial y cinco como no completos.

No se identificaron contradicciones directas con los textos originales.

**Consideración metodológica:** la rúbrica inicial de completitud también incorporó el cumplimiento de reglas de extracción. Por ello, algunas calificaciones negativas corresponden principalmente a problemas de asignación de campos o tratamiento de ambigüedades, más que a omisiones estrictas.

Los resultados corresponden a una muestra limitada y no permiten establecer conclusiones generales sobre el rendimiento del modelo en otros conjuntos documentales.

## 4. Recomendación de uso

Se recomienda utilizar precisión, cobertura y F1 como métricas iniciales de comparación automática, especialmente para detectar diferencias textuales entre referencias y respuestas.

Sin embargo, **no se recomienda utilizar el F1 léxico como único criterio de aceptación de metadatos**.

Para mejorar el proceso de evaluación se proponen las siguientes medidas:

1. Complementar las métricas léxicas con una comparación independiente de los campos `institucion` y `ciudad`.
2. Identificar explícitamente los casos en que ambos valores esperados y obtenidos son nulos.
3. Incorporar reglas de validación para instituciones que contienen nombres geográficos.
4. Definir una política para textos que mencionan múltiples instituciones o ciudades.
5. Mantener una muestra de revisión humana que incluya respuestas con puntuaciones altas y bajas.
6. Registrar por separado los errores del proveedor y los errores de extracción.
7. Conservar las respuestas originales, referencias y observaciones para permitir auditoría y reproducibilidad.

### Conclusión

La evaluación de Archive AI Lab demuestra que las métricas basadas en coincidencia de tokens son útiles para detectar diferencias entre respuestas y referencias, pero presentan limitaciones al evaluar información estructurada.

Los casos analizados evidencian que una puntuación elevada no garantiza el cumplimiento de las reglas de extracción y que una puntuación baja no implica necesariamente una respuesta incorrecta.

Por ello, se recomienda utilizar las métricas automáticas como apoyo para priorizar revisiones, manteniendo la validación humana como componente fundamental del control de calidad.
