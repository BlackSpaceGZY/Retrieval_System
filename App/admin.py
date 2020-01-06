from django.contrib import admin
from .models import Paper, Comment, Profile
# Register your models here.


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'abstract')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'paper', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'body')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_id")

