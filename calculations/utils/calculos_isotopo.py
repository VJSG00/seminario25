import numpy as np
### FUNCIONES DE ASISTENCIA vvv ###----------------------------------------------------------

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

### FUNCIONES DE ASISTENCIA ^^^ ###----------------------------------------------------------

