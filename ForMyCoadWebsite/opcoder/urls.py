from django.urls import path
from .import views
from .import views1
from .import views2

urlpatterns = [
# For views
    path('', views.index, name='opcoder'),

    path('search/', views.search, name='search'),
    path('login/', views.login, name='login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('private/', views.private, name='private'),
    path('videos/', views.video, name='video'),
    path('video_playing/', views.video_playing, name='video_playing'),
    path('photos/', views.photos, name='photo'),
    path('blogs/', views.blog, name='blog'),
    path('blogpost/<str:slug>',views.blogpost,name='blogpost'),

# For views1
    path('comment/', views1.comment, name='comment'),
    path('log_submit/', views1.log_submit, name='log_submit'),
    path('sign_submit/', views1.sign_submit, name='sign_submit'),

# For views2
]
