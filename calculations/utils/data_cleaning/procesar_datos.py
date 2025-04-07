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

    E = np.array(data["E,ev"], dtype=float)
    Sig = np.array(data["Sig,b"], dtype=float)
    dSig = np.array(data["dSig,b"], dtype=float)

    # La forma más simple de procesar estos datos es con pandas.
    df = pd.DataFrame({
        'E,ev': E,
        'Sig,b': Sig,
        'dSig,b': dSig,
    })

    df = df.sort_values('E,ev')
    df = df.drop_duplicates(subset='E,ev', keep='first')

    # Devolvemos arrays
    data.update({
        "E,ev": df['E,ev'].tolist(),
        "Sig,b": df['Sig,b'].tolist(),
        "dSig,b": df['dSig,b'].tolist(),
    })

  print(f"datos procesados")
  return data_list

def interpolar_datos(datos_procesados:list, num_puntos_adicionales:int=1000):
  """
  TODO
  """
  data_output = copy.deepcopy(datos_procesados)

  for data in data_output:
    E = np.array(data["E,ev"])
    Sig = np.array(data["Sig,b"])

    hermite_interp = PchipInterpolator(E, Sig)
    E_interp = np.linspace(E.min(), E.max(), num_puntos_adicionales)
    secciones_interp = hermite_interp(E_interp)

    data['E,ev'] = E_interp.tolist()
    data['Sig,b'] = secciones_interp.tolist()

  print(f"datos interpolados")
  return data_output

def filtrar_datos(datos_interpolados:list, E_back:float, E_beam:float):
  """
  TODO
  """
  data_output = copy.deepcopy(datos_interpolados)

  for data in data_output:
    E = np.array(data["E,ev"])
    Sig = np.array(data["Sig,b"])

    mask = (E >= E_back) & (E <= E_beam)
    E_filt = E[mask]
    Sig_filt = Sig[mask]

    data['E,ev'] = E_filt.tolist()
    data['Sig,b'] = Sig_filt.tolist()

  print(f"datos filtrados")
  return data_output


