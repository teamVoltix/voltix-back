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
from authentication.views import registro_usuario, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('voltix/', include('voltix.urls')),
    path('', index),  # La ruta actual de voltix
    #path('', include('voltix.urls')),  # Redirigir la raíz hacia voltix
    path("auth/",  include("authentication.urls")),
    path('api/auth/', CustomLoginView.as_view(), name='login'),
    path("invoices/", include("invoices.urls")),
    path('measurements/', include('measurements.urls')),
    path('notifications/', include('notifications.urls')),
    path('userprofile/', include('userprofile.urls')),
    path('users/', include('users.urls')),
]


