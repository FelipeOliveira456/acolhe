from django.contrib import admin
from django.utils.html import format_html

from pessoas.models import Adocao
from .models import Abrigo
from .models import Animal
from .models import Especie
from .models import Prontuario


class ProntuarioInline(admin.TabularInline):
    model = Prontuario
    extra = 0


class AdocaoInline(admin.TabularInline):
    model = Adocao
    extra = 0
    fields = ('solicitante', 'data_pedido', 'status', 'observacao')


class EspecieAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


class AbrigoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'capacidade', 'vagas_ocupadas')
    search_fields = ('nome', 'cidade', 'endereco')
    list_filter = ('cidade',)

    @admin.display(description='Vagas ocupadas')
    def vagas_ocupadas(self, obj):
        return f"{obj.ocupacao()} de {obj.capacidade}"


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'nome', 'especie', 'abrigo', 'sexo', 'porte', 'status', 'castrado', 'data_entrada')
    list_display_links = ('miniatura', 'nome')
    search_fields = ('nome', 'descricao', 'especie__nome', 'abrigo__nome')
    list_filter = ('especie', 'abrigo', 'status', 'sexo', 'porte', 'castrado')
    date_hierarchy = 'data_entrada'
    ordering = ('nome',)
    list_editable = ('status',)
    list_per_page = 20
    inlines = [ProntuarioInline, AdocaoInline]

    @admin.display(description='Foto')
    def miniatura(self, obj):
        if obj.foto:
            return format_html('<img src="{}" alt="{}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 4px;">', obj.foto.url, obj.nome)
        return '-'


class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data', 'veterinario')
    search_fields = ('animal__nome', 'veterinario', 'descricao')
    list_filter = ('data', 'animal__especie', 'veterinario')
    date_hierarchy = 'data'


admin.site.register(Especie, EspecieAdmin)
admin.site.register(Abrigo, AbrigoAdmin)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Prontuario, ProntuarioAdmin)

admin.site.site_header = 'Administração da ONG'
admin.site.index_title = 'Bem-vindo à administração do Acolhe'
