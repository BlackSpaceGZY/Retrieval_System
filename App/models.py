from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.conf import settings
import os


# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Paper(models.Model):
    STATUS_CHOICES = (
        ('unpublished', 'Unpublished'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paper')
    abstract = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpublished')
    category = TaggableManager()
    pdf_url = models.CharField(max_length=250)
    ppt_url = models.CharField(max_length=250)

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    objects = models.Manager()
    published = PublishedManager()

    def get_absolute_url(self):
        return reverse('App:paper_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])


# 扩展User模型
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    student_id = models.IntegerField()

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)


class Comment(models.Model):
    paper = models.ForeignKey(Paper,
                             on_delete=models.CASCADE,
                             related_name='comments')
    # 应该用外键
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created', )

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.paper)