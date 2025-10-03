import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .factories import AIGeneratorFactory

@csrf_exempt
@require_POST
def chat_ia(request):
    """AI chat endpoint using Factory Pattern for generators."""
    try:
        data = json.loads(request.body)
        descripcion = data.get("descripcion", "").strip()
        
        if len(descripcion) < 3:
            return JsonResponse({
                "error": "La descripción debe tener al menos 3 caracteres",
                "status": "error"
            }, status=400)

        # Usar Factory Pattern para crear generadores
        factory = AIGeneratorFactory()
        
        # 1. Generar recomendación de texto
        text_generator = factory.create_generator('text')
        text_result = text_generator.generate(descripcion)
        
        if not text_result['success']:
            return JsonResponse({
                "error": text_result['error'],
                "status": "error"
            }, status=500)
        
        recomendacion = text_result['content']
        
        # 2. Generar imagen si hay recomendación válida
        imagen_b64 = None
        if recomendacion and "No encontré" not in recomendacion:
            # Extraer nombre del producto (antes de los dos puntos)
            producto_nombre = recomendacion.split(":")[0].strip()
            
            image_generator = factory.create_generator('image')
            image_result = image_generator.generate(producto_nombre)
            
            if image_result['success']:
                imagen_b64 = image_result['content']
            else:
                print(f"Error generando imagen: {image_result['error']}")
        
        return JsonResponse({
            "producto": recomendacion,
            "imagen": imagen_b64,
            "status": "success"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido", "status": "error"}, status=400)
    except ValueError as e:
        return JsonResponse({"error": str(e), "status": "error"}, status=400)
    except Exception as e:
        print(f"Error en endpoint: {str(e)}")
        return JsonResponse({
            "error": "Error interno del servidor",
            "status": "error"
        }, status=500)

# AI generation functions moved to factories.py using Factory Pattern