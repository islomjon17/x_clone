

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Conversation, Message


class InboxView(LoginRequiredMixin, View):
    """Barcha chatlar ro'yxatini ko'rsatish"""

    def get(self, request):
        conversations = Conversation.objects.filter(participants=request.user).order_by(
            "-created_at"
        )

        return render(request, "chat/inbox.html", {"conversations": conversations})


class ChatView(LoginRequiredMixin, View):
    """Aniq bir chat ichidagi xabarlarni ko'rsatish"""

    def get(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)

        # Xabarlarni o'qilgan deb belgilash (ixtiyoriy)
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True
        )

        return render(request, "chat/chat.html", {"conversation": conversation})


class SendMessageView(LoginRequiredMixin, View):
    """Xabar yuborish va Reply (javob berish) logikasi"""

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        text = request.POST.get("text")
        reply_id = request.POST.get("reply_id")  # Formadan kelayotgan reply ID si

        if text:
            reply_to_msg = None
            # Agar reply_id bo'sh bo'lmasa va raqam bo'lsa
            if reply_id and reply_id.isdigit():
                try:
                    # O'z xabariga yoki boshqanikiga javob berishidan qat'i nazar xabarni topamiz
                    reply_to_msg = Message.objects.get(id=int(reply_id))
                except Message.DoesNotExist:
                    reply_to_msg = None

            # Yangi xabar yaratish
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                text=text,
                reply_to=reply_to_msg,  # Bu yerda ForeignKey bog'lanadi
            )

        return redirect("chat:chat", pk=pk)


class StartChatView(LoginRequiredMixin, View):
    """Yangi foydalanuvchi bilan chat boshlash"""

    def get(self, request, username):
        user2 = get_object_or_404(User, username=username)

        # Ikki foydalanuvchi o'rtasidagi mavjud chatni qidirish
        conversation = (
            Conversation.objects.filter(participants=request.user)
            .filter(participants=user2)
            .first()
        )

        # Agar chat mavjud bo'lmasa, yangisini yaratish
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, user2)

        return redirect("chat:chat", pk=conversation.id)


