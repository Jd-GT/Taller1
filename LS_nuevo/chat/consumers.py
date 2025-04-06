import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 👇 Cargar los últimos mensajes desde la base de datos
        messages = await self.get_last_messages(self.room_name)

        # Enviarlos al cliente cuando se conecta
        for message in messages:
            await self.send(text_data=json.dumps({
                'username': message['username'],
                'message': message['message'],
                'timestamp': message['timestamp'],
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data.get('username', 'Anonimo')

        # Guardar el mensaje en la base de datos
        await self.save_message(username, self.room_name, message)

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': now().strftime('%H:%M')  # Opcional
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
            'timestamp': event['timestamp'],
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        return Message.objects.create(username=username, room=room, content=message)

    @sync_to_async
    def get_last_messages(self, room):
        mensajes = Message.objects.filter(room=room).order_by('-timestamp')[:25]
        return [
            {
                'username': m.username,
                'message': m.content,
                'timestamp': m.timestamp.strftime('%H:%M'),
            }
            for m in reversed(mensajes)
        ]
