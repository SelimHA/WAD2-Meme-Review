from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    dob = models.DateTimeField()

    def __str__(self):
        return self.user.username

class Meme(models.Model):
    TITLE_MAX_LENGTH = 64
    id = models.IntegerField(primary_key=True)
    username = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    picture = models.ImageField(upload_to='meme_images', blank=True)
    date = models.DateField(default=datetime.now)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id}: {self.title}"

class Comment(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    meme = models.OneToOneField(Meme, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date = models.DateField(default=datetime.now)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id}: {self.text}"

class Category(models.Model):
    NAME_MAX_LENGTH = 64
    name = models.CharField(primary_key=True, max_length=NAME_MAX_LENGTH)
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name}"
