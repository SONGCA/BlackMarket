from turtle import update
from rest_framework import serializers
from articles.models import Image, Article, Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.nickname
    
    class Meta:
        model = Comment
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("content",) # 마지막에 콤마를 꼭 해줘야 한다!!

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    comment_set = CommentSerializer(many=True)
    
    def get_user(self, obj):
        return obj.user.email
    
    class Meta:
        model = Article
        fields = '__all__'


# 게시글 생성 serial
class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("user", "title", "image", "content", "price")

# 게시글 리스트 serial
class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.email

    class Meta:
        model = Article
        fields = ("pk", "title","image","price","user",)
  
# 게시글 업데이트 serial
class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("title", "content", "price")
