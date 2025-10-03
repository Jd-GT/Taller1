"""
API REST - Serializers para Recomendaciones

Este módulo contiene los serializers específicos para el modelo
de recomendaciones de IA en la aplicación chat_recomendaciones.
"""

from rest_framework import serializers
from .models import Recomendacion


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