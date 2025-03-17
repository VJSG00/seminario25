import pandas as pd
import numpy as np
import re
from scipy.interpolate import PchipInterpolator

# Aqui ingresan los datos evaluados:

def split_by_reaction(evaluated_data):
    # Creamos un diccionario para agrupar los DataFrames.
    # La clave "no_elastic_data" se usará para las reacciones que contengan "NON"
    grupos = {}
    non_elastic_key = "no_elastic_data"
    grupos[non_elastic_key] = []  # Inicializamos el grupo especial no elástico.

    # Iteramos sobre la lista de DataFrames.
    for df in evaluated_data:
        # Se asume que cada DataFrame tiene una única reacción,
        # por lo que podemos tomar el valor de la primera fila.
        reaction_value = df["reaction"].iloc[0]

        # Si la reacción contiene "NON" (sin importar mayúsculas/minúsculas), la añadimos al grupo no-elástico.
        if re.search(r'NON', reaction_value, re.IGNORECASE):
            grupos[non_elastic_key].append(df)
        else:
            # Sino, se agrupa por la reacción exacta.
            if reaction_value not in grupos:
                grupos[reaction_value] = []
            grupos[reaction_value].append(df)

    return grupos