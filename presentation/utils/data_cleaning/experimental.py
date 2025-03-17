import numpy as np
from scipy.interpolate import PchipInterpolator

def Interpolar_Puntos_Adicionales(energias, secciones, num_puntos_adicionales):
    """
    Aplica el Interpolador de Hermite y linspace para obtener puntos adicionales.
    El objetivo es preparar y comparar los datos para la integración.
    """

    hermite_interp = PchipInterpolator(energias, secciones)
    energias_interp = np.linspace(energias.min(), energias.max(), num_puntos_adicionales)
    secciones_interp = hermite_interp(energias_interp)

    return energias_interp, secciones_interp


def procesar_datos(datos_evaluados):
  """
  Procesa los datos experimentales y devuelve dos listas de arrays.
  La primera lista es de secciones eficaces y la segunda de energias.
  """

  # Limpieza de los datos.
  for df in datos_evaluados:
    df.sort_values('E,ev', inplace=True)
    df.drop_duplicates(subset='E,ev', keep='first', inplace=True)

  # Almacena datos relevantes.
  secciones = []
  energias = []
  for df in datos_evaluados:
    e, s = Interpolar_Puntos_Adicionales(df['E,ev'], df['Sig,b'], 1000)
    secciones.append(s)
    energias.append(e)

  return secciones, energias

def filtrar_datos_interpolados(energias_interp, secciones_interp, E_back, E_beam):
  mask = (energias_interp >= E_back) & (energias_interp <= E_beam)
  energias_intp_filt = energias_interp[mask]
  secciones_intp_filt = secciones_interp[mask]
  return energias_intp_filt, secciones_intp_filt

