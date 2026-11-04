from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.http import JsonResponse

from gestao_ong.util import erro
from gestao_ong.util import ler_data
from gestao_ong.util import ler_json
from gestao_ong.util import papel_de
from pessoas.permissoes import login_json
from pessoas.permissoes import papel_json
from .models import Abrigo
from .models import Animal
from .models import Especie
from .models import Prontuario


def escolha_valida(valor, opcoes):
    return valor in dict(opcoes)


def montar_animal(dados, animal=None):
    nome = (dados.get('nome') or '').strip()
    if not nome:
        return None, 'Informe o nome do animal.'

    especie = Especie.objects.filter(id=dados.get('especie_id')).first()
    abrigo = Abrigo.objects.filter(id=dados.get('abrigo_id')).first()
    if not especie or not abrigo:
        return None, 'Selecione a espécie e o abrigo.'

    if not escolha_valida(dados.get('sexo'), Animal.SEXO):
        return None, 'Selecione o sexo.'
    if not escolha_valida(dados.get('porte'), Animal.PORTE):
        return None, 'Selecione o porte.'
    if not escolha_valida(dados.get('status'), Animal.STATUS):
        return None, 'Selecione o status.'

    data_entrada = ler_data(dados.get('data_entrada'))
    if not data_entrada:
        return None, 'Informe a data de entrada.'

    if animal is None:
        animal = Animal()
    animal.nome = nome
    animal.especie = especie
    animal.abrigo = abrigo
    animal.sexo = dados.get('sexo')
    animal.porte = dados.get('porte')
    animal.status = dados.get('status')
    animal.data_entrada = data_entrada
    animal.castrado = bool(dados.get('castrado'))
    animal.descricao = (dados.get('descricao') or '').strip()
    try:
        animal.clean()
    except ValidationError as e:
        return None, e.messages[0]
    return animal, None


@login_json
def especies(request):
    if request.method != 'GET':
        return erro('Método não permitido.', 405)
    lista = [{'id': item.id, 'nome': item.nome} for item in Especie.objects.all()]
    return JsonResponse(lista, safe=False)


@login_json
def abrigos(request):
    if request.method == 'GET':
        lista = [item.como_dict() for item in Abrigo.objects.all()]
        return JsonResponse(lista, safe=False)
    if request.method == 'POST':
        return salvar_abrigo(request, None)
    return erro('Método não permitido.', 405)


@papel_json('gestor')
def abrigo_detalhe(request, id):
    abrigo = Abrigo.objects.filter(id=id).first()
    if not abrigo:
        return erro('Abrigo não encontrado.', 404)
    if request.method == 'PUT':
        return salvar_abrigo(request, abrigo)
    if request.method == 'DELETE':
        try:
            abrigo.delete()
        except ProtectedError:
            return erro('Não é possível excluir: existem animais neste abrigo.')
        return JsonResponse({'ok': True})
    return erro('Método não permitido.', 405)


def salvar_abrigo(request, abrigo):
    if papel_de(request.user) != 'gestor':
        return erro('Você não tem permissão para esta ação.', 403)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')

    nome = (dados.get('nome') or '').strip()
    cidade = (dados.get('cidade') or '').strip()
    endereco = (dados.get('endereco') or '').strip()
    if not nome or not cidade or not endereco:
        return erro('Informe nome, cidade e endereço.')
    try:
        capacidade = int(dados.get('capacidade'))
    except (TypeError, ValueError):
        return erro('Informe a capacidade.')
    if capacidade < 1:
        return erro('A capacidade deve ser maior que zero.')

    if abrigo is None:
        abrigo = Abrigo()
    abrigo.nome = nome
    abrigo.cidade = cidade
    abrigo.endereco = endereco
    abrigo.capacidade = capacidade
    abrigo.save()
    return JsonResponse(abrigo.como_dict())


@login_json
def animais(request):
    if request.method == 'GET':
        consulta = Animal.objects.select_related('especie', 'abrigo')
        if papel_de(request.user) == 'adotante':
            consulta = consulta.filter(status='disponivel')
        else:
            status = request.GET.get('status', '').strip()
            if status:
                consulta = consulta.filter(status=status)
        especie = request.GET.get('especie', '').strip()
        if especie:
            consulta = consulta.filter(especie_id=especie)
        q = request.GET.get('q', '').strip()
        if q:
            consulta = consulta.filter(nome__icontains=q)
        return JsonResponse([item.como_dict() for item in consulta], safe=False)

    if request.method == 'POST':
        if papel_de(request.user) not in ('voluntario', 'gestor'):
            return erro('Você não tem permissão para esta ação.', 403)
        dados = ler_json(request)
        if dados is None:
            return erro('Dados inválidos.')
        animal, mensagem = montar_animal(dados)
        if mensagem:
            return erro(mensagem)
        animal.save()
        return JsonResponse(animal.como_dict(), status=201)
    return erro('Método não permitido.', 405)


@login_json
def animal_detalhe(request, id):
    animal = Animal.objects.select_related('especie', 'abrigo').filter(id=id).first()
    if not animal:
        return erro('Animal não encontrado.', 404)

    if request.method == 'GET':
        if papel_de(request.user) == 'adotante' and animal.status != 'disponivel':
            if not animal.adocoes.filter(solicitante=request.user).exists():
                return erro('Você não tem permissão para ver este animal.', 403)
        animal = Animal.objects.select_related('especie', 'abrigo').prefetch_related('prontuarios').get(id=id)
        mostrar = papel_de(request.user) != 'adotante'
        return JsonResponse(animal.como_dict(com_prontuario=mostrar))

    if papel_de(request.user) not in ('voluntario', 'gestor'):
        return erro('Você não tem permissão para esta ação.', 403)

    if request.method == 'PUT':
        dados = ler_json(request)
        if dados is None:
            return erro('Dados inválidos.')
        animal, mensagem = montar_animal(dados, animal)
        if mensagem:
            return erro(mensagem)
        animal.save()
        return JsonResponse(animal.como_dict())

    if request.method == 'DELETE':
        if papel_de(request.user) != 'gestor':
            return erro('Você não tem permissão para esta ação.', 403)
        try:
            animal.delete()
        except ProtectedError:
            return erro('Não é possível excluir: este animal possui adoções.')
        return JsonResponse({'ok': True})
    return erro('Método não permitido.', 405)


@papel_json('voluntario', 'gestor')
def prontuarios(request):
    if request.method != 'POST':
        return erro('Método não permitido.', 405)
    dados = ler_json(request)
    if dados is None:
        return erro('Dados inválidos.')

    animal = Animal.objects.filter(id=dados.get('animal_id')).first()
    if not animal:
        return erro('Animal não encontrado.', 404)
    data = ler_data(dados.get('data'))
    veterinario = (dados.get('veterinario') or '').strip()
    descricao = (dados.get('descricao') or '').strip()
    if not data or not veterinario or not descricao:
        return erro('Informe a data, o veterinário e a descrição.')

    item = Prontuario.objects.create(
        animal=animal,
        data=data,
        veterinario=veterinario,
        descricao=descricao,
    )
    return JsonResponse(item.como_dict(), status=201)
