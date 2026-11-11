
# Bloque 21: Agente con herramientas

## Objetivo

Implementar un agente de consulta archivística con
LangChain y Gemini, capaz de seleccionar herramientas
según la solicitud del usuario.

## Herramientas implementadas

1. `buscar_documentos`: búsqueda por tema en un
   inventario documental ficticio.

2. `consultar_metadatos`: recuperación de metadatos
   mediante un identificador documental.

## Ejecución real 1

Consulta:
"Busca documentos sobre conservación documental."

Herramienta ejecutada:
`buscar_documentos`

Observación registrada en `intermediate_steps`:
DOC-001: Manual de conservación documental

Resultado:
El agente identificó el documento DOC-001.

Estado: CORRECTO.

## Ejecución real 2

Consulta:
"¿Cuál es la fecha y el soporte del documento DOC-003?"

Herramienta ejecutada:
`consultar_metadatos`

Observación registrada en `intermediate_steps`:
Identificador: DOC-003
Título: Entrevista sobre patrimonio audiovisual
Institución: Archivo de Demostración
Fecha: 2022-11-04
Soporte: Audio digital
Descripción: Entrevista sobre preservación y acceso
a colecciones audiovisuales.

Resultado:
El agente respondió con la fecha 2022-11-04
y el soporte Audio digital.

Estado: CORRECTO.

## Consulta sin herramientas

Consulta:
"¿Qué es la conservación preventiva de documentos?"

Resultado:
No se completó debido a un error 503 UNAVAILABLE
del proveedor Gemini.

Esta ejecución no permite determinar si el agente
habría respondido sin utilizar herramientas.

## Pruebas automatizadas

- Búsqueda con coincidencias: APROBADA.
- Búsqueda sin coincidencias: APROBADA.
- Consulta de metadatos existentes: APROBADA.
- Consulta de identificador inexistente: APROBADA.

Resultado general del repositorio:
56 pruebas aprobadas.

## Conclusión

Se verificó mediante ejecuciones reales que el agente
selecciona correctamente las dos herramientas
implementadas.

Las herramientas utilizan exclusivamente registros
ficticios creados para esta actividad.
