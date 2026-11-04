import json
from datetime import date
from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse


def ler_json(request):
    try:
        return json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return None


def erro(mensagem, status=400):
    return JsonResponse({'erro': mensagem}, status=status)


def ler_data(valor):
    try:
        return date.fromisoformat(valor)
    except (TypeError, ValueError):
        return None


def ler_decimal(valor):
    if valor is None or valor == '':
        return None
    try:
        return Decimal(str(valor).replace(',', '.'))
    except InvalidOperation:
        return None


def validar_senha(senha, usuario, email):
    try:
        validate_password(senha, User(username=usuario, email=email))
    except ValidationError as e:
        return ' '.join(e.messages)
    return None


def papel_de(user):
    perfil = getattr(user, 'perfil', None)
    if perfil:
        return perfil.papel
    if not user.is_authenticated:
        return ''
    if user.is_superuser:
        return 'gestor'
    return 'adotante'


def dados_usuario(user):
    from pessoas.models import Perfil

    papel = papel_de(user)
    perfil = getattr(user, 'perfil', None)
    return {
        'id': user.id,
        'usuario': user.username,
        'nome': user.first_name or user.username,
        'email': user.email,
        'telefone': perfil.telefone if perfil else '',
        'papel': papel,
        'papel_label': dict(Perfil.PAPEL)[papel],
        'is_staff': user.is_staff,
    }
