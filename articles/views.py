import random
from datetime import datetime
import jwt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from articles.models import Image
from articles.serializers import ArticleSerializer

import cv2 
import numpy as np

# Create your views here.
def paint(filestr):
    npimg = np.fromstring(filestr, np.uint8)
    input_img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    # 화풍 랜덤하게 선택하기
    path1 = 'models/eccv16/'
    path2 = 'models/instance_norm/'
    paints = {
        1: path1+'composition.t7',
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
    
    time = datetime.now().strftime('%Y-%m-%d%H:%M:%s')
    cv2.imwrite(f'output/{time}.jpeg', output) 
    result = f'output/{time}.jpeg'

    return result

class ArticleView(APIView):
    def post(self, request):
        data = request.data
        output_img = paint(
                filestr=request.FILES['input'].read(),
            )
        image_info = Image.objects.create(output_img=output_img)
        image_info.save()

        data = {
            "user" : request.user.id,
            "image" : output_img,
            "title" : request.data["title"],
            "content" : request.data["content"]
        }

        article_serializer = ArticleSerializer(data=data)

        if article_serializer.is_valid():
            article_serializer.save()
            return Response(article_serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response(article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)