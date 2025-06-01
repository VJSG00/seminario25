from calculations.models import Isotope, Reaction

def validar_datos_con_BD(isotopo, corriente, E_in, E_out, ti, tp):
    """
    Valida las variables recibidas.
    Se realiza una comprobacion en la Base de Datos.
    """
    errores = []

    # --- Validaciones Energía ---
    if E_in <= E_out:
        errores.append("La energía de entrada debe ser mayor a la energía de salida.")
    if E_in <= 0 or E_out <= 0:
        errores.append("Las energías deben ser mayores que cero.")
    if E_in > 30e6 or E_out > 30e6:
        errores.append("Las energías no pueden ser mayores a 50.")

    # --- Validaciones Tiempo ---
    if ti <= 0 or tp <= 0:
        errores.append("Los tiempos deben ser positivos.")
    if ti > 720 or tp > 720:
        errores.append("Los tiempos no deben ser mayores a 3 días (72 horas cada uno).")

    # --- Validaciones Corriente ---
    if corriente <= 0:
        errores.append("La corriente debe ser positiva.")
    if corriente >= 1000:
        errores.append("La corriente debe valer menos de 1000.")

        # --- Validación del Isótopo ---
    try:
        # Buscamos el isótopo usando la base de datos "nuclear_properties"
        Isotope.objects.using('nuclear_data').get(symbol=isotopo)
    except Isotope.DoesNotExist:
        errores.append(f"No se encontró el isótopo: {isotopo}")

    return errores

def validar_datos_API(isotopo, corriente, E_in, E_out, ti, tp):
    """
    Valida en servidor el valor de las variables recibidas.
    """
    errores = []

    # --- Validaciones Energía ---
    if E_in <= E_out:
        errores.append("La energía de entrada debe ser mayor a la energía de salida.")
    if E_in <= 0 or E_out <= 0:
        errores.append("Las energías deben ser mayores que cero.")
    if E_in > 30e6 or E_out > 30e6:
        errores.append("Las energías no pueden ser mayores a 50.")

    # --- Validaciones Tiempo ---
    if ti <= 0 or tp <= 0:
        errores.append("Los tiempos deben ser positivos.")
    if ti > 720 or tp > 720:
        errores.append("Los tiempos no deben ser mayores a 3 días (72 horas cada uno).")

    # --- Validaciones Corriente ---
    if corriente <= 0:
        errores.append("La corriente debe ser positiva.")
    if corriente >= 1000:
        errores.append("La corriente debe valer menos de 1000.")

    return errores

def existe_informacion(isotope_value: str, libreria_preferida: str, tipo_busqueda: str) -> bool:
    """
    Valida que haya cualquier informacion de la reaccion en la base de datos.

    Args:
        isotope_value (str): El valor del isótopo a buscar (producto o blanco).
        libreria_preferida (str): La librería de referencia preferida.
        tipo_busqueda (str): El tipo de búsqueda ("Prod" para producto, "Targ" para blanco).

    Returns:
        bool: True si existe información que coincide con los criterios, False en caso contrario.

    Raises:
        ValueError: Si el tipo de búsqueda no es válido.
    """

    if tipo_busqueda == "Prod":
        return Reaction.objects.using('nuclear_data').filter(
            product=isotope_value.upper(),
            api="endf",
            # reference=libreria_preferida,
        ).exists()
    elif tipo_busqueda == "Targ":
        return Reaction.objects.using('nuclear_data').filter(
            target=isotope_value.upper(),
            api="endf",
            # reference=libreria_preferida,
        ).exists()
    else:
        raise ValueError("Tipo de búsqueda no válido. Debe ser 'Prod' o 'Targ'.")