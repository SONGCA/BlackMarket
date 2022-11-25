import random
from datetime import datetime
import time
import jwt
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from articles.serializers import ArticleSerializer, ArticleCreateSerializer, ArticleListSerializer, CommentSerializer, CommentCreateSerializer
from articles.models import Article, Comment, Image

import cv2 
import numpy as np

# 이미지 유화 변환 함수
def paint(filestr):
    npimg = np.fromstring(filestr, np.uint8)
    input_img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)  # 이미지 로드하기
    # 화풍 랜덤하게 선택하기
    path1 = 'articles/models/eccv16/'
    path2 = 'articles/models/instance_norm/'
    paints = {
        1: path1+'composition_vii.t7',
        2: path1+'la_muse.t7',
        3: path1+'starry_night.t7',
        4: path1+'the_wave.t7',
        5: path2+'candy.t7',
        6: path2+'feathers.t7',
        7: path2+'la_muse.t7',
        8: path2+'mosaic.t7',
        9: path2+'starry_night.t7',
        10: path2+'the_scream.t7',
        11: path2+'udnie.t7',
    }
    num = random.randrange(1, 12)
    # OpenCV의 dnn 모듈 사용. 선택된 딥러닝 모델 로드하기
    net = cv2.dnn.readNetFromTorch(paints[num])
    
    # 높이, 너비, 채널
    h, w, c = input_img.shape
    
    # 이미지 resize : 가로는500, 세로는 가로 비율에 맞게(이미지 비율 유지하면서 크기 변형. h:w=new_h:500) 소수점이 나올 수 있기에 정수로 바꿔주기
    input_img = cv2.resize(input_img, dsize=(500, int(h / w * 500)))
    
    # blobFromImage는 전처리를 도와준다. 차원변형을 해줌
    MEAN_VALUE = [103.939, 116.779, 123.680]
    blob = cv2.dnn.blobFromImage(input_img, mean=MEAN_VALUE)

    # 전처리한 결과를 input으로 지정
    net.setInput(blob)
    output = net.forward()
    
    # 후처리
    output = output.squeeze().transpose((1, 2, 0))
    output += MEAN_VALUE
    output = np.clip(output, 0, 255)
    output = output.astype('uint8')
   
    ts = time.time()
    file_name = datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%H-%M-%S')

    cv2.imwrite(f"media/output/{file_name}.jpeg", output) # 파일 생성
    result = f'/media/output/{file_name}.jpeg'

    # 파일 경로명 리턴
    return result

# 게시글 보기/작성하기 -> 좌우 스크롤 보기에 불러올 것
class ArticleView(APIView):
    # authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        articles = Article.objects.all().order_by('-updated_at')
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        output_img = paint(
                filestr=request.FILES['article_image'].read(),
            )
        image_info = Image.objects.create(output_img=output_img)  # Image db에 저장
        image_info.save()

        data = {
            "user" : request.user.id,
            "image" : output_img,
            "title" : request.data["article_title"],
            "content" : request.data["article_content"],
            "price": request.data["article_price"]
        }

        article_serializer = ArticleCreateSerializer(data=data)

        if article_serializer.is_valid():
            article_serializer.save()
            return Response(article_serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response(article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            serializer.save(user=request.user, article_id=article_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
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
