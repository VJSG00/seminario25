import numpy as np # Asegúrate de tener esto al principio de tu views.py

def formatear_numpy(value, precision=8, is_scientific=True, conversion_power=None):
    """
    Formatea un número (incluyendo np.float64) a un string con la precisión deseada.
    Puede aplicar una conversión de potencia antes del formateo.

    Args:
        value: El número a formatear (puede ser float, np.float64, u otro).
        precision (int): El número de dígitos después del punto decimal.
        is_scientific (bool): Si es True, formatea en notación científica (E).
                              Si es False, formatea en punto fijo (f).
        conversion_power (int, optional): Si se proporciona, el número se multiplica
                                          por 10 elevado a esta potencia antes del formateo.
                                          Ej: conversion_power=6 multiplica por 1e6.

    Returns:
        str: El número formateado como string.
        str: El valor original convertido a string si no es un tipo numérico válido.
    """
    try:
        # Intentar convertir a float para asegurar que es un número
        num = float(value)

        # Aplicar la conversión de potencia si se especifica
        if conversion_power is not None:
            num *= (10 ** conversion_power)

        if is_scientific:
            return f"{num:.{precision}E}" # Notación científica (E mayúscula)
        else:
            return f"{num:.{precision}f}" # Notación de punto fijo
    except (ValueError, TypeError):
        # Si el valor no es un número o es None, devuelve su representación string
        return str(value)