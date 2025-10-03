"""
Strategy Pattern implementation for search algorithms.
Provides multiple search strategies with runtime switching capability.
"""

from abc import ABC, abstractmethod
from django.db.models import Q, QuerySet
from typing import Dict, List, Any
import re
from .models import Search


class SearchStrategy(ABC):
    """Abstract base class for search strategies."""
    
    @abstractmethod
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """Execute search using specific strategy."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy identifier name."""
        pass


class ExactMatchStrategy(SearchStrategy):
    """Exact match search strategy."""
    
    def get_strategy_name(self) -> str:
        return "exact_match"
    
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """
        Búsqueda por coincidencia exacta en nombre y categoría.
        
        Args:
            queryset: QuerySet de productos
            query: Término de búsqueda exacto
            
        Returns:
            QuerySet con productos que coinciden exactamente
        """
        if not query.strip():
            return queryset.none()
        
        return queryset.filter(
            Q(name__iexact=query) | 
            Q(category__iexact=query)
        )


class ContainsStrategy(SearchStrategy):
    """Contains-based search strategy (case-insensitive)."""
    
    def get_strategy_name(self) -> str:
        return "contains"
    
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """
        Búsqueda por contenido en nombre y categoría.
        
        Args:
            queryset: QuerySet de productos
            query: Término de búsqueda
            
        Returns:
            QuerySet con productos que contienen el término
        """
        if not query.strip():
            return queryset.none()
        
        return queryset.filter(
            Q(name__icontains=query) | 
            Q(category__icontains=query)
        ).distinct()


class FuzzySearchStrategy(SearchStrategy):
    """Fuzzy search with multiple terms and relevance scoring."""
    
    def get_strategy_name(self) -> str:
        return "fuzzy"
    
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """
        Búsqueda difusa usando múltiples términos y coincidencias parciales.
        
        Args:
            queryset: QuerySet de productos
            query: Términos de búsqueda (pueden ser múltiples palabras)
            
        Returns:
            QuerySet con productos ordenados por relevancia
        """
        if not query.strip():
            return queryset.none()
        
        # Dividir query en palabras individuales
        words = [word.strip() for word in re.split(r'\s+', query.lower()) if word.strip()]
        
        if not words:
            return queryset.none()
        
        # Crear filtros para cada palabra
        filters = Q()
        for word in words:
            word_filter = (
                Q(name__icontains=word) |
                Q(category__icontains=word)
            )
            filters |= word_filter
        
        results = queryset.filter(filters).distinct()
        
        # Ordenar por relevancia (productos que contienen más palabras primero)
        return self._order_by_relevance(results, words)
    
    def _order_by_relevance(self, queryset: QuerySet, words: List[str]) -> QuerySet:
        """
        Ordena los resultados por relevancia basada en coincidencias de palabras.
        
        Args:
            queryset: QuerySet de productos filtrados
            words: Lista de palabras de búsqueda
            
        Returns:
            QuerySet ordenado por relevancia
        """
        # Convertir a lista para poder calcular relevancia
        products = list(queryset)
        
        def calculate_relevance(product):
            relevance_score = 0
            name_lower = product.name.lower()
            category_lower = product.category.lower()
            
            for word in words:
                # Puntuación por coincidencias en nombre (mayor peso)
                if word in name_lower:
                    relevance_score += 3
                # Puntuación por coincidencias en categoría
                if word in category_lower:
                    relevance_score += 2
                # Bonus por coincidencia exacta en nombre
                if word == name_lower:
                    relevance_score += 5
            
            return relevance_score
        
        # Ordenar por puntuación de relevancia (descendente)
        products.sort(key=calculate_relevance, reverse=True)
        
        # Retornar QuerySet con el orden personalizado
        if products:
            ordered_ids = [product.id for product in products]
            return queryset.filter(id__in=ordered_ids).extra(
                select={'ordering': f"CASE WHEN id={ordered_ids[0]} THEN 0 " + 
                       " ".join([f"WHEN id={id} THEN {i+1}" for i, id in enumerate(ordered_ids[1:], 1)]) + 
                       " END"}
            ).order_by('ordering')
        
        return queryset


class PriceRangeStrategy(SearchStrategy):
    """Price range filtering strategy."""
    
    def get_strategy_name(self) -> str:
        return "price_range"
    
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """
        Búsqueda por rango de precios.
        
        Args:
            queryset: QuerySet de productos
            query: No usado en esta estrategia
            **kwargs: Debe contener 'min_price' y/o 'max_price'
            
        Returns:
            QuerySet con productos en el rango de precio especificado
        """
        min_price = kwargs.get('min_price')
        max_price = kwargs.get('max_price')
        
        if min_price is not None and max_price is not None:
            return queryset.filter(price__gte=min_price, price__lte=max_price)
        elif min_price is not None:
            return queryset.filter(price__gte=min_price)
        elif max_price is not None:
            return queryset.filter(price__lte=max_price)
        
        return queryset


class CategoryStrategy(SearchStrategy):
    """Category-specific search strategy."""
    
    def get_strategy_name(self) -> str:
        return "category"
    
    def search(self, queryset: QuerySet, query: str, **kwargs) -> QuerySet:
        """
        Búsqueda por categoría específica.
        
        Args:
            queryset: QuerySet de productos
            query: Término de búsqueda dentro de la categoría (opcional)
            **kwargs: Debe contener 'category' 
            
        Returns:
            QuerySet con productos de la categoría especificada
        """
        category = kwargs.get('category')
        
        if not category:
            return queryset.none()
        
        # Filtrar por categoría
        results = queryset.filter(category__icontains=category)
        
        # Si hay query adicional, buscar dentro de la categoría
        if query and query.strip():
            results = results.filter(name__icontains=query.strip())
        
        return results


class SearchContext:
    """
    Contexto que utiliza las estrategias de búsqueda.
    
    Implementa el patrón Strategy permitiendo cambiar algoritmos
    de búsqueda en tiempo de ejecución.
    
    Ejemplo de uso:
        context = SearchContext()
        context.set_strategy(FuzzySearchStrategy())
        results = context.execute_search("laptop gaming")
    """
    
    def __init__(self, strategy: SearchStrategy = None):
        """
        Inicializa el contexto con una estrategia por defecto.
        
        Args:
            strategy: Estrategia inicial (por defecto: ContainsStrategy)
        """
        self._strategy = strategy or ContainsStrategy()
        self._queryset = Search.objects.all()
    
    def set_strategy(self, strategy: SearchStrategy):
        """
        Cambia la estrategia de búsqueda en tiempo de ejecución.
        
        Args:
            strategy: Nueva estrategia a utilizar
        """
        self._strategy = strategy
    
    def set_queryset(self, queryset: QuerySet):
        """
        Establece el QuerySet base para las búsquedas.
        
        Args:
            queryset: QuerySet base de productos
        """
        self._queryset = queryset
    
    def execute_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la búsqueda usando la estrategia actual.
        
        Args:
            query: Término de búsqueda
            **kwargs: Parámetros adicionales para la estrategia
            
        Returns:
            Dict con resultados de búsqueda y metadatos
        """
        try:
            results = self._strategy.search(self._queryset, query, **kwargs)
            
            return {
                'success': True,
                'results': results,
                'count': results.count(),
                'strategy_used': self._strategy.get_strategy_name(),
                'query': query,
                'parameters': kwargs
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'results': Search.objects.none(),
                'count': 0,
                'strategy_used': self._strategy.get_strategy_name(),
                'query': query,
                'parameters': kwargs
            }
    
    def get_current_strategy(self) -> SearchStrategy:
        """
        Retorna la estrategia actual.
        
        Returns:
            SearchStrategy: Estrategia actualmente configurada
        """
        return self._strategy


class SearchStrategyFactory:
    """
    Factory para crear diferentes estrategias de búsqueda.
    Combina Factory Pattern con Strategy Pattern.
    """
    
    _strategies = {
        'exact': ExactMatchStrategy,
        'contains': ContainsStrategy,
        'fuzzy': FuzzySearchStrategy,
        'price_range': PriceRangeStrategy,
        'category': CategoryStrategy,
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str) -> SearchStrategy:
        """
        Crea una instancia de la estrategia especificada.
        
        Args:
            strategy_type: Tipo de estrategia ('exact', 'contains', 'fuzzy', etc.)
            
        Returns:
            SearchStrategy: Instancia de la estrategia
            
        Raises:
            ValueError: Si el tipo de estrategia no está soportado
        """
        if strategy_type not in cls._strategies:
            available = ', '.join(cls._strategies.keys())
            raise ValueError(
                f"Estrategia '{strategy_type}' no soportada. "
                f"Disponibles: {available}"
            )
        
        strategy_class = cls._strategies[strategy_type]
        return strategy_class()
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """
        Retorna lista de estrategias disponibles.
        
        Returns:
            List[str]: Lista de nombres de estrategias
        """
        return list(cls._strategies.keys())


# Función de conveniencia para crear contextos de búsqueda
def create_search_context(strategy_type: str = 'contains') -> SearchContext:
    """
    Crea un contexto de búsqueda con la estrategia especificada.
    
    Args:
        strategy_type: Tipo de estrategia por defecto
        
    Returns:
        SearchContext: Contexto configurado y listo para usar
    """
    factory = SearchStrategyFactory()
    strategy = factory.create_strategy(strategy_type)
    return SearchContext(strategy)