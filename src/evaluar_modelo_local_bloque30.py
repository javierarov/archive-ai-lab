
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

from src.dataset_tipologias_bloque29 import (
    TIPOLOGIAS,
)


RAIZ = Path(__file__).resolve().parents[1]

MODELO = "qwen2.5:1.5b"

URL = "http://localhost:11434/api/generate"

RUTA_RESULTADO = (
    RAIZ / "resultados"
    / "evaluacion_modelo_local_bloque30.json"
)


CASOS = [
    (
        "carta",
        "Estimada senora: le escribo para solicitar "
        "la devolucion de las fotografias facilitadas "
        "para la exposicion. Reciba un cordial saludo.",
    ),
    (
        "carta",
        "Querido profesor: quisiera agradecerle "
        "personalmente los materiales que envio "
        "para nuestra investigacion.",
    ),
    (
        "carta",
        "Distinguido director: me permito invitarle "
        "a la inauguracion de nuestra biblioteca. "
        "Esperamos contar con su presencia.",
    ),
    (
        "carta",
        "De mi consideracion: deseo manifestar "
        "mi preocupacion por el cierre del museo "
        "y solicitar antecedentes al respecto.",
    ),
    (
        "acta",
        "A las nueve horas se constituyo la mesa "
        "de trabajo. Se aprobaron dos propuestas "
        "y se registro una abstencion.",
    ),
    (
        "acta",
        "Los representantes de ambas instituciones "
        "dejan constancia de la recepcion conforme "
        "de quince unidades de almacenamiento.",
    ),
    (
        "acta",
        "En presencia de los asistentes se procedio "
        "a la lectura de los acuerdos anteriores. "
        "No se formularon observaciones.",
    ),
    (
        "acta",
        "Concluida la votacion, se registro el "
        "resultado y se levanto la sesion "
        "a las dieciocho horas.",
    ),
    (
        "decreto",
        "En uso de las atribuciones que confiere "
        "la ley, se dispone la clausura temporal "
        "del recinto municipal.",
    ),
    (
        "decreto",
        "Considerando los antecedentes expuestos "
        "y las facultades legales de esta autoridad, "
        "se ordena la creacion de una nueva unidad.",
    ),
    (
        "decreto",
        "Apruebase la asignacion presupuestaria "
        "para el programa de restauracion. "
        "Anotese, comuniquese y archivese.",
    ),
    (
        "decreto",
        "La autoridad comunal, en ejercicio de "
        "sus atribuciones legales, establece "
        "el nuevo horario de atencion publica.",
    ),
    (
        "informe",
        "La inspeccion de cincuenta cajas revelo "
        "presencia de hongos en doce unidades. "
        "Se recomienda su aislamiento.",
    ),
    (
        "informe",
        "El analisis comparativo evidencia una "
        "disminucion del tiempo de respuesta "
        "tras incorporar el nuevo sistema.",
    ),
    (
        "informe",
        "Los resultados de las encuestas muestran "
        "que el acceso remoto es la modalidad "
        "preferida por los investigadores.",
    ),
    (
        "informe",
        "Se examinaron las condiciones de seguridad "
        "del deposito y se identificaron cuatro "
        "deficiencias de infraestructura.",
    ),
    (
        "memorando",
        "De: Recursos Humanos. Para: Departamento "
        "Tecnico. Remitir las solicitudes de "
        "vacaciones antes del viernes.",
    ),
    (
        "memorando",
        "A todo el personal administrativo: "
        "actualizar las contrasenas institucionales "
        "antes del cierre de mes.",
    ),
    (
        "memorando",
        "De: Direccion. Para: Unidad de Finanzas. "
        "Asunto: Entrega de antecedentes internos "
        "para la revision presupuestaria.",
    ),
    (
        "memorando",
        "Se comunica al equipo interno que las "
        "reuniones de coordinacion se realizaran "
        "los dias martes desde la proxima semana.",
    ),
]


def construir_prompt(texto):

    categorias = "\n".join(
        f"- {tipo}: {categoria}"
        for tipo, categoria in TIPOLOGIAS.items()
    )

    return f"""
Eres un clasificador de tipologias documentales.

Clasifica el texto utilizando exclusivamente
una de las siguientes tipologias y su categoria:

{categorias}

Devuelve solamente un objeto JSON valido,
sin Markdown ni explicaciones.

El objeto debe contener exactamente dos campos:
"tipologia" y "categoria".

Respeta los valores indicados anteriormente.

Texto documental:
{texto}
""".strip()


def consultar_ollama(texto):

    payload = {
        "model": MODELO,
        "prompt": construir_prompt(texto),
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 42,
            "num_predict": 200,
        },
    }

    peticion = Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    inicio = time.perf_counter()

    with urlopen(peticion, timeout=180) as respuesta:
        resultado = json.load(respuesta)

    latencia = (
        time.perf_counter() - inicio
    ) * 1000

    return resultado["response"], latencia


def evaluar_respuesta(respuesta, esperada):

    resultado = {
        "json_valido": False,
        "esquema_valido": False,
        "clasificacion_correcta": False,
        "categoria_consistente": False,
        "tipologia_predicha": None,
        "categoria_predicha": None,
    }

    try:
        datos = json.loads(respuesta.strip())

    except json.JSONDecodeError:
        return resultado

    resultado["json_valido"] = True

    if not isinstance(datos, dict):
        return resultado

    tipologia = datos.get("tipologia")
    categoria = datos.get("categoria")

    resultado["tipologia_predicha"] = tipologia
    resultado["categoria_predicha"] = categoria

    tipologia_valida = (
        isinstance(tipologia, str)
        and tipologia in TIPOLOGIAS
    )

    categoria_valida = (
        isinstance(categoria, str)
        and categoria in TIPOLOGIAS.values()
    )

    resultado["esquema_valido"] = (
        set(datos) == {"tipologia", "categoria"}
        and tipologia_valida
        and categoria_valida
    )

    resultado["clasificacion_correcta"] = (
        tipologia == esperada
    )

    resultado["categoria_consistente"] = (
        tipologia_valida
        and categoria == TIPOLOGIAS[tipologia]
    )

    return resultado


def main():

    print("BLOQUE 30: EVALUACION LOCAL DEL CITD")
    print("=" * 55)

    print("Modelo:", MODELO)
    print("Casos:", len(CASOS))

    registros = []

    for numero, (esperada, texto) in enumerate(
        CASOS,
        start=1,
    ):

        print(f"\nCASO {numero:02d}")
        print("Esperada:", esperada)

        respuesta, latencia = consultar_ollama(texto)

        evaluacion = evaluar_respuesta(
            respuesta,
            esperada,
        )

        registro = {
            "id": f"baseline-{numero:03d}",
            "texto": texto,
            "tipologia_esperada": esperada,
            "respuesta_original": respuesta,
            "latencia_ms": round(latencia, 2),
            **evaluacion,
        }

        registros.append(registro)

        print(
            "Predicha:",
            evaluacion["tipologia_predicha"],
        )

        print(
            "JSON valido:",
            evaluacion["json_valido"],
        )

        print(
            "Esquema valido:",
            evaluacion["esquema_valido"],
        )

        print(
            "Clasificacion correcta:",
            evaluacion["clasificacion_correcta"],
        )

        print(
            f"Latencia: {latencia:.2f} ms"
        )

    total = len(registros)

    metricas = {}

    for campo in (
        "json_valido",
        "esquema_valido",
        "clasificacion_correcta",
        "categoria_consistente",
    ):

        correctos = sum(
            registro[campo]
            for registro in registros
        )

        metricas[campo] = {
            "correctos": correctos,
            "total": total,
            "porcentaje": round(
                correctos / total * 100,
                2,
            ),
        }

    incumplimientos = (
        total
        - metricas["esquema_valido"]["correctos"]
    )

    resumen = {
        "modelo": MODELO,
        "total_casos": total,
        "datos_sinteticos": True,
        "entrenamiento_ejecutado": False,
        "json_forzado": False,
        "temperature": 0,
        "seed": 42,
        "metricas": metricas,
        "incumplimientos_formato": incumplimientos,
        "problema_de_formato_o_tono": (
            incumplimientos >= 3
        ),
        "latencia_promedio_ms": round(
            sum(
                r["latencia_ms"]
                for r in registros
            ) / total,
            2,
        ),
        "llamadas_gemini": 0,
        "costo_api_externa_usd": 0.0,
        "registros": registros,
    }

    RUTA_RESULTADO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RUTA_RESULTADO.write_text(
        json.dumps(
            resumen,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 55)
    print("RESULTADOS FINALES")

    for campo, metrica in metricas.items():

        print(
            f"{campo}: "
            f"{metrica['correctos']}/{total} "
            f"({metrica['porcentaje']}%)"
        )

    print(
        "Incumplimientos de formato:",
        incumplimientos,
    )

    print(
        "Problema de formato o tono:",
        resumen["problema_de_formato_o_tono"],
    )

    print(
        "Latencia promedio:",
        resumen["latencia_promedio_ms"],
        "ms",
    )

    print("Reporte:", RUTA_RESULTADO)

    print("\nEVALUACION LOCAL FINALIZADA")
    print("SIN LLAMADAS A GEMINI")


if __name__ == "__main__":
    main()
