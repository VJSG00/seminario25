import numpy as np
import re

def procesar_reaction(texto):
    # 1. Eliminar todos los guiones
    texto_sin_guiones = re.sub(r'-', '', texto)
    # Aplicar el filtro de ',SIG' a texto_sin_guiones
    texto_filtrado = re.sub(r',SIG$', '', texto_sin_guiones)

    # 2. Extraer la letra siguiente a "(" (Projectile)
    match_inicio = re.search(r'\((.)', texto_sin_guiones)
    letra_siguiente = match_inicio.group(1) if match_inicio else None

    # 3. Extraer el texto entre la coma y ")"
    match_entre = re.search(r',([^,)]+)\)', texto_filtrado)
    texto_entre_coma_y_parentesis = match_entre.group(1) if match_entre else None

    # 4. Extraer todo el texto siguiente a ")" (Product)
    match_texto = re.search(r'\)(.*)', texto_sin_guiones)
    texto_despues = match_texto.group(1) if match_texto else None
    if texto_despues:
        texto_despues = re.sub(r',SIG$', '', texto_despues)

    return texto_filtrado, letra_siguiente, texto_entre_coma_y_parentesis, texto_despues

def eliminar_sig(texto):
    # Utilizar expresiones regulares para eliminar ",SIG" al final del texto
    resultado = re.sub(r',SIG$', '', texto)
    return resultado

def eliminar_guiones(texto):
  texto_sin_guiones = re.sub(r'-', '', texto)
  return texto_sin_guiones

#---------------------------------------------------------------------------------------
# Datos Experimentales
#---------------------------------------------------------------------------------------

def filtrar_elementos(elemento):
    """
    Filtra elementos según las condiciones especificadas.
    """
    # Contar el número de guiones en el elemento.
    num_guiones = elemento.count('-')

    # Si el elemento tiene menos de 3 guiones, conservarlo.
    if num_guiones < 3:
        return True

    # Si el elemento tiene 3 o más guiones, aplicar las condiciones adicionales.
    if num_guiones >= 3:
        # Verificar si es "M" o "G"
        if elemento.endswith('-M') or elemento.endswith('-G'):
            return True  # Mantener el elemento
        else:
            return False  # Eliminar el elemento
    # Si el elemento tiene un slash "/" eliminarlo.
    if '/' in elemento:
      return False

def extraer_producto_nivel(texto):
    """
    Extrae el producto y el nivel de una cadena de texto con el formato "NUM-ELEMENTO-NUM-NIVEL".
    """
    match = re.match(r'(\d+)-([A-Za-z]+)-(\d+)(?:-([A-Za-z]))?', texto)
    if match:
        producto = match.group(2) + match.group(3)
        nivel = match.group(4) if match.group(4) else ''
        return producto, nivel
    else:
        return None, None

def extract_data_en_info(column_name):
    """
    Extrae información de los nombres de columna con formato "DATA (UNIT) STEP" o "EN (UNIT) STEP".
    """

    pattern = r"(\w+)\s*\((\w+)\)\s*(\d+\.?\d*)"  # Pattern for DATA and EN columns
    match = re.match(pattern, column_name)

    if match:
        name = match.group(1)
        unit = match.group(2)
        step = match.group(3)
        return name, unit, step
    else:
        return None, None, None

def extract_err_info(column_name):
    """
    Extrae información de los nombres de columna con formato "DATA-ERR (UNIT) STEP" o "ERR-T (UNIT) STEP".
    """

    pattern = r"(\w+-\w+)\s*\(([^\)]+)\)\s*(\d+\.?\d*)"  # Pattern for DATA-ERR and ERR-T columns
    match = re.match(pattern, column_name)

    if match:
        name = match.group(1)
        unit = match.group(2)
        step = match.group(3)
        return name, unit, step
    else:
        return None, None, None

def convertir_unidades(name,unit,step,df_column):
  """
  TODO
  """
  #----------------------------------
  # Validar los datos

  #----------------------------------
  # Diccionario
  dic_unidades={
      "MICRO-B": 1e-6,
      "MB": 1e-3,
      "B":1,
      "EV": 1,
      "MEV": 1e6,
      "GEV": 1e9,
  }
  #----------------------------------
  # Caso unico, percent.
  #----------------------------------
  # Multiplicar unidades -> convertir a barns y eV.
  try:
    df_column = (df_column*dic_unidades[unit]).round(6)
  except(KeyError):
    return None
  #----------------------------------
  return df_column.to_list()

def eliminar_guiones(texto):
    """
    Elimina los guiones en una cadena de texto con el formato '27-CO-58' o '25-MN-54'.
    """
    # Utilizamos la función sub del módulo re para reemplazar los guiones con una cadena vacía.
    # El patrón de la expresión regular r'-' busca todos los guiones en la cadena de texto.
    # texto_sin_guiones = re.sub(r'-', '', texto)
    texto_sin_guiones = re.sub(r'(-)', '', texto, count=2)

    return texto_sin_guiones

def eliminar_numeros_iniciales(texto):
    """
    Elimina los primeros números antes de los símbolos de letras en una cadena de texto.
    """
    # Utilizamos la función sub del módulo re para reemplazar los números iniciales con una cadena vacía.
    # El patrón de la expresión regular r'^\d+' busca uno o más dígitos al principio de la cadena.
    texto_sin_numeros_iniciales = re.sub(r'^\d+', '', texto)

    return texto_sin_numeros_iniciales

#---------------------------------------------------------------------------------------
# Api IAEA
#---------------------------------------------------------------------------------------

def extraer_producto_datos_evaluados(texto):
  """
  Extrae el núcleo del producto de una reacción nuclear.

  Parámetros:
    texto (str): La reacción nuclear en formato de texto.

  Retorna:
    str: El núcleo del producto.

  Ejemplo:
    extraer_nucleo_producto('NI64(P,N)CU64') == 'CU64'
    extraer_nucleo_producto('NI64(P,T)NI62') == 'NI62'
  """

  # Buscar el texto después del cierre del paréntesis
  match = re.search(r'\)([A-Za-z0-9]+)', texto)

  # Si se encuentra una coincidencia, devolver el texto
  if match:
    return match.group(1)

  # Si no se encuentra una coincidencia, devolver None
  return None