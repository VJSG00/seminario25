from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache

# Otros paquetes
import time
import uuid
from collections import defaultdict
import copy
from calculations.utils.calculations.integral_ratios import integral_ratios, calculo_ratio_producto
from calculations.utils.data_cleaning.dividir_productos import dividir_productos, dividir_por_proyectil_y_target
from calculations.utils.graphs.activity import grafico_actividad_producto
from calculations.utils.validaciones import validar_datos
from scipy.integrate import trapezoid

import numpy as np


# Funciones propias
from .utils.graphs.data import grafico_actividad
from calculations.utils.calculations.activity import numero_nucleos_y_actividad, numero_nucleos_y_actividad_producto
from calculations.models import Isotope
from .utils.elementos import densidad
from .utils.diccionario_de_cargas import diccionario_de_cargas, diccionario_de_masa_equivalente
from .utils.get_data_db import get_nuclear_properties_by_symbol, get_reactions_by_target_projectile, consultar_reaccion_por_producto, obtener_targets_unicos, obtener_proyectiles_unicos
from calculations.utils.calculations.bethe_bloch import bethe_bloch
from calculations.utils.calculations.sigma_integral import calculo_sigma, filtrar_y_calcular_sigma
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
        tipo_datos = str(request.POST.get('tipo_datos'))
        tipo_busqueda = str(request.POST.get('tipo_busqueda'))
        isotope = (str(request.POST.get('isotopo'))).upper()
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
            isotopo = Isotope.objects.using('nuclear_data').get(symbol=isotope)
        
        except Isotope.DoesNotExist: 
            result = "No se encontró el isótopo."
        #-------------------------------------------------------------------------------
        #
        #TODO: Falta validación para comprobar que el isotopo ingresado es pseudo-stable.
        #
        #-------------------------------------------------------------------------------
	    # Usar datos de DB nuclear_properties
        #Z_p = isotopo.Z
        #A_p = isotopo.A
        # Consultar densidad en elementos.py
        #rho_p = densidad[Z_p]

        # Calcular otros datos
        #I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))
        #Bi = 1
        
        #-------------------------------------------------------------------------------
        # Consultar las reacciones a la base de datos.
        # TODO: Mejorar la logica de este codigo. Se hizo asi por falta de tiempo.
        #-------------------------------------------------------------------------------
        if tipo_busqueda=="Targ":
            if tipo_datos=="Ev":
                datos_obtenidos = get_reactions_by_target_projectile(isotope, projectile,"endf")
                evaluated_labels = [d["reference"] for d in datos_obtenidos]
            elif tipo_datos=="Ex":
                datos_obtenidos = get_reactions_by_target_projectile(isotope, projectile,"exfor")
                evaluated_labels = [d["author"] for d in datos_obtenidos]
            else:
                return HttpResponse("Hubo un error con el tipo de dato seleccionado",400)
            
            #--------------------------------------------------------------------------
            # Contenido para los checkboxes (Se necesita por UX y validaciones)
            # 1) contenido para labels
            
            # 2) esto crea fieldsets distintos. Guardamos en caché.
            emission_groups = defaultdict(list)
            for idx, d in enumerate(datos_obtenidos):
                emission_groups[d["emission"]].append({
                    "idx":   idx,
                    "label": evaluated_labels[idx],
                })

            #testing
            #print(f'\nemission_groups:{emission_groups}\n')

            #--------------------------------------------------------------------------

        elif tipo_busqueda=="Prod":
            if tipo_datos=="Ev":
                datos_obtenidos = consultar_reaccion_por_producto(isotope, projectile, "endf")
                evaluated_labels = [d["reference"] for d in datos_obtenidos]
            elif tipo_datos=="Ex":
                datos_obtenidos = consultar_reaccion_por_producto(isotope, projectile, "exfor")    
                evaluated_labels = [d["author"] for d in datos_obtenidos]       

            # Contenido para los checkboxes (Se necesita por UX y validaciones)
            proyectiles = obtener_proyectiles_unicos(datos_obtenidos)
            targets = obtener_targets_unicos(datos_obtenidos)            
            # TODO: Mejorar este codigo.
            grupos_datos = defaultdict(list)
            for proyectil in proyectiles:
              for target in targets:
                for i, data in enumerate(datos_obtenidos):
                    emission = data['emission']
                    if data['projectile'] == proyectil and data['target'] == target:
                        grupos_datos[(proyectil, target,emission)].append({
                            'i': i,
                            'label': evaluated_labels[i],
                        })

        else:
            return HttpResponse("Hubo un error con el tipo de busqueda seleccionado",400)

        # Validacion adicional
        if not datos_obtenidos:
            return HttpResponse("La reaccion solicitada no se encuentra en la base de datos.",400)

        #datos_evaluados, datos_experimentales = get_reactions_by_target_projectile(isotope, projectile)
        
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
            #"Z_p": Z_p, 
            #"A_p": A_p,
            #"rho_p": rho_p,
            #"I": I,
            #"Bi": Bi,
            "datos_obtenidos": datos_obtenidos,
            "tipo_busqueda": tipo_busqueda,
            #"datos_experimentales": datos_experimentales,
        }, timeout=1800)  # 30 minutos
        # Graficos
        #raise SyntaxError("Error para test")

        #experimental_plot = grafico_secciones_experimentales(datos_experimentales)
        evaluated_plot = grafico_secciones_evaluadas(datos_obtenidos, tipo_datos)

        #experimental_author = list(data["author"] for data in datos_experimentales)
        #evaluated_library = list(data["reference"] for data in datos_evaluados)


        context = {
		#"experimental_plot":experimental_plot,
        "evaluated_plot": evaluated_plot,
	    #"experimental_author":experimental_author,
        #"evaluated_library": evaluated_library,
        "cache_key": cache_key,
        }

#        return render(request, "calculations/rendimiento_filtrar_datos.html", context)
        if tipo_busqueda=="Targ":
            context["emission_groups"] = dict(emission_groups)
            return render(request, "calculations/filtrar_busqueda_target.html", context)
        elif tipo_busqueda=="Prod":
            context["grupos_datos"] = dict(grupos_datos)
            return render(request, "calculations/filtrar_busqueda_isotopo.html", context)

def rendimiento_mostrar_resultados(request):
    if request.method == "POST":
       
        # Me interesa medir el tiempo de calculo.
        start_time = time.time()

        #--------------------------------------------------------------------------
        # Recupera la clave de la caché
        cache_key = request.POST.get("cache_key")
        data = cache.get(cache_key)
        
        # Validación de si el caché existe.
        if data is None:
            # En caso de que los datos no estén en la caché,
            # puedes reconsultar la API o notificar un error.
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
        #Z_p = data["Z_p"]
        #A_p = data["A_p"]
        #rho_p = data["rho_p"]
        #I = data["I"]
        #Bi = data["Bi"]
        #experimental_data = data["datos_experimentales"]
        datos_obtenidos = data["datos_obtenidos"]
        tipo_busqueda = data["tipo_busqueda"]
        
        #--------------------------------------------------------------------------
        isotopo = Isotope.objects.using('nuclear_data').get(symbol=isotope)
        # Consultamos datos necesarios.
        Z_p = isotopo.Z
        A_p = isotopo.A
        # Consultar densidad en elementos.py
        rho_p = densidad[Z_p]

        # Calcular otros datos
        I = Z_p*(9.76 + 58.8*(Z_p**(-1.19)))
        Bi = 1
        
        #--------------------------------------------------------------------------
        #Establecemos 
        S=1.0
        #q_e = -1.602e-19 # Coulomb
        
        ################################################################################
        # TODO: Filtrar tambien los experimentales.
        # experimentales_seleccionados = request.POST.getlist("selected_experimentals")
        # experimentales_seleccionados = [int(i) for i in experimentales_seleccionados]
        # print("No se ha seleccionado datos experimentales")

        #--------------------------------------------------------------------------
        # 1) saber cuales emisisones existen.
        if tipo_busqueda == "Targ":
            emission_keys = list({ d["emission"] for d in datos_obtenidos })
            #print(f'\nemission_keys:{emission_keys}\n')
        elif tipo_busqueda == "Prod":
            emission_keys = list({(d["projectile"],d["target"],d["emission"]) for d in datos_obtenidos })

        # 2) recuperar los indices marcados.
        todos_idxs = []
        for em in emission_keys:
            raw = request.POST.getlist(f"selected_{em}")  # ej. ['2','7']
            todos_idxs.extend(int(i) for i in raw)


        # 3) ordenar indices. El orden es importante despues.
            arr = np.array(todos_idxs, dtype=int)
            arr.sort()
            evaluados_seleccionados = arr.tolist()
        


        # testing
        #print(f'\nevaluados seleccionados:{evaluados_seleccionados}\n')

        ### Datos seleccionados ###
        #evaluados_seleccionados = request.POST.getlist("selected_evaluated")
        #print(evaluados_seleccionados)
        #evaluados_seleccionados = [int(i) for i in evaluados_seleccionados]

        datos_seleccionados = [datos_obtenidos[i] for i in evaluados_seleccionados]
        ################################################################################
        # Consultar datos de los hijos a la API
        
        products = []
        for data in datos_seleccionados:
            products.append(data["product"])

        products = np.unique(products).tolist()

        for isotope in products:
            if isotope == '':
                products.pop(products.index(isotope))

        products = [x for x in products]

        # testing
        #print(f"productos: {products}")
        
        # Crear el engine apuntando a nuclear_properties.db
        isotopes = []
        for product in products:
            isotope = get_nuclear_properties_by_symbol(product)
            isotopes.append(isotope)

        for isotope in isotopes:
            for data in datos_seleccionados:
                if data['product'] == isotope.symbol: #<-- Una BD tiene los symbol en mayus (reactions_data.db)
                    data['final_isotope'] = isotope

        #testing
        #print(f"isotopos: {isotopes}")
        #raise SyntaxError("Error para test")


        ################################################################################
        # Procesamos los datos extraidos de la BD
        datos_procesados = procesar_datos(datos_seleccionados)

        datos_interpolados = interpolar_datos(datos_procesados, num_puntos_adicionales=500 )

        datos_filtrados = filtrar_datos(datos_interpolados, E_out, E_in)

        ################################################################################
        ### Diferencial para el elemento target ###
        #TODO: MEJORAR ESTO PARA OTRAS PARTICULAS INCIDENTES# Intervalos equisdistantes para integrar
        # Intervalos a integrar
        m_0 = diccionario_de_masa_equivalente[projectile]

        z_p = diccionario_de_cargas[projectile]

        N = 500
        E = np.linspace(E_out, E_in, N)
        dEdx = np.array([bethe_bloch(e, I, rho_p, Z_p, A_p, z_p, m_0) for e in E ])

        ################################################################################
        # Interpolamos sigma para los puntos de integración. 
        datos_con_sigma = filtrar_y_calcular_sigma(datos_filtrados, E)

        ################################################################################
        # Dividimos los datos por producto final
        datos_divididos = dividir_productos(datos_con_sigma)
        #print(f"\nDatos divididos: {datos_divididos}\n")

        ################################################################################
        # Integral del volumen
        int_vol = trapezoid(y=1 / dEdx, x=E)
        vtar = S*int_vol
        
        ################################################################################
        # integrales
        datos_con_ratios = integral_ratios(datos_divididos, vtar, z_p, current, dEdx, E)
        #print(f"\ndatos con ratios: {datos_con_ratios.keys()}\n")
        
        ################################################################################
        # Ecuaciones diferenciales para la actividad:
        datos_finales = numero_nucleos_y_actividad(datos_con_ratios, products, A_p, ti, tp, rho_p, vtar, Bi)
        #print(len(datos_finales))
        #print(f"\ndatos finales: {datos_finales}\n")


        plot_html = grafico_actividad(ti, tp, datos_finales, products)

        # Tiempo de carga:
        elapsed_time = time.time() - start_time

        # Contexto para resultados en render
        context = {
            'isotope': isotope,
            'projectile': projectile,
            'current': current*1e6,
            'E_in': E_in,
            'E_out': E_out,
            'vtar':vtar,
            'ti': ti,
            'tc': tp,
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'calculations/rendimiento_resultado_target.html', context)

    else:

        return redirect(rendimiento_ingresar_datos)
    
def rendimiento_resultados_isotopo(request):
    
    if request.method == "POST":
   
        # Me interesa medir el tiempo de calculo.
        start_time = time.time()

        #--------------------------------------------------------------------------
        # Recupera la clave de la caché
        cache_key = request.POST.get("cache_key")
        data = cache.get(cache_key)
        
        # Validación de si el caché existe.
        if data is None:
            # En caso de que los datos no estén en la caché,
            # puedes reconsultar la API o notificar un error.
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
        #experimental_data = data["datos_experimentales"]
        datos_obtenidos = data["datos_obtenidos"]
        tipo_busqueda = data["tipo_busqueda"]
        
        #--------------------------------------------------------------------------
        #Establecemos 
        S=1.0
        #q_e = -1.602e-19 # Coulomb
        
        ################################################################################
        # TODO: Filtrar tambien los experimentales.
        # experimentales_seleccionados = request.POST.getlist("selected_experimentals")
        # experimentales_seleccionados = [int(i) for i in experimentales_seleccionados]
        # print("No se ha seleccionado datos experimentales")

        #--------------------------------------------------------------------------
        # 1) saber cuales emisisones existen.
        emission_keys = list({(d["projectile"],d["target"],d["emission"]) for d in datos_obtenidos })

        # 2) recuperar los indices marcados.
        todos_idxs = []
        for em in emission_keys:
            raw = request.POST.getlist(f"selected_{em}")  # ej. ['2','7']
            todos_idxs.extend(int(i) for i in raw)


        # 3) ordenar indices. El orden es importante despues.
            arr = np.array(todos_idxs, dtype=int)
            arr.sort()
            evaluados_seleccionados = arr.tolist()
        


        # testing
        #print(f'\nevaluados seleccionados:{evaluados_seleccionados}\n')

        ### Datos seleccionados ###
        #evaluados_seleccionados = request.POST.getlist("selected_evaluated")
        #print(evaluados_seleccionados)
        #evaluados_seleccionados = [int(i) for i in evaluados_seleccionados]

        datos_seleccionados = [datos_obtenidos[i] for i in evaluados_seleccionados]
        ################################################################################
        # Consultar datos de los hijos a la API
        
        #testing
        #print(f"isotopos: {isotopes}")
        #raise SyntaxError("Error para test")


        ################################################################################
        # Procesamos los datos extraidos de la BD
        datos_procesados = procesar_datos(datos_seleccionados)

        datos_interpolados = interpolar_datos(datos_procesados, num_puntos_adicionales=500 )

        datos_filtrados = filtrar_datos(datos_interpolados, E_out, E_in)
        
        N = 500
        E = np.linspace(E_out, E_in, N)

        datos_con_sigma = filtrar_y_calcular_sigma(datos_filtrados, E)

        datos_divididos = dividir_por_proyectil_y_target(datos_con_sigma)

        pares_de_datos = list(datos_divididos.keys())
        for par in pares_de_datos:
            if len(datos_divididos[par]) < 2:
                datos_divididos.pop(par)
        ################################################################################
        # Calculos 
        isotopo = Isotope.objects.using('nuclear_data').get(symbol=isotope)

        datos_con_ratios = calculo_ratio_producto(datos_divididos, current, E_in, E_out)
        
        half_life= isotopo.half_life
        datos_finales = numero_nucleos_y_actividad_producto(datos_con_ratios, ti, tp, half_life)

        plot_html = grafico_actividad_producto(datos_finales, ti, tp)

        # Tiempo de carga:
        elapsed_time = time.time() - start_time

        # Contexto para resultados en render
        context = {
            'isotope': isotope,
            'projectile': projectile,
            'current': current*1e6,
            'E_in': E_in,
            'E_out': E_out,
            'ti': ti,
            'tc': tp,
            'plot_html': plot_html,
            'elapsed_time': elapsed_time
        }

        return render(request, 'calculations/rendimiento_resultado_producto.html', context)

    else:

        return redirect(rendimiento_ingresar_datos)
