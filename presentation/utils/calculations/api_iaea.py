import requests
import pandas as pd
import io
import numpy as np
from ..elementos import elementos, densidad   # Asegúrate de que el archivo densidad.py define el diccionario "densidad"

def get_isotope_data(nuclide):
    """
    Consulta la API del IAEA para extraer datos de decaimiento de un isótopo
    y retorna los datos relevantes junto con la densidad basada en el número Z.
    
    Parámetros:
      nuclide (str): Nombre del isótopo (ejemplo: "Cu64").
    
    Retorna:
      dict: Diccionario con las variables de interés y la densidad asociada al valor Z.
    """
    url = "https://nds.iaea.org/relnsd/v1/data"
    rad_types = ["e", "a", "bp", "bm", "g", "x"]

    response_list = []
    for rad in rad_types:
        args = {"fields": "decay_rads", "nuclides": nuclide, "rad_types": rad}
        r = requests.get(url, params=args)
        response_list.append(r)

    content_list = []
    for response in response_list:
        decoded = response.content.decode('utf-8')
        if len(decoded) >= 4:
            content_list.append(decoded)

    df_list = []
    for content in content_list:
        csv_data = io.StringIO(content)
        df = pd.read_csv(csv_data)
        df_list.append(df)

    # Inicializamos las variables que se extraerán de los datos.
    Decay = []
    Decay_percent = []
    Lambda = []
    N = []
    Z = []
    A = []
    symbol = []

    for i in range(len(content_list)):
        Decay.extend(df_list[i]['decay'].unique().tolist())
        Decay_percent.extend(df_list[i]['decay_%'].unique().tolist())
        Lambda.extend(df_list[i]['half_life_sec'].unique().tolist())
        n_val = df_list[i]['p_n'].unique().tolist()[0]
        z_val = df_list[i]['p_z'].unique().tolist()[0]
        N.append(n_val)
        Z.append(z_val)
        A.append(z_val + n_val)
        symbol.append(df_list[i]['p_symbol'].unique().tolist()[0])

    # Convertir y eliminar duplicados
    Decay = np.unique(Decay).tolist()
    Decay_percent = np.unique(Decay_percent).tolist()
    Lambda = int(np.unique(Lambda)[0])
    N_val = int(np.unique(N)[0])
    Z_val = int(np.unique(Z)[0])
    A_val = int(np.unique(A)[0])
    symbol_val = str(np.unique(symbol)[0])

    # Accedemos a la densidad utilizando el valor Z obtenido.
    density = densidad.get(Z_val, None)  # Devuelve None si Z_val no se encuentra en el diccionario

    # Convertir a horas
    Lambda *= 1/3600

    # Se retornan todos los datos en un diccionario.
    return {
        'Decay': Decay,
        'Decay_percent': Decay_percent,
        'Lambda': Lambda,
        'N': N_val,
        'Z': Z_val,
        'A': A_val,
        'symbol': symbol_val,
        'density': density
    }

def get_stable_isotope(nuclide):
    """
    Similar a get_isotope_data pero para isótopos estables.
    Se omiten los datos de decaimiento (Decay, Decay_percent y Lambda).
    
    Parámetros:
      nuclide (str): Nombre del isótopo estable (ejemplo: "Cu64").
    
    Retorna:
      dict: Diccionario con los datos:
            - N, Z, A, symbol y density (densidad basada en Z)
    """
    url = "https://nds.iaea.org/relnsd/v1/data"
    rad_types = ["e", "a", "bp", "bm", "g", "x"]

    response_list = []

    args = {"fields": "levels", "nuclides": nuclide}
    r = requests.get(url, params=args)
    response_list.append(r)

    content_list = []
    for response in response_list:
        decoded = response.content.decode('utf-8')
        if len(decoded) >= 4:
            content_list.append(decoded)

    df_list = []
    for content in content_list:
        csv_data = io.StringIO(content)
        df = pd.read_csv(csv_data)
        df_list.append(df)

    # Se extraen únicamente los datos estructurales: N, Z, A y symbol
    N = []
    Z = []
    A = []
    symbol = []

    for i in range(len(content_list)):
        n_val = df_list[i]['n'].unique().tolist()[0]
        z_val = df_list[i]['z'].unique().tolist()[0]
        N.append(n_val)
        Z.append(z_val)
        A.append(z_val + n_val)
        symbol.append(df_list[i]['symbol'].unique().tolist()[0])

    N_val = int(np.unique(N)[0])
    Z_val = int(np.unique(Z)[0])
    A_val = int(np.unique(A)[0])
    symbol_val = str(np.unique(symbol)[0])

    density = densidad.get(Z_val, None)

    return {
        'N': N_val,
        'Z': Z_val,
        'A': A_val,
        'symbol': symbol_val,
        'density': density
    }

def get_inestable_isotope(A_p, Z_p):
    """
    Para un isótopo inestable, se parte del padre utilizando:
      - A_p: número de masa del padre (se mantiene)
      - Z_p: número atómico del padre
    Se calcula el isótopo de la hija con:
      Z_d = Z_p + 1  y  A_d = A_p.
    Luego se busca en el diccionario 'elementos' el símbolo que corresponde a Z_d.
    Se forma el isótopo como 'símbolo + A_p' y se consulta la API con get_isotope_data.
    
    Parámetros:
      A_p (int): Número de masa del padre.
      Z_p (int): Número atómico del padre.
    
    Retorna:
      dict: Los datos obtenidos por get_isotope_data(nuclide) para el isótopo de la hija.
    """
    # Calcular el número atómico del elemento hija
    Z_d = Z_p + 1

    # Buscar el símbolo del elemento hija usando el diccionario 'elementos'
    symbol_d = None
    for sym, atomic_number in elementos.items():
        if atomic_number == Z_d:
            symbol_d = sym
            break

    if symbol_d is None:
        raise ValueError(f"No se encontró símbolo para el número atómico {Z_d} en el diccionario elementos.")

    # Formar el nombre del isótopo de la hija (ejemplo: "Zn64")
    nuclide = f"{symbol_d}{A_p}"

    # Se obtienen y retornan los datos de la API usando get_isotope_data
    return get_isotope_data(nuclide)

