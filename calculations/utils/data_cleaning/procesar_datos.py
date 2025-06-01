import numpy as np
import pandas as pd
import copy

from scipy.interpolate import PchipInterpolator


def procesar_datos(datos_evaluados: list) -> list:
  """
  TODO
  """
  data_list = copy.deepcopy(datos_evaluados)

  for data in data_list:

    E = np.array(data["Energy"], dtype=float)
    Sig = np.array(data["Sig"], dtype=float)
    dSig = np.array(data["dSig"], dtype=float)

    # La forma más simple de procesar estos datos es con pandas.
    df = pd.DataFrame({
        'Energy': E,
        'Sig': Sig,
        'dSig': dSig,
    })

    df = df.sort_values('Energy')
    df = df.drop_duplicates(subset='Energy', keep='first')

    # Devolvemos arrays
    data.update({
        "Energy": df['Energy'].tolist(),
        "Sig": df['Sig'].tolist(),
        "dSig": df['dSig'].tolist(),
    })

  print(f"datos procesados")
  return data_list

def interpolar_datos(datos_procesados:list, num_puntos_adicionales:int=1000):
  """
  TODO
  """
  data_output = copy.deepcopy(datos_procesados)

  for data in data_output:
    E = np.array(data["Energy"])
    Sig = np.array(data["Sig"])

    hermite_interp = PchipInterpolator(E, Sig)
    E_interp = np.linspace(E.min(), E.max(), num_puntos_adicionales)
    secciones_interp = hermite_interp(E_interp)

    data['Energy'] = E_interp.tolist()
    data['Sig'] = secciones_interp.tolist()

  print(f"datos interpolados")
  return data_output

def filtrar_datos(datos_interpolados:list, E_back:float, E_beam:float):
  """
  TODO
  """
  data_output = copy.deepcopy(datos_interpolados)

  for data in data_output:
    E = np.array(data["Energy"])
    Sig = np.array(data["Sig"])

    mask = (E >= E_back) & (E <= E_beam)
    E_filt = E[mask]
    Sig_filt = Sig[mask]

    data['Energy'] = E_filt.tolist()
    data['Sig'] = Sig_filt.tolist()

  print(f"datos filtrados")
  return data_output

def calculo_energias_maximas(datos_interpolados:list):
  """
  TODO
  """
  datos_con_energias = copy.deepcopy(datos_interpolados)

  for data in datos_con_energias:
    energy = np.array(data['Energy'])
    sig = np.array(data['Sig'])

    # indice sig maximo
    max_sig_index = np.argmax(sig)

    # Energia y seccion eficaz maxima
    #max_sig_value = sig[max_sig_index]
    energy_at_max_sig = energy[max_sig_index]

    data['Energia_max'] = energy_at_max_sig

  return datos_con_energias

def filtrar_datos_con_energias(datos_interpolados:list, E_back:float):
  """
  TODO
  """
  data_output = copy.deepcopy(datos_interpolados)

  for data in data_output:
    E = np.array(data["Energy"])
    Sig = np.array(data["Sig"])
    E_beam = data["Energia_max"]

    mask = (E >= E_back) & (E <= E_beam)
    E_filt = E[mask]
    Sig_filt = Sig[mask]

    data['Energy'] = E_filt.tolist()
    data['Sig'] = Sig_filt.tolist()

  print(f"datos filtrados")
  return data_output