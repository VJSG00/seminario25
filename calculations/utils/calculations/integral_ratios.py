from calculations.utils.calculations.bethe_bloch import bethe_bloch
from calculations.utils.get_data_db import get_nuclear_properties_by_symbol
from ..elementos import densidad
from ..diccionario_de_cargas import diccionario_de_cargas, diccionario_de_masa_equivalente
from scipy.integrate import trapezoid
import numpy as np
import copy

def integral_ratios(datos_divididos, vtar, z_p, current, dEdx, E ):
    
    q_e = 1.602e-19 # Coulomb
    K = (current/(z_p*q_e))*(1/vtar)

    datos_con_ratios = copy.deepcopy(datos_divididos)

    for resultado, lista in datos_con_ratios.items():
        
        if resultado == 'no_elastic_data':

            for data_non in lista:
                
                # Ratio de todas las producciones.
                sigma_non = data_non['sigma']
                rt_prod = K * trapezoid(y=sigma_non/dEdx, x=E)
                rt_prod *= 1e-24
                data_non['rt_prod'] = rt_prod  
            
            continue

        for data in lista:
            
            sigma = np.array(data['sigma'])

            # Ratio de creación
            rti = K * trapezoid(y=sigma/dEdx , x=E)
            rti *= 1e-24
            data['rti'] = rti
            if rti<0:
                raise ValueError("Error en el signo de rti. Revisar el signo de K.")

            for data_non in datos_con_ratios['no_elastic_data']:
                # Ratio RT
                ## TODO Quisiera simplificar esta logica la verdad.
                sigma_non = np.array(data_non['sigma'])
                d_sigma = sigma_non - sigma
                rt = K * trapezoid(y=d_sigma/dEdx, x=E)
                rt *= 1e-24

                rt_info = {
                    'library': data_non['reference'],
                    'rt': float(rt),
                }
                if 'rt_list' not in data:
                    data['rt_list'] = []
                data['rt_list'].append(rt_info)
    
    return datos_con_ratios

def calculo_ratio_producto(data_tag_test, I_beam, E_beam, E_back):
  
  q_e = 1.602e-19 # Coulomb
  resultado = {}

  for tag, group_list in data_tag_test.items():

    target = group_list[0]['target']

    # Consultar en la base de datos:
    target = get_nuclear_properties_by_symbol(target)
    A_p = target.A
    Z_p = target.Z
    rho_p = densidad[Z_p]
    projectile = group_list[0]['projectile']
    I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))
    S= 1.0

    m_0 = diccionario_de_masa_equivalente[projectile]
    z_p = diccionario_de_cargas[projectile]

    N = 500
    E = np.linspace(E_back, E_beam, N)
    dEdx = np.array([bethe_bloch(e, I, rho_p, Z_p, A_p, z_p, m_0) for e in E ])

    vtar = S*trapezoid(y=1 / dEdx, x=E)
    K = (I_beam/(z_p*q_e))*(1/vtar)

    resultado[tag] = {
        'target_symbol': target.symbol,
        'projectile': projectile,
        'A_p': A_p,
        'Z_p': Z_p,
        'rho_p': rho_p,
        'vtar': vtar,
    }

    for data in group_list:
      
      if data['emission'] == 'NON':
        sigma_non = np.array(data['sigma'])
        rt_prod = K * trapezoid(y=sigma_non/dEdx, x=E)
        rt_prod *= 1e-24
        resultado[tag]['rt_prod'] = rt_prod
      else: #<-- Si no es non, entonces es prod.
        resultado[tag]['reaction'] = data['reaction']
        sigma = np.array(data['sigma'])
        rti = K * trapezoid(y=sigma/dEdx , x=E)
        rti *= 1e-24
        resultado[tag]['rti'] = rti
  
  return resultado