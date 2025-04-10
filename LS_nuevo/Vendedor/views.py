from django.shortcuts import render, redirect
from Vendedor.forms import PostForm
from Vendedor.models import Post

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
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Importante: request.FILES para manejar la imagen
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la misma página tras guardar el post
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-fecha_creacion')
    return render(request, 'Vendedor/inicio.html', {'form': form, 'posts': posts})
"""
def inicio(request):
    return render(request, 'Vendedor/inicio.html')

def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # Usamos request.FILES para manejar archivos
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la página de inicio o donde desees
    else:
        form = PostForm()
    #posts = Post.objects.all()    

    return render(request, 'Vendedor/inicio.html', {'form': form})

"""    