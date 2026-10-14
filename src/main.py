# Archive AI Lab
# Unidad 1.3 - Funciones en Python

def contar_caracteres(texto):
    return len(texto)

def contar_palabras(texto):
    return len(texto.split())

def analizar_documento(texto):
    cantidad_caracteres = contar_caracteres(texto)
    cantidad_palabras = contar_palabras(texto)

    resultado = {
        "texto_original": texto,
        "cantidad_caracteres": cantidad_caracteres,
        "cantidad_palabras": cantidad_palabras,
        "estado": "procesado"
    }

    return resultado

def main():
    texto = (
        "El Museo de Historia Natural inauguró "
        "una exposición de fotografías antiguas "
        "en Santiago de Chile."
    )

    resultado = analizar_documento(texto)

    print("ARCHIVE AI LAB")
    print("----------------------------")
    print(resultado)

if __name__ == "__main__":
    main()