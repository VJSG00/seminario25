import numpy as np
from presentation.utils.calculations.api_iaea import get_half_life
from presentation.utils.funciones_asistentes import extraer_producto_datos_evaluados

# Función de irradiación
def numero_nucleos(ti, tp, rho, A, rt_dict, rti_dict, vtar, Bi):

  # constantes
  na = 6.022e23 # numero de avogadro, entidades/mol

  # tiempo de irradiación y post-irradiación
  ti = np.linspace(0, ti, ti*2) #[horas]
  tp = np.linspace(0, tp, tp*2) #[horas]

  # numero inicial de nucleos en el target.
  nt_0 = (na/A)*Bi*rho*vtar

  Ni_dict = {}
  Np_dict = {}

  # Itera sobre cada conjunto de reacciones
  for (reaction, rt_list), rti_list in zip(rt_dict.items() , rti_dict.values() ):
    #----------------------------------------------------------
    # Obtener half life del isotopo creado
    producto = extraer_producto_datos_evaluados(reaction)
    hl = get_half_life(producto)  # segundos
    #print(reaction, hl)
    if not hl:
      #print(f"{producto} es un nucleo estable.")
      continue

    lam = (np.log(2)/hl) *3600
    #----------------------------------------------------------

    Ni_list = []
    Np_list = []

    # Itera sobre cada conjunto de datos, para una reacción determinada
    for rt, rti in zip(rt_list, rti_list):

      # Calculos necesarios.
      ## constantes convertidas a horas⁻¹
      rt *= 3600  #[horas⁻¹]
      rti *= 3600 #[horas⁻¹]

      # Factor de creación - primer orden.
      creation_term = nt_0*(rti/ (lam - rt))

      # Nucleos de i en el tiempo de creación - primer orden.
      Ni = creation_term * (np.exp(-rt * ti) - np.exp(-lam * ti))

      # Nucleos de i en el tiempo de enfriamiento.
      Ni_max = Ni.max()

      Np = Ni_max*np.exp(-lam*tp)

      # Almacenar
      Ni_list.append(Ni)
      Np_list.append(Np)

    Ni_dict[reaction] = Ni_list
    Np_dict[reaction] = Np_list

  return Ni_dict, Np_dict

def actividad(Ni_dict, Np_dict):

  Ai_dict = {}
  Ap_dict = {}

  # Itera sobre cada reacción
  for (reaction, Ni_list), Np_list in zip(Ni_dict.items(), Np_dict.values()):
    #----------------------------------------------------------
    # Obtener half life del isotopo creado
    producto = extraer_producto_datos_evaluados(reaction)
    hl = get_half_life(producto)  # segundos
    if not hl:
      #print(f"{producto} es un nucleo estable.")
      continue
    lam = (np.log(2)/hl) *3600
    #----------------------------------------------------------

    Ai_list = []
    Ap_list = []

    # Itera sobre el conjunto de datos de cada reacción.
    for Ni, Np in zip(Ni_list, Np_list):

      # Calculo de la actividad
      Ai = lam/3600 * Ni
      Ap = lam/3600 * Np

      # Almacenar
      Ai_list.append(Ai)
      Ap_list.append(Ap)

    Ai_dict[reaction] = Ai_list
    Ap_dict[reaction] = Ap_list

  return Ai_dict, Ap_dict