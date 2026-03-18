from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, PostNews

# Groupni admin paneldan olib tashlaymiz
admin.site.unregister(Group)


# Profile'ni admin panelga qo‘shamiz
admin.site.register(Profile)


# User sahifasida Profile'ni birga ko‘rsatish uchun
class ProfileInline(admin.StackedInline):
    model = Profile


# User admin sozlamalari
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]  # faqat username ko‘rsatiladi
    inlines = [ProfileInline]  # Profile inline qo‘shiladi


#  User'ni admin paneldan olib tashlaymiz
admin.site.unregister(User)

# User'ni qayta ro‘yxatdan o‘tkazamiz
admin.site.register(User, UserAdmin)
admin.site.register(PostNews)
