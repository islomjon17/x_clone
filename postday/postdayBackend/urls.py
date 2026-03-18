from django.urls import path, include
from .views import *

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("profile_list/", ProfileListView.as_view(), name="profile_list"),
    path("profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("login", UserLoginView.as_view(), name="login"),
    path("logout", UserLogoutView.as_view(), name="logout"),
    path("signup/", UserSignupView.as_view(), name="signup"),
    path("update_user/", UserUpdateView.as_view(), name="update_user"),
    path("post/<int:pk>/like/", PostLikeView.as_view(), name="post_like"),
    path("post_show/<int:pk>/", PostShowView.as_view(), name="post_show"),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post_edit'),
]
