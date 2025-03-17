import re

def eliminar_texto_antes_de_guion(texto):
    # Utilizar expresiones regulares para eliminar texto antes del primer "-"
    resultado = re.sub(r'^[^-]*-', '', texto)
    return resultado

def eliminar_sig(texto):
    # Utilizar expresiones regulares para eliminar ",SIG" al final del texto
    resultado = re.sub(r',SIG$', '', texto)
    return resultado