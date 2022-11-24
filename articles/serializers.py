from turtle import update
from rest_framework import serializers
from articles.models import Article, Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",) # 마지막에 콤마를 꼭 해줘야 한다!!

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return obj.user.email
    
    
    class Meta:
        model = Article
        fields = '__all__'


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("title", "image", "content")

class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email

    class Meta:
        model = Article
        fields = ("pk","title","image","updated_at","user",)