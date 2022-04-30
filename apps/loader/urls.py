from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "loader"

urlpatterns = [
    path('', views.crypto_history_file_load, name='loader-home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)