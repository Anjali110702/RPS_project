from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('friend-game/', views.friend_game, name='friend_game'),
    path('computer-game/', views.computer_game, name='computer_game'),
    path('video-feed-friend/', views.video_feed_friend, name='video_feed_friend'),
    path('video-feed-computer/', views.video_feed_computer, name='video_feed_computer'),
    path('select_opponent/', views.select_opponent, name='select_opponent'),
    path('about/', views.about, name='about'),
]
