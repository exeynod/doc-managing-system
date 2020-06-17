from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('cabinet/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('signup/', views.signup, name='signup'),
]