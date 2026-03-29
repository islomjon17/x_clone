from django import forms
from .models import PostNews, Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class PostNewsForm(forms.ModelForm):
    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Write your post in here",
                "class": "form-control",
            }
        ),
        label="",
    )

    class Meta:
        model = PostNews
        exclude = ("user",)


class LoginForm(forms.Form):  # ModelForm emas, oddiy Form!
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Login yoki parol xato")
            if not user.is_active:
                raise forms.ValidationError("Akkaunt faol emas")
            self.user = user
        return cleaned_data


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        ),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last name (optional)"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Bu username band")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu email allaqachon ro'yxatdan o'tgan")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Parollar mos emas")
        return cleaned_data


# class UserUpdateForm(forms.ModelForm):
#     first_name = forms.CharField(required=True)
#     last_name = forms.CharField(required=False)

#     class Meta:
#         model = User
#         fields = ["first_name", "last_name", "email"]


class ProfilePictureForm(forms.ModelForm):
    profile_image = forms.ImageField(label="Profile picture")

    class Meta:
        model = Profile
        fields = ("profile_image",)
      
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    profile_image = forms.ImageField(label="Profil surati", required=False)
    
    # Ijtimoiy tarmoqlar uchun widgetlar orqali chiroyli ko'rinish beramiz
    website_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}))
    facebook_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'Facebook profil havolasi'}))
    instagram_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'Instagram profil havolasi'}))
    linkedin_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'LinkedIn profil havolasi'}))
    twitter_link = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'X (Twitter) profil havolasi'}))

    class Meta:
        model = Profile
        fields = [
            "bio", "profile_image", "website_link", 
            "facebook_link", "instagram_link", 
            "linkedin_link", "twitter_link"
        ]