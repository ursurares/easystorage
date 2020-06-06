from django.urls import path
from .import views

urlpatterns = [
    #path('',views.index,name='index'),

    path('home/',views.home,name='home'),

    path('', views.loginUser,name='base_generic'),
    path('login', views.loginUser,name='login_main'),
    path('logout/', views.logoutUser,name='logout_main'),
    path('register/', views.RegisterView.as_view(),name='register'),
    path('confirm-email/<str:user_id>/<str:token>/', views.ConfirmRegistrationView.as_view(), name='confirm_email'),
    
    path('uploadDoc/',views.DocumentView.as_view(),name='upload_doc2'),
    path('upload/',views.upload,name='upload'),
    
    path('docs/',views.docs_list, name='docs_list'),
    path('class/docs/',views.DocsListView.as_view(), name='class_docs_list'),

    path('docs/upload',views.upload_doc, name='upload_doc'),
    path('class/upload',views.UploadCreateView.as_view(),name='class_upload_doc'),
    path('docs/<int:pk>',views.delete_doc,name = 'delete_doc'),

]