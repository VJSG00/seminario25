"""
URL configuration for simulation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from calculations.views import rendimiento_ingresar_datos, rendimiento_filtrar_datos, rendimiento_mostrar_resultados, rendimiento_resultados_isotopo, busqueda_simplificada, simplificada_resultado
from presentation.views import index, rendimiento_api, rendimiento_api_form, rendimiento_api_resultado, reacciones_disponibles


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="home"),
    path('datos/',reacciones_disponibles, name='datos_disponibles' ),

    path('rendimiento/', rendimiento_ingresar_datos, name="rendimiento_ingresar"),
    path('rendimiento/seleccionar', rendimiento_filtrar_datos, name="rendimiento_filtrar"),
    path('rendimiento/resultado/target', rendimiento_mostrar_resultados, name="rendimiento_resultado_target"),
    path('rendimiento/resultado/isotopo', rendimiento_resultados_isotopo, name="rendimiento_resultado_isotopo"),
    
    path('rendimiento/api', rendimiento_api,name="rendimiento_api"),
    path('rendimiento/api/form', rendimiento_api_form, name="rendimiento_api_form" ),
    path('rendimiento/api/resultado', rendimiento_api_resultado, name="rendimiento_api_resultado"),

    path('rendimiento/simplificado', busqueda_simplificada, name="simplificado_ingresar"),
    path('rendimiento/simplificado/resultado', simplificada_resultado, name="simplificado_resultado"), 

]
