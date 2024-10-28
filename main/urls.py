from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("home/", views.ProductList.as_view(), name="home"),
    # ↓ECサイト初回授業のHTMLCSSの確認用
    # path("home/", views.home, name="home"),
    # path("account/", views.account, name="account"),
    # path("cart/", views.cart, name="cart"),
    # path("test/", views.test, name="test"),
]