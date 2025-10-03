"""
FACTORY PATTERN - Generadores de IA

Este módulo implementa el patrón Factory para crear diferentes tipos
de generadores de contenido AI (texto e imágenes).

Ventajas del Factory Pattern:
- Encapsula la creación de objetos complejos
- Permite agregar nuevos tipos de generadores sin modificar código existente
- Separa la lógica de creación de la lógica de uso
- Facilita el testing y mantenimiento
"""

from abc import ABC, abstractmethod
import requests
import base64
from django.conf import settings
from typing import Dict, Any, Optional


class AIGenerator(ABC):
    """
    Clase abstracta base para todos los generadores de IA.
    Define la interfaz común que deben implementar todos los generadores.
    """
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Genera contenido basado en el prompt proporcionado.
        
        Args:
            prompt (str): El texto de entrada para la generación
            **kwargs: Parámetros adicionales específicos del generador
            
        Returns:
            Dict[str, Any]: Resultado de la generación
        """
        pass
    
    @abstractmethod
    def validate_input(self, prompt: str) -> bool:
        """
        Valida que el input sea apropiado para este generador.
        
        Args:
            prompt (str): El prompt a validar
            
        Returns:
            bool: True si el input es válido
        """
        pass


class TextGenerator(AIGenerator):
    """
    Generador de texto usando modelos de lenguaje.
    Implementa la interfaz AIGenerator para recomendaciones de productos.
    """
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    def validate_input(self, prompt: str) -> bool:
        """Valida que el prompt tenga al menos 3 caracteres."""
        return len(prompt.strip()) >= 3
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Genera recomendaciones de productos usando IA de texto.
        
        Args:
            prompt (str): Descripción del producto deseado
            **kwargs: Parámetros como temperature, max_tokens, etc.
            
        Returns:
            Dict con 'success', 'content', y 'error' si aplica
        """
        if not self.validate_input(prompt):
            return {
                'success': False,
                'error': 'El prompt debe tener al menos 3 caracteres',
                'content': None
            }
        
        # Configurar parámetros por defecto
        temperature = kwargs.get('temperature', 0.7)
        max_tokens = kwargs.get('max_tokens', 50)
        
        system_prompt = """Eres un experto en recomendaciones de productos para estudiantes universitarios. 
Responde ÚNICAMENTE con el formato: "Nombre del producto: breve descripción (máximo 8 palabras)"

Ejemplo: "Cuaderno profesional: 200 hojas con espiral metálico"

Usuario: {prompt}
Asistente:"""
        
        data = {
            "inputs": system_prompt.format(prompt=prompt),
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "do_sample": True
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=25)
            
            if response.status_code == 200:
                resultado = response.json()
                if isinstance(resultado, list) and resultado:
                    texto = resultado[0].get('generated_text', '')
                    # Limpiar la respuesta
                    if "Asistente:" in texto:
                        content = texto.split("Asistente:")[1].strip().strip('"')
                    else:
                        content = texto.strip().strip('"')
                    
                    return {
                        'success': True,
                        'content': content,
                        'error': None
                    }
            
            return {
                'success': False,
                'error': f'Error de API: {response.status_code}',
                'content': "No encontré productos. Por favor describe mejor lo que necesitas."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': "El servicio de recomendaciones no está disponible temporalmente."
            }


class ImageGenerator(AIGenerator):
    """
    Generador de imágenes usando modelos de difusión.
    Implementa la interfaz AIGenerator para crear imágenes de productos.
    """
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    def validate_input(self, prompt: str) -> bool:
        """Valida que el prompt no esté vacío y no contenga contenido inapropiado."""
        if not prompt.strip():
            return False
        
        # Lista de palabras no permitidas (expandir según necesidades)
        forbidden_words = ['violence', 'weapon', 'drug']
        prompt_lower = prompt.lower()
        return not any(word in prompt_lower for word in forbidden_words)
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Genera imágenes de productos usando IA.
        
        Args:
            prompt (str): Nombre del producto para generar imagen
            **kwargs: Parámetros como width, height, steps, etc.
            
        Returns:
            Dict con 'success', 'content' (base64), y 'error' si aplica
        """
        if not self.validate_input(prompt):
            return {
                'success': False,
                'error': 'Prompt inválido o contiene contenido inapropiado',
                'content': None
            }
        
        # Configurar parámetros por defecto
        width = kwargs.get('width', 512)
        height = kwargs.get('height', 512)
        steps = kwargs.get('steps', 20)
        
        # Mejorar el prompt para e-commerce
        enhanced_prompt = f"Fotografía profesional de {prompt}, fondo blanco, estilo e-commerce, alta calidad, 4k"
        
        data = {
            "inputs": enhanced_prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": steps
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                image_b64 = base64.b64encode(response.content).decode('utf-8')
                return {
                    'success': True,
                    'content': image_b64,
                    'error': None
                }
            
            return {
                'success': False,
                'error': f'Error de API: {response.status_code} - {response.text}',
                'content': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None
            }


class AIGeneratorFactory:
    """
    Factory class para crear diferentes tipos de generadores de IA.
    
    Implementa el patrón Factory Method para encapsular la creación
    de objetos AIGenerator y permitir extensibilidad futura.
    
    Ejemplo de uso:
        factory = AIGeneratorFactory()
        text_gen = factory.create_generator('text')
        image_gen = factory.create_generator('image')
    """
    
    # Registro de tipos disponibles
    _generators = {
        'text': TextGenerator,
        'image': ImageGenerator,
    }
    
    @classmethod
    def create_generator(cls, generator_type: str) -> AIGenerator:
        """
        Crea y retorna un generador del tipo especificado.
        
        Args:
            generator_type (str): Tipo de generador ('text' o 'image')
            
        Returns:
            AIGenerator: Instancia del generador solicitado
            
        Raises:
            ValueError: Si el tipo de generador no está soportado
        """
        if generator_type not in cls._generators:
            available_types = ', '.join(cls._generators.keys())
            raise ValueError(
                f"Tipo de generador '{generator_type}' no soportado. "
                f"Tipos disponibles: {available_types}"
            )
        
        generator_class = cls._generators[generator_type]
        return generator_class()
    
    @classmethod
    def register_generator(cls, generator_type: str, generator_class: type):
        """
        Registra un nuevo tipo de generador en la factory.
        
        Permite agregar nuevos tipos sin modificar el código existente.
        
        Args:
            generator_type (str): Nombre del tipo de generador
            generator_class (type): Clase que implementa AIGenerator
        """
        if not issubclass(generator_class, AIGenerator):
            raise ValueError("La clase debe heredar de AIGenerator")
        
        cls._generators[generator_type] = generator_class
    
    @classmethod
    def get_available_types(cls) -> list:
        """
        Retorna la lista de tipos de generadores disponibles.
        
        Returns:
            list: Lista de strings con los tipos disponibles
        """
        return list(cls._generators.keys())


# Función de conveniencia para uso directo
def create_ai_generator(generator_type: str) -> AIGenerator:
    """
    Función de conveniencia para crear generadores de IA.
    
    Args:
        generator_type (str): Tipo de generador ('text' o 'image')
        
    Returns:
        AIGenerator: Instancia del generador
    """
    factory = AIGeneratorFactory()
    return factory.create_generator(generator_type)