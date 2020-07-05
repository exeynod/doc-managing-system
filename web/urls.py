from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('user/', views.user_page, name='user'),
    path('group/', views.group_review, name='group'),
    path('<str:username>/approve/', views.approve, name='approve'),
    path('<str:username>/remove/', views.remove_user, name='remove_user'),
    path('update-account/', views.update_account, name='update_account'),
    path('new-post/', views.new_post, name='new-post'),
    path('add-post/', views.add_new_document, name='add-post'),
    path('cabinet/', views.show_documents, name='cabinet'),
    path('search/', views.search, name='search'),
    path('<str:filename>/sign/', views.sign, name='document_sign'),
    path('<str:filename>/edit/', views.edit_document, name='document_edit'),
    path('<str:filename>/cancel/', views.cancel, name='document_cancel'),
    path('<str:filename>/apply/', views.apply_edits, name='document_edit_apply'),
    path('<str:filename>/review/', views.review, name='document_review'),
    path('<str:filename>/review/new/', views.new_review, name='new_document_review'),
    path('<str:filename>/review/download/', views.download, name='new_document_download'),
    path('.well-known/acme-challenge/wl02Bwi2-dCe4gkHdf5kP0XM3m-kuKq8WgVMjGvv2AM',
         views.certbot_auth, name='certbot_auth')
]
