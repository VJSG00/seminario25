import pandas as pd
import numpy as np
import os
import io 
import requests

from presentation.utils.utils import eliminar_sig, eliminar_texto_antes_de_guion

def conexion_datos_experimentales(target, proyectil):
  """
  Extrae los datos de EXFOR y devuelve archivos csv o dataframes segun sea solicitado.
  """
  # Parametros de la busqueda
  quantity = 'SIG'  # Siempre extraeremos la sección eficaz
  reaction = proyectil + ',*'  # Todas las reacciones

  # Argumentos para el Get.
  url = 'https://nds.iaea.org/exfor/x4list?&txt'
  args = {'Target':target, 'Reaction':reaction, 'Quantity':quantity}

  # Resultado de la busqueda.
  response = requests.get(url, params=args)

  # Formatear la respuesta
  array = response.content.decode('utf-8').split('\n')

  # Limpiar los '' que siempre aparecen en la respuesta.
  for e in array:
    if e=='':
      array.remove('')

  # Almacenamos los dataframes en una lista de dataframes:
  dataframes = []

  # Busqueda para cada id.
  for e in array:
    url = 'https://nds.iaea.org/exfor/x4get?'
    args = {'DatasetID':e, 'op':'csv'}

    # Respuesta y formateo a csv.
    response = requests.get(url, params=args)
    content = response.content.decode('utf-8')

    # Filtramos los datos. Solo analizamos datos con error en la seccion eficaz
    if "DATA-ERR (MB) 0.911" not in content:
      continue

    else:
      # Almacenar datos en csv.
      csv_data = io.StringIO(content)

      # Leer columnas deseadas y almacenar.
      df = pd.read_csv(csv_data, usecols=['EN (MEV) 1.1', 'DATA (MB) 0.1', 'DATA-ERR (MB) 0.911', 'Proj', 'Emission', 'Targ1', 'Prod', 'author1', 'year1', 'DatasetID'])
      
            # Ajustar la reacción y el autor. Despues borrar columnas innecesarias.
      df['tar'] = df['Targ1'].apply(eliminar_texto_antes_de_guion)
      df['prod'] = df['Prod'].apply(eliminar_texto_antes_de_guion)
      df['React'] = df["tar"] + "(" + df['Proj'] + "," + df['Emission'] + ")" + df['prod']
      df['author'] = df['author1'] + " (" + df['year1'].astype(str) + ")"
      df.drop(columns=['Proj', 'Targ1', 'Prod', 'author1', 'year1', 'tar', 'prod'], inplace=True)

      # Ajustar unidades y renombrar columnas
      df["EN (MEV) 1.1"] = df["EN (MEV) 1.1"]*1e6
      df["DATA (MB) 0.1"] = df["DATA (MB) 0.1"]*1e-3
      df["DATA-ERR (MB) 0.911"] = df["DATA-ERR (MB) 0.911"]*1e-3
      df.rename( columns={
                "EN (MEV) 1.1" : "E,ev",
                "DATA (MB) 0.1" : "Sig,b",
                "DATA-ERR (MB) 0.911" : "dSig",
                },
                inplace=True)
      
      # Almacenar
      dataframes.append(df)

      # Esto se requiere para los datos evaluados.
      emissions = []
      for df in dataframes:
        emissions.append(df["Emission"][0])
      emissions = list(np.unique(emissions))

  return dataframes, emissions
      ## Testing
      #print(response.url)

def conexion_datos_evaluados(target, projectile, emissions=[]):
  """
  Extrae los datos de ENDF y devuelve archivos csv o dataframes segun sea solicitado.
  """

  # Argumentos para la busqueda
  projectile = projectile.upper()
  string = ''

  if emissions != []:
    # Formateamos las reacciones posibles
    for emission in emissions:
      string += projectile + "," + emission + ";"

  # Argumentos de la busqueda
  target = target.upper()
  reaction = projectile + ",NON" + ";" + string
  quantity = 'SIG'

  # Argumentos para el Get.
  url = 'https://nds.iaea.org/exfor/e4list?&json'
  args = {'Target':target, 'Reaction':reaction, 'Quantity':quantity}

  # Resultado de la busqueda.
  response = requests.get(url, params=args)

  # Formatear la respuesta.
  response_dict = response.json()

  # Es necesario convertir la respuesta en diccionario y acceder a sus datos:
  # Almacenamos los id y las bibliotecas de la respuesta.
  data_ids = []
  lib_names = []
  for section in response_dict["sections"]:
      data_ids.append(section["SectID"])
      lib_names.append(section["LibName"])

  # Por defecto solo queremos los datos evaluados de la IAEA y JENDL
  selected_ids = []

  # Iteramos simultáneamente por lib_names y data_ids
  for lib_name, data_id in zip(lib_names, data_ids):
      # Verificamos si 'JENDL' o 'IAEA' se encuentran en el nombre de la librería
      if 'JENDL' in lib_name or 'IAEA' in lib_name:
          selected_ids.append(data_id)

  # Se extraen y se almacenan los datos.
  to_dataframe = []
  for id in selected_ids:
    url = 'https://nds.iaea.org/exfor/e4sig?&json'
    args = {'SectID':id}
    response = requests.get(url, params=args)

    # Convertir respuesta json en un diccionario.
    dic = response.json()

    # Almacenamos en formato diccionario.
    to_dataframe.append(dic)

  # Es necesario completar los datos: dSig
  for dic in to_dataframe:
      pts_list = dic['datasets'][0]['pts']
      for point in pts_list:
          if 'dSig' not in point:
              point['dSig'] = 0

  # Extraemos info para crear dataframes
  list_df = []
  for dic in to_dataframe:

    d = {
        'reaction' : dic['datasets'][0]['REACTION'],
        'library': dic['datasets'][0]['LIBRARY'],
        'E,ev' : [],
        'Sig,b' : [],
        'dSig' : []
    }

    for point in dic['datasets'][0]['pts']:
      d['E,ev'].append(point['E'])
      d['Sig,b'].append(point['Sig'])
      d['dSig'].append(point['dSig'])

    # Almacenamos en df
    df = pd.DataFrame(d)
    df['reaction'] = df['reaction'].apply(eliminar_sig)
    list_df.append(df)

  return list_df

def conexion_api(target, projectile):
  """
  Extrae los datos de EXFOR y ENDF y devuelve archivos csv o dataframes segun sea solicitado.
  """
  datos_experimentales, emission = conexion_datos_experimentales(target, projectile)

  datos_evaluados = conexion_datos_evaluados(target, projectile, emission)

  return datos_experimentales, datos_evaluados

