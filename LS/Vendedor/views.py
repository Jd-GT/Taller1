from django.shortcuts import render

def perfil_view(request):
    # Datos estáticos para la demostración visual
    context = {
        'nombre_usuario': 'JaneDoe',
        'nombre_completo': 'Jane Doe',
        'biografia': 'Lorem ipsum dolor',
        'seguidores': 1450,
        'siguiendo': 789,
        'avatar_url': 'static/img/Perfil.png'  # Usar una imagen real o placeholder
    }
    return render(request, 'Vendedor/perfil.html', context)
def inicio(request):
    return render(request, 'Vendedor/inicio.html')