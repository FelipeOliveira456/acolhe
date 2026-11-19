from django.urls import path

from . import views

urlpatterns = [
    path('animais', views.AnimalListView.as_view(), name='animais'),
    path('animais/novo', views.AnimalCreateView.as_view(), name='animal_novo'),
    path('animais/<int:pk>', views.AnimalDetailView.as_view(), name='animal_detalhe'),
    path('animais/<int:pk>/editar', views.AnimalUpdateView.as_view(), name='animal_editar'),
    path('animais/<int:pk>/excluir', views.AnimalDeleteView.as_view(), name='animal_excluir'),
    path('animais/<int:pk>/prontuario', views.prontuario_novo, name='prontuario_novo'),
    path('prontuarios/<int:pk>/excluir', views.ProntuarioDeleteView.as_view(), name='prontuario_excluir'),
    path('abrigos', views.AbrigoListView.as_view(), name='abrigos'),
    path('abrigos/novo', views.AbrigoCreateView.as_view(), name='abrigo_novo'),
    path('abrigos/<int:pk>/editar', views.AbrigoUpdateView.as_view(), name='abrigo_editar'),
    path('abrigos/<int:pk>/excluir', views.AbrigoDeleteView.as_view(), name='abrigo_excluir'),
    path('especies', views.EspecieListView.as_view(), name='especies'),
    path('especies/nova', views.EspecieCreateView.as_view(), name='especie_nova'),
    path('especies/<int:pk>/editar', views.EspecieUpdateView.as_view(), name='especie_editar'),
    path('especies/<int:pk>/excluir', views.EspecieDeleteView.as_view(), name='especie_excluir'),
]
