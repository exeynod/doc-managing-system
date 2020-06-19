from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('cabinet/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('new-post/', views.new_post, name='new-post'),
    path('add-post/', views.add_new_post, name='add-post'),
    path('review/', views.review, name='document_review'),
]