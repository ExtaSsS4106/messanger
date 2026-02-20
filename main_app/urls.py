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
    path('add-friend/', views.add_friend, name='add_friend'),  # ОДИН РАЗ!
    
    path("groups/create/", views.create_group_chat, name="create_group_chat"),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('private_chat/<int:user_id>/', open_private_chat, name='open_private_chat'),
    
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    
    path('api/chats/', views.get_user_chats, name='api_chats'),
    path('api/chats/create/', views.create_chat_api, name='create_chat_api'),
    path('api/chats/<int:chat_id>/messages/', views.get_chat_messages, name='api_messages'),
    path('api/chats/<int:chat_id>/send/', views.send_message_api, name='api_send'),
    path('api/chats/<int:chat_id>/delete/', views.delete_chat_api, name='delete_chat_api'),
    
    path('api/friends/', views.get_friends, name='api_friends'),
    path('api/friends/<int:user_id>/remove/', views.remove_friend_api, name='remove_friend_api'),
    
    path('api/friend-requests/', views.get_friend_requests, name='api_friend_requests'),
    path('api/friend-requests/send/', views.send_friend_request_api, name='api_send_friend_request'),
    
    path('api/users/search/', views.search_users, name='api_search'),
    path('chat/<int:chat_id>/invite/create/', views.create_chat_invite, name='create_chat_invite'),
    path('chat/<int:chat_id>/invites/', views.chat_invites_list, name='chat_invites_list'),
    path('invite/<int:invite_id>/deactivate/', views.deactivate_invite, name='deactivate_invite'),
    path('join/<str:code>/', views.join_chat_by_code, name='join_chat_by_code'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)