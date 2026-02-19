from django.urls import path
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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)