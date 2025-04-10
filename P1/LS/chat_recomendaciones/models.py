from django.db import models

class Recomendacion(models.Model):
    descripcion = models.TextField()
    producto_recomendado = models.CharField(max_length=255)
    imagen_url = models.URLField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.producto_recomendado
