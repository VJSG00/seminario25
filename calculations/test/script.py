# Ejemplo de vista o script:
from calculations.models import Isotope


def get_isotope_info(nuclide):
    try:
        isotope = Isotope.objects.get(symbol=nuclide)
        data = {
            'symbol': isotope.symbol,
            'is_stable': isotope.is_stable,
            'lambda_value': isotope.lambda_value,
            'A': isotope.A,
            'Z': isotope.Z,
            'N': isotope.N,
        }
        return data
    except Isotope.DoesNotExist:
        return None

# Uso:
nuclide = "Te124"
info = get_isotope_info(nuclide)
if info:
    print("Información nuclear:", info)
else:
    print("No se encontró información para el isótopo", nuclide)
