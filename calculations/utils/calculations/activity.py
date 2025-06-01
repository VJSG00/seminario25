import numpy as np
import copy
from ..elementos import densidad

# Función de irradiación
def numero_nucleos_y_actividad(datos_productos: dict, products: list, A:int ,ti:int, tp:int, rho:float, vtar:float , Bi:float):

  data_output = copy.deepcopy(datos_productos)
  #print("\nDatos dentro de numero nucleos y actividad\n", data_output )

  # constantes
  na = 6.022e23 # numero de avogadro, entidades/mol

  # tiempo de irradiación y post-irradiación
  ti = np.linspace(0, ti, ti*2) #[horas]
  tp = np.linspace(0, tp, tp*2) #[horas]

  # numero inicial de nucleos en el target.
  nt_0 = (na/A)*Bi*rho*vtar

  # Iterar sobre cada isotopo producido
  for product in products:
    
    #print(f"entrada de datos: {data_output[product]}")

    # Iterar sobre cada conjunto de datos.
    for data in data_output[product]:

      if not data['final_isotope'].half_life:
        continue

      #print(f"\ndata: {data}\n")
      Lambda = (data['final_isotope'].half_life)/3600 #horas⁻¹
      Lambda = np.log(2)/Lambda #[horas⁻¹]
      #print(f"Lambda: {Lambda}")
      rti = data['rti']
      rti *= 3600 #[horas⁻¹]

      # Hay n rt's en rt_list. Hacemos los calculos con todos.
      for index in range(len(data['rt_list'])):
        rt = data['rt_list'][index]['rt']
        rt *= 3600  #[horas⁻¹]
        library = data['rt_list'][index]['library']

        ### TODO: Todo esto es primer orden.
        # Factor de creación - primer orden.
        creation_term = nt_0*(rti/ (Lambda - rt))
        #print("\n", creation_term, rt, Lambda, rti)

        # Nucleos de i en el tiempo de creación - primer orden.
        Ni = creation_term * (np.exp(-rt * ti)  -np.exp(-Lambda * ti))
        
        # Nucleos de i en el tiempo de enfriamiento.
        Ni_max = Ni.max()

        Np = Ni_max*np.exp(-Lambda*tp)
        # Calculo de la actividad
        Ai = (Lambda/3600) * Ni    # 1/seg
        Ap = (Lambda/3600) * Np

        # Almacenar
        N_dict = {
            'library': library,
            'Ni': Ni,
            'Np': Np,
        }

        #print(Ai, Ap, "\n")
        A_dict = {
            'library': library,
            'Ai': Ai,
            'Ap': Ap,
        }

        if 'N_list' not in data:
          data['N_list'] = []
        data['N_list'].append(N_dict)

        if 'A_list' not in data:
          data['A_list'] = []
        data['A_list'].append(A_dict)

  return data_output

def numero_nucleos_y_actividad_producto(resultado, ti, tp, half_life):
  """
  TODO
  """
  na = 6.022e23
  Bi = 1

  ti = np.linspace(0, ti, ti*2) #[horas]
  tp = np.linspace(0, tp, tp*2) #[horas]

  resultado_final = {}
  data_input = copy.deepcopy(resultado)
  
  for tag, data in data_input.items():
    
    A = data['A_p']
    Z = data['Z_p']
    rho = data['rho_p']
    vtar = data['vtar']

    nt_0 = (na/A)*Bi*rho*vtar

    Lambda = (np.log(2)/half_life)*3600
    rti = data['rti']
    rt = data['rt_prod']

    rt *= 3600
    rti *= 3600

    creation_term = nt_0*(rti/ (Lambda - rt))

    Ni = creation_term *(np.exp(-rt * ti)  -np.exp(-Lambda * ti))
    Ni_max = Ni.max()

    Np = Ni_max*np.exp(-Lambda*tp)


    Ai = (Lambda/3600) * Ni    # 1/seg
    Ap = (Lambda/3600) * Np
    Ai_max = Ai.max()

    resultado_final[tag] = {
        'target_symbol': data['target_symbol'],
        'projectile': data['projectile'],
        'reaction': data['reaction'],
        'rt':data['rt_prod'],
        'rti':data['rti'],
        'vtar':data['vtar'],
        'Ai': Ai,
        'Ap': Ap,
        'A_max':Ai_max,
        'Ni': Ni,
        'Np': Np,
        'N_max':Ni_max,
        'ti': ti,
        'tp': tp,
    }

  return resultado_final

def calcular_actividad_nucleos_simplificado(resultado):
  
  na = 6.022e23
  Bi = 1

  datos_entrantes = copy.deepcopy(resultado)
  resultado_final = {}

  tp = np.linspace(0, 72, 72*3)

  for tag, data in datos_entrantes.items():
    # Acceder a los isotopos
    target = data['target']
    product = data['product']

    # Variables del target
    A = target.A
    Z = target.Z
    rho = densidad[Z]
    vtar = data['vtar']

    nt_0 = (na/A)*Bi*rho*vtar
    
    # Variables del producto
    half_life = product.half_life       #seg
    Lambda = (np.log(2)/half_life)*3600 #1/h

    rt = data['rt_prod']*3600           #1/h
    rti = data['rti']*3600              #1/h
    
    creation_term = nt_0*(rti/ (Lambda - rt))
    
    t_max = (np.log(Lambda/rt))/(Lambda - rt) #1/h
    t = np.linspace(0, t_max, int(t_max*3))


    Ni = creation_term *(np.exp(-rt * t)  -np.exp(-Lambda * t))
    Ni_max = Ni.max()
    Np = Ni_max*np.exp(-Lambda*tp)

    Ai = (Lambda/3600) * Ni    # 1/seg
    Ap = (Lambda/3600) * Np
    Ai_max = Ai.max()

    resultado_final[tag] = {
    'target_symbol': target.symbol,
    'projectile': product.symbol,
    'reaction': data['reaction'],
    'N_max':Ni_max,
    't_max': t_max,
    'rt':data['rt_prod'],
    'rti':data['rti'],
    'vtar':data['vtar'],
    'A_max':Ai_max,
    'E_max': data['E_max'],
    'Ai': Ai,
    'Ap': Ap,
    'Ni': Ni,
    'Np': Np,
    't': t,
    'tp': tp,
    }

  return resultado_final