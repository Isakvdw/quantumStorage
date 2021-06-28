from django.urls import path

from . import views
urlpatterns = [
    # path('', views.index, name='index'),
    path('bucket', views.bucket_list,),
    path('bucket/add/<str:bucket_name>', views.bucket_add,),
    path('bucket/remove/<str:bucket_name>', views.bucket_remove,),
    path('file/add/<str:bucket_name>/', views.file_add),
    path('file/add/<str:bucket_name>/<path:location>', views.file_add),
    path('file/mkdir/<str:bucket_name>/<path:location>', views.file_mkdir),
    path('file/remove/<str:bucket_name>/<path:file_location>', views.file_remove),
    path('file/get/<str:bucket_name>/<path:file_location>', views.file_get),
    path('file/download/<str:token>', views.file_download),
    path('file/quota', views.file_quota),
]

