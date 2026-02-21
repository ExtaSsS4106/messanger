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
    path('select_chats', views.select_chats),
    path('send_friend_request', views.send_friend_request),
    path('accept_friend_request', views.accept_friend_request),
    path('decline_friend_request', views.decline_friend_request),
    path('chek_for_friends_requests', views.chek_for_friends_requests),
    path('select_users_for_add', views.select_users_for_add),
    path('remove_friend_api', views.remove_friend_api),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)