import json
from pathlib import Path

from cliente import consultar_modelo
from pipeline_texto import metadatos_a_texto, procesar_texto


CASOS = [
    
    {
        "id": 1,
        "entrada": "El Museo de Historia Natural está en Santiago de Chile.",
        "referencia": {
            "institucion": "Museo de Historia Natural",
            "ciudad": "Santiago de Chile"
        }
    },
    {
        "id": 2,
        "entrada": "La Biblioteca Nacional organiza una exposición en Santiago.",
        "referencia": {
            "institucion": "Biblioteca Nacional",
            "ciudad": "Santiago"
        }
    },
    {
        "id": 3,
        "entrada": (
            "La Universidad de Concepción inauguró "
            "una exposición en Concepción."
        ),
        "referencia": {
            "institucion": "Universidad de Concepción",
            "ciudad": "Concepción"
        }
    },
    {
        "id": 4,
        "entrada": "El Museo Regional de Magallanes está ubicado en Punta Arenas.",
        "referencia": {
            "institucion": "Museo Regional de Magallanes",
            "ciudad": "Punta Arenas"
        }
    },

        {
        "id": 5,
        "entrada": "La Universidad Austral de Chile realizó una actividad en Valdivia.",
        "referencia": {
            "institucion": "Universidad Austral de Chile",
            "ciudad": "Valdivia"
        }
    },
    {
        "id": 6,
        "entrada": "La Biblioteca de Santiago organizó una jornada cultural.",
        "referencia": {
            "institucion": "Biblioteca de Santiago",
            "ciudad": None
        }
    },
    {
        "id": 7,
        "entrada": "En Temuco se realizó una exposición de fotografía histórica.",
        "referencia": {
            "institucion": None,
            "ciudad": "Temuco"
        }
    },
    {
        "id": 8,
        "entrada": "El Museo de Arte Contemporáneo anunció una nueva exposición.",
        "referencia": {
            "institucion": "Museo de Arte Contemporáneo",
            "ciudad": None
        }
    },
    {
        "id": 9,
        "entrada": "La Universidad de La Frontera presentó un proyecto en Temuco.",
        "referencia": {
            "institucion": "Universidad de La Frontera",
            "ciudad": "Temuco"
        }
    },
    {
        "id": 10,
        "entrada": "El Archivo Nacional recibió documentos históricos en Santiago.",
        "referencia": {
            "institucion": "Archivo Nacional",
            "ciudad": "Santiago"
        }
    },
    {
        "id": 11,
        "entrada": "En Concepción se inauguró una muestra sobre la historia regional.",
        "referencia": {
            "institucion": None,
            "ciudad": "Concepción"
        }
    },
    {
        "id": 12,
        "entrada": "El Museo de Historia Natural de Concepción organizó una actividad.",
        "referencia": {
            "institucion": "Museo de Historia Natural de Concepción",
            "ciudad": None
        }
    },
    {
        "id": 13,
        "entrada": "La Biblioteca Municipal de Valparaíso presentó una colección.",
        "referencia": {
            "institucion": "Biblioteca Municipal de Valparaíso",
            "ciudad": None
        }
    },
    {
        "id": 14,
        "entrada": "El Museo Histórico Nacional realizó una charla en Santiago.",
        "referencia": {
            "institucion": "Museo Histórico Nacional",
            "ciudad": "Santiago"
        }
    },
    {
        "id": 15,
        "entrada": "La Universidad de Chile participó en un encuentro en Valparaíso.",
        "referencia": {
            "institucion": "Universidad de Chile",
            "ciudad": "Valparaíso"
        }
    },
    {
        "id": 16,
        "entrada": "El Museo Regional de Atacama presentó una exposición en Copiapó.",
        "referencia": {
            "institucion": "Museo Regional de Atacama",
            "ciudad": "Copiapó"
        }
    },
    {
        "id": 17,
        "entrada": "La Biblioteca Nacional y el Archivo Nacional participaron en Santiago.",
        "referencia": {
            "institucion": None,
            "ciudad": "Santiago"
        }
    },
    {
        "id": 18,
        "entrada": "La Universidad de Concepción organizó actividades en Chillán y Concepción.",
        "referencia": {
            "institucion": "Universidad de Concepción",
            "ciudad": None
        }
    },
    {
        "id": 19,
        "entrada": "El Centro Cultural Gabriela Mistral presentó una obra en Santiago.",
        "referencia": {
            "institucion": "Centro Cultural Gabriela Mistral",
            "ciudad": "Santiago"
        }
    },
    {
        "id": 20,
         "entrada": (
            "Durante la jornada se discutieron nuevas "
            "estrategias de conservación documental."
        ),
        "referencia": {
            "institucion": None,
            "ciudad": None
        }
    }
]


def evaluar_casos():
    resultados = []

    for caso in CASOS:
        print(f"\nProcesando caso {caso['id']}...")

        referencia_texto = metadatos_a_texto(
            caso["referencia"]
        )

        try:
            respuesta = consultar_modelo(
                caso["entrada"],
                intentos=2,
                espera_segundos=2
            )

            respuesta_texto = metadatos_a_texto(respuesta)

            resultado = {
                "id": caso["id"],
                "entrada": caso["entrada"],
                "referencia": caso["referencia"],
                "respuesta_modelo": respuesta,
                "texto_referencia": referencia_texto,
                "texto_respuesta": respuesta_texto,
                "coincidencia_cruda": (
                    referencia_texto == respuesta_texto
                ),
                "tokens_referencia": procesar_texto(
                    referencia_texto
                ),
                "tokens_respuesta": procesar_texto(
                    respuesta_texto
                )
            }

            resultado["coincidencia_procesada"] = (
                resultado["tokens_referencia"]
                == resultado["tokens_respuesta"]
            )

        except Exception as error:
            print(
                f"Error en el caso {caso['id']}: "
                f"{type(error).__name__}: {error}"
            )

            resultado = {
                "id": caso["id"],
                "entrada": caso["entrada"],
                "referencia": caso["referencia"],
                "error": str(error),
                "tipo_error": type(error).__name__
            }

        resultados.append(resultado)

        # Guardamos avances después de cada caso.
        guardar_resultados(resultados)

    print("\nEvaluación terminada.")


def guardar_resultados(resultados):
    carpeta = Path("resultados")
    carpeta.mkdir(exist_ok=True)

    ruta = carpeta / "evaluacion_bloque15.json"

    ruta.write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"Resultados guardados en: {ruta}")


if __name__ == "__main__":
    evaluar_casos()