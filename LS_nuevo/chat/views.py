from django.shortcuts import render

def room(request, room_name):
    return render(request, "chat/chat_room.html", 
    {"room_name": room_name,
    "username": request.user.username if request.user.is_authenticated else "Anonimo",
    })
