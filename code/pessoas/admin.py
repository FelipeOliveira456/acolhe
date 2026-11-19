from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Adocao
from .models import Doacao
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    max_num = 1


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ('username', 'first_name', 'email', 'papel', 'is_staff', 'is_active')
    list_filter = ('perfil__papel', 'is_staff', 'is_superuser', 'is_active')

    @admin.display(description='Papel', ordering='perfil__papel')
    def papel(self, obj):
        perfil = getattr(obj, 'perfil', None)
        return perfil.get_papel_display() if perfil else '-'


class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'papel', 'telefone')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__email', 'telefone')
    list_filter = ('papel',)


class AdocaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'solicitante', 'data_pedido', 'status')
    search_fields = ('animal__nome', 'solicitante__username', 'solicitante__first_name', 'observacao')
    list_filter = ('status', 'data_pedido', 'animal__especie', 'animal__abrigo')
    list_select_related = ('animal', 'solicitante')
    date_hierarchy = 'data_pedido'
    ordering = ('-data_pedido',)
    actions = ['aprovar', 'recusar']

    @admin.action(description='Aprovar as adoções selecionadas')
    def aprovar(self, request, queryset):
        aprovadas = 0
        for adocao in queryset:
            adocao.refresh_from_db()
            adocao.animal.refresh_from_db()
            if adocao.status != 'aprovada' and adocao.animal.status == 'disponivel':
                adocao.status = 'aprovada'
                adocao.save()
                aprovadas += 1
        self.message_user(request, f'{aprovadas} adoção(ões) aprovada(s).', messages.SUCCESS)
        if aprovadas < queryset.count():
            self.message_user(request, 'Algumas adoções não foram aprovadas porque o animal não estava disponível.', messages.WARNING)

    @admin.action(description='Recusar as adoções selecionadas')
    def recusar(self, request, queryset):
        recusadas = 0
        for adocao in queryset.filter(status='analise'):
            adocao.status = 'recusada'
            adocao.save()
            recusadas += 1
        self.message_user(request, f'{recusadas} adoção(ões) recusada(s).', messages.SUCCESS)


class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('doador_nome', 'tipo', 'valor', 'data', 'registrado_por')
    search_fields = ('doador_nome', 'descricao', 'registrado_por__username')
    list_filter = ('tipo', 'data', 'registrado_por')
    list_select_related = ('registrado_por',)
    date_hierarchy = 'data'
    ordering = ('-data',)


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Adocao, AdocaoAdmin)
admin.site.register(Doacao, DoacaoAdmin)
