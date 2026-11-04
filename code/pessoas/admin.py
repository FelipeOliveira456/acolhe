from django.contrib import admin

from .models import Adocao
from .models import Doacao
from .models import Perfil


class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'papel', 'telefone')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__email', 'telefone')
    list_filter = ('papel',)


class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'solicitante', 'data_pedido', 'status')
    search_fields = ('animal__nome', 'solicitante__username', 'solicitante__first_name', 'observacao')
    list_filter = ('status', 'data_pedido', 'animal__especie', 'animal__abrigo')
    date_hierarchy = 'data_pedido'
    ordering = ('-data_pedido',)


class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('doador_nome', 'tipo', 'valor', 'data', 'registrado_por')
    search_fields = ('doador_nome', 'descricao', 'registrado_por__username')
    list_filter = ('tipo', 'data')
    date_hierarchy = 'data'
    ordering = ('-data',)


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Adocao, AdocaoAdmin)
admin.site.register(Doacao, DoacaoAdmin)
