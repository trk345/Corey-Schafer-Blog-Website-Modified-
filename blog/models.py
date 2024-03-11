from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User #User is a class
from django.urls import reverse
from PIL import Image
from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
# class Category(models.Model):
#     name = models.CharField(max_length=250)
#
#     def __str__(self):
#         return self.name
#
#     def get_absolute_url(self):
#         return reverse('post-detail', kwargs = {'pk':self.pk})

class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name
class Post(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default = None)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)#an author can have many posts
                                                             #but a post can have only one authusor
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="blog_like", blank=True)

    def number_of_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs = {'pk':self.pk})








