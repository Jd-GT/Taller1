"""
API REST - ViewSets

Este módulo contiene las ViewSets de Django REST Framework
que implementan los endpoints de la API REST.

Patrones implementados:
- ViewSet pattern para endpoints RESTful
- Mixins para funcionalidades específicas
- Filtrado y búsqueda avanzada
- Documentación automática con drf-spectacular
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import Search
from .serializers import (
    ProductSerializer, ProductSummarySerializer, 
    AIGenerationRequestSerializer, AIGenerationResponseSerializer,
    SearchRequestSerializer, SearchResponseSerializer
)
from .strategies import SearchContext, SearchStrategyFactory
from chat_recomendaciones.factories import AIGeneratorFactory
from chat_recomendaciones.models import Recomendacion
from chat_recomendaciones.serializers import RecommendationSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de productos.
    
    Proporciona endpoints RESTful completos (CRUD) para productos
    con funcionalidades avanzadas de búsqueda y filtrado.
    
    Endpoints disponibles:
    - GET /api/products/ - Listar productos
    - POST /api/products/ - Crear producto
    - GET /api/products/{id}/ - Detalle de producto
    - PUT /api/products/{id}/ - Actualizar producto
    - PATCH /api/products/{id}/ - Actualización parcial
    - DELETE /api/products/{id}/ - Eliminar producto
    - POST /api/products/advanced_search/ - Búsqueda avanzada
    """
    
    queryset = Search.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Cambiar en producción
    
    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['name', 'category']
    ordering_fields = ['name', 'price', 'category']
    ordering = ['name']
    
    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        
        Usa ProductSummarySerializer para listados y 
        ProductSerializer para detalles y modificaciones.
        """
        if self.action == 'list':
            return ProductSummarySerializer
        return ProductSerializer
    
    @extend_schema(
        summary="Búsqueda avanzada de productos",
        description="""
        Endpoint para búsqueda avanzada usando diferentes estrategias:
        - exact: Búsqueda exacta
        - contains: Búsqueda por contenido (default)
        - fuzzy: Búsqueda difusa con múltiples términos
        - price_range: Filtrado por rango de precios
        - category: Búsqueda específica por categoría
        """,
        request=SearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=SearchResponseSerializer,
                description="Búsqueda ejecutada correctamente"
            ),
            400: OpenApiResponse(description="Parámetros de búsqueda inválidos"),
        },
        tags=['Products']
    )
    @action(detail=False, methods=['post'])
    def advanced_search(self, request):
        """
        Endpoint para búsqueda avanzada usando Strategy Pattern.
        
        Permite usar diferentes algoritmos de búsqueda y filtrado
        según los parámetros proporcionados.
        """
        # Validar datos de entrada
        request_serializer = SearchRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extraer parámetros validados
        validated_data = request_serializer.validated_data
        query = validated_data.get('q', '')
        category = validated_data.get('category', '')
        search_type = validated_data.get('search_type', 'contains')
        min_price = validated_data.get('min_price')
        max_price = validated_data.get('max_price')
        
        try:
            # Crear contexto de búsqueda usando Strategy Pattern
            search_context = SearchContext()
            factory = SearchStrategyFactory()
            
            # Configurar estrategia según parámetros
            if min_price or max_price:
                strategy = factory.create_strategy('price_range')
                search_context.set_strategy(strategy)
                
                kwargs = {}
                if min_price:
                    kwargs['min_price'] = min_price
                if max_price:
                    kwargs['max_price'] = max_price
                
                search_result = search_context.execute_search(query, **kwargs)
                
                # Aplicar filtro adicional de texto si existe
                if query:
                    products = search_result['results'].filter(name__icontains=query)
                    search_result['results'] = products
                    search_result['count'] = products.count()
            
            elif category:
                strategy = factory.create_strategy('category')
                search_context.set_strategy(strategy)
                search_result = search_context.execute_search(query, category=category)
            
            else:
                # Búsqueda normal con estrategia especificada
                if search_type not in factory.get_available_strategies():
                    search_type = 'contains'
                
                strategy = factory.create_strategy(search_type)
                search_context.set_strategy(strategy)
                search_result = search_context.execute_search(query)
            
            # Serializar resultados
            products_serializer = ProductSummarySerializer(
                search_result['results'], 
                many=True,
                context={'request': request}
            )
            
            # Preparar respuesta estandarizada
            response_data = {
                'success': search_result['success'],
                'results': products_serializer.data,
                'count': search_result['count'],
                'strategy_used': search_result['strategy_used'],
                'query': search_result['query'],
                'parameters': search_result['parameters']
            }
            
            if not search_result['success']:
                response_data['error'] = search_result.get('error', 'Error desconocido')
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'error': f'Error en búsqueda avanzada: {str(e)}',
                    'results': [],
                    'count': 0,
                    'strategy_used': 'error',
                    'query': query,
                    'parameters': validated_data
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Obtener categorías disponibles",
        description="Retorna una lista de todas las categorías de productos disponibles",
        responses={
            200: OpenApiResponse(
                description="Lista de categorías",
                examples=[
                    {
                        "categories": [
                            {"name": "Electrónicos", "count": 15},
                            {"name": "Ropa", "count": 8},
                            {"name": "Hogar", "count": 22}
                        ]
                    }
                ]
            )
        },
        tags=['Products']
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Endpoint para obtener todas las categorías disponibles con conteos.
        """
        try:
            # Obtener categorías únicas con conteos
            from django.db.models import Count
            
            categories = (
                Search.objects
                .values('category')
                .annotate(count=Count('id'))
                .order_by('category')
            )
            
            categories_data = [
                {
                    'name': cat['category'],
                    'count': cat['count']
                }
                for cat in categories
            ]
            
            return Response(
                {'categories': categories_data},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo categorías: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para recomendaciones con IA.
    
    Proporciona endpoints para generar y consultar recomendaciones
    usando inteligencia artificial (Factory Pattern).
    
    Endpoints disponibles:
    - GET /api/recommendations/ - Listar recomendaciones guardadas
    - GET /api/recommendations/{id}/ - Detalle de recomendación
    - POST /api/recommendations/generate/ - Generar nueva recomendación
    """
    
    queryset = Recomendacion.objects.all().order_by('-fecha')
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.AllowAny]
    
    # Configuración de filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['descripcion', 'producto_recomendado']
    ordering_fields = ['fecha']
    ordering = ['-fecha']
    
    @extend_schema(
        summary="Generar recomendación con IA",
        description="""
        Genera una nueva recomendación de producto usando inteligencia artificial.
        
        El endpoint utiliza el Factory Pattern para crear generadores de IA:
        - Generador de texto: Crea recomendaciones basadas en la descripción
        - Generador de imagen: Crea imágenes del producto recomendado
        
        Parámetros opcionales permiten personalizar la generación.
        """,
        request=AIGenerationRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=AIGenerationResponseSerializer,
                description="Recomendación generada correctamente"
            ),
            400: OpenApiResponse(description="Datos de entrada inválidos"),
            500: OpenApiResponse(description="Error en generación de IA"),
        },
        tags=['AI Recommendations']
    )
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Endpoint para generar recomendaciones usando Factory Pattern.
        
        Utiliza diferentes generadores de IA para crear contenido
        personalizado basado en la descripción del usuario.
        """
        # Validar datos de entrada
        request_serializer = AIGenerationRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            return Response(
                request_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = request_serializer.validated_data
        descripcion = validated_data['descripcion']
        temperature = validated_data.get('temperature', 0.7)
        max_tokens = validated_data.get('max_tokens', 50)
        generate_image = validated_data.get('generate_image', True)
        
        try:
            # Usar Factory Pattern para crear generadores
            factory = AIGeneratorFactory()
            
            # 1. Generar recomendación de texto
            text_generator = factory.create_generator('text')
            text_result = text_generator.generate(
                descripcion,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            if not text_result['success']:
                return Response(
                    {
                        'status': 'error',
                        'error': text_result['error'],
                        'producto': None,
                        'imagen': None,
                        'metadata': {
                            'descripcion': descripcion,
                            'parameters': validated_data
                        }
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            producto_recomendado = text_result['content']
            imagen_b64 = None
            
            # 2. Generar imagen si se solicita y hay recomendación válida
            if generate_image and producto_recomendado and "No encontré" not in producto_recomendado:
                # Extraer nombre del producto para generar imagen
                producto_nombre = producto_recomendado.split(":")[0].strip()
                
                image_generator = factory.create_generator('image')
                image_result = image_generator.generate(
                    producto_nombre,
                    width=512,
                    height=512,
                    steps=20
                )
                
                if image_result['success']:
                    imagen_b64 = image_result['content']
            
            # 3. Guardar recomendación en base de datos
            try:
                recomendacion = Recomendacion.objects.create(
                    descripcion=descripcion,
                    producto_recomendado=producto_recomendado,
                    imagen_url=f"data:image/png;base64,{imagen_b64}" if imagen_b64 else ""
                )
                
                # Serializar para incluir en respuesta
                recommendation_data = RecommendationSerializer(recomendacion).data
                
            except Exception as save_error:
                print(f"Error guardando recomendación: {save_error}")
                recommendation_data = None
            
            # Preparar respuesta
            response_data = {
                'status': 'success',
                'producto': producto_recomendado,
                'imagen': imagen_b64,
                'metadata': {
                    'descripcion': descripcion,
                    'parameters': validated_data,
                    'text_generation_success': text_result['success'],
                    'image_generation_success': bool(imagen_b64),
                    'saved_recommendation': recommendation_data
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response(
                {
                    'status': 'error',
                    'error': str(ve),
                    'producto': None,
                    'imagen': None,
                    'metadata': {'descripcion': descripcion}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'error': f'Error interno del servidor: {str(e)}',
                    'producto': None,
                    'imagen': None,
                    'metadata': {'descripcion': descripcion}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Obtener estadísticas de recomendaciones",
        description="Retorna estadísticas sobre las recomendaciones generadas",
        responses={
            200: OpenApiResponse(
                description="Estadísticas de recomendaciones",
                examples=[
                    {
                        "total_recommendations": 156,
                        "recent_recommendations": 23,
                        "top_categories": [
                            {"category": "Electrónicos", "count": 45},
                            {"category": "Ropa", "count": 32}
                        ]
                    }
                ]
            )
        },
        tags=['AI Recommendations']
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Endpoint para obtener estadísticas de recomendaciones.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            
            # Estadísticas básicas
            total_recommendations = Recomendacion.objects.count()
            
            # Recomendaciones recientes (últimos 7 días)
            week_ago = timezone.now() - timedelta(days=7)
            recent_recommendations = Recomendacion.objects.filter(
                fecha__gte=week_ago
            ).count()
            
            # Categorías más populares en recomendaciones
            # (analizar productos recomendados)
            top_categories = []
            try:
                from django.db.models import Count
                
                # Buscar categorías basadas en productos existentes
                recommendations = Recomendacion.objects.all()[:100]  # Limitar para rendimiento
                category_counts = {}
                
                for rec in recommendations:
                    # Buscar si el producto recomendado existe en la base de datos
                    producto_nombre = rec.producto_recomendado.split(":")[0].strip()
                    existing_products = Search.objects.filter(
                        name__icontains=producto_nombre
                    )
                    
                    for product in existing_products:
                        category = product.category
                        category_counts[category] = category_counts.get(category, 0) + 1
                
                # Convertir a lista ordenada
                top_categories = [
                    {'category': cat, 'count': count}
                    for cat, count in sorted(
                        category_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                ]
                
            except Exception as cat_error:
                print(f"Error calculando categorías populares: {cat_error}")
            
            return Response(
                {
                    'total_recommendations': total_recommendations,
                    'recent_recommendations': recent_recommendations,
                    'top_categories': top_categories,
                    'period_analyzed': '7 days'
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )