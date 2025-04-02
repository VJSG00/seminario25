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
  columns_of_interest = ['EN (MEV) 1.1', 'DATA (MB) 0.1', 'DATA-ERR (MB) 0.911', 'Proj', 'Emission', 'Targ1', 'Prod', 'author1', 'year1', 'DatasetID']

  # Testeo - Contadores para filas omitidas
  omitted_rows_nan = 0
  omitted_rows_missing_cols = 0

  # Busqueda para cada id.
  for e in array:
    url = 'https://nds.iaea.org/exfor/x4get?'
    args = {'DatasetID':e, 'op':'csv'}

    # Respuesta y formateo a csv.
    response = requests.get(url, params=args)
    content = response.content.decode('utf-8')

    # Filtramos los datos. Solo analizamos datos con error en la seccion eficaz

    if not all(column in content for column in columns_of_interest):
      omitted_rows_missing_cols += 1
      continue  # Omitir si faltan columnas

    # Almacenar datos en csv.
    csv_data = io.StringIO(content)
    # Leer columnas deseadas y almacenar.
    df = pd.read_csv(csv_data, usecols=['EN (MEV) 1.1', 'DATA (MB) 0.1', 'DATA-ERR (MB) 0.911', 'Proj', 'Emission', 'Targ1', 'Prod', 'author1', 'year1', 'DatasetID'])
    
    # 2. Verificar si hay valores NaN en las columnas de interés
    if df[columns_of_interest].isnull().values.any():
      omitted_rows_nan += 1
      continue  # Omitir si hay NaN

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
              inplace=True
              )
    
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

def extraer_dataframe(dic):
  """
  Convierte un diccionario obtenido de la API en un DataFrame.
  Se asegura de que cada punto tenga la clave 'dSig', asignando 0 si falta.
  """
  pts_list = dic['datasets'][0]['pts']
  for point in pts_list:
      if 'dSig' not in point:
          point['dSig'] = 0

  d = {
      'reaction': dic['datasets'][0]['REACTION'],
      'library': dic['datasets'][0]['LIBRARY'],
      'E,ev': [],
      'Sig,b': [],
      'dSig': []
  }

  for point in pts_list:
      d['E,ev'].append(point['E'])
      d['Sig,b'].append(point['Sig'])
      d['dSig'].append(point['dSig'])

  df = pd.DataFrame(d)
  df['reaction'] = df['reaction'].apply(eliminar_sig)  # Se asume que eliminar_sig existe
  return df

def conexion_datos_evaluados(target, projectile, emissions=[], libs_to_check = ['IAEA', 'JENDL']):
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
        if any(lib in lib_name for lib in libs_to_check):
            selected_ids.append(data_id)

######################################
# Obtenemos una lista de dataframes #
######################################  
  list_df = []
  for sid in selected_ids:
    url_datos = 'https://nds.iaea.org/exfor/e4sig?&json'
    args = {'SectID': sid}
    response = requests.get(url_datos, params=args)
    dic = response.json()
    list_df.append(extraer_dataframe(dic))
  
  # Verificar si hay una reacción NON en IAEA o JENDL
  found_non_reaction = any('NON' in df['reaction'].iloc[0] for df in list_df)
  if found_non_reaction:
    return list_df  # Se retorna directamente sin buscar en TENDL

######################################
# Busqueda en TENDL #
######################################   
  print("No se encontró una reacción con 'NON' en IAEA o JENDL. Buscando en TENDL...")
  tendl_ids = [data_id for lib_name, data_id in zip(lib_names, data_ids) if 'TENDL' in lib_name]

  tendl_dfs = []
  for tid in tendl_ids:
      url_datos = 'https://nds.iaea.org/exfor/e4sig?&json'
      args = {'SectID': tid}
      response = requests.get(url_datos, params=args)
      dic = response.json()
      tendl_dfs.append(extraer_dataframe(dic))

  # Filtrar dataframes de TENDL que cumplan con las condiciones
  valid_tendl_dfs = []
  for df in tendl_dfs:
      zero_count = (df['Sig,b'] == 0).sum()
      if zero_count <= 1:  # Máximo un valor en cero
          valid_tendl_dfs.append(df)

  if not valid_tendl_dfs:
      print("No se encontró ningún conjunto de TENDL válido según las condiciones.")
      return list_df  # Solo se retorna IAEA/JENDL

  # Seleccionar el mejor conjunto de datos de TENDL con valores más grandes de Sig,b
  best_tendl_df = max(valid_tendl_dfs, key=lambda df: df['Sig,b'].mean())

  # Agregar el mejor conjunto de TENDL a list_df
  list_df.append(best_tendl_df)

  return list_df

def conexion_api(target, projectile):
  """
  Extrae los datos de EXFOR y ENDF y devuelve archivos csv o dataframes segun sea solicitado.
  """
  datos_experimentales, emission = conexion_datos_experimentales(target, projectile)

  datos_evaluados = conexion_datos_evaluados(target, projectile, emission)

  return datos_experimentales, datos_evaluados

