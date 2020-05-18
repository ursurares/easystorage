from django.urls import path
from .import views

urlpatterns = [
    #path('',views.index,name='index'),

    path('home/',views.home,name='home'),

    path('', views.loginUser,name='base_generic'),
    path('logout/', views.logoutUser,name='logout'),
    path('register/', views.register,name='register'),
    

    path('upload/',views.upload,name='upload'),
    
    path('docs/',views.docs_list, name='docs_list'),
    path('class/docs/',views.DocsListView.as_view(), name='class_docs_list'),

    path('docs/upload',views.upload_doc, name='upload_doc'),
    path('class/upload',views.UploadCreateView.as_view(),name='class_upload_doc'),
    path('docs/<int:pk>',views.delete_doc,name = 'delete_doc'),

]