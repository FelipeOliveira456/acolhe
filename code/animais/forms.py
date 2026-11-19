from django import forms

from gestao_ong.forms import FormularioBootstrap
from .models import Abrigo
from .models import Animal
from .models import Especie
from .models import Prontuario


class AnimalForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['nome', 'especie', 'abrigo', 'sexo', 'porte', 'status', 'data_entrada', 'foto', 'descricao', 'castrado']
        widgets = {
            'data_entrada': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class AbrigoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Abrigo
        fields = ['nome', 'cidade', 'endereco', 'capacidade']


class EspecieForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Especie
        fields = ['nome']


class ProntuarioForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Prontuario
        fields = ['data', 'veterinario', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'veterinario': forms.TextInput(attrs={'placeholder': 'Veterinário(a)'}),
            'descricao': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Descrição do atendimento'}),
        }
