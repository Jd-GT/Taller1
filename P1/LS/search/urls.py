from django.urls import path
from .views import search_products

urlpatterns = [
    path('', search_products, name='search_products'),
]
