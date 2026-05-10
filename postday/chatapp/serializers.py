from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender", "text", "reply_to", "created_at", "is_read"]

    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                "id": obj.reply_to.id,
                "sender": obj.reply_to.sender.username,
                "text": obj.reply_to.text[:80],
            }
        return None


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserBriefSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "participants", "last_message", "unread_count", "created_at"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return {
                "text": msg.text[:60],
                "sender": msg.sender.username,
                "created_at": msg.created_at,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request:
            return obj.messages.filter(is_read=False).exclude(
                sender=request.user
            ).count()
        return 0


class SendMessageSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)
    reply_id = serializers.IntegerField(required=False, allow_null=True)