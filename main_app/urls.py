
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home', views.home, name="home"),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout_view, name='logout'),
    path('add_friends', views.add_friends, name='add_friends'),
    path('select_friends', views.select_friends, name='select_friends'),
    path('add_new_friend/<int:usr_id>/', views.add_new_friend, name='add_new_friend'),
    path('create_channel', views.create_channel, name='create_channel'),
    path('open_chat', views.open_chat, name='open_chat'),
    path('', views.index, name='index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
