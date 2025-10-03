"""
API REST - Serializers

Este módulo contiene los serializers de Django REST Framework
para la conversión entre objetos Python y representaciones JSON.

Funcionalidades implementadas:
- Serialización completa de modelos de productos
- Validaciones personalizadas
- Campos calculados y relaciones
- Soporte para diferentes niveles de detalle
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Search
from chat_recomendaciones.models import Recomendacion
from decimal import Decimal
from typing import Dict, Any


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el modelo Search (productos).
    
    Incluye validaciones personalizadas y campos calculados.
    """
    
    # Campos calculados
    price_formatted = serializers.SerializerMethodField()
    has_images = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    # Campo de solo lectura para URL de API
    url = serializers.HyperlinkedIdentityField(
        view_name='product-detail',
        lookup_field='pk'
    )
    
    class Meta:
        model = Search
        fields = [
            'id', 'url', 'name', 'category', 'price', 'price_formatted',
            'images', 'has_images', 'image_count'
        ]
        read_only_fields = ['id', 'url', 'price_formatted', 'has_images', 'image_count']
    
    def get_price_formatted(self, obj) -> str:
        """
        Formatea el precio con símbolo de moneda.
        
        Returns:
            str: Precio formateado (ej: "$199.99")
        """
        return f"${obj.price:,.2f}" if obj.price else "$0.00"
    
    def get_has_images(self, obj) -> bool:
        """
        Indica si el producto tiene imágenes.
        
        Returns:
            bool: True si tiene imágenes
        """
        return bool(obj.images)
    
    def get_image_count(self, obj) -> int:
        """
        Cuenta el número de imágenes del producto.
        
        Returns:
            int: Número de imágenes
        """
        return len(obj.images) if obj.images else 0
    
    def validate_name(self, value: str) -> str:
        """
        Valida que el nombre del producto sea apropiado.
        
        Args:
            value: Nombre del producto
            
        Returns:
            str: Nombre validado
            
        Raises:
            serializers.ValidationError: Si el nombre no es válido
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre del producto debe tener al menos 2 caracteres."
            )
        
        # Verificar que no sea solo números
        if value.strip().isdigit():
            raise serializers.ValidationError(
                "El nombre del producto no puede ser solo números."
            )
        
        return value.strip().title()  # Capitalizar cada palabra
    
    def validate_category(self, value: str) -> str:
        """
        Valida y normaliza la categoría del producto.
        
        Args:
            value: Categoría del producto
            
        Returns:
            str: Categoría validada y normalizada
        """
        if not value:
            return "General"
        
        return value.strip().title()
    
    def validate_price(self, value: Decimal) -> Decimal:
        """
        Valida que el precio sea positivo y razonable.
        
        Args:
            value: Precio del producto
            
        Returns:
            Decimal: Precio validado
            
        Raises:
            serializers.ValidationError: Si el precio no es válido
        """
        if value < 0:
            raise serializers.ValidationError(
                "El precio no puede ser negativo."
            )
        
        if value > Decimal('999999.99'):
            raise serializers.ValidationError(
                "El precio no puede exceder $999,999.99."
            )
        
        return value
    
    def validate_images(self, value: list) -> list:
        """
        Valida la lista de imágenes.
        
        Args:
            value: Lista de URLs de imágenes
            
        Returns:
            list: Lista validada de imágenes
        """
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Las imágenes deben ser una lista de URLs."
            )
        
        # Limitar número máximo de imágenes
        if len(value) > 10:
            raise serializers.ValidationError(
                "No se pueden agregar más de 10 imágenes por producto."
            )
        
        return value


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados de productos.
    
    Incluye solo los campos esenciales para mejor rendimiento
    en listados y búsquedas.
    """
    
    price_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Search
        fields = ['id', 'name', 'category', 'price', 'price_formatted']
    
    def get_price_formatted(self, obj) -> str:
        """Formatea el precio con símbolo de moneda."""
        return f"${obj.price:,.2f}" if obj.price else "$0.00"


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo de recomendaciones de IA.
    
    Incluye campos calculados para mejorar la presentación
    de los datos de recomendaciones.
    """
    
    # Campos calculados
    fecha_formatted = serializers.SerializerMethodField()
    descripcion_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Recomendacion
        fields = [
            'id', 'descripcion', 'descripcion_preview', 
            'producto_recomendado', 'imagen_url', 
            'fecha', 'fecha_formatted'
        ]
        read_only_fields = ['id', 'fecha', 'fecha_formatted', 'descripcion_preview']
    
    def get_fecha_formatted(self, obj) -> str:
        """
        Formatea la fecha de creación.
        
        Returns:
            str: Fecha formateada
        """
        return obj.fecha.strftime("%d/%m/%Y %H:%M") if obj.fecha else ""
    
    def get_descripcion_preview(self, obj) -> str:
        """
        Crea un preview de la descripción (primeras 100 caracteres).
        
        Returns:
            str: Preview de la descripción
        """
        if not obj.descripcion:
            return ""
        
        preview = obj.descripcion[:100]
        if len(obj.descripcion) > 100:
            preview += "..."
        
        return preview


class AIGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer para requests de generación con IA.
    
    Valida los datos de entrada para los endpoints de
    recomendaciones y generación de imágenes.
    """
    
    descripcion = serializers.CharField(
        max_length=1000,
        min_length=3,
        help_text="Descripción del producto deseado (mínimo 3 caracteres)"
    )
    
    # Parámetros opcionales para personalizar la generación
    temperature = serializers.FloatField(
        default=0.7,
        min_value=0.1,
        max_value=2.0,
        required=False,
        help_text="Creatividad del modelo (0.1 - 2.0, default: 0.7)"
    )
    
    max_tokens = serializers.IntegerField(
        default=50,
        min_value=10,
        max_value=200,
        required=False,
        help_text="Máximo número de tokens a generar (10-200, default: 50)"
    )
    
    generate_image = serializers.BooleanField(
        default=True,
        required=False,
        help_text="Si generar imagen del producto recomendado (default: true)"
    )
    
    def validate_descripcion(self, value: str) -> str:
        """
        Valida la descripción del producto.
        
        Args:
            value: Descripción proporcionada
            
        Returns:
            str: Descripción validada
        """
        # Limpiar espacios extra
        value = value.strip()
        
        # Verificar longitud mínima
        if len(value) < 3:
            raise serializers.ValidationError(
                "La descripción debe tener al menos 3 caracteres."
            )
        
        # Verificar que no sea solo espacios o caracteres especiales
        if not any(c.isalnum() for c in value):
            raise serializers.ValidationError(
                "La descripción debe contener al menos una letra o número."
            )
        
        return value


class AIGenerationResponseSerializer(serializers.Serializer):
    """
    Serializer para respuestas de generación con IA.
    
    Estandariza el formato de respuesta de los endpoints
    de inteligencia artificial.
    """
    
    status = serializers.CharField(
        help_text="Estado de la operación (success/error)"
    )
    
    producto = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Producto recomendado por la IA"
    )
    
    imagen = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Imagen generada en formato base64"
    )
    
    error = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Mensaje de error si la operación falló"
    )
    
    metadata = serializers.DictField(
        required=False,
        help_text="Información adicional sobre la generación"
    )


class SearchRequestSerializer(serializers.Serializer):
    """
    Serializer para requests de búsqueda avanzada.
    
    Valida y documenta los parámetros disponibles para
    las diferentes estrategias de búsqueda.
    """
    
    q = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        help_text="Término de búsqueda principal"
    )
    
    category = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text="Filtrar por categoría específica"
    )
    
    search_type = serializers.ChoiceField(
        choices=[
            ('exact', 'Búsqueda exacta'),
            ('contains', 'Búsqueda por contenido'),
            ('fuzzy', 'Búsqueda difusa'),
            ('price_range', 'Búsqueda por rango de precios'),
            ('category', 'Búsqueda por categoría'),
        ],
        default='contains',
        required=False,
        help_text="Tipo de algoritmo de búsqueda a utilizar"
    )
    
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        help_text="Precio mínimo para filtrar"
    )
    
    max_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        help_text="Precio máximo para filtrar"
    )
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validación cruzada de parámetros de búsqueda.
        
        Args:
            data: Datos validados individualmente
            
        Returns:
            Dict[str, Any]: Datos validados completamente
        """
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        # Validar que min_price < max_price
        if min_price and max_price and min_price > max_price:
            raise serializers.ValidationError(
                "El precio mínimo no puede ser mayor al precio máximo."
            )
        
        return data


class SearchResponseSerializer(serializers.Serializer):
    """
    Serializer para respuestas de búsqueda.
    
    Estandariza el formato de respuesta de los endpoints
    de búsqueda con metadatos adicionales.
    """
    
    success = serializers.BooleanField(
        help_text="Indica si la búsqueda fue exitosa"
    )
    
    results = ProductSummarySerializer(
        many=True,
        help_text="Lista de productos encontrados"
    )
    
    count = serializers.IntegerField(
        help_text="Número total de resultados"
    )
    
    strategy_used = serializers.CharField(
        help_text="Estrategia de búsqueda utilizada"
    )
    
    query = serializers.CharField(
        allow_null=True,
        help_text="Término de búsqueda procesado"
    )
    
    parameters = serializers.DictField(
        help_text="Parámetros utilizados en la búsqueda"
    )
    
    error = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Mensaje de error si la búsqueda falló"
    )