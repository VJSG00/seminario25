from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache

# Otros paquetes
import time
import uuid
from collections import defaultdict
import copy
from calculations.utils.calculations.integral_ratios import integral_ratios
from calculations.utils.data_cleaning.dividir_productos import dividir_productos
from calculations.utils.validaciones import validar_datos
from scipy.integrate import trapezoid

import numpy as np


# Funciones propias
from .utils.graphs.data import grafico_actividad
from calculations.utils.calculations.activity import numero_nucleos_y_actividad
from calculations.models import Isotope
from .utils.elementos import densidad
from .utils.get_data_db import get_nuclear_properties_by_symbol, get_reactions_by_target_projectile
from calculations.utils.calculations.bethe_bloch import bethe_bloch
from calculations.utils.calculations.sigma_integral import calculo_sigma
from calculations.utils.data_cleaning.procesar_datos import filtrar_datos, interpolar_datos, procesar_datos
from calculations.utils.graphs.evaluated import grafico_secciones_evaluadas
from calculations.utils.graphs.experimental import grafico_secciones_experimentales


def rendimiento_ingresar_datos(request):
    return render(request, "calculations/rendimiento_ingresar_datos.html", {})

def rendimiento_filtrar_datos(request):
    
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

        # Ajustar datos
        E_in *=1e6
        E_out *=1e6
        current *=1e-6

        #-------------------------------------------------------------------------------
        # Validar datos entrantes
        errores = validar_datos(isotope,current, E_in, E_out, ti, tp)
        if errores:
            mensaje_errores = "<br>".join(errores)
            return HttpResponse(mensaje_errores, status=400)
        #-------------------------------------------------------------------------------
        # Consulta al isotopo.
        try: 
            isotopo = Isotope.objects.using('nuclear_properties').get(symbol=isotope)
        
        except Isotope.DoesNotExist: 
            result = "No se encontró el isótopo."
        #-------------------------------------------------------------------------------
        #
        #TODO: Falta validación para comprobar que el isotopo ingresado es pseudo-stable.
        #
        #-------------------------------------------------------------------------------
	    # Usar datos de DB nuclear_properties
        Z_p = isotopo.Z
        A_p = isotopo.A
        # Consultar densidad en elementos.py
        rho_p = densidad[Z_p]

        # Calcular otros datos
        I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))
        Bi = 1

        # Consultar las reacciones a la base de datos. 
        datos_evaluados, datos_experimentales = get_reactions_by_target_projectile(isotope, projectile)
        
        ### Testing ###
        #print(len(datos_evaluados),"\n")
        #print(len(datos_experimentales),"\n")
        ###############

        # Guardar en caché (expira en 30 minutos) 
        cache_key = str(uuid.uuid4())
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
            "I": I,
            "Bi": Bi,
            "datos_evaluados": datos_evaluados,
            #"datos_experimentales": datos_experimentales,
        }, timeout=1800)  # 30 minutos

        # Graficos
        #experimental_plot = grafico_secciones_experimentales(datos_experimentales)
        evaluated_plot = grafico_secciones_evaluadas(datos_evaluados)

        experimental_author = list(data["author"] for data in datos_experimentales)
        evaluated_library = list(data["reference"] for data in datos_evaluados)

        context = {
		#"experimental_plot":experimental_plot,
        "evaluated_plot": evaluated_plot,
	    "experimental_author":experimental_author,
        "evaluated_library": evaluated_library,
        "cache_key": cache_key,
        }

#        return render(request, "calculations/rendimiento_filtrar_datos.html", context)
        return render(request, "calculations/filtrar_nuevo.html", context)

def rendimiento_mostrar_resultados(request):
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
        I = data["I"]
        Bi = data["Bi"]
        #experimental_data = data["datos_experimentales"]
        datos_evaluados = data["datos_evaluados"]

        #Establecemos 
        S=1.0
        #q_e = -1.602e-19 # Coulomb
        
        
        ################################################################################
        # TODO: Filtrar los DataFrames seleccionados
        # experimentales_seleccionados = request.POST.getlist("selected_experimentals")
        # experimentales_seleccionados = [int(i) for i in experimentales_seleccionados]
        # print("No se ha seleccionado datos experimentales")

        ### Datos seleccionados ###
        evaluados_seleccionados = request.POST.getlist("selected_evaluated")
        #print(evaluados_seleccionados)
        evaluados_seleccionados = [int(i) for i in evaluados_seleccionados]

        datos_seleccionados = [datos_evaluados[i] for i in evaluados_seleccionados]
        ################################################################################
        # Consultar datos de los hijos a la API
        
        products = []
        for data in datos_seleccionados:
            products.append(data["product"])

        products = np.unique(products).tolist()

        for isotope in products:
            if isotope == '':
                products.pop(products.index(isotope))

        products = [x.lower().capitalize() for x in products]
        
        # Crear el engine apuntando a nuclear_properties.db
        isotopes = []
        for product in products:
            isotope = get_nuclear_properties_by_symbol(product)
            isotopes.append(isotope)

        for isotope in isotopes:
            for data in datos_seleccionados:
                if data['product'] == isotope.symbol:
                    data['final_isotope'] = isotope

        ################################################################################
        # Procesamos los datos extraidos de la BD
        datos_procesados = procesar_datos(datos_seleccionados)

        datos_interpolados = interpolar_datos(datos_procesados, num_puntos_adicionales=500 )

        datos_filtrados = filtrar_datos(datos_interpolados, E_out, E_in)
        
        ################################################################################
        ### Diferencial para el elemento target ###
        #TODO: MEJORAR ESTO PARA OTRAS PARTICULAS INCIDENTES# Intervalos equisdistantes para integrar
        # Intervalos a integrar
        N = 500
        E = np.linspace(E_out, E_in, N)
        z_p = 1
        dEdx = np.array([bethe_bloch(e, I, rho_p, Z_p, A_p) for e in E ])

        ################################################################################
        # Interpolamos sigma para los puntos de integración. 
        for data in datos_filtrados:
            data['sigma'] = calculo_sigma(data, E).tolist()
        
        ################################################################################
        # Dividimos los datos por producto final
        datos_divididos = dividir_productos(datos_filtrados)

        ################################################################################
        # Integral del volumen
        int_vol = trapezoid(y=1 / dEdx, x=E)
        vtar = S*int_vol
        
        ################################################################################
        # integrales
        datos_con_ratios = integral_ratios(datos_divididos, vtar, z_p, current, dEdx, E)
        #print(datos_con_ratios['I124'][0]['rti'])

        ################################################################################
        # Ecuaciones diferenciales para la actividad:
        datos_finales = numero_nucleos_y_actividad(datos_con_ratios, products, A_p, ti, tp, rho_p, vtar, Bi)
        #print(datos_finales)


        plot_html = grafico_actividad(ti, tp, datos_finales, products)

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
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'calculations/rendimiento_resultado.html', context)

    else:

        return redirect(rendimiento_ingresar_datos)
    
