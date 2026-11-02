# Archive AI Lab

**Miniaplicación Python de extracción de metadatos documentales mediante inteligencia artificial generativa.**

Proyecto desarrollado durante la Especialización en IA Avanzada para Roles Emergentes de Skillnest y Accenture.

## 1. Descripción

Archive AI Lab es una miniaplicación desarrollada en Python que utiliza la API de Google Gemini para analizar textos y extraer información documental estructurada.

Actualmente identifica dos campos:

- `institucion`: nombre de la institución mencionada explícitamente.
- `ciudad`: ciudad mencionada explícitamente.

Cuando alguno de estos datos no aparece en el texto, la aplicación solicita que se represente mediante `null`.

El objetivo es explorar la aplicación de modelos generativos a procesos de descripción documental, manteniendo validaciones y controles básicos.

## 2. Funcionalidades

- Consumo de la API de Gemini mediante solicitudes HTTP.
- Uso de instrucciones de sistema.
- Generación de respuestas JSON estructuradas.
- Validación de entradas y respuestas.
- Manejo de errores HTTP, conexión y tiempo de espera.
- Medición de latencia.
- Registro de tokens utilizados.
- Consulta de tokens de razonamiento.
- Estimación de costos mediante tarifas configurables.
- Protección de credenciales mediante variables de entorno.

## 3. Tecnologías utilizadas

- Python 3.
- Google Gemini API.
- Biblioteca `requests`.
- Biblioteca `python-dotenv`.
- Git y GitHub.
- Visual Studio Code.

## 4. Instalación

### 4.1. Clonar el repositorio

Abrir una terminal y ejecutar:

```bash
git clone https://github.com/javierarov/archive-ai-lab.git
cd archive-ai-lab
```

### 4.2. Crear un entorno virtual

En Windows:

```powershell
python -m venv .venv
```

Activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4.3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

## 5. Configuración de credenciales

La aplicación requiere una clave de API válida de Google Gemini.

Crear un archivo `.env` en la raíz del proyecto utilizando `.env.example` como referencia.

En Windows:

```powershell
Copy-Item .env.example .env
```

Editar el archivo `.env` y configurar:

```env
GEMINI_API_KEY=TU_CLAVE_API
```

**Importante:** nunca publicar credenciales reales en GitHub.

El archivo `.env` está excluido del control de versiones mediante `.gitignore`.

## 6. Ejecución

Con el entorno virtual activado, ejecutar desde la carpeta principal:

```powershell
python src/consumir_gemini.py
```

La aplicación enviará un texto de ejemplo a Gemini y mostrará el resultado del análisis junto con métricas de ejecución.

## 7. Ejemplo de funcionamiento

Texto de entrada:

> El Museo de Historia Natural inauguró una exposición en Santiago de Chile.

Respuesta esperada:

```json
{
    "institucion": "Museo de Historia Natural",
    "ciudad": "Santiago de Chile"
}
```

Si el texto no menciona una ciudad:

```json
{
    "institucion": "Museo de Historia Natural",
    "ciudad": null
}
```

La respuesta es generada por el modelo y debe revisarse antes de utilizarse como metadato definitivo.

## 8. Validaciones y manejo de errores

La aplicación contempla:

- Validación de textos vacíos o inválidos.
- Comprobación de existencia de la clave de API.
- Control de errores HTTP.
- Control de errores de conexión.
- Control de tiempos de espera.
- Validación del formato JSON.
- Comprobación de campos y tipos de datos.

Estas medidas permiten controlar errores frecuentes sin exponer credenciales.

## 9. Métricas y costos

La aplicación registra:

- Tokens de entrada.
- Tokens de salida.
- Tokens de razonamiento, cuando están disponibles.
- Tokens totales.
- Latencia de la solicitud.

También dispone de una función para estimar costos mediante tarifas configurables.

Las estimaciones no necesariamente representan el importe efectivamente facturado por el proveedor.

## 10. Documentación técnica

La carpeta `docs/` contiene las evidencias del desarrollo.

**Arquitectura:**
- `docs/arquitectura/diagrama_archive_ai_lab.png`
- `docs/arquitectura/diagrama_archive_ai_lab.drawio`

**Decisión técnica:**
- `docs/arquitectura/decision_modelo.md`

**Validación de prompts:**
- `docs/banco_pruebas_prompts.md`

## 11. Limitaciones

La versión actual utiliza textos de ejemplo definidos en el código y requiere conexión a Internet y una clave válida para la API.

La identificación de entidades se limita a instituciones y ciudades.

Aunque se utilizan instrucciones para evitar inferencias, las respuestas generadas por IA pueden contener errores y deben someterse a revisión humana.

Las pruebas iniciales incluyeron cinco casos breves, por lo que sus resultados no representan una evaluación exhaustiva de precisión.

## 12. Estado del proyecto

Versión funcional desarrollada como parte de la preparación para el Gate 1: Habilitación técnica.

Se prevé continuar incorporando pruebas automatizadas, mejoras de configuración y ampliaciones de las funcionalidades documentales.

## 13. Autora

**Javiera Rojas**

Licenciada en Gestión de Información, Bibliotecología y Archivística.

Proyecto de aprendizaje orientado a la integración de inteligencia artificial generativa en procesos de gestión documental.