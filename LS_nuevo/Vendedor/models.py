from django.db import models

class Post(models.Model):
    titulo = models.CharField(max_length=100,default="")
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='posts/', null=True, blank=True)  # Campo para la imagen
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
