from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.thread_list, name='thread_list'),
    path('create/', views.thread_create, name='thread_create'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path("thread/<int:thread_id>/load_more/", views.load_more_replies, name="load_more_replies"),
    path("threads/load_more/", views.load_more_threads, name="load_more_threads"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
