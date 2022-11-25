from rest_framework import serializers
from users.models import User
# from articles.serializers import ArticleListSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# 회원가입과 회원정보수정에서 사용할 serial
class UserProfileSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True)
    followings = serializers.StringRelatedField(many=True)
    # article_set = ArticleListSerializer(many=True)
    
    class Meta:
        model = User
        fields = ("id", "email", "nickname", "followings", "followers",)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


# 로그인 시 사용할 serial
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        # ...

        return token