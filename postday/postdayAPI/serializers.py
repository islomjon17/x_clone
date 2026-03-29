# api/serializers/auth_serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from postdayBackend.models import Profile
from postdayBackend.models import PostNews

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Parollar mos kelmadi")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password1")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(**attrs)
        if not user:
            raise serializers.ValidationError("Login yoki parol xato")
        if not user.is_active:
            raise serializers.ValidationError("Akkaunt faol emas")
        attrs["user"] = user
        return attrs
    
class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = PostNews
        fields = [
            "id", "body", "created_at",
            "total_likes", "is_liked", "is_owner", "author",
        ]
        read_only_fields = ["id", "created_at"]

    def get_author(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "profile_image": (
                obj.user.profile.profile_image.url
                if obj.user.profile.profile_image
                else None
            ),
        }

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request:
            return obj.user == request.user or request.user.is_superuser
        return False
    



class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "bio", "profile_image",
            "website_link", "facebook_link", "instagram_link",
            "linkedin_link", "twitter_link",
            "followers_count", "following_count", "is_following",
        ]

    def get_followers_count(self, obj):
        # O'zini o'zi follow qilganligi uchun -1
        return obj.followed_by.count() - 1

    def get_following_count(self, obj):
        return obj.follows.count() - 1

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.followed_by.filter(user=request.user).exists()
        return False


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = Profile
        fields = [
            "first_name", "last_name", "email",
            "bio", "profile_image",
            "website_link", "facebook_link", "instagram_link",
            "linkedin_link", "twitter_link",
        ]

    def update(self, instance, validated_data):
        # User ma'lumotlarini ajratib olish
        user_data = validated_data.pop("user", {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Profile ma'lumotlarini yangilash
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance