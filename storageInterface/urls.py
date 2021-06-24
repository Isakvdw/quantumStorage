from django.urls import path

from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('bucket', views.bucket_list, name='bucket_list'),
    path('bucket/add/<str:bucket_name>', views.bucket_add, name='bucket_add'),
    path('bucket/remove/<str:bucket_name>', views.bucket_remove, name='bucket_remove'),
    path('file/add/<str:bucket_name>/<path:location>', views.file_add, name='bucket_add'),
    path('file/add/<str:bucket_name>/', views.file_add, name='bucket_add'),
]

