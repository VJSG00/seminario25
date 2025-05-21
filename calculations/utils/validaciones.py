from calculations.models import Isotope

def validar_datos(isotopo, corriente, E_in, E_out, ti, tp):
    """
    Valida las variables recibidas.
    """
    errores = []

    # --- Validaciones Energía ---
    if E_in <= E_out:
        errores.append("La energía de entrada debe ser mayor a la energía de salida.")
    if E_in <= 0 or E_out <= 0:
        errores.append("Las energías deben ser mayores que cero.")
    if E_in > 50e6 or E_out > 50e6:
        errores.append("Las energías no pueden ser mayores a 50.")

    # --- Validaciones Tiempo ---
    if ti <= 0 or tp <= 0:
        errores.append("Los tiempos deben ser positivos.")
    if ti > 72 or tp > 72:
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
