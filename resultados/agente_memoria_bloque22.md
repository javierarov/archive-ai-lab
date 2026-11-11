
# Bloque 22: Herramientas estructuradas y memoria

## Objetivo

Ampliar el agente archivístico con herramientas de argumentos
estructurados mediante Pydantic y memoria conversacional por sesión.

## Implementación

- Herramienta `buscar_documentos_filtrados`.
- Validación de argumentos mediante `BaseModel`, `Field`
  y `args_schema`.
- Herramienta `consultar_metadatos`, reutilizada del Bloque 21.
- Agente creado con `create_tool_calling_agent` y `AgentExecutor`.
- Memoria con `RunnableWithMessageHistory`.
- Historiales independientes mediante `session_id`.
- Normalización de respuestas de Gemini para evitar errores
  de formato en el historial.

## Ejecuciones reales con Gemini

Modelo utilizado: gemini-3.5-flash-lite.

### Prueba 1: Recuperación documental

Sesión: sesion-a

Consulta:
Busca el documento DOC-003 sobre patrimonio audiovisual.

Herramienta ejecutada:
consultar_metadatos

Resultado:
DOC-003 corresponde a la entrevista sobre patrimonio
audiovisual, fechada el 2022-11-04, en soporte Audio digital.

Estado: CORRECTO.

### Prueba 2: Memoria conversacional

Sesión: sesion-a

Consulta:
¿Cuál es la fecha de ese documento?

Herramientas ejecutadas:
Ninguna.

Resultado:
El agente identificó DOC-003 mediante el contexto anterior
y respondió correctamente: 4 de noviembre de 2022.

Estado: CORRECTO.

### Prueba 3: Independencia entre sesiones

Sesión: sesion-b

Consulta:
¿De qué documento estábamos hablando?

Herramientas ejecutadas:
Ninguna.

Resultado:
El agente indicó que no existía una referencia documental
previa en esa conversación.

Estado: CORRECTO.

## Verificación del historial

- Sesión A: 4 mensajes.
- Sesión B: 2 mensajes.

Las sesiones mantuvieron historiales independientes.

## Pruebas automatizadas

Resultado general:
65 pruebas aprobadas.

Las nuevas pruebas verifican:

- Búsqueda mediante argumentos estructurados.
- Validación de valores permitidos.
- Independencia de sesiones.
- Integración de la memoria con el agente.

## Limitaciones conocidas

- La memoria es temporal y no persiste después de finalizar
  el proceso.
- RunnableWithMessageHistory e InMemoryChatMessageHistory
  presentan advertencias de obsolescencia.
- LangChain recomienda utilizar LangGraph para futuras
  implementaciones de memoria.

## Conclusión

El agente archivístico utiliza herramientas estructuradas,
conserva el contexto entre consultas y mantiene independientes
las conversaciones identificadas mediante session_id.
