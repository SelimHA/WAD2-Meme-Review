from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    dob = models.DateField()
    bio = models.TextField(default="", blank=True)

    def __str__(self):
        return self.user.username

class Category(models.Model):
    NAME_MAX_LENGTH = 64
    name = models.CharField(primary_key=True, max_length=NAME_MAX_LENGTH)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Meme(models.Model):
    TITLE_MAX_LENGTH = 64
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    picture = models.ImageField(upload_to='meme_images', blank=True)
    date = models.DateField(default=datetime.now)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    nsfw = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}: {self.title}"

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateField(default=datetime.now)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id}: {self.text}"

class View(models.Model):
    viewer_id = models.CharField(max_length=64)
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)

class MemeRating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)
    # 1 for like and -1 for dislike, 0 is default
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = (('user', 'meme'),)

class CommentRating(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    # 1 for like and -1 for dislike, 0 is default
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = (('user', 'comment'),)
