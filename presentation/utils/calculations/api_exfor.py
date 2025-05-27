import requests
import io
import pandas as pd
import numpy as np

from presentation.utils.funciones_asistentes import convertir_unidades, eliminar_guiones, eliminar_numeros_iniciales, eliminar_sig, extract_data_en_info, extract_err_info, extraer_producto_nivel, filtrar_elementos, procesar_reaction

# Nueva API
#---------------------------------------------------------------
# TODO: Seguro puedo añadir el producto.
#---------------------------------------------------------------
# Parametros de la busqueda
def conexion_datos_experimentales(target, proyectil):
  """
  Extrae los datos de EXFOR y devuelve dataframes.
  """
  quantity = 'SIG'
  reaction = proyectil + ',*'

  # Argumentos para el Get.
  url = 'https://nds.iaea.org/exfor/x4list?&txt'
  args = {'Target':target,
          'Reaction':reaction,
          'Quantity':quantity,
          # 'Product': product,   #<------ ver TODO
          }

  # Resultado de la busqueda.
  response = requests.get(url, params=args)

  # Formatear la respuesta
  array = response.content.decode('utf-8').split('\n')

  # Limpiar los '' que siempre aparecen en la respuesta.
  for e in array:
    if e=='':
      array.remove('')

  #---------------------------------------------------------------
  # Validar array cuando es vacio
  if not array:
    #print("No hay datos disponibles")
    return
  #---------------------------------------------------------------
  # Bucle de formatear datos.
  dataframes = []

  for e in array:
    url = 'https://nds.iaea.org/exfor/x4get?'
    args = {'DatasetID':e, 'op':'csv'}

    # Respuesta y formateo a csv.
    response = requests.get(url, params=args)
    content = response.content.decode('utf-8')

    # Almacenar datos en csv.
    csv_data = io.StringIO(content)
    # Leer columnas deseadas
    try:
      df = pd.read_csv(csv_data,
                    #  usecols=['EN (MEV) 1.1', 'DATA (MB) 0.1', 'DATA-ERR (MB) 0.911', 'Proj', 'Emission', 'Targ1', 'Prod', 'author1', 'year1', 'DatasetID']
                    )
      dataframes.append(df)
    except:
      #print(f"Error en {e}")
      continue

  #print(f"Consulta exitosa.")
  return dataframes

#----------------------------------
# Celda de procesamiento
#----------------------------------

def procesar_datos_experimentales(dataframes):
  """
  Aplica filtros y almacena resultados en dataframes.
  """
  #----------------------------------
  # TODO:
  # Faltaria tomar (MICRO-B}
  #----------------------------------
  dataframes_procesados = []
  # data_test = []  #<-- testing
  i = 0
  for df in dataframes:
      #----------------------------------
      # Filtro de datos entrantes: Mas de 4 muestras
      if len(df)<5:
        i+=1
        continue
      #----------------------------------
      # Almacenar producto y nivel.
      producto, nivel = extraer_producto_nivel(df['Prod'].unique()[0])
      target, nivel_t = extraer_producto_nivel(df['Targ1'].unique()[0])

      #----------------------------------
      # Creamos el contenido de reaction.
      prod = eliminar_numeros_iniciales(eliminar_guiones(str(df['Prod'].unique()[0])))
      targ = eliminar_numeros_iniciales(eliminar_guiones(str(df['Targ1'].unique()[0])))
      proj = df['Proj'].unique()[0]
      Emission = df['Emission'].unique()[0]
      reaction = f"{targ}({proj},{Emission}){prod}"

      # Filtro a reaccines raras
      if '/' in reaction:
        continue

      #----------------------------------
      # Diccionario con resultados.
      data = {
          'api':'exfor',
          'DatasetID': df['DatasetID'].unique()[0],
          'year': int(df['year1'].unique()[0]),
          'author': df['author1'].unique()[0],
          'DATA': None,
          'EN': None,
          'DATA-ERR': None,
          'product': producto,
          'level': nivel,
          'target': target,
          'projectile': df['Proj'].unique()[0],
          'emission': df['Emission'].unique()[0],
          'reaction': reaction,
      }
      #----------------------------------
      for column_name in df.columns:
          # Try extracting DATA/EN info first
          #print(f"Analizamos {column_name}")
          name, unit, step = extract_data_en_info(column_name)

          # If DATA/EN info not found, try extracting ERR info
          if name is None:
              name, unit, step = extract_err_info(column_name)

          #----------------------------------
          # Validar: Solo las columnas de interes.
          columnas_datos = ['DATA','EN']
          columnas_errores = ['DATA-ERR','ERR-T','ERR-S']
          #----------------------------------
          # Tratamiento a datos.
          if name in columnas_datos:
            data[name] = convertir_unidades(name,unit,step,df[column_name])
          #----------------------------------
          # Tratamiento a errores.
          elif name in columnas_errores:
            if unit=="PER-CENT":
              data['DATA-ERR'] = ((np.array(data['DATA'])*(df[column_name]*1e-2)).round(6)).tolist()
            else:
              result = convertir_unidades(name,unit,step,df[column_name])

              if result is None: #<--- Previniendo unidades raras
                # print(f"Error en {df['DatasetID'].unique()[0]}")
                continue

              data['DATA-ERR'] = result

          else:
            #print(f"Error en {column_name}")
            continue
          #----------------------------------
          # if name:
            # print(f"Column: {column_name}, Name: {name}, Unit: {unit}, Step: {step}")
      #----------------------------------
      #Borrar clave:valor de data si sigue almacenando None
      for key, value in list(data.items()):
          if value is None:
              del data[key]
      #----------------------------------
      # Validar que data no este vacio
      if not data:
        continue
      #----------------------------------
      # print(data)
      # data_test.append(data)
      # Almacenar dataframes
      try:
        df_procesado = pd.DataFrame([data])
        df_procesado = df_procesado.explode(['EN', 'DATA', 'DATA-ERR'])  # Desglosar las columnas 'EN', 'DATA' y 'DATA-ERR'
        dataframes_procesados.append(df_procesado)
        # print("\n")
      except:
        print(f"Error en {df['DatasetID'].unique()[0]}")
        # print("\n")
      #----------------------------------
  print(f"datos con menos de 5 muestras: {i}")
  return dataframes_procesados

#----------------------------------
# Celda de reacciones faltantes
#----------------------------------
def validar_reacciones_experimentales(dataframes, dataframes_procesados):
  """
  Devuelve aquellas reacciones no procesadas en los datos.
  """
  #----------------------------------
  # Almacenar aquellas reacciones que no se almacenaron.
  # Estas reacciones requieren ingresar manualmente su informacion.
  reacciones_faltantes =  []  #<--- Inicializar fuera de todo bucle.
  #----------------------------------
  # Reacciones Entrantes
  reacciones_entrada=[]
  for df in dataframes:
    reacciones_entrada.append(df['Prod'].unique()[0])

  # Quitar nan
  reacciones_entrada = [x for x in reacciones_entrada if str(x) != 'nan']
  # Valores unicos (para comparar)
  reacciones_entrada = list(np.unique(reacciones_entrada))
  # Filtrado de reacciones 'raras'
  reacciones_entrada = np.array(list(filter(filtrar_elementos, reacciones_entrada)))

  # Imprimir el array filtrado
  reacciones = []
  for elemento in reacciones_entrada:
    producto, nivel = extraer_producto_nivel(elemento)
    if producto:
      reacciones.append(producto + nivel)
  #----------------------------------
  # Reacciones finales tras proceso de los datos.
  reacciones_salida=[]
  for data in dataframes_procesados:
    try:
      reacciones_salida.append((data['product'] + data['level']).unique()[0])
    except KeyError:
      continue
  reacciones_salida = np.unique(reacciones_salida)
  #----------------------------------
  # Comparacion de reacciones de entrada y salida
  elementos_faltantes = np.setdiff1d(reacciones, reacciones_salida)
  reacciones_faltantes.append(list(elementos_faltantes))

  return reacciones_faltantes

# datos evaluados necesarios
def extraer_dataframe_datos_no_elasticos(dic):
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
    target = eliminar_guiones(dic['datasets'][0]['TARGET'])
    reaction, projectile, emission, product = procesar_reaction(reaction)
    #----------------------------------------------------------------------
    d = {
        'api': 'endf',
        'DatasetID': dic['datasets'][0]['id'],
        'reaction': reaction,
        'projectile': projectile,
        'emission': emission,
        'target':target,
        'product': product,
        'level': '',
        'author': dic['datasets'][0]['LIBRARY'],
        'year': '',
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

def conexion_datos_no_elasticos(target:str, projectile:str) -> list:
  """
  Extrae los datos de ENDF y devuelve una lista de DataFrames.
  Las columnas finales son:
  reaction  projectile  emission  product   library   EN  DATA  DATA-ERR
  """

  #----------------------------------------------------------------------
  # Consultar las reacciones de interes.
  reacciones_definidas = ['NON']
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
    list_df.append(extraer_dataframe_datos_no_elasticos(dic))

  #----------------------------------------------------------------------
  return list_df

def flujo_de_datos_experimentales(target, proyectil):
  """
  Funcion que resume el flujo de datos experimentales.
  """
  dataframes = conexion_datos_experimentales(target, proyectil)
  dataframes_procesados = procesar_datos_experimentales(dataframes)
  reacciones_faltantes = validar_reacciones_experimentales(dataframes, dataframes_procesados)
  datos_no_elasticos = conexion_datos_no_elasticos(target, proyectil)
  dataframes_procesados.extend(datos_no_elasticos)

  return dataframes_procesados#, reacciones_faltantes