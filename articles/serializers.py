from rest_framework import serializers
from articles.models import Image, Article

class ArticleSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.fullname

    class Meta:
        model = Article
        fields = ["id", "title", "content", "created_at", "updated_at", "username", "user", "image"] 