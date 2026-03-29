from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Auth
    path("auth/register/", RegisterAPIView.as_view()),
    path("auth/login/",    LoginAPIView.as_view()),
    path("auth/logout/",   LogoutAPIView.as_view()),
    path("auth/refresh/",  TokenRefreshView.as_view()),

    # Posts
    path("posts/",             PostListCreateAPIView.as_view()),
    path("posts/<int:pk>/",    PostDetailAPIView.as_view()),
    path("posts/<int:pk>/like/", PostLikeAPIView.as_view()),

    # Profiles
    path("profiles/",                      ProfileListAPIView.as_view()),
    path("profiles/<int:pk>/",             ProfileDetailAPIView.as_view()),
    path("profiles/<int:pk>/follow/",      ProfileFollowAPIView.as_view()),
    path("user/me/",                       MeAPIView.as_view()),
]