# tinylink_project/urls.py
from django.contrib import admin
from django.urls import path, re_path
from links import views as link_views
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check
    path('healthz', link_views.healthz, name='healthz'),

    # API endpoints
    # Create link (POST)
    path('api/links', link_views.create_link, name='create_link'),

    # List all links (GET)
    path('api/links/', link_views.list_links, name='list_links'),

    # GET + DELETE for a single link (both with and without trailing slash)
    path('api/links/<str:code>', link_views.link_detail, name='link_detail'),
    path('api/links/<str:code>/', link_views.link_detail, name='link_detail_slash'),

    # Root dashboard (optional)
    path('', TemplateView.as_view(template_name="index.html"), name='dashboard'),

    # Redirect short codes (must be LAST to avoid catching api routes)
    re_path(r'^(?P<code>[A-Za-z0-9]{6,8})$', link_views.redirect_view, name='redirect_view'),
]
