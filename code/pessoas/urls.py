from django.urls import path

from . import views

urlpatterns = [
    path('adocoes', views.AdocaoListView.as_view(), name='adocoes'),
    path('adocoes/solicitar/<int:animal_id>', views.adocao_solicitar, name='adocao_solicitar'),
    path('adocoes/<int:pk>/status', views.adocao_status, name='adocao_status'),
    path('adocoes/<int:pk>/cancelar', views.adocao_cancelar, name='adocao_cancelar'),
    path('doacoes', views.DoacaoListView.as_view(), name='doacoes'),
    path('doacoes/nova', views.DoacaoCreateView.as_view(), name='doacao_nova'),
    path('doacoes/<int:pk>/editar', views.DoacaoUpdateView.as_view(), name='doacao_editar'),
    path('doacoes/<int:pk>/excluir', views.DoacaoDeleteView.as_view(), name='doacao_excluir'),
    path('pessoas', views.PessoaListView.as_view(), name='pessoas'),
    path('pessoas/nova', views.pessoa_nova, name='pessoa_nova'),
    path('pessoas/<int:pk>/papel', views.pessoa_papel, name='pessoa_papel'),
]
