from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from animais.models import Animal
from gestao_ong.util import dados_usuario
from gestao_ong.util import erro
from gestao_ong.util import ler_data
from gestao_ong.util import ler_decimal
from gestao_ong.util import ler_json
from gestao_ong.util import papel_de
from gestao_ong.util import validar_senha
from .models import Adocao
from .models import Doacao
from .models import Perfil
from .permissoes import login_json
from .permissoes import papel_json


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({'ok': True})


def cadastro(request):
    if request.method != 'POST':
        return erro('Método não permitido.', 405)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')

    usuario = (dados.get('usuario') or '').strip()
    email = (dados.get('email') or '').strip()
    senha = dados.get('senha') or ''
    nome = (dados.get('nome') or '').strip()
    telefone = (dados.get('telefone') or '').strip()

    if not usuario or not email or not nome:
        return erro('Informe usuário, nome e e-mail.')
    if '@' not in email:
        return erro('Informe um e-mail válido.')
    mensagem = validar_senha(senha, usuario, email)
    if mensagem:
        return erro(mensagem)
    if User.objects.filter(username=usuario).exists():
        return erro('Já existe um usuário com esse nome. Tente novamente.')

    user = User.objects.create_user(username=usuario, email=email, password=senha, first_name=nome)
    Perfil.objects.create(usuario=user, papel='adotante', telefone=telefone)
    login_django(request, user)
    return JsonResponse(dados_usuario(user), status=201)


def login(request):
    if request.method != 'POST':
        return erro('Método não permitido.', 405)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')

    usuario = (dados.get('usuario') or '').strip()
    senha = dados.get('senha') or ''
    user = authenticate(username=usuario, password=senha)
    if user:
        login_django(request, user)
        return JsonResponse(dados_usuario(user))
    return erro('Usuário ou senha inválidos. Tente novamente.')


def logout(request):
    if request.method != 'POST':
        return erro('Método não permitido.', 405)
    logout_django(request)
    return JsonResponse({'ok': True})


@ensure_csrf_cookie
def me(request):
    if not request.user.is_authenticated:
        return erro('Faça login para continuar.', 401)
    return JsonResponse(dados_usuario(request.user))


@login_json
def painel(request):
    if request.method != 'GET':
        return erro('Método não permitido.', 405)
    papel = papel_de(request.user)
    dados = {
        'disponiveis': Animal.objects.filter(status='disponivel').count(),
        'em_tratamento': Animal.objects.filter(status='em_tratamento').count(),
        'adotados': Animal.objects.filter(status='adotado').count(),
    }
    if papel == 'adotante':
        dados['minhas_adocoes'] = Adocao.objects.filter(solicitante=request.user).count()
        dados['em_analise'] = Adocao.objects.filter(solicitante=request.user, status='analise').count()
    else:
        dados['em_analise'] = Adocao.objects.filter(status='analise').count()
        dados['doacoes'] = Doacao.objects.count()
    return JsonResponse(dados)


@login_json
def adocoes(request):
    if request.method == 'GET':
        consulta = Adocao.objects.select_related('animal', 'animal__especie', 'solicitante')
        if papel_de(request.user) == 'adotante':
            consulta = consulta.filter(solicitante=request.user)
        return JsonResponse([item.como_dict() for item in consulta], safe=False)

    if request.method == 'POST':
        if papel_de(request.user) != 'adotante':
            return erro('Apenas adotantes podem solicitar adoção.', 403)
        dados = ler_json(request)
        if dados is None:
            return erro('Dados inválidos.')
        animal = Animal.objects.filter(id=dados.get('animal_id')).first()
        if not animal:
            return erro('Animal não encontrado.', 404)
        if animal.status != 'disponivel':
            return erro('Este animal não está disponível para adoção.')
        if Adocao.objects.filter(animal=animal, solicitante=request.user, status='analise').exists():
            return erro('Você já possui um pedido em análise para este animal.')
        item = Adocao.objects.create(
            animal=animal,
            solicitante=request.user,
            data_pedido=timezone.localdate(),
            observacao=(dados.get('observacao') or '').strip(),
        )
        return JsonResponse(item.como_dict(), status=201)
    return erro('Método não permitido.', 405)


@papel_json('gestor')
def adocao_detalhe(request, id):
    if request.method != 'PUT':
        return erro('Método não permitido.', 405)
    adocao = Adocao.objects.select_related('animal').filter(id=id).first()
    if not adocao:
        return erro('Adoção não encontrada.', 404)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')
    status = dados.get('status')
    if status not in dict(Adocao.STATUS):
        return erro('Selecione um status válido.')
    if status == 'aprovada' and adocao.animal.status != 'disponivel' and adocao.status != 'aprovada':
        return erro('Este animal não está mais disponível.')

    adocao.status = status
    adocao.save()
    return JsonResponse(adocao.como_dict())


@papel_json('voluntario', 'gestor')
def doacoes(request):
    if request.method == 'GET':
        lista = [item.como_dict() for item in Doacao.objects.select_related('registrado_por')]
        return JsonResponse(lista, safe=False)
    if request.method != 'POST':
        return erro('Método não permitido.', 405)

    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')
    doador = (dados.get('doador_nome') or '').strip()
    tipo = dados.get('tipo')
    data = ler_data(dados.get('data'))
    if not doador or tipo not in dict(Doacao.TIPO) or not data:
        return erro('Informe o doador, o tipo e a data.')
    valor = ler_decimal(dados.get('valor'))
    if dados.get('valor') not in (None, '') and (valor is None or valor < 0):
        return erro('Informe um valor válido.')

    item = Doacao.objects.create(
        doador_nome=doador,
        tipo=tipo,
        valor=valor,
        descricao=(dados.get('descricao') or '').strip(),
        data=data,
        registrado_por=request.user,
    )
    return JsonResponse(item.como_dict(), status=201)


@papel_json('gestor')
def voluntarios(request):
    if request.method == 'GET':
        perfis = Perfil.objects.filter(papel='voluntario').select_related('usuario')
        lista = [{
            'id': item.id,
            'usuario': item.usuario.username,
            'nome': item.usuario.first_name,
            'email': item.usuario.email,
            'telefone': item.telefone,
        } for item in perfis]
        return JsonResponse(lista, safe=False)

    if request.method != 'POST':
        return erro('Método não permitido.', 405)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')

    usuario = (dados.get('usuario') or '').strip()
    email = (dados.get('email') or '').strip()
    senha = dados.get('senha') or ''
    nome = (dados.get('nome') or '').strip()
    telefone = (dados.get('telefone') or '').strip()
    if not usuario or not email or not nome:
        return erro('Informe usuário, nome e e-mail.')
    if '@' not in email:
        return erro('Informe um e-mail válido.')
    mensagem = validar_senha(senha, usuario, email)
    if mensagem:
        return erro(mensagem)
    if User.objects.filter(username=usuario).exists():
        return erro('Já existe um usuário com esse nome. Tente novamente.')

    user = User.objects.create_user(username=usuario, email=email, password=senha, first_name=nome)
    perfil = Perfil.objects.create(usuario=user, papel='voluntario', telefone=telefone)
    return JsonResponse({
        'id': perfil.id,
        'usuario': user.username,
        'nome': user.first_name,
        'email': user.email,
        'telefone': perfil.telefone,
    }, status=201)
