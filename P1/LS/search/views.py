from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Search
from .utils import JSONDataLoader 
from .strategies import SearchContext, SearchStrategyFactory

def search_products(request):
    """Enhanced search view using Strategy Pattern for multiple search algorithms."""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    search_type = request.GET.get('search_type', 'contains').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Crear contexto de búsqueda
    context = SearchContext()
    
    try:
        # Configurar estrategia basada en parámetros
        factory = SearchStrategyFactory()
        
        # Determinar qué estrategia usar basada en los parámetros
        if min_price or max_price:
            # Si hay filtros de precio, usar estrategia de rango de precios
            strategy = factory.create_strategy('price_range')
            context.set_strategy(strategy)
            
            # Convertir precios a float si están presentes
            kwargs = {}
            if min_price:
                try:
                    kwargs['min_price'] = float(min_price)
                except (ValueError, TypeError):
                    kwargs['min_price'] = None
            if max_price:
                try:
                    kwargs['max_price'] = float(max_price)
                except (ValueError, TypeError):
                    kwargs['max_price'] = None
            
            # Ejecutar búsqueda por precio
            search_result = context.execute_search(query, **kwargs)
            products = search_result['results']
            
            # Si también hay query de texto, aplicar filtro adicional
            if query:
                products = products.filter(name__icontains=query)
        
        elif category:
            # Si hay categoría especificada, usar estrategia de categoría
            strategy = factory.create_strategy('category')
            context.set_strategy(strategy)
            search_result = context.execute_search(query, category=category)
            products = search_result['results']
        
        else:
            # Búsqueda normal con la estrategia especificada
            if search_type not in factory.get_available_strategies():
                search_type = 'contains'  # fallback a estrategia por defecto
            
            strategy = factory.create_strategy(search_type)
            context.set_strategy(strategy)
            search_result = context.execute_search(query)
            products = search_result['results']
        
        # Preparar contexto para template
        template_context = {
            'products': products,
            'query': query,
            'category': category,
            'search_type': search_type,
            'min_price': min_price,
            'max_price': max_price,
            'no_results': not products.exists(),
            'results_count': products.count(),
            'strategy_used': context.get_current_strategy().get_strategy_name(),
            'available_strategies': factory.get_available_strategies()
        }
        
        return render(request, 'search_results.html', template_context)
    
    except Exception as e:
        # En caso de error, usar búsqueda básica como fallback
        print(f"Error en búsqueda: {str(e)}")
        
        products = Search.objects.all()
        if query:
            products = products.filter(name__icontains=query)
        if category:
            products = products.filter(category__icontains=category)
        
        template_context = {
            'products': products,
            'query': query,
            'category': category,
            'no_results': not products.exists(),
            'error': 'Ocurrió un error en la búsqueda. Mostrando resultados básicos.',
            'strategy_used': 'basic_fallback'
        }
        
        return render(request, 'search_results.html', template_context)

@csrf_exempt
def create_product(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_name = data.get("name")
        if product_name and not Search.objects.filter(name=product_name).exists():
            new_product = Search.objects.create(
                name=product_name,
                category="Desconocida",
                price=0.0,
                images=[]
            )
            new_product.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Producto ya existe"})
    return JsonResponse({"success": False, "error": "Método no permitido"})


def search_results(request):
    loader = JSONDataLoader('search/search_data.json')  
    data = loader.load_data() 
    return render(request, 'search_results.html', {'data': data})