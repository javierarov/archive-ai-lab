
import json
import random
from collections import Counter
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATASET = RAIZ / "datasets" / "bloque29"

SEMILLA = 42

TIPOLOGIAS = {
    "carta": "Comunicacion",
    "acta": "Constancia documental",
    "decreto": "Acto administrativo",
    "informe": "Analisis y evaluacion",
    "memorando": "Comunicacion interna",
}


TEXTOS = {
    "carta": [
        "Estimada directora: solicito su autorizacion para consultar la coleccion fotografica de la institucion. Saluda atentamente, una investigadora.",
        "De nuestra consideracion: agradecemos la colaboracion prestada durante la exposicion patrimonial realizada en septiembre.",
        "Estimado senor: nos dirigimos a usted para invitarlo a participar en las jornadas de memoria local.",
        "Junto con saludar, solicito antecedentes sobre los registros historicos correspondientes al periodo 1980-1990.",
        "Distinguida profesora: agradezco la donacion de su coleccion personal a nuestro centro de documentacion.",
        "Senora directora: por medio de la presente manifiesto mi interes en establecer un convenio de colaboracion cultural.",
        "Estimado investigador: lamentamos comunicarle que los materiales solicitados se encuentran temporalmente fuera de consulta.",
        "Reciba nuestros saludos y agradecimientos por su participacion en el proyecto de recuperacion de la memoria comunitaria.",
        "A quien corresponda: solicito una copia autorizada de los antecedentes relacionados con la historia de mi familia.",
        "Estimada conservadora: mediante la presente deseo expresarle mi reconocimiento por el trabajo realizado con nuestra coleccion.",
    ],

    "acta": [
        "Siendo las 10:00 horas se inicia la sesion del comite de archivo. Los asistentes acuerdan aprobar el calendario de transferencias.",
        "Se reunen los integrantes de la comision de patrimonio. Tras revisar los antecedentes, se aprueba la incorporacion de una nueva coleccion.",
        "A las 15:30 horas comienza la reunion extraordinaria. Se registra la asistencia de seis integrantes y la aprobacion unanime de los acuerdos.",
        "Durante la sesion se revisan las propuestas de digitalizacion. Los participantes acuerdan priorizar los soportes audiovisuales deteriorados.",
        "Con la presencia de los representantes de las distintas unidades, se procede a votar la propuesta presentada. Resultado: cinco votos favorables.",
        "Se deja constancia de la entrega de veinte cajas documentales, verificadas y recibidas conforme por ambas partes.",
        "Los miembros del consejo revisan los compromisos anteriores y establecen una nueva fecha para la siguiente sesion.",
        "Reunida la comision evaluadora, se examinan tres propuestas y se acuerda seleccionar la segunda alternativa.",
        "Se registra la asistencia, el desarrollo de los temas tratados y las decisiones adoptadas durante la jornada de trabajo.",
        "Finalizada la discusion de los asuntos pendientes, se aprueban los acuerdos y se cierra la sesion a las 17:20 horas.",
    ],

    "decreto": [
        "Vistos los antecedentes legales y considerando la necesidad de proteger el patrimonio comunal, se dispone la creacion del archivo historico municipal.",
        "En ejercicio de las facultades conferidas por la normativa vigente, se aprueba la designacion de la persona responsable del archivo institucional.",
        "Considerando la disponibilidad presupuestaria, se autoriza la adquisicion de equipamiento destinado a la conservacion documental.",
        "La autoridad municipal dispone la entrada en vigencia del reglamento de acceso a las colecciones patrimoniales.",
        "Vistos los antecedentes administrativos, se establece la constitucion de una comision encargada de evaluar las transferencias documentales.",
        "En virtud de las atribuciones legales correspondientes, se declara de interes comunal la preservacion de una coleccion historica.",
        "Se aprueba formalmente el programa anual de proteccion del patrimonio documental y se ordena su ejecucion.",
        "Considerando las necesidades del servicio, la autoridad competente dispone la reorganizacion de la unidad de documentacion.",
        "Se establece la aprobacion del convenio de colaboracion suscrito entre la municipalidad y una institucion cultural. Registrese y comuniquese.",
        "La autoridad dispone la asignacion de recursos para el proyecto de recuperacion documental, conforme a las facultades establecidas por ley.",
    ],

    "informe": [
        "La revision de la coleccion permitio identificar deterioro por humedad en el 15 por ciento de las unidades examinadas. Se recomienda intervenir los materiales afectados.",
        "Durante el periodo evaluado se digitalizaron 320 documentos. Los resultados evidencian una mejora en la disponibilidad de las colecciones.",
        "El diagnostico realizado considero condiciones ambientales, infraestructura y estado de conservacion. Se identificaron tres riesgos prioritarios.",
        "Se analizaron los tiempos de procesamiento documental antes y despues de implementar herramientas de automatizacion. Se observo una reduccion de las demoras.",
        "La evaluacion de los registros descriptivos revelo inconsistencias en nombres propios y fechas. Se propone aplicar un proceso de normalizacion.",
        "El estudio examina las necesidades de acceso de los usuarios y presenta recomendaciones para mejorar los instrumentos de consulta.",
        "Los antecedentes recopilados muestran que una parte de los soportes audiovisuales presenta signos de degradacion. Se recomienda su migracion.",
        "Se compararon dos metodologias de clasificacion documental, considerando costos, tiempos y calidad de los resultados.",
        "La inspeccion tecnica permitio determinar que las condiciones de almacenamiento son insuficientes para garantizar una preservacion adecuada.",
        "Los resultados del analisis estadistico indican un aumento de las solicitudes de acceso durante el ultimo trimestre.",
    ],

    "memorando": [
        "De: Jefatura de Archivo. Para: Equipo de Catalogacion. Asunto: Actualizacion de criterios descriptivos. Aplicar las nuevas instrucciones desde el lunes.",
        "Se solicita a las unidades administrativas remitir sus inventarios actualizados antes del cierre de la jornada.",
        "Para el personal del centro de documentacion: recordar que los prestamos internos deben registrarse en el sistema.",
        "De: Coordinacion de Digitalizacion. Para: Equipo Tecnico. Priorizar los materiales incluidos en la planificacion semanal.",
        "Se comunica a los funcionarios que el sistema de gestion documental estara fuera de servicio durante la mantencion programada.",
        "A todas las unidades: utilizar exclusivamente la plantilla institucional para registrar las transferencias de documentos.",
        "La jefatura solicita actualizar los indicadores de procesamiento documental antes de la reunion de coordinacion.",
        "De: Administracion. Para: Unidad de Archivo. Asunto: Uso de espacios de almacenamiento. Mantener despejadas las zonas de circulacion.",
        "Se recuerda al equipo interno que las modificaciones de registros deben quedar documentadas en el sistema de auditoria.",
        "Se instruye al personal de catalogacion revisar los registros pendientes antes de iniciar el siguiente lote de trabajo.",
    ],
}


def construir_dataset():
    ejemplos = []

    for tipologia, textos in TEXTOS.items():

        for numero, texto in enumerate(textos, start=1):

            salida = {
                "tipologia": tipologia,
                "categoria": TIPOLOGIAS[tipologia],
            }

            ejemplos.append({
                "id": f"{tipologia}-{numero:03d}",
                "text_input": texto,
                "output": json.dumps(
                    salida,
                    ensure_ascii=False,
                ),
            })

    return ejemplos


def dividir_dataset(ejemplos):

    generador = random.Random(SEMILLA)

    entrenamiento = []
    evaluacion = []

    for tipologia in TIPOLOGIAS:

        grupo = [
            ejemplo for ejemplo in ejemplos
            if json.loads(ejemplo["output"])["tipologia"]
            == tipologia
        ]

        generador.shuffle(grupo)

        entrenamiento.extend(grupo[:8])
        evaluacion.extend(grupo[8:])

    generador.shuffle(entrenamiento)
    generador.shuffle(evaluacion)

    return entrenamiento, evaluacion


def guardar_jsonl(ruta, ejemplos):

    with ruta.open("w", encoding="utf-8") as archivo:

        for ejemplo in ejemplos:
            archivo.write(
                json.dumps(
                    ejemplo,
                    ensure_ascii=False,
                ) + "\n"
            )


def obtener_balance(ejemplos):

    return Counter(
        json.loads(ejemplo["output"])["tipologia"]
        for ejemplo in ejemplos
    )


def main():

    RUTA_DATASET.mkdir(
        parents=True,
        exist_ok=True,
    )

    ejemplos = construir_dataset()

    entrenamiento, evaluacion = dividir_dataset(
        ejemplos
    )

    guardar_jsonl(
        RUTA_DATASET / "tipologias_documentales.jsonl",
        ejemplos,
    )

    guardar_jsonl(
        RUTA_DATASET / "entrenamiento.jsonl",
        entrenamiento,
    )

    guardar_jsonl(
        RUTA_DATASET / "evaluacion.jsonl",
        evaluacion,
    )

    print("BLOQUE 29: DATASET ARCHIVISTICO")
    print("=" * 55)

    print("\nCLASIFICADOR DE TIPOLOGIAS DOCUMENTALES")

    print("Total de ejemplos:", len(ejemplos))
    print("Tipologias:", len(TIPOLOGIAS))
    print("Semilla:", SEMILLA)

    print("\nDATASET COMPLETO")

    for tipo, cantidad in obtener_balance(
        ejemplos
    ).items():
        print(f" - {tipo}: {cantidad}")

    print("\nENTRENAMIENTO:", len(entrenamiento))

    for tipo, cantidad in obtener_balance(
        entrenamiento
    ).items():
        print(f" - {tipo}: {cantidad}")

    print("\nEVALUACION:", len(evaluacion))

    for tipo, cantidad in obtener_balance(
        evaluacion
    ).items():
        print(f" - {tipo}: {cantidad}")

    print("\nARCHIVOS GENERADOS")

    for nombre in (
        "tipologias_documentales.jsonl",
        "entrenamiento.jsonl",
        "evaluacion.jsonl",
    ):
        print(" -", RUTA_DATASET / nombre)

    print("\nDATASET ARCHIVISTICO CREADO")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()
