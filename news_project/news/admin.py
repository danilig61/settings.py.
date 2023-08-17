from django.contrib import admin
from .models import Article, UserProfile

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')

admin.site.register(Article, ArticleAdmin, UserProfile)
