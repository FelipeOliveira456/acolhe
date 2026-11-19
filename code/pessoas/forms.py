from django import forms

from gestao_ong.forms import FormularioBootstrap
from usuarios.forms import CadastroForm
from .models import Doacao
from .models import Perfil


class DoacaoForm(FormularioBootstrap, forms.ModelForm):
    class Meta:
        model = Doacao
        fields = ['doador_nome', 'tipo', 'valor', 'data', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex.: 20 kg de ração para filhotes'}),
        }


class NovaPessoaForm(CadastroForm):
    papel = forms.ChoiceField(label='Papel', choices=Perfil.PAPEL, initial='voluntario')
