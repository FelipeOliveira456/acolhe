from django.urls import path

from . import views

urlpatterns = [
    path('csrf', views.csrf, name='csrf'),
    path('cadastro', views.cadastro, name='cadastro'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('me', views.me, name='me'),
    path('painel', views.painel, name='painel'),
    path('adocoes', views.adocoes, name='adocoes'),
    path('adocoes/<int:id>', views.adocao_detalhe, name='adocao_detalhe'),
    path('doacoes', views.doacoes, name='doacoes'),
    path('voluntarios', views.voluntarios, name='voluntarios'),
]
