
# Límites de autonomía y supervisión humana del agente

**Proyecto:** Archive AI Lab
**Actividad:** Bloque 23, Unidad 2.4
**Tipo:** Documento de gobernanza y supervisión de agentes de IA

## 1. Descripción del agente

Archive AI Lab es un proyecto experimental de asistencia
archivística que utiliza LangChain y Gemini para consultar
un inventario documental ficticio.

El agente puede buscar registros, consultar metadatos y
mantener el contexto dentro de una sesión conversacional.

Las herramientas de consulta operan sobre datos ficticios.
No se dispone de conexión a repositorios institucionales
ni de permisos para modificar registros reales.

El sistema incorpora una función independiente de
supervisión para simular solicitudes de eliminación
documental y verificar decisiones de aprobación o rechazo.

## 2. Clasificación de herramientas por riesgo

| Herramienta | Operación | Riesgo | Autonomía |
|---|---|---|---|
| buscar_documentos | Consulta temática de registros | Bajo | Autónoma |
| buscar_documentos_filtrados | Consulta con filtros validados mediante Pydantic | Bajo | Autónoma |
| consultar_metadatos | Recuperación de información descriptiva | Bajo | Autónoma |
| simular_eliminacion_documental | Simulación de una solicitud de eliminación | Alto por la naturaleza de la acción representada | Requiere aprobación humana |

Las herramientas de consulta son de bajo riesgo porque
no modifican el inventario y utilizan información ficticia.

La simulación de eliminación se clasifica como una operación
sensible, porque representa una decisión que, en un entorno
real, podría afectar la integridad y conservación documental.

La función de eliminación simulada no está disponible como
herramienta invocable directamente por Gemini.

## 3. Supervisión y aprobación humana

### Operaciones de bajo riesgo

El agente puede ejecutar búsquedas y consultas de metadatos
sin autorización previa.

Estas operaciones deben permanecer restringidas a lectura.

### Operaciones de alto riesgo

Las solicitudes que impliquen eliminación, modificación
irreversible o alteración de documentos deben someterse
a revisión humana antes de cualquier ejecución.

En el prototipo se implementó la función
`simular_eliminacion_documental`.

Su comportamiento es:

1. Comprobar que el identificador exista.
2. Verificar el valor de `aprobacion_humana`.
3. Rechazar la operación si no existe aprobación explícita.
4. Registrar la decisión y su motivo.
5. Permitir únicamente una simulación cuando el parámetro
   representa una aprobación.

La función no elimina ni modifica documentos, incluso cuando
recibe una aprobación.

La aprobación del prototipo está representada por un
parámetro booleano. No se implementó autenticación de
supervisores ni un flujo formal de autorización.

Por esta razón, el mecanismo demuestra el principio de
supervisión humana, pero no constituye un sistema de
autorización apto para producción.

## 4. Registro y revisión de trazas

El proyecto incorpora el módulo `trazas_bloque23.py`,
que permite registrar ejecuciones en formato JSONL.

Cada registro puede contener:

- Fecha y hora de la ejecución.
- Identificador de sesión.
- Entrada del usuario.
- Herramientas ejecutadas.
- Argumentos enviados a cada herramienta.
- Observaciones obtenidas.
- Respuesta final.

El sistema también incorpora una función para detectar
llamadas consecutivas a una misma herramienta dentro
de una traza.

### Evidencia disponible

Se ejecutó una demostración local mediante
`ejecutar_auditoria_bloque23.py`.

La demostración generó:

`resultados/auditoria_bloque23.jsonl`

Se registraron dos situaciones:

1. Una traza simulada de consulta documental.
2. Una ejecución local real de la función de supervisión,
   que rechazó una solicitud sin aprobación humana.

La ejecución no corresponde a una conversación real
con Gemini.

### Frecuencia de revisión propuesta

Durante el desarrollo:

- Revisar las trazas después de cada prueba relevante.
- Revisar inmediatamente cualquier operación rechazada.
- Inspeccionar los argumentos y observaciones cuando
  aparezcan resultados inesperados.

Para una eventual implementación operativa:

- Definir revisiones periódicas según el volumen y riesgo.
- Generar alertas ante comportamientos anómalos.
- Conservar evidencias de aprobación y rechazo.
- Establecer responsables de revisión y plazos de retención.

Estas medidas operativas son propuestas de gobernanza;
no están implementadas automáticamente en el prototipo.

## 5. Respuesta ante comportamientos inesperados

### Caso A: Herramienta incorrecta

Si el agente selecciona una herramienta inadecuada:

1. Revisar la entrada del usuario.
2. Examinar las herramientas y argumentos registrados.
3. Revisar las instrucciones del agente.
4. Corregir las descripciones o validaciones.
5. Ejecutar pruebas de regresión.

### Caso B: Llamadas repetidas

Si se detectan llamadas consecutivas repetidas:

1. Examinar la traza de ejecución.
2. Identificar si existe un ciclo o una justificación válida.
3. Revisar los límites de iteración del agente.
4. Ajustar herramientas o instrucciones si corresponde.

El agente dispone de un límite de iteraciones en su
configuración, pero la detección implementada no bloquea
automáticamente las llamadas repetidas.

### Caso C: Solicitud sensible sin autorización

Si se solicita una eliminación sin aprobación:

1. Rechazar la solicitud.
2. Registrar el identificador documental.
3. Registrar el motivo del rechazo.
4. Mantener intacto el inventario.
5. Escalar a revisión humana si se tratara de una
   solicitud institucional real.

### Caso D: Error de proveedor o respuesta inválida

Ante errores de la API o formatos incompatibles:

1. Registrar el error.
2. Evitar repetir indefinidamente las solicitudes.
3. Revisar los mecanismos de recuperación disponibles.
4. Comprobar el comportamiento mediante pruebas locales.
5. No ejecutar operaciones sensibles durante un estado
   de error o incertidumbre.

## 6. Limitaciones actuales

El prototipo presenta las siguientes limitaciones:

- Utiliza un inventario ficticio.
- No ejecuta eliminaciones reales.
- No autentica ni identifica formalmente a supervisores.
- El registro de aprobaciones de la función de supervisión
  permanece en memoria durante la ejecución.
- El módulo JSONL se ejecuta de manera explícita y todavía
  no registra automáticamente todas las interacciones
  del agente con Gemini.
- La demostración de auditoría utiliza una traza documental
  simulada y una decisión local real de rechazo.
- El detector de anomalías identifica únicamente llamadas
  consecutivas repetidas dentro de una misma traza.
- No existen alertas automáticas ni un panel de auditoría.

## 7. Validación técnica

El proyecto incluye pruebas automatizadas para:

- Rechazo de solicitudes sin aprobación.
- Rechazo por defecto.
- Simulación con aprobación explícita.
- Conservación del inventario documental.
- Escritura y lectura de registros JSONL.
- Almacenamiento de varias interacciones.
- Detección de llamadas repetidas.
- Ausencia de alertas ante secuencias normales.
- Manejo de archivos de trazas inexistentes.

En la última ejecución de pytest se aprobaron
74 pruebas del repositorio.

## 8. Conclusión

Archive AI Lab incorpora mecanismos experimentales de
supervisión humana y trazabilidad para ilustrar cómo
limitar la autonomía de un agente archivístico.

Las consultas de solo lectura pueden ejecutarse de
manera autónoma, mientras que las operaciones sensibles
deben quedar sujetas a autorización humana.

El prototipo demuestra el rechazo seguro por defecto,
el registro de decisiones y la revisión básica de trazas.

Una implementación institucional requeriría controles
adicionales de autenticación, autorización, auditoría
automática y gobernanza documental.
