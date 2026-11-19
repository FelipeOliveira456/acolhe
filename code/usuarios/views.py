from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as login_django
from django.contrib.auth import logout as logout_django
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from animais.models import Abrigo
from animais.models import Animal
from animais.models import Especie
from pessoas.models import Adocao
from pessoas.models import Doacao
from pessoas.models import Perfil
from .forms import CadastroForm
from .forms import PerfilForm
from .forms import SenhaForm
from .permissoes import papel_de


def login(request):
    if request.user.is_authenticated:
        return redirect('painel')
    proxima = request.POST.get('next') or request.GET.get('next') or ''
    if request.method == 'GET':
        return render(request, 'login.html', {'next': proxima})

    usuario = request.POST.get('usuario', '').strip()
    senha = request.POST.get('senha', '')
    user = authenticate(request, username=usuario, password=senha)
    if user:
        login_django(request, user)
        if url_has_allowed_host_and_scheme(proxima, allowed_hosts={request.get_host()}):
            return redirect(proxima)
        return redirect('painel')
    messages.error(request, 'Usuário ou senha inválidos. Tente novamente.')
    return render(request, 'login.html', {'next': proxima, 'usuario': usuario})


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('painel')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.salvar()
        login_django(request, user)
        messages.success(request, 'Cadastro realizado com sucesso! Bem-vindo(a) ao Acolhe.')
        return redirect('painel')
    return render(request, 'cadastro.html', {'form': form})


def logout(request):
    if request.method == 'POST':
        logout_django(request)
        messages.success(request, 'Você saiu do sistema.')
    return redirect('principal')


@login_required
def perfil(request):
    user = request.user
    perfil = Perfil.objects.filter(usuario=user).first()
    if request.method == 'POST':
        form = PerfilForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['nome']
            user.email = form.cleaned_data['email']
            user.save()
            perfil, _ = Perfil.objects.get_or_create(usuario=user, defaults={'papel': papel_de(user)})
            perfil.telefone = form.cleaned_data['telefone']
            perfil.save()
            messages.success(request, 'Dados atualizados com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilForm(initial={
            'nome': user.first_name,
            'email': user.email,
            'telefone': perfil.telefone if perfil else '',
        })
    context = {
        'form': form,
        'papel_label': dict(Perfil.PAPEL)[papel_de(user)],
    }
    return render(request, 'perfil.html', context)


@login_required
def senha(request):
    form = SenhaForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('perfil')
    context = {
        'form': form,
        'titulo': 'Alterar senha',
        'icone': 'fa-key',
        'voltar': reverse('perfil'),
    }
    return render(request, 'formulario.html', context)


@login_required
def painel(request):
    papel = papel_de(request.user)
    context = {
        'disponiveis': Animal.objects.filter(status='disponivel').count(),
    }

    if papel == 'adotante':
        pedidos = Adocao.objects.filter(solicitante=request.user).select_related('animal', 'animal__especie')
        context.update({
            'pedidos': pedidos[:5],
            'total_pedidos': pedidos.count(),
            'em_analise': pedidos.filter(status='analise').count(),
            'aprovadas': pedidos.filter(status='aprovada').count(),
            'novos': Animal.objects.filter(status='disponivel').select_related('especie').order_by('-data_entrada')[:4],
        })
        return render(request, 'painel.html', context)

    hoje = timezone.localdate()
    por_status = dict(Animal.objects.values_list('status').annotate(total=Count('id')))
    especies = Especie.objects.annotate(total=Count('animais', filter=~Q(animais__status='adotado')))
    context.update({
        'em_tratamento': por_status.get('em_tratamento', 0),
        'adotados': por_status.get('adotado', 0),
        'em_analise': Adocao.objects.filter(status='analise').count(),
        'doacoes_mes': Doacao.objects.filter(data__year=hoje.year, data__month=hoje.month).count(),
        'total_doado': Doacao.objects.filter(tipo='dinheiro').aggregate(total=Sum('valor'))['total'] or 0,
        'pendentes': Adocao.objects.filter(status='analise').select_related('animal', 'solicitante')[:5],
        'abrigos': Abrigo.objects.annotate(ocupados=Count('animais', filter=~Q(animais__status='adotado'))),
        'grafico_status': {
            'labels': [nome for _, nome in Animal.STATUS],
            'dados': [por_status.get(codigo, 0) for codigo, _ in Animal.STATUS],
        },
        'grafico_especies': {
            'labels': [item.nome for item in especies],
            'dados': [item.total for item in especies],
        },
    })
    return render(request, 'painel.html', context)
