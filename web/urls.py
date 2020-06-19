from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('user/', views.user_page, name='user'),
    path('update-account/', views.update_account, name='update_account'),
    path('new-post/', views.new_post, name='new-post'),
    path('add-post/', views.add_new_document, name='add-post'),
    path('cabinet/', views.show_documents, name='cabinet'),
    path('search/<str:text>/', views.search, name='search'),
    path('<str:filename>/review/', views.review, name='document_review'),
    path('<str:filename>/review/new/', views.new_review, name='new_document_review'),
    path('<str:filename>/review/download/', views.download, name='new_document_download'),
]