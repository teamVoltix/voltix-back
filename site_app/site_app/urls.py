"""
URL configuration for site_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from voltix.views import index
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Voltix API",
      default_version='v1',
      description="Documentación de la API para Voltix",
      terms_of_service="https://example.com/terms/",  # Enlace pendiente de definir
      contact=openapi.Contact(email="voltix899@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),  # Permitir acceso a todos
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('voltix/', include('voltix.urls')),
    path('', index),  # La ruta actual de voltix
    #path('', include('voltix.urls')),  # Redirigir la raíz hacia voltix
    path("api/auth/",  include("authentication.urls")),
    path("api/invoices/", include("invoices.urls")),
    path('measurements/', include('measurements.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/profile/', include('userprofile.urls')),
    path('users/', include('users.urls')),

    # Rutas de Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   

]
