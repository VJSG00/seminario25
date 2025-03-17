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

def workflow(data_dict, E_back, E_beam, I, rho, Z, A):
  """
  Calcula las constantes de producción.
  """

  rt_dict = {}
  rti_dict = {}

  # Calculo para la no elastica.
  no_elastic_data_list = data_dict['no_elastic_data']
  print(f"Procesando datos no elasticos")
  print(type(no_elastic_data_list))
  print(type(no_elastic_data_list[0]))
  print(no_elastic_data_list[0].columns)
  list_of_sigma_non = workflow_no_elastic_data(no_elastic_data_list, E_back, E_beam)

  # Para cada conjunto de datos:
  for reaction, list_df in data_dict.items():

    if reaction == 'no_elastic_data':
      continue
    else:
      print(f"Procesando datos elasticos de la reaccion {reaction}")
      list_of_sigma_in, dEdx, E = workflow_data(list_df, E_back, E_beam, I, rho, Z, A)
      if list_of_sigma_in == None:
        continue

    # Calculo de la integral de la constante de producción
    list_of_rt_int = []
    list_of_rti_int = []
    for sigma in list_of_sigma_in:
      rt_int = trapezoid(y=sigma / dEdx, x=E)
      list_of_rt_int.append(rt_int)

      for sigma_non in list_of_sigma_non:
        d_sigma = sigma_non - sigma
        rti_trap = trapezoid(y =d_sigma / dEdx, x =E)
        list_of_rti_int.append(rti_trap)

    # Integral del volumen
    S = 1 #cm²
    int_vol = trapezoid(y=1 / dEdx, x=E)
    vtar = S*int_vol

    # Constantes de producción
    I_beam = 60e-6 #microA
    z_p = 1 # una carga fundamental en el protón

    rt_list = []
    rti_list = []

    for rt_int, i in zip(list_of_rt_int, range(len(list_of_rt_int))):

      # Integral de R_T
      rt = (I_beam/(z_p*q_e))*(1/vtar)*rt_int
      rt *= 1e-24
      rt_list.append(rt)

      # Integral R_{T->i}
      rti_int = list_of_rti_int[i]
      rti = (I_beam/(z_p*q_e))*(1/vtar)*rti_int
      rti *= 1e-24
      rti_list.append(rti)

    rt_dict[reaction] = rt_list
    rti_dict[reaction] = rti_list

  return rt_dict, rti_dict, E, vtar