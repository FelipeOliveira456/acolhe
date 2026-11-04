from django.contrib import admin
from django.urls import include, path, re_path

from .views import spa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('animais.urls')),
    path('api/', include('pessoas.urls')),
    re_path(r'^(?!static/|admin/|api/).*$', spa),
]
