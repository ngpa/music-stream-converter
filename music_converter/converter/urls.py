from django.urls import path
import converter.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('enter-url/', views.enter_url, name='enter-url'),
    path('authorize-spotify/', views.authorize_spotify, name='authorize-spotify'),
    path('login-spotify/', views.login_spotify, name='login-spotify'),
    path('logout-spotify/', views.logout_spotify, name='logout-spotify'),
    path('login-apple-music/', views.login_apple_music, name='login-apple-music'),
    path('logout-apple-music/', views.logout_apple_music, name='logout-apple-music'),
    path('convert-spotify/', views.convert_to_spotify, name='convert-to-spotify'),
    path('convert-apple-music/', views.convert_to_apple_music, name='convert-to-apple-music')
]