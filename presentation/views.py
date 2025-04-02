# Imports django
from django.shortcuts import render, redirect
from django.core.cache import cache

# Otros paquetes
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import uuid

# Funciones propias
from .utils.calculations.api_iaea import get_inestable_isotope, get_stable_isotope
from .utils.calculations.api import conexion_api
from .utils.data_cleaning.experimental import procesar_datos
from .utils.graphs.data import grafico_actividad, interpolation_vs_experimental_data, grafico_secciones_evaluadas, grafico_secciones_experimentales
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
        rt_dict, rti_dict, rt_all_dict, E, vtar = workflow(data_dict, E_out, E_in, current, I, rho_p, Z_p, A_p)

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
            'rt_all': rt_all_dict,
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

def rendimiento_datos_form(request):
    return render(request, "presentation/rendimiento_seleccionar_datos.html", {})

def rendimiento_seleccionar_datos(request):
    
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

	    # Esto se tiene que saber por la API
        isotope_parent_data = get_stable_isotope(isotope)
        Z_p = isotope_parent_data['Z']
        A_p = isotope_parent_data['A']
        rho_p = isotope_parent_data['density']
        #Consulta a la API de la hija
        isotope_daughter_data = get_inestable_isotope(A_p, Z_p)

        Z_d = isotope_daughter_data['Z']
        Lambda = isotope_daughter_data['Lambda']
        Lambda = np.log(2)/Lambda
        #rho_I124 = 6.237
        #A = 124
        I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))
        Bi = 1

        # API
        experimental_data, evaluated_data = conexion_api(isotope, projectile)

        # Generar una clave única para la caché
        cache_key = str(uuid.uuid4())
        print(cache_key)
        
        # Guardar en caché (expira en 30 minutos) 
        cache.set(cache_key, {
            "isotope": isotope, 
            "projectile": projectile, 
            "current": current,
            "E_in": E_in, 
            "E_out": E_out, 
            "ti": ti, 
            "tp": tp,
            "Z_p": Z_p, 
            "A_p": A_p,
            "rho_p": rho_p,
            "Z_d": Z_d, 
            "Lambda": Lambda, 
            "I": I,
            "Bi": Bi,
            "experimental_data": experimental_data,
            "evaluated_data" : evaluated_data
        }, timeout=1800)  # 30 minutos

        # Graficos
        experimental_plot = grafico_secciones_experimentales(experimental_data)
        evaluated_plot = grafico_secciones_evaluadas(evaluated_data)

        experimental_author = list(df["author"][0] for df in experimental_data)
        evaluated_library = list(df["library"][0] for df in evaluated_data)

        context = {
		"experimental_plot":experimental_plot,
        "evaluated_plot": evaluated_plot,
		"experimental_author":experimental_author,
        "evaluated_library": evaluated_library,
        "cache_key": cache_key,
        }

        return render(request, "presentation/rendimiento_datos.html", context)

def rendimiento_mostrar_datos(request):
    if request.method == "POST":
       
        start_time = time.time()

        # Recupera la clave de la caché
        cache_key = request.POST.get("cache_key")
        data = cache.get(cache_key)


        if data is None:
            # En caso de que los datos no estén en la caché,
            # puedes reconsultar la API o notificar un error.
            return render(request, "error.html", {"mensaje": "Los datos han expirado, por favor intente nuevamente."})
        
        # Extraer valores necesarios
        isotope = data["isotope"]
        projectile = data["projectile"]
        current = data["current"]
        E_in = data["E_in"]
        E_out = data["E_out"]
        ti = data["ti"]
        tp = data["tp"]
        Z_p = data["Z_p"]
        A_p = data["A_p"]
        rho_p = data["rho_p"]
        Z_d = data["Z_d"]
        Lambda = data["Lambda"]
        I = data["I"]
        Bi = data["Bi"]
        experimental_data = data["experimental_data"]
        evaluated_data = data["evaluated_data"]
        
        # experimentales_seleccionados = request.POST.getlist("selected_experimentals")
        # experimentales_seleccionados = [int(i) for i in experimentales_seleccionados]
        # print("No se ha seleccionado datos experimentales")

        evaluados_seleccionados = request.POST.getlist("selected_evaluated")
        evaluados_seleccionados = [int(i) for i in evaluados_seleccionados]


        # Filtrar los DataFrames seleccionados
        datos_seleccionados = [evaluated_data[i] for i in evaluados_seleccionados]
        
        # Aquí puedes aplicar análisis, cálculos o procesar datos_seleccionados
        ## Separar datos por interacciones.
        data_dict = split_by_reaction(datos_seleccionados)
        
        ## Calcular constantes de producción por reacción
        rt_dict, rti_dict, rt_all_dict, E, vtar = workflow(data_dict, E_out, E_in, current, I, rho_p, Z_p, A_p)

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
            'rt_all': rt_all_dict,
            'rti': rti_dict,
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'presentation/rendimiento_result.html', context)

    else:

        return redirect(rendimiento)
    