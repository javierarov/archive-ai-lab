# Banco de pruebas de prompts - Archive AI Lab

## Objetivo

Evaluar la consistencia de Gemini en la extracción de instituciones
y ciudades mediante respuestas JSON estructuradas.

## Casos de prueba

### Caso 1: Institución y ciudad explícitas

Texto:
El Museo de Historia Natural inauguró una exposición en Santiago de Chile.

Resultado esperado:
{
  "institucion": "Museo de Historia Natural",
  "ciudad": "Santiago de Chile"
}

### Caso 2: Institución sin ciudad

Texto:
La Biblioteca Nacional inauguró una exposición sobre patrimonio documental.

Resultado esperado:
{
  "institucion": "Biblioteca Nacional",
  "ciudad": null
}

### Caso 3: Ciudad sin institución

Texto:
En Valparaíso se realizó una jornada de conservación patrimonial.

Resultado esperado:
{
  "institucion": null,
  "ciudad": "Valparaíso"
}

### Caso 4: Información ausente

Texto:
Durante la jornada se presentaron nuevas iniciativas culturales.

Resultado esperado:
{
  "institucion": null,
  "ciudad": null
}

### Caso 5: Evitar inferencias

Texto:
El Museo de Historia Natural presentó una nueva colección.

Resultado esperado:
{
  "institucion": "Museo de Historia Natural",
  "ciudad": null
}

## Criterios de evaluación

1. El resultado debe ser un JSON válido.
2. Debe contener exactamente los campos "institucion" y "ciudad".
3. Los valores deben ser cadenas de texto o null.
4. No debe inventar información ausente.
5. Debe respetar las denominaciones presentes en el texto.

## Resultados

## Resultados

Las pruebas se realizaron el 2 de noviembre de 2026
mediante la API de Gemini, utilizando instrucciones
de sistema y respuestas JSON estructuradas.

| Caso | Latencia | Tokens entrada | Tokens salida | Tokens totales | Resultado |
|---|---:|---:|---:|---:|---|
| 1. Institución y ciudad | 2,02 s | 71 | 26 | 97 | Aprobado |
| 2. Institución sin ciudad | 1,62 s | 68 | 19 | 87 | Aprobado |
| 3. Ciudad sin institución | 1,01 s | 70 | 21 | 91 | Aprobado |
| 4. Información ausente | 1,92 s | 66 | 17 | 83 | Aprobado |
| 5. Evitar inferencias | 2,37 s | 67 | 22 | 89 | Aprobado |

### Evaluación de consistencia

Los cinco casos produjeron respuestas JSON válidas
con los campos esperados.

Las respuestas coincidieron con los resultados definidos
para cada caso.

En los ejemplos donde faltaba información,
Gemini utilizó correctamente valores null.

### Limitaciones

Las pruebas se realizaron con cinco textos breves
y una ejecución por caso.

Los resultados no permiten establecer una precisión
general del modelo.

Se recomienda ampliar el banco de pruebas con
documentos más extensos, entidades ambiguas
y múltiples ejecuciones por caso.

### Conclusión

El prompt de sistema y el esquema JSON permiten
obtener resultados estructurados y adecuados
para la extracción básica de metadatos documentales.

El banco de pruebas inicial obtuvo 5 resultados
correctos de 5 casos evaluados.