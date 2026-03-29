from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Profile, PostNews
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.html import linebreaks
from django.utils.dateparse import parse_datetime
from django.db.models import Q


from .forms import (
    PostNewsForm,
    LoginForm,
    SignupForm,
    UserUpdateForm,
    ProfilePictureForm,
    ProfileUpdateForm,
)


class HomeView(View):

    def get(self, request):
        query = request.GET.get("q", "")
        form = PostNewsForm()

        posts = PostNews.objects.none()
        users = User.objects.none()

        if query:
            posts = PostNews.objects.filter(body__icontains=query).order_by(
                "-created_at"
            )

            users = User.objects.filter(username__icontains=query)

        else:
            posts = PostNews.objects.all().order_by("-created_at")

        context = {
            "query": query,
            "postnews": posts,
            "users": users,
            "form": form,
        }
        return render(request, "home2.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Ro'yxatdan o'tish talab etiladi")
            return redirect("home")

        form = PostNewsForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post yuklandi")
            return redirect("home")

        posts = PostNews.objects.all().order_by("-created_at")
        context = {
            "postnews": posts,
            "form": form,
        }
        return render(request, "home2.html", context)


class PostShowView(View):
    def get(self, request, pk):
        post = get_object_or_404(PostNews, id=pk)
        return render(request, "pages/post_show.html", {"post": post})


###################################
###################################
###################################
class ProfileListView(View):
    def get(self, request):
        if request.user.is_authenticated:
            profiles = Profile.objects.exclude(user=request.user)
            return render(request, "pages/profile_list.html", {"profiles": profiles})
        else:
            messages.success(request, ("Ro'yxatdan o'tish talab etiladi"))
            return redirect("home")


###################################
###################################
###################################
class ProfileView(View):

    def get(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Ro'yxatdan o'tish talab etiladi")
            return redirect("home")

        try:
            profile = Profile.objects.get(user_id=pk)
            postnews = PostNews.objects.filter(user_id=pk).order_by("-created_at")
        except Profile.DoesNotExist:
            messages.error(request, "Bunday foydalanuvchi mavjud emas")
            return redirect("home")

        return render(
            request,
            "pages/profile.html",
            {"profile": profile, "postnews": postnews},
        )

    def post(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Ro'yxatdan o'tish talab etiladi")
            return redirect("home")

        try:
            profile = Profile.objects.get(user_id=pk)
            current_user_profile = request.user.profile
            action = request.POST.get("follow")

            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)

            current_user_profile.save()

        except Profile.DoesNotExist:
            messages.error(request, "Bunday foydalanuvchi mavjud emas")
            return redirect("home")

        return redirect("profile", pk=pk)


###################################
###################################
####authentication section####
###################################
###################################
class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")  # Allaqachon kirgan bo'lsa
        form = LoginForm()
        return render(request, "pages/auth/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, "Muvaffaqiyatli tizimga kirdingiz")
            return redirect("home")
        return render(request, "pages/auth/login.html", {"form": form})


class UserSignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, "pages/auth/signup.html", {"form": form})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            login(request, user)
            messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz")
            return redirect("home")

        return render(request, "pages/auth/signup.html", {"form": form})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, "Tizimdan chiqdingiz")
        return redirect("home")


class UserUpdateView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Ro'yxatdan o'tish talab etiladi")
            return redirect("login")

        # Formalarni joriy ma'lumotlar bilan to'ldiramiz
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        profile_pic_form = ProfilePictureForm(instance=request.user.profile)

        return render(
            request,
            "pages/update/update_user.html",
            {
                "user_form": user_form,
                "profile_form": profile_form,
                "profile_pic_form": profile_pic_form,
            },
        )

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Ro'yxatdan o'tish talab etiladi")
            return redirect("login")

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        profile_pic_form = ProfilePictureForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if (
            user_form.is_valid()
            and profile_form.is_valid()
            and profile_pic_form.is_valid()
        ):
            user_form.save()
            profile_form.save()
            profile_pic_form.save()

            messages.success(request, "Barcha ma'lumotlar muvaffaqiyatli saqlandi!")
            return redirect("profile", request.user.id)

        context = {
            "user_form": user_form,
            "profile_form": profile_form,
            "profile_pic_form": profile_pic_form,
        }
        return render(request, "pages/update/update_user.html", context)


class PostLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(PostNews, id=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return redirect(request.META.get("HTTP_REFERER", "home"))


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PostNews
    success_url = reverse_lazy("home")
    template_name = "pages/update/post_confirm_delete.html"

    def test_func(self):
        post = self.get_object()

        return self.request.user == post.user or self.request.user.is_superuser

    def handle_no_permission(self):

        messages.error(self.request, "Sizda bu postni o'chirish huquqi yo'q!")
        return redirect("home")


class PostEditView(View):

    def get(self, request, pk):
        post = get_object_or_404(PostNews, pk=pk)
        return render(request, "pages/update/post_edit.html", {"post": post})

    def post(self, request, pk):
        post = get_object_or_404(PostNews, pk=pk)

        body = request.POST.get("body")
        created_at = request.POST.get("created_at")

        post.body = body

        if created_at:
            post.created_at = parse_datetime(created_at)

        post.save()

        return redirect("home")
