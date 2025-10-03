"""
URL configuration for LS project.

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
from django.conf import settings
from django.conf.urls.static import static  # Faltaba importar esto

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Aplicaciones web tradicionales
    path('', include('landing.urls')), 
    path('search/', include('search.urls')), 
    path("recomendaciones/", include("chat_recomendaciones.urls")),
    
    # API REST (nuevos endpoints)
    path('', include('api_urls')),
]

# Servir archivos de la carpeta media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
