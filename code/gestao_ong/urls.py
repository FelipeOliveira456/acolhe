from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from usuarios.views import painel
from .views import principal

urlpatterns = [
    path('', principal, name='principal'),
    path('painel', painel, name='painel'),
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('', include('animais.urls')),
    path('', include('pessoas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
