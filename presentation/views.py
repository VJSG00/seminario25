# Imports django
from django.shortcuts import render, redirect

# Otros paquetes
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Funciones propias
from .utils.calculations.api_iaea import get_inestable_isotope, get_stable_isotope
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
        isotope = str(request.POST.get('isotopo'))
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
        isotope_parent_data = get_stable_isotope(isotope)
        Z_p = isotope_parent_data['Z']
        A_p = isotope_parent_data['A']
        rho_p = isotope_parent_data['density']

        isotope_daughter_data = get_inestable_isotope(A_p, Z_p)

        Z_d = isotope_daughter_data['Z']
        Lambda = isotope_daughter_data['Lambda']
        Lambda = np.log(2)/Lambda
        #rho_I124 = 6.237
        #A = 124
        
        I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))

        # Ejecutar funciones: Modulo de calculos.
        
        ## API
        experimental_data, evaluated_data = conexion_api(isotope, projectile)

        ## Separar datos por interacciones.
        data_dict = split_by_reaction(evaluated_data)

        ## Calcular constantes de producción por reacción
        rt_dict, rti_dict, E, vtar = workflow(data_dict, E_out, E_in, current, I, rho_p, Z_p, A_p)

        ## Solve Differential Equations
        Ni_dict, Np_dict = numero_nucleos(ti, tp, Lambda, rho_p, A_p, rt_dict, rti_dict, vtar, Bi)
        Ai_dict, Ap_dict = actividad(Lambda, Ni_dict, Np_dict)

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
    
def rendimiento_test(request):
    return render(request, "presentation/rendimiento_test.html", {})

def rendimiento_form_test(request):

    if request.method == "POST":
        
        # Medimos el tiempo
        start_time = time.time()

        print("\nFormulario recibido\n")
        print(f"request.POST: {request.POST}")

        # Get variables
        rti = float(request.POST.get('rti'))
        rt = float(request.POST.get('rt'))
        Lambda = float(request.POST.get('Lambda'))
        ti = int(request.POST.get('tiempo_irradiacion'))
        tp = int(request.POST.get('tiempo_enfriamiento'))
        rho = float(request.POST.get('densidad'))
        vtar = float(request.POST.get('volumen'))
        A = int(request.POST.get('A'))
        

        # Ajustamos valores
        rti *= 1e-11
        rt *= 1e-11
        Lambda = np.log(2)/Lambda
        Bi=1
        rt_dict = {"reaction" : [rt]}
        rti_dict = {"reaction": [rti]}

        # Calculos
        Ni_dict, Np_dict = numero_nucleos(ti, tp, Lambda, rho, A, rt_dict, rti_dict, vtar, Bi)
        Ai_dict, Ap_dict = actividad(Lambda, Ni_dict, Np_dict)

        plot_html = grafico_actividad(ti, tp, Ai_dict, Ap_dict)

        # Tiempo de carga
        elapsed_time = time.time() - start_time

        # Contexto de resultados
        context = {
            'plot_html':plot_html,
            'rti':rti,
            'rt':rt,
            'Lambda':Lambda,
            'rho':rho,
            'vtar':vtar,
            'A':A,
            'elapsed_time':elapsed_time
        }

        return render(request, 'presentation/result_test.html', context)


    return redirect(rendimiento_test)