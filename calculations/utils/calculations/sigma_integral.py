import numpy as np
import copy

def calculo_sigma(dato_filtrado:dict, E:np.array) -> np.array:
  """
  TODO
  """
  data_output = copy.deepcopy(dato_filtrado)

  E_data = np.array(data_output["E,ev"])
  Sig_data = np.array(data_output["Sig,b"])
  # Calcular sigma en los puntos de la integral (E)
  sigma = np.interp(E, E_data, Sig_data)
  return sigma