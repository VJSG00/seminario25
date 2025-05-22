import copy
from collections import defaultdict

def dividir_productos(datos_filtrados):
    """
    TODO
    Divide los datos en categorias, en función del producto final de la reacción

    Devuelve un defaultdict, para almacenar los datos de forma sencilla.
    """
    data_input = copy.deepcopy(datos_filtrados)
    datos_divididos = defaultdict(list)

    for data in data_input:
        if data['emission'] == 'NON':
            datos_divididos['no_elastic_data'].append(data)
        else:
            product = data['product']
            datos_divididos[product].append(data)
    
    return datos_divididos

def dividir_por_proyectil_y_target(datos_con_sigma):
  """
  TODO
  """
  data_input = copy.deepcopy(datos_con_sigma)
  data_tag = defaultdict(list)

  for data in data_input:
    tag = (data['projectile'], data['target'])
    data_tag[tag].append(data)
  return data_tag