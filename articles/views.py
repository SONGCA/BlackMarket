from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from articles.serializers import ArticleSerializer, ArticleCreateSerializer, ArticleListSerializer, CommentSerializer, CommentCreateSerializer
from articles.models import Article, Comment
from rest_framework.generics import get_object_or_404

# 게시글 보기/작성하기
class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 게시글 상세보기/수정하기/삭제하기
class ArticleDetailView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        # 요청자가 게시글 작성자일 경우에만 수정 가능
        if request.user == article.post_author:
            serializer = ArticleCreateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()  # 수정이기 때문에 user정보 불필요
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.post_author:
            article.delete()
            return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

# 댓글 보기/작성하기
class CommentView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        comments = article.comment_set.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # 댓글은 user뿐만 아니라 article_id도 필수이다
            serializer.save(comment_author=request.user, comment_postid_id=article_id)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 댓글 수정하기/삭제하기
class CommentDetailView(APIView):
    def put(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        # 요청자가 댓글 작성자일 경우에만 수정 가능
        if request.user == comment.comment_author:
            serializer = CommentCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()  # 수정이기 때문에 user, article_id 정보 불필요
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN) 

    def delete(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.comment_author:
            comment.delete()
            return Response("삭제되었습니다.", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

# 게시글 좋아요
class LikeView(APIView):
    def post(self, request, article_id):
        # 게시글 가져오기
        article = get_object_or_404(Article, id=article_id)
        # 현재 사용자가 article의 likes 필드에 있다면
        if request.user in article.post_like.all():
            # 해당 사용자를 필드값에서 제거
            article.post_like.remove(request.user)
            return Response("like가 취소되었습니다", status=status.HTTP_200_OK)
        else:
            # 해당 사용자를 필드값에 추가
            article.post_like.add(request.user)
            return Response("like가 되었습니다", status=status.HTTP_200_OK)