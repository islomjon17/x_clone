from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)


class InboxAPIView(APIView):
    """
    GET /api/chat/inbox/
    Foydalanuvchining barcha chatlarini qaytaradi
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user
        ).order_by("-created_at")

        serializer = ConversationSerializer(
            conversations, many=True, context={"request": request}
        )
        return Response(serializer.data)


class ConversationMessagesAPIView(APIView):
    """
    GET  /api/chat/<pk>/messages/   — xabarlarni olish
    POST /api/chat/<pk>/messages/   — xabar yuborish
    """
    permission_classes = [IsAuthenticated]

    def get_conversation(self, pk, user):
        return get_object_or_404(Conversation, id=pk, participants=user)

    def get(self, request, pk):
        conversation = self.get_conversation(pk, request.user)

        # O'qilmagan xabarlarni o'qilgan deb belgilash
        conversation.messages.filter(is_read=False).exclude(
            sender=request.user
        ).update(is_read=True)

        messages = conversation.messages.select_related(
            "sender", "reply_to", "reply_to__sender"
        ).order_by("created_at")

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        conversation = self.get_conversation(pk, request.user)
        serializer = SendMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reply_to = None
        reply_id = serializer.validated_data.get("reply_id")
        if reply_id:
            try:
                reply_to = Message.objects.get(id=reply_id)
            except Message.DoesNotExist:
                pass

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=serializer.validated_data["text"],
            reply_to=reply_to,
        )

        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED,
        )


class StartChatAPIView(APIView):
    """
    POST /api/chat/start/<username>/
    Foydalanuvchi bilan yangi chat boshlash yoki mavjudini qaytarish
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        if username == request.user.username:
            return Response(
                {"detail": "O'zingiz bilan chat boshlash mumkin emas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user2 = get_object_or_404(User, username=username)

        conversation = (
            Conversation.objects.filter(participants=request.user)
            .filter(participants=user2)
            .first()
        )

        created = False
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, user2)
            created = True

        serializer = ConversationSerializer(
            conversation, context={"request": request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class DeleteMessageAPIView(APIView):
    """
    DELETE /api/chat/message/<pk>/
    Faqat o'z xabarini o'chirish mumkin
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        message = get_object_or_404(Message, id=pk, sender=request.user)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)