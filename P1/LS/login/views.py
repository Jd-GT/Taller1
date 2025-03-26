from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import UserProfile

def login_view(request):
    context = {}  
    storage = messages.get_messages(request)
    storage.used = True


    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso")
            
            user_profile = UserProfile.objects.get(user=user)

            if user_profile.user_type == "cliente":
                return redirect("cliente")  
            elif user_profile.user_type == "vendedor":
                return redirect("vendedor")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")


def home_view_vendedor(request):
    return HttpResponse("<h1>Bienvenido vendedor, has iniciado sesión correctamente</h1>")

def home_view_cliente(request):
    return HttpResponse("<h1>Bienvenido cliente, has iniciado sesión correctamente</h1>")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso! Ahora puedes loguearte.", extra_tags="register success")  
            return redirect('login')  
        else:
            messages.error(request, "Hubo un error en el registro. Por favor, revisa los campos.", extra_tags="register_error")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


