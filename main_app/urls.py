from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import chat_detail, open_private_chat

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name="home"),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout_view, name='logout'),
    path("friends/remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("groups/create/", views.create_group_chat, name="create_group_chat"),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('private_chat/<int:user_id>/', open_private_chat, name='open_private_chat'),
    path('add-friend/', views.add_friend, name='add_friend'),
    
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    
    path('api/chats/', views.get_user_chats, name='api_chats'),
    path('api/chats/<int:chat_id>/messages/', views.get_chat_messages, name='api_messages'),
    path('api/chats/<int:chat_id>/send/', views.send_message_api, name='api_send'),
    
    path('api/friends/', views.get_friends, name='api_friends'),
    
    path('api/friend-requests/', views.get_friend_requests, name='api_friend_requests'),
    path('api/friend-requests/send/', views.send_friend_request_api, name='api_send_friend_request'),
    
    path('api/users/search/', views.search_users, name='api_search'),
    path('remove_friend_api', views.remove_friend_api, name='remove_friend_api'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)