from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator

from gestao_ong.forms import FormularioBootstrap
from pessoas.models import Perfil


class CadastroForm(FormularioBootstrap, forms.Form):
    usuario = forms.CharField(label='Usuário', max_length=150, validators=[UnicodeUsernameValidator()])
    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput)
    confirma_senha = forms.CharField(label='Repetir senha', widget=forms.PasswordInput)

    def clean_usuario(self):
        usuario = self.cleaned_data['usuario']
        if User.objects.filter(username__iexact=usuario).exists():
            raise forms.ValidationError('Já existe um usuário com esse nome. Tente novamente.')
        return usuario

    def clean(self):
        dados = super().clean()
        senha = dados.get('senha')
        if not senha:
            return dados
        if senha != dados.get('confirma_senha'):
            self.add_error('confirma_senha', 'As senhas não coincidem.')
            return dados
        user = User(username=dados.get('usuario', ''), email=dados.get('email', ''), first_name=dados.get('nome', ''))
        try:
            validate_password(senha, user)
        except forms.ValidationError as e:
            self.add_error('senha', e)
        return dados

    def salvar(self, papel='adotante'):
        dados = self.cleaned_data
        user = User.objects.create_user(
            username=dados['usuario'],
            email=dados['email'],
            password=dados['senha'],
            first_name=dados['nome'],
        )
        Perfil.objects.create(usuario=user, papel=papel, telefone=dados['telefone'])
        return user


class PerfilForm(FormularioBootstrap, forms.Form):
    nome = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='E-mail')
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)


class SenhaForm(FormularioBootstrap, PasswordChangeForm):
    pass
