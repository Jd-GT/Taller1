from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Search
from .utils import JSONDataLoader 

def search_products(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    products = Search.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category__icontains=category)
    
    context = {
        'products': products,
        'query': query,
        'category': category,
        'no_results': not products.exists()
    }
    return render(request, 'search_results.html', context)

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