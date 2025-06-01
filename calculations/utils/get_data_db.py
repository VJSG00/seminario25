from calculations.models import Isotope, Reaction
import numpy as np

### FUNCION DE ASISTENCIA vvv #-----------------------------------------------

# Necesito obtener los targets unicos
def obtener_targets_unicos(datos_obtenidos):
  """
  TODO
  Funcion de asistencia.
  """
  targets = []
  for data in datos_obtenidos:
    # if data['target'] not in targets:
      targets.append(data['target'])

  targets = np.unique(targets).tolist()
  return targets

# Necesito obtener los proyectiles unicos
def obtener_proyectiles_unicos(datos_obtenidos):
  """
  TODO
  Funcion de asistencia.
  """
  proyectiles = []
  for data in datos_obtenidos:
    if data['projectile'] not in proyectiles:
      proyectiles.append(data['projectile'])

  proyectiles = np.unique(proyectiles).tolist()
  return proyectiles

### FUNCION DE ASISTENCIA ^^^ #-----------------------------------------------

def get_nuclear_properties_by_symbol(isotopo:str) -> Isotope:
    try:
        isotope = Isotope.objects.using('nuclear_data').get(symbol=isotopo)
        # result = {
        #     'symbol': isotope.symbol,
        #     'is_stable': isotope.is_stable,
        #     'lambda_value': isotope.lambda_value,
        #     'A': isotope.A,
        #     'Z': isotope.Z,
        #     'N': isotope.N,
        # }
        return isotope
    except Isotope.DoesNotExist:
        print("No se encontró el isótopo.")

def get_reactions_by_target_projectile(target_value: str, projectile_value: str, tipo_datos:str):
    """
    Funcion que consulta a la base de datos, las reacciones pedidas por el usuario.
    TODO: Disminuir el codigo de esta funcion, para el caso de datos experimentales
    """
    
    # Filtrar las reacciones por target y projectile en la BD 'reactions'
    reactions_qs = Reaction.objects.using('nuclear_data').filter(
        target=target_value.upper(),
        projectile=projectile_value,
        api=tipo_datos,
    )

    #endf_results = []   # evaluated data
    #exfor_results = []  # experimental data
    resultados = []

    for reaction in reactions_qs:
        # Obtener las mediciones relacionadas para cada reacción
        measurements = reaction.measurements.using('nuclear_data').all()
        
        # Extraer los valores de cada medición en listas
        Energy_values = [m.Energy for m in measurements]
        Sig_values = [m.Sig for m in measurements]
        dSig_values = [m.dSig for m in measurements]
        
        # Crear el diccionario de resultado
        reaction_dict = {
            'id': reaction.id,
            'api_id': reaction.id_api,
            'api': reaction.api,
            'author': reaction.author,
            'reference': reaction.reference,
            'target': reaction.target,
            'projectile': reaction.projectile,
            'product': reaction.product,
            'emission': reaction.emission,
            'reaction': reaction.reaction,
            'Energy': Energy_values,
            'Sig': Sig_values,
            'dSig': dSig_values,
        }

        resultados.append(reaction_dict)

    if tipo_datos=="exfor": #<-- Los datos experimentales carecen de datos no elasticos. Los datos no elasticos los necesitamos para los calculos.
        reactions_qs = Reaction.objects.using('nuclear_data').filter(
            target=target_value.upper(),
            projectile=projectile_value,
            emission="NON",
            api="endf",
        )

        for reaction in reactions_qs:
            # Obtener las mediciones relacionadas para cada reacción
            measurements = reaction.measurements.using('nuclear_data').all()
            
            # Extraer los valores de cada medición en listas
            Energy_values = [m.Energy for m in measurements]
            Sig_values = [m.Sig for m in measurements]
            dSig_values = [m.dSig for m in measurements]
            
            # Crear el diccionario de resultado
            reaction_dict = {
                'id': reaction.id,
                'api_id': reaction.id_api,
                'api': reaction.api,
                'author': reaction.author,
                'reference': reaction.reference,
                'target': reaction.target,
                'projectile': reaction.projectile,
                'product': reaction.product,
                'emission': reaction.emission,
                'reaction': reaction.reaction,
                'Energy': Energy_values,
                'Sig': Sig_values,
                'dSig': dSig_values,
            }
            
            resultados.append(reaction_dict)

    #raise SyntaxError("Error para test")

    # Separamos según el valor de api (convirtiéndolo a minúsculas para evitar problemas de mayúsculas)
    return resultados


### FUNCION DE ASISTENCIA vvv #-----------------------------------------------
def extraer_informacion_consultada(react):
  """
  TODO
  Para no repetir codigo.
  """
  measurements = react.measurements.using('nuclear_data').all()
  react_dict = {
      'id': react.id,
      'api_id': react.id_api,  # Nota: el campo se llama id_api en la BD pero se devuelve como "api_id"
      'api': react.api,
      'author': react.author,
      'reference': react.reference,
      'target': react.target,
      'projectile': react.projectile,
      'product': react.product,
      'level': react.level,
      'emission': react.emission,
      'reaction': react.reaction,
      # Se insertan las listas para las mediciones
      'Energy': [m.Energy for m in measurements],
      'Sig': [m.Sig for m in measurements],
      'dSig': [m.dSig for m in measurements]
  }

  return react_dict
### FUNCION DE ASISTENCIA ^^^ #-----------------------------------------------

def consultar_reaccion_por_producto(product_value: str, projectile_value:str, tipo_datos:str):
  """
  TODO
  TODO: Disminuir el codigo. Es largo por falta de tiempo.
  """

  # Filtrar las reacciones por target y projectile en la BD 'reactions'
  reactions_qs = Reaction.objects.using('nuclear_data').filter(
      product=product_value.upper(),
      api=tipo_datos,
  )

  resultados = []
  for react in reactions_qs:
      # Se arma un diccionario con los campos de la reacción
      react_dict = extraer_informacion_consultada(react)
      resultados.append(react_dict)

  #-----------------------------------------------
  # Necesitamos los datos no elasticos.

  targets = obtener_targets_unicos(resultados)  #<-- Informacion necesaria

  for target in targets:
    reactions_non = Reaction.objects.using('nuclear_data').filter(
        target=target,
        api='endf',
        emission='NON',
    )

    for react in reactions_non:
      react_dict = extraer_informacion_consultada(react)
      resultados.append(react_dict)
  #-----------------------------------------------
  return resultados

def consulta_simplificada(isotope_value:str, libreria_preferida:str):
    """
    TODO
    """
    
    # Validacion
    
    # Filtrar las reacciones por target y projectile en la BD 'reactions'
    reactions_qs = Reaction.objects.using('nuclear_data').filter(
        product=isotope_value.upper(),
        api="endf",
        reference=libreria_preferida,
    )

    resultados = []
    for react in reactions_qs:
        # Se arma un diccionario con los campos de la reacción
        react_dict = extraer_informacion_consultada(react)
        resultados.append(react_dict)


    #-----------------------------------------------
    # Necesitamos los datos no elasticos.

    targets = obtener_targets_unicos(resultados)  #<-- Informacion necesaria

    for target in targets:
        reactions_non = Reaction.objects.using('nuclear_data').filter(
            target=target,
            api='endf',
            reference = libreria_preferida,
            emission='NON',
        )

        for react in reactions_non:
            react_dict = extraer_informacion_consultada(react)
            resultados.append(react_dict)
    #-----------------------------------------------



    return resultados