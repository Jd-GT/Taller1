"""
API REST - URLs Configuration

Este archivo configura las rutas para la API REST usando
Django REST Framework routers y ViewSets.

Características implementadas:
- Rutas automáticas para ViewSets
- Versionado de API (v1)
- Documentación automática con Swagger/ReDoc
- Endpoints organizados por funcionalidad
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from search.api_views import ProductViewSet, AIRecommendationViewSet


# Configurar router automático para ViewSets
router = DefaultRouter()

# Registrar ViewSets en el router
router.register(
    r'products', 
    ProductViewSet, 
    basename='product'
)

router.register(
    r'recommendations', 
    AIRecommendationViewSet, 
    basename='recommendation'
)

# URLs de la API
api_urlpatterns = [
    # Incluir todas las rutas generadas automáticamente por el router
    path('', include(router.urls)),
    
    # Documentación de la API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'docs/', 
        SpectacularSwaggerView.as_view(url_name='schema'), 
        name='swagger-ui'
    ),
    path(
        'redoc/', 
        SpectacularRedocView.as_view(url_name='schema'), 
        name='redoc'
    ),
    
    # Autenticación de DRF (para browsable API)
    path('auth/', include('rest_framework.urls')),
]

# URLs principales con versionado
urlpatterns = [
    # API v1 (versión principal)
    path('api/v1/', include(api_urlpatterns)),
    
    # API sin versión (apunta a v1) - Solo para endpoints principales, no auth
    path('api/', include([
        path('', include(router.urls)),
        path('schema/', SpectacularAPIView.as_view(), name='schema-no-version'),
        path(
            'docs/', 
            SpectacularSwaggerView.as_view(url_name='schema-no-version'), 
            name='swagger-ui-no-version'
        ),
        path(
            'redoc/', 
            SpectacularRedocView.as_view(url_name='schema-no-version'), 
            name='redoc-no-version'
        ),
    ])),
]

# Información adicional sobre los endpoints disponibles
"""
ENDPOINTS DISPONIBLES:

=== PRODUCTOS ===
GET    /api/products/                     - Listar todos los productos
POST   /api/products/                     - Crear nuevo producto
GET    /api/products/{id}/                - Obtener producto específico
PUT    /api/products/{id}/                - Actualizar producto completo
PATCH  /api/products/{id}/                - Actualización parcial de producto
DELETE /api/products/{id}/                - Eliminar producto

POST   /api/products/advanced_search/     - Búsqueda avanzada con Strategy Pattern
GET    /api/products/categories/          - Obtener todas las categorías disponibles

=== RECOMENDACIONES IA ===
GET    /api/recommendations/              - Listar recomendaciones guardadas
GET    /api/recommendations/{id}/         - Obtener recomendación específica
POST   /api/recommendations/generate/     - Generar nueva recomendación con IA
GET    /api/recommendations/statistics/   - Estadísticas de recomendaciones

=== DOCUMENTACIÓN ===
GET    /api/schema/                       - Esquema OpenAPI (JSON)
GET    /api/docs/                         - Documentación Swagger UI
GET    /api/redoc/                        - Documentación ReDoc
GET    /api/auth/                         - Autenticación DRF (browsable API)

=== FILTROS Y BÚSQUEDA ===

Parámetros de query disponibles en listados:

Para productos (/api/products/):
- search: Búsqueda en nombre y categoría
- category: Filtrar por categoría exacta
- price: Filtrar por precio exacto
- ordering: Ordenar por campos (name, price, category)
  Ejemplo: ?ordering=-price (descendente)
- page: Número de página para paginación
- page_size: Elementos por página (máximo configurado en settings)

Ejemplo de URLs:
- /api/products/?search=laptop&ordering=-price
- /api/products/?category=Electrónicos&page=2
- /api/products/?price__gte=100&price__lte=500

Para búsqueda avanzada (/api/products/advanced_search/):
Enviar POST con JSON:
{
    "q": "término de búsqueda",
    "category": "categoría opcional",
    "search_type": "contains|exact|fuzzy|price_range|category",
    "min_price": 10.00,
    "max_price": 100.00
}

=== AUTENTICACIÓN ===

Métodos soportados:
- Session Authentication (para browsable API)
- Basic Authentication
- Sin autenticación (desarrollo - cambiar en producción)

=== CORS ===

Configurado para permitir todos los orígenes en desarrollo.
En producción, configurar CORS_ALLOWED_ORIGINS en settings.py

=== RATE LIMITING ===

Límites configurados:
- Usuarios anónimos: 100 requests/hora
- Usuarios autenticados: 1000 requests/hora

=== CÓDIGOS DE RESPUESTA ===

200: OK - Operación exitosa
201: Created - Recurso creado exitosamente
400: Bad Request - Datos de entrada inválidos
401: Unauthorized - Autenticación requerida
403: Forbidden - Sin permisos suficientes
404: Not Found - Recurso no encontrado
429: Too Many Requests - Límite de rate excedido
500: Internal Server Error - Error interno del servidor

=== PAGINACIÓN ===

Respuesta paginada estándar:
{
    "count": 100,
    "next": "http://api.example.org/accounts/?page=4",
    "previous": "http://api.example.org/accounts/?page=2",
    "results": [...]
}

Parámetros:
- page: Número de página (empieza en 1)
- page_size: Elementos por página (máximo definido en settings)
"""