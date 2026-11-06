import re


# ============================================================
# 1. LIMPIEZA DE TEXTO
# ============================================================

def limpiar_texto(texto: str) -> str:
    """
    Normaliza un texto:
    - Convierte a minúsculas.
    - Elimina signos de puntuación.
    - Elimina espacios repetidos.
    """

    texto = texto.lower()

    texto = re.sub(r"[^\w\s]", " ", texto)

    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


# ============================================================
# 2. TOKENIZACIÓN
# ============================================================

def tokenizar(texto_limpio: str) -> list[str]:
    """
    Convierte un texto limpio en una lista de palabras.
    """

    return texto_limpio.split()


# ============================================================
# 3. PIPELINE COMPLETO
# ============================================================

def procesar_texto(texto: str) -> list[str]:
    """
    Limpia y tokeniza un texto.
    """

    texto_limpio = limpiar_texto(texto)

    return tokenizar(texto_limpio)



# ============================================================
# 4. CONVERSION DE METADATOS A TEXTO
# ============================================================

def metadatos_a_texto(metadatos: dict) -> str:
    """
    Convierte los metadatos documentales del cliente
    en texto para su evaluación.

    Conserva el orden de los campos.
    No inventa información cuando un valor es null.
    """

    campos = ["institucion", "ciudad"]

    valores = []

    for campo in campos:
        valor = metadatos.get(campo)

        if isinstance(valor, str) and valor.strip():
            valores.append(valor.strip())

    return " ".join(valores)