import numpy as np
import copy

def calculo_sigma(dato_filtrado:dict, E:np.array) -> np.array:
  """
  TODO
  """
  data_output = copy.deepcopy(dato_filtrado)

  E_data = np.array(data_output["Energy"])
  Sig_data = np.array(data_output["Sig"])
  # Calcular sigma en los puntos de la integral (E)
  sigma = np.interp(E, E_data, Sig_data)
  return sigma


def filtrar_y_calcular_sigma(datos_filtrados:list, E:np.array)-> list:
  """
  TODO
  """
  datos_con_sigma = []

  for data in datos_filtrados:
    if data['Energy'] == [] or data['Sig'] == []:
      continue
    
    else:
      dato_guardar = copy.deepcopy(data)  #<-- Se hace asi para arreglar un bug.
      dato_guardar['sigma'] = calculo_sigma(data, E).tolist()
      datos_con_sigma.append(dato_guardar)


  return datos_con_sigma