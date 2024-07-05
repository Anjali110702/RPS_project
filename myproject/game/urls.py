# gesture_game/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start_game/', views.start_game, name='start_game'),
    path('player1/', views.player1, name='player1'),
    path('player2/<str:game_id>/', views.player2, name='player2'),
    path('gesture_capture/<str:game_id>/<int:player>/', views.gesture_capture, name='gesture_capture'),
]
