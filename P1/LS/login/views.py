from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse

def login_view(request):
    context = {}  # Diccionario para enviar datos al template
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso")
            return redirect("home")  # Redirige a la página principal
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")


def home_view(request):
    return HttpResponse("<h1>Bienvenido, has iniciado sesión correctamente</h1>")

