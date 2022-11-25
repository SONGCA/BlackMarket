from django.db import models
from users.models import User

# Create your models here.
class Image(models.Model):
    output_img = models.FileField("결과사진", upload_to="media/", null=True)
    
    def __str__(self):
        return str(self.output_img)
    
class Article(models.Model):
    user = models.ForeignKey(User, verbose_name="작성자", on_delete=models.CASCADE)
    content = models.TextField()
    title = models.CharField("제목", max_length=50)
    price = models.CharField("가격", max_length=50)
    image = models.CharField(max_length=120)
    created_at = models.DateTimeField("등록 일자", auto_now_add=True)
    updated_at = models.DateTimeField("수정 일자", auto_now=True)
    
    def __str__(self):
        return str(self.title)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now =True)

    def __str__(self):
        return str(self.content)