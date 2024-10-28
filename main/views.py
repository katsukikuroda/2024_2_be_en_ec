from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from .forms import LoginForm, SignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView

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

class ProductList(TemplateView):
    template_name = "main/home.html"

class AccountView(LoginRequiredMixin, ListView):
    template_name = "main/account.html"
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return user.has_ordered.order_by("-created_at")

class ProductDetail(TemplateView):
    template_name = "main/product_detail.html"

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
