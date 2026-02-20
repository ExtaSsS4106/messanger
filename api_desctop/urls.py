from django.contrib import admin
from django.urls import path, re_path
from .import views 
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login', views.login_api),
    path('sign_up', views.sign_up_api),
    path('logout', views.logout_api),
    path('select_friends', views.select_friends),
    path('get_messages', views.get_messages),
    path('send_message', views.send_message),
 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)