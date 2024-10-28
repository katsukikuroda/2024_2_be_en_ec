from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE, SET_NULL

class User(AbstractUser):
    pass

class Product(models.Model):
    name = models.CharField(max_length=50)                  # 商品名
    image = models.ImageField(null=True, blank=True)        # 商品の画像
    price = models.IntegerField(default=0)                  # 価格
    explanation = models.TextField(max_length=300)          # 説明
    created_at = models.DateTimeField(auto_now=True)        # 商品が登録された日時

    def __str__(self):
        return self.name

class OrderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name="has_ordered")           # 購入したユーザー
    product = models.ForeignKey(Product, on_delete=SET_NULL, null=True, related_name="product_history")    # 購入された商品
    created_at = models.DateTimeField(auto_now_add=True)                                    # 購入日時
    price = models.IntegerField(default=0)                                                  # 商品の価格
    num = models.IntegerField(default=1)                                                    # 購入した個数

    def __str__(self):
        return f"<購入者:{self.user.username} 商品名: {self.product.name}>"