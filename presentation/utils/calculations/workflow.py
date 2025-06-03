import numpy as np
from scipy.integrate import simpson, trapezoid
from presentation.utils.calculations.bethe_bloch import bethe_bloch
from presentation.utils.data_cleaning.experimental import filtrar_datos_interpolados, procesar_datos

q_e=1.6e-19

def workflow_data(list_df, E_back, E_beam, I, rho, Z, A):

    secciones, energias = procesar_datos(list_df)

    # Filtro de datos Api
    for i in range(len(energias)):
      energias[i], secciones[i] = filtrar_datos_interpolados(energias[i], secciones[i], E_back, E_beam)

    # Integral
    N = 500
    E = np.linspace(E_back, E_beam, N)

    # Diferencial - Ecuación de Bethe
    dEdx = np.array([bethe_bloch(e, I, rho, Z, A) for e in E])

    # Para cada conjunto de datos, funcionalizamos su sección eficaz
    try:
      list_of_sigma_in = []
      for i in range(len(energias)):
        sigma_in = np.interp(E, energias[i], secciones[i])
        list_of_sigma_in.append(sigma_in)
      return list_of_sigma_in, dEdx, E
    except(ValueError):
      return None, None, None

def workflow_no_elastic_data(list_df, E_back, E_beam):

    secciones, energias = procesar_datos(list_df)

    # Filtro de datos Api
    for i in range(len(energias)):
      energias[i], secciones[i] = filtrar_datos_interpolados(energias[i], secciones[i], E_back, E_beam)

    # Integral
    N = 500
    E = np.linspace(E_back, E_beam, N)

    # Para cada conjunto de datos, funcionalizamos su sección eficaz
    try:
      list_of_sigma_non = []
      for i in range(len(energias)):
        sigma_non = np.interp(E, energias[i], secciones[i])
        list_of_sigma_non.append(sigma_non)
      return list_of_sigma_non
    except(ValueError):
      return None

def workflow(data_dict, E_back, E_beam, I_beam, I_mean, rho, Z, A, z_p = 1, S=1.0):
  """
  Calcula las constantes de producción.
  """

  rt_dict = {}
  rti_dict = {}

  # Calculo para la no elastica.
  no_elastic_data_list = data_dict['no_elastic_data']
  #print(f"Procesando datos no elasticos")
  #print(type(no_elastic_data_list))
  #print(type(no_elastic_data_list[0]))
  #print(no_elastic_data_list[0].columns)
  list_of_sigma_non = workflow_no_elastic_data(no_elastic_data_list, E_back, E_beam)

  # Para cada conjunto de datos:
  for reaction, list_df in data_dict.items():

    if reaction == 'no_elastic_data':
      continue
    else:
      #print(f"Procesando datos elasticos de la reaccion {reaction}")
      list_of_sigma_in, dEdx, E = workflow_data(list_df, E_back, E_beam, I_mean,rho, Z, A)
      if list_of_sigma_in == None:
        continue
  
    # Almacenamos
    rt_list = []
    rti_list = []
    
    # Integral del volumen
    int_vol = trapezoid(y=1 / dEdx, x=E)
    vtar = S*int_vol

    # Termino de produccion
    K = (I_beam/(z_p*q_e))*(1/vtar)
    
    for sigma, sigma_non in zip(list_of_sigma_in, list_of_sigma_non):

      rti_int = trapezoid(y=sigma / dEdx, x=E)
      rti = K*rti_int
      rti *= 1e-24
      rti_list.append(rti)

      # Integral de R_T
      rt_int = trapezoid(y=sigma_non / dEdx, x=E)
      rt = K*rt_int
      rt *= 1e-24
      rt_list.append(rt)

    rt_dict[reaction] = rt_list
    rti_dict[reaction] = rti_list

  return rt_dict, rti_dict, E, vtar #, rt_prod_list