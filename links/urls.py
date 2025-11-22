# links/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('healthz', views.healthz, name='healthz'),
    path('api/links', views.list_links, name='list_links'),
    path('api/links/', views.list_links, name='list_links_slash'),  # support trailing slash
    path('api/links/<str:code>', views.get_link, name='get_link'),
    path('api/links/<str:code>/', views.get_link, name='get_link_slash'),
    path('api/links', views.create_link, name='create_link'),  # POST to same path (handled by method)
    path('api/links/', views.create_link, name='create_link_slash'),
    path('api/links/<str:code>', views.delete_link, name='delete_link'),  # DELETE also same path
]
