import requests
import pandas as pd
import numpy as np
from presentation.utils.funciones_asistentes import eliminar_sig, procesar_reaction

### Funcion asistente vvv #----------------------------------------------------------------------
def extraer_dataframe(dic):
    """
    Convierte un diccionario obtenido de la API en un DataFrame.
    Se asegura de que cada punto tenga la clave 'dSig', asignando 0 si falta.
    """
    pts_list = dic['datasets'][0]['pts']
    for point in pts_list:
        if 'dSig' not in point:
            point['dSig'] = 0
    #----------------------------------------------------------------------
    reaction = dic['datasets'][0]['REACTION']
    reaction, projectile, emission, product = procesar_reaction(reaction)
    #----------------------------------------------------------------------
    d = {
        'reaction': reaction,
        'projectile': projectile,
        'emission': emission,
        'product': product,
        'library': dic['datasets'][0]['LIBRARY'],
        'EN': [],
        'DATA': [],
        'DATA-ERR': []
    }

    for point in pts_list:
        d['EN'].append(point['E'])
        d['DATA'].append(point['Sig'])
        d['DATA-ERR'].append(point['dSig'])

    df = pd.DataFrame(d)
    df['reaction'] = df['reaction'].apply(eliminar_sig)  # Se asume que eliminar_sig existe
    return df

### Funcion asistente ^^^ #----------------------------------------------------------------------

def conexion_datos_evaluados(target:str, projectile:str) -> list:
  """
  Extrae los datos de ENDF y devuelve una lista de DataFrames.
  Las columnas finales son:
  reaction 	projectile 	emission 	product 	library 	EN 	DATA 	DATA-ERR
  """

  #----------------------------------------------------------------------
  # Consultar las reacciones de interes.
  reacciones_definidas = ['N','2N','2P','NON','G','D','T','N+A']
  reaccion_a_consultar = ''
  for reaccion in reacciones_definidas:
    reaccion_a_consultar+=projectile+','+reaccion+';'
  # print(reaccion_a_consultar)
  quantity = 'SIG'

  #----------------------------------------------------------------------
  # Realizar búsqueda inicial. Obtenemos los id existentes
  url_busqueda = 'https://nds.iaea.org/exfor/e4list?&json'
  args = {'Target': target,
          'Reaction': reaccion_a_consultar,
          'Quantity': quantity,
          # 'Product': 'Co58' <--TODO: Esto se podria añadir como argumento.
          }
  response = requests.get(url_busqueda, params=args)
  response_dict = response.json()

  #----------------------------------------------------------------------
  # Usamos los ids para consultar los datos existentes.
  data_ids = []
  for section in response_dict["sections"]:
      data_ids.append(section["SectID"])

  # Consultamos los ids.
  list_dic = []
  for sid in data_ids:
      url_datos = 'https://nds.iaea.org/exfor/e4sig?&json'
      args = {'SectID': sid}
      response = requests.get(url_datos, params=args)
      dic = response.json()
      list_dic.append(dic)

  #----------------------------------------------------------------------
  # Convertimos los diccionarios en dataframes.
  list_df = []
  for dic in list_dic:
    list_df.append(extraer_dataframe(dic))

  #----------------------------------------------------------------------
  return list_df