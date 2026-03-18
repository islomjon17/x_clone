from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Har bir foydalanuvchi uchun profil modeli (follow tizimi)
class Profile(models.Model):
    # User bilan bog'lanish
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Shaxsiy ma'lumotlar
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")
    
    # Ijtimoiy tarmoqlar (URLField link formatini tekshiradi)
    website_link = models.URLField(max_length=200, blank=True, null=True)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    twitter_link = models.URLField(max_length=200, blank=True, null=True)

    # Follow tizimi
    follows = models.ManyToManyField(
        "self", 
        related_name="followed_by", 
        symmetrical=False, 
        blank=True
    )

    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

# Yangi User yaratilganda avtomatik Profile yaratish
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

        # Foydalanuvchi o'zini o'zi follow qilishi uchun
        profile.follows.set([profile])


# create post model


class PostNews(models.Model):
    user = models.ForeignKey(User, related_name="post", on_delete=models.CASCADE)
    body = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()  #  like sonini qaytaradi

    def __str__(self):
        return f"{self.user} ({self.created_at:%Y-%m-%d %H:%M}) - {self.body}"
