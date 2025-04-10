import requests
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def chat_ia(request):
    """Endpoint mejorado para el chat de recomendaciones"""
    try:
        data = json.loads(request.body)
        descripcion = data.get("descripcion", "").strip()
        
        if len(descripcion) < 3:
            return JsonResponse({
                "error": "La descripción debe tener al menos 3 caracteres",
                "status": "error"
            }, status=400)

        # 1. Primero generamos la recomendación de texto
        recomendacion = generar_recomendacion(descripcion)
        
        # 2. Si hay recomendación válida, generamos imagen
        imagen_b64 = None
        if recomendacion and "No encontré" not in recomendacion:
            # Extraemos solo el nombre del producto (antes de los dos puntos)
            producto_nombre = recomendacion.split(":")[0].strip()
            imagen_b64 = generar_imagen(producto_nombre)
        
        return JsonResponse({
            "producto": recomendacion,
            "imagen": imagen_b64,
            "status": "success"
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido", "status": "error"}, status=400)
    except Exception as e:
        print(f"Error en endpoint: {str(e)}")
        return JsonResponse({
            "error": "Error interno del servidor",
            "status": "error"
        }, status=500)

def generar_recomendacion(descripcion):
    """Genera recomendaciones usando un modelo accesible"""
    url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    prompt = f"""Eres un experto en recomendaciones de productos para estudiantes universitarios. 
Responde ÚNICAMENTE con el formato: "Nombre del producto: breve descripción (máximo 8 palabras)"

Ejemplo: "Cuaderno profesional: 200 hojas con espiral metálico"

Usuario: {descripcion}
Asistente:"""

    data = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 50,
            "do_sample": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=25)
        
        if response.status_code == 200:
            resultado = response.json()
            if isinstance(resultado, list) and resultado:
                texto = resultado[0].get('generated_text', '')
                # Limpieza de la respuesta
                if "Asistente:" in texto:
                    return texto.split("Asistente:")[1].strip().strip('"')
                return texto.strip().strip('"')
        
        return "No encontré productos. Por favor describe mejor lo que necesitas."
    
    except Exception as e:
        print(f"Error en generación: {str(e)}")
        return "El servicio de recomendaciones no está disponible temporalmente."

def generar_imagen(producto_nombre):
    """Genera imágenes usando SDXL con manejo de errores"""
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    prompt = f"Fotografía profesional de {producto_nombre}, fondo blanco, estilo e-commerce, alta calidad, 4k"

    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "width": 512,
                    "height": 512,
                    "num_inference_steps": 20
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        
        print(f"Error en imagen: {response.status_code} - {response.text}")
        return None
    
    except Exception as e:
        print(f"Error en generación de imagen: {str(e)}")
        return None