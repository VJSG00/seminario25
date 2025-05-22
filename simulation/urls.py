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
from calculations.views import rendimiento_ingresar_datos, rendimiento_filtrar_datos, rendimiento_mostrar_resultados, rendimiento_resultados_isotopo
from presentation.views import index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="home"),
    path('rendimiento/', rendimiento_ingresar_datos, name="rendimiento_ingresar"),
    path('rendimiento/seleccionar', rendimiento_filtrar_datos, name="rendimiento_filtrar"),
    path('rendimiento/resultado/target', rendimiento_mostrar_resultados, name="rendimiento_resultado_target"),
    path('rendimiento/resultado/isotopo', rendimiento_resultados_isotopo, name="rendimiento_resultado_isotopo")
    #path('calculations/', name="calculations_test"),
#    path('rendimiento/form/', rendimiento_form, name="rendimiento_form" ),
#    path('rendimiento/test/', rendimiento_test, name="test"),
#    path('rendimiento/test/resultado', rendimiento_form_test, name="test_result"),
#    path('rendimiento/datos/', rendimiento_datos_form, name="rendimiento_seleccionar_datos"),

]
