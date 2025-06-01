# Imports django
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache

# Otros paquetes
import time
from calculations.utils.validaciones import validar_datos_API
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import uuid
from collections import defaultdict


# Funciones propias
from presentation.utils.calculations.api_endf import conexion_datos_evaluados
from presentation.utils.calculations.api_exfor import flujo_de_datos_experimentales
from .utils.calculations.api_iaea import get_inestable_isotope, get_stable_isotope
from .utils.data_cleaning.experimental import procesar_datos
from .utils.graphs.data import grafico_actividad, interpolation_vs_experimental_data, grafico_secciones_evaluadas, grafico_secciones_experimentales
from .utils.calculations.rendimiento import split_by_reaction
from .utils.elementos import densidad, elementos
from presentation.utils.calculations.workflow import workflow
from presentation.utils.calculations.diferential_equation import actividad, numero_nucleos

# Create your views here.
def index(request):
    return render(request, "presentation/index.html", {})

def rendimiento_api(request):
    return render(request, "presentation/rendimiento_ingresar_datos.html", {})

def rendimiento_api_form(request):
    
    start_time = time.time()

    if request.method == "POST":
        print("\nFormulario recibido\n")
        print(f"request.POST: {request.POST}")

        # Get variables
        tipo_datos = str(request.POST.get('tipo_datos'))
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
        
        errores = validar_datos_API(isotope,current, E_in, E_out, ti, tp)
        if errores:
            mensaje_errores = "<br>".join(errores)
            return HttpResponse(mensaje_errores, status=400)

	    # Esto se tiene que saber por la API
        #isotope_parent_data = get_stable_isotope(isotope)
        #Z_p = isotope_parent_data['Z']
        #A_p = isotope_parent_data['A']
        #rho_p = isotope_parent_data['density']

        #isotope_daughter_data = get_inestable_isotope(A_p, Z_p)

        #Z_d = isotope_daughter_data['Z']
        #Lambda = isotope_daughter_data['Lambda']
        #Lambda = np.log(2)/Lambda
        #rho_I124 = 6.237
        #A = 124
        
        #I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))

        # Ejecutar funciones: Modulo de calculos.
        #-----------------------------------------------------------------------
        # Consulta de datos.
        if tipo_datos=="endf":
            datos_obtenidos=conexion_datos_evaluados(isotope, projectile)
            labels = [df["library"].iloc[0] for df in datos_obtenidos]
            plot_html = grafico_secciones_evaluadas(datos_obtenidos)

        elif tipo_datos=="exfor":
            datos_obtenidos=flujo_de_datos_experimentales(isotope, projectile)
            labels = [df["author"].iloc[0] for df in datos_obtenidos]
            plot_html = grafico_secciones_experimentales(datos_obtenidos)

        else:
            return HttpResponse("Hubo un error con el tipo de dato seleccionado",400)
        
        if not datos_obtenidos:
            return HttpResponse("Hubo un error con la API.",400)

        #-----------------------------------------------------------------------
        # Creamos las categorias para el filtro del usuario.
        emission_groups = defaultdict(list)
        for idx, d in enumerate(datos_obtenidos):
            emission_groups[d["emission"].iloc[0]].append({
                "idx":   idx,
                "label": labels[idx],
            })

        #-----------------------------------------------------------------------
        # Guardamos en cache
        cache_key = str(uuid.uuid4())
        cache.set(cache_key, {
            "isotope": isotope, 
            "projectile": projectile, 
            "current": current,
            "E_in": E_in, 
            "E_out": E_out, 
            "ti": ti, 
            "tp": tp,
            "datos_obtenidos": datos_obtenidos,
            "tipo_datos": tipo_datos,
        }, timeout=1800) # 30 minutos

        context = {
        "evaluated_plot": plot_html,
        "cache_key": cache_key,
        "emission_groups": dict(emission_groups),
        }
        #raise SyntaxError("Error para test")
        return render(request, "presentation/rendimiento_filtrar_datos.html", context)

def rendimiento_api_resultado(request):
    if request.method == "POST":
        
        # Me interesa medir el tiempo de calculo.
        start_time = time.time()

        #--------------------------------------------------------------------------
        # Recupera la clave de la caché
        cache_key = request.POST.get("cache_key")
        data = cache.get(cache_key)
        
        # Validación de si el caché existe.
        if data is None:
            # En caso de que los datos no estén en la caché, puedes reconsultar la API o notificar un error.
            return HttpResponse("Los datos han expirado. Reintente la operación", status=400)
        #--------------------------------------------------------------------------
        # Extraer valores necesarios
        isotope = data["isotope"]
        projectile = data["projectile"]
        current = data["current"]
        E_in = data["E_in"]
        E_out = data["E_out"]
        ti = data["ti"]
        tp = data["tp"]
        datos_obtenidos = data["datos_obtenidos"]
        tipo_datos = data["tipo_datos"]
        #--------------------------------------------------------------------------
        # Obtener datos del target:
        data_isotope = get_stable_isotope(isotope)
        Z_p = data_isotope['Z']
        A_p = data_isotope['A']
        symbol_p = data_isotope['symbol']
        rho_p = densidad[Z_p]
        I_Z = 9.76 + 58.8*(Z_p**(-1.19)) # en eV
        I = I_Z*Z_p
        Bi = 1.0

        ## Separar datos por interacciones.
        data_dict = split_by_reaction(datos_obtenidos)
        #print(data_dict.keys())
#        raise SyntaxError("Error para test")
        #for key, value in data_dict.items():
            #print("\n",key, value)
        ## Calcular constantes de producción por reacción
        rt_dict, rti_dict, E, vtar = workflow(data_dict, E_out, E_in, current, I, rho_p, Z_p, A_p)
        #--->print("\n",rt_dict,"\n",rti_dict)

        ## Solve Differential Equations
        Ni_dict, Np_dict = numero_nucleos(ti, tp, rho_p, A_p, rt_dict, rti_dict, vtar, Bi)
        Ai_dict, Ap_dict = actividad(Ni_dict, Np_dict)
        #print("\n",Ni_dict,"\n", Np_dict)
        #print("\n",Ai_dict,"\n",Ap_dict)
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
            'rt_dict': rt_dict,
            'rti': rti_dict,
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'presentation/rendimiento_api_resultado.html', context)
