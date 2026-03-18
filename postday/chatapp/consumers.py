import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type") 

        # 1. Typing status ishlov berish
        if message_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_typing",
                    "sender_name": self.scope["user"].username,
                    "typing": data.get("typing"),
                },
            )
        
        # 2. Oddiy xabarni saqlash va yuborish
        else:
            message_text = data.get("message")
            reply_id = data.get("reply_id") # Reply uchun ID
            sender = self.scope["user"]
            
            if message_text:
                # Bazaga saqlaymiz
                new_msg_data = await self.save_message(sender, message_text, reply_id)
                
                # Guruhga tarqatamiz
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message_text,
                        "sender_id": sender.id,
                        "sender_name": sender.username,
                        "created_at": new_msg_data["created_at"],
                        "reply_to_text": new_msg_data.get("reply_text"),
                    },
                )

    # BU METODLAR KLASS ICHIDA (INDENTATION TO'G'RI) BO'LISHI SHART
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, sender, text, reply_id=None):
        conv = Conversation.objects.get(id=self.room_id)
        
        reply_to = None
        if reply_id:
            try:
                reply_to = Message.objects.get(id=reply_id)
            except Message.DoesNotExist:
                reply_to = None
                
        msg = Message.objects.create(
            conversation=conv, 
            sender=sender, 
            text=text, 
            reply_to=reply_to
        )
        
        return {
            "id": msg.id, 
            "created_at": msg.created_at.strftime("%H:%M"),
            "reply_text": reply_to.text if reply_to else None
        }