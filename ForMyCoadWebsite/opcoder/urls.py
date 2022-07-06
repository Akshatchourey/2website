from django.urls import path
from .import views
from .import views1
from .import views2

urlpatterns = [
# For views1
    path('', views.index, name='opcoder'),

    path('login/', views.login, name='login'),
    path('sign_up/', views.sign_up, name='sign up'),
    path('private/', views.private, name='private'),
    path('video/', views.video, name='video'),
    path('video_playing/', views.video_playing, name='video_playing'),
    path('blogs/', views.blogs, name='blog'),
    path('photos/', views.photos, name='photo'),

# For views2
    path('comment/', views1.comment, name='comment'),
    path('comment_submit/', views1.comment_submit, name='comment_submit'),
    path('log_submit/', views1.log_submit, name='log_submit'),
    path('sign_submit/', views1.sign_submit, name='sign_submit'),

# For views3
]
