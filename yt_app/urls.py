from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('results/', views.search_results, name='results'),
    path('subscribeList/', views.subscribeList, name='subscribeList'),
    path('channel_id/', views.find_channel_id, name='find_channel_id'), 
    path('upload_video/', views.upload_video, name='upload_video'),
    path('accounts/', include('allauth.urls')),
]