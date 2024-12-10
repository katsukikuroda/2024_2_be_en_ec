from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .forms import LoginForm, SignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .forms import ProductSearchForm #23で追加
from .models import Product #23で追加
from django.views.generic.detail import DetailView #24で追加
from .forms import ProductNumForm #24で追加
from django.shortcuts import redirect #25で追加
from django.conf import settings #27で追加
import stripe #27で追加
from django.shortcuts import render #27で追加
from django.views.generic.base import View #27で追加
from .models import OrderHistory #27で追加


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "main/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class Login(LoginView):
    authentication_form = LoginForm
    template_name = "main/login.html"

class Logout(LogoutView):
    pass

class ProductList(ListView):
    paginate_by = 1
    template_name = "main/home.html"

    def get_queryset(self):
        products = Product.objects.order_by("-created_at")

        form = ProductSearchForm(self.request.GET)

        if form.is_valid():
            keyword = form.cleaned_data.get("keyword")
            if keyword:
                products = products.filter(name__icontains=keyword)

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ProductSearchForm(self.request.GET)
        context["form"] = form
        if form.is_valid():
            context["keyword"] = form.cleaned_data.get("keyword")
        return context

class AccountView(LoginRequiredMixin, ListView):
    template_name = "main/account.html"
    paginate_by = 1

    def get_queryset(self):
        user = self.request.user
        return user.has_ordered.order_by("-created_at")

class ProductDetail(DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ProductNumForm()
        return context

    #25で追加↓
    def post(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        num = self.request.POST.get("num")

        # 既にカートに商品が登録されているかどうかで条件分岐
        if "cart" in self.request.session:
            cart = self.request.session["cart"]
            num_dict = self.request.session["num_dict"]

            # カートに追加した商品が既にカートに入っているかどうかでさらに条件分岐
            if str(pk) in num_dict:
                # 既にカートに入っていた場合は、個数を足す
                num_dict[str(pk)] += int(num)
            else:
                # 入っていなかった場合は、新たに商品の pk と個数を登録する
                cart.append(pk)
                num_dict[str(pk)] = int(num)

            self.request.session["cart"] = cart
            self.request.session["num_dict"] = num_dict
        else:
            self.request.session["cart"] = [pk]
            self.request.session["num_dict"] = {str(pk): int(num)}
        return redirect("home")

#↓25で追加
class Cart(LoginRequiredMixin, ListView):
    paginate_by = 1
    template_name = "main/cart.html"

    def get_queryset(self):
        if "cart" in self.request.session:
            self.products = Product.objects.filter(pk__in=self.request.session["cart"]).order_by("pk")
            return self.products
        else:
            return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "cart" in self.request.session:
            num_dict = self.request.session["num_dict"]
            context["total_price"] = sum(self.product_net(product, num_dict) for product in self.products)  # 合計金額の算出
            context["num_dict"] = num_dict
            context["total_num"] = sum(num_dict.values())  # 27追加
            context["data_key"] = settings.STRIPE_PUBLISHABLE_KEY  # 27追加
        else:
            context["total_price"] = 0
            context["total_num"] = 0  # 27追加

        return context

    def product_net(self, product, num_dict):
        """1 つの商品についての小計を計算する関数"""
        return product.price * int(num_dict[str(product.pk)])

    def post(self, request, *args, **kwargs):
        pk = request.POST.get("delete_pk")
        cart = request.session["cart"]
        num_dict = request.session["num_dict"]
        cart.remove(int(pk))
        num_dict.pop(pk)
        request.session["cart"] = cart
        request.session["num_dict"] = num_dict
        return redirect("cart")

#↓27で追加
class CheckoutView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY

        token = request.POST['stripeToken']

        try:
            # 決済処理
            charge = stripe.Charge.create(
                amount=int(request.POST["price"]),
                currency='jpy',
                source=token,
                description="BeEn_ec",
            )
        except stripe.error.CardError as e:
            # 決済が失敗したときのテンプレートを描画する
            return render(request, "main/error.html", {
                "message": "決済に失敗しました。",
            })

        purchased_products = self.request.session["cart"]
        num_dict = self.request.session["num_dict"]

        # 決済が成功したのでカートの内容を破棄する
        del self.request.session["cart"]
        del self.request.session["num_dict"]

        # 商品の購入履歴を作成する
        for product_pk in purchased_products:
            product = Product.objects.get(pk=product_pk)
            OrderHistory.objects.create(user=self.request.user, product=product, price=product.price, num=num_dict[str(product_pk)])

        # 決済が成功した旨を伝えるテンプレートを描画する
        return render(request, "main/complete.html", {
            "products": Product.objects.filter(pk__in=purchased_products).order_by("pk"),
            "num_dict": num_dict,
        })

# ↓初回授業のHTML,CSSの確認用
# from django.shortcuts import render
# from django.http import HttpResponse

# def test(request):
#     return render(request, 'main/base.html')

# def home(request):
#     return HttpResponse('home')

# def account(request):
#     return HttpResponse('account')

# def cart(request):
#     return HttpResponse('cart')
