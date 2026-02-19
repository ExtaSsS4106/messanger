from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home', views.home, name="home"),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout', views.logout_view, name='logout'),
    path('', views.index, name='index'),
    path("friends/remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("groups/create/", views.create_group_chat, name="create_group_chat"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)