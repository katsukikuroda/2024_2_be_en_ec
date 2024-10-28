from django.contrib import admin
from django.contrib.staticfiles.urls import static   
from django.urls import include, path

from django.conf import settings   

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("main.urls")),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
