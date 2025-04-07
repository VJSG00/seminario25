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