from django.urls import path

from . import views

urlpatterns = [
    path('especies', views.especies, name='especies'),
    path('abrigos', views.abrigos, name='abrigos'),
    path('abrigos/<int:id>', views.abrigo_detalhe, name='abrigo_detalhe'),
    path('animais', views.animais, name='animais'),
    path('animais/<int:id>', views.animal_detalhe, name='animal_detalhe'),
    path('prontuarios', views.prontuarios, name='prontuarios'),
]
