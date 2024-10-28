from django.contrib import admin
#↓ 教科書の会員登録、ログインの確認用にcreatesuperuserとともに先出しで設定
from .models import User

admin.site.register(User)