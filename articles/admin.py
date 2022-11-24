from django.contrib import admin
from articles.models import Article, Image, Comment

admin.site.register(Article)
admin.site.register(Image)
admin.site.register(Comment)