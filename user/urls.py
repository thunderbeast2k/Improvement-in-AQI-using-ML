from django.urls import path
from . import views

urlpatterns = [

    path('', views.user_login, name='login'),
    path('register/', views.user_register, name='user_register'),

    path('home/', views.user_home, name='home'),

    path('air_quality_analysis/', views.air_quality_analysis, name='air_quality_analysis'),

    path('pollution_analysis/', views.pollution_analysis, name='pollution_analysis'),

    path('logout/', views.logout, name='logout'),

]