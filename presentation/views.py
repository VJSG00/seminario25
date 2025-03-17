# Imports django
from django.shortcuts import render, redirect

# Otros paquetes
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Funciones propias
from .utils.calculations.api import conexion_api
from .utils.data_cleaning.experimental import procesar_datos
from .utils.graphs.data import grafico_actividad, interpolation_vs_experimental_data
from .utils.calculations.rendimiento import split_by_reaction
from presentation.utils.calculations.workflow import workflow
from presentation.utils.calculations.diferential_equation import actividad, numero_nucleos

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, "presentation/index.html", {})

def rendimiento(request):
    return render(request, "presentation/rendimiento.html", {})

def rendimiento_form(request):
    
    start_time = time.time()

    if request.method == "POST":
        print("\nFormulario recibido\n")
        print(f"request.POST: {request.POST}")

        # Get variables
        isotope = request.POST.get('isotopo')
        projectile = request.POST.get('proyectil')
        current = float(request.POST.get('corriente'))
        E_in = float(request.POST.get('energia_entrada'))
        E_out = float(request.POST.get('energia_salida'))
        ti = int(request.POST.get('tiempo_irradiacion'))
        tp = int(request.POST.get('tiempo_enfriamiento'))

        # Datos
        E_in *=1e6
        E_out *=1e6
        current *=1e-6
        Bi=1

	    # Esto se tiene que saber por la API
        Z = 52
        lam_I124 = np.log(2)/100.224
        rho_I124 = 6.237
        A = 124



        # Ejecutar funciones: Modulo de calculos.
        
        ## API
        experimental_data, evaluated_data = conexion_api(isotope, projectile)

        ## Separar datos por interacciones.
        data_dict = split_by_reaction(evaluated_data)

        ## Calcular constantes de producción por reacción
        rt_dict, rti_dict, E, vtar = workflow(data_dict, E_out, E_in, current, rho_I124, Z, A)

        ## Solve Differential Equations
        Ni_dict, Np_dict = numero_nucleos(ti, tp, lam_I124, rho_I124, A, rt_dict, rti_dict, vtar, Bi)
        Ai_dict, Ap_dict = actividad(lam_I124, Ni_dict, Np_dict)

        plot_html = grafico_actividad(ti, tp, Ai_dict, Ap_dict)

        # Tiempo de carga:
        elapsed_time = time.time() - start_time

        # Contexto para resultados en render
        context = {
            'isotope': isotope,
            'projectile': projectile,
            'current': current,
            'E_in': E_in,
            'E_out': E_out,
            'ti': ti,
            'tc': tp,
            'rt': rt_dict,
            'rti': rti_dict,
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'presentation/rendimiento_result.html', context)

    else:

        return redirect(rendimiento)