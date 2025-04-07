from calculations.models import Isotope, Reaction


def get_nuclear_properties_by_symbol(isotopo:str) -> Isotope:
    try:
        isotope = Isotope.objects.using('nuclear_properties').get(symbol=isotopo)
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

def get_reactions_by_target_projectile(target_value: str, projectile_value: str):
    
    # Filtrar las reacciones por target y projectile en la BD 'reactions'
    reactions_qs = Reaction.objects.using('reactions').filter(
        target=target_value.upper(),
        projectile=projectile_value
    )

    endf_results = []   # evaluated data
    exfor_results = []  # experimental data

    for reaction in reactions_qs:
        # Obtener las mediciones relacionadas para cada reacción
        measurements = reaction.measurements.using('reactions').all()
        
        # Extraer los valores de cada medición en listas
        E_ev_values = [m.E_ev for m in measurements]
        Sig_b_values = [m.Sig_b for m in measurements]
        dSig_b_values = [m.dSig_b for m in measurements]
        
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
            'E,ev': E_ev_values,
            'Sig,b': Sig_b_values,
            'dSig,b': dSig_b_values,
        }

        # Separamos según el valor de api (convirtiéndolo a minúsculas para evitar problemas de mayúsculas)
        if reaction.api == 'endf':
            endf_results.append(reaction_dict)
        elif reaction.api == 'exfor':
            exfor_results.append(reaction_dict)
        else:
            continue
    
    return endf_results, exfor_results
