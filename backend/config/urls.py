"""
URL configuration for XiAv Speech AI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
"""
URL configuration for XiAv Speech AI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/conversations/', include('apps.conversations.urls')),
    path('api/training/', include('apps.training.urls')),
    path('api/classroom/', include('apps.classroom.urls')),
    path('api/learning/', include('apps.learning.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
