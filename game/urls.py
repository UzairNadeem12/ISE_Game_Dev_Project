from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing'),
    
    # Game views
    path('home/', views.game_home, name='home'),
    path('select-challenge/', views.select_challenge, name='select_challenge'),
    path('check-answer/', views.check_answer, name='check_answer'),
    
    # Custom login view
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('user/', views.user_profile, name='user_profile'),
    
    # Custom logout view
    path('logout/', views.custom_logout, name='logout'),
    path('game-over/', views.game_over, name='game_over'),
    path('game-win/', views.game_win, name='game_win'),
] 