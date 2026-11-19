from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView

from animais.models import Animal
from usuarios.permissoes import EQUIPE
from usuarios.permissoes import PapelMixin
from usuarios.permissoes import papel_de
from usuarios.permissoes import papel_required
from .forms import DoacaoForm
from .forms import NovaPessoaForm
from .models import Adocao
from .models import Doacao
from .models import Perfil


def filtros_da_busca(request):
    parametros = request.GET.copy()
    parametros.pop('page', None)
    return parametros.urlencode() + '&' if parametros else ''


def voltar_para(request, padrao):
    destino = request.POST.get('voltar', '')
    if url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
        return redirect(destino)
    return redirect(padrao)


class AdocaoListView(LoginRequiredMixin, ListView):
    template_name = 'adocoes.html'
    context_object_name = 'adocoes'
    paginate_by = 15

    def get_queryset(self):
        consulta = Adocao.objects.select_related('animal', 'animal__especie', 'solicitante')
        filtros = self.request.GET
        if papel_de(self.request.user) in EQUIPE:
            if filtros.get('q'):
                consulta = consulta.filter(
                    Q(animal__nome__icontains=filtros['q'])
                    | Q(solicitante__username__icontains=filtros['q'])
                    | Q(solicitante__first_name__icontains=filtros['q'])
                )
        else:
            consulta = consulta.filter(solicitante=self.request.user)
        if filtros.get('status'):
            consulta = consulta.filter(status=filtros['status'])
        return consulta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'busca': self.request.GET,
            'filtros': filtros_da_busca(self.request),
            'situacoes': Adocao.STATUS,
        })
        return context


@papel_required('adotante')
def adocao_solicitar(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    if request.method != 'POST':
        return redirect(animal)
    if animal.status != 'disponivel':
        messages.error(request, 'Este animal não está disponível para adoção.')
    elif Adocao.objects.filter(animal=animal, solicitante=request.user, status='analise').exists():
        messages.warning(request, 'Você já tem um pedido em análise para este animal.')
    else:
        Adocao.objects.create(
            animal=animal,
            solicitante=request.user,
            data_pedido=timezone.localdate(),
            observacao=request.POST.get('observacao', '').strip()[:1000],
        )
        messages.success(request, f'Pedido de adoção de {animal.nome} enviado! Acompanhe a resposta nesta página.')
        return redirect('adocoes')
    return redirect(animal)


@papel_required('gestor')
def adocao_status(request, pk):
    adocao = get_object_or_404(Adocao.objects.select_related('animal'), pk=pk)
    status = request.POST.get('status')
    if request.method == 'POST' and status in dict(Adocao.STATUS):
        adocao.status = status
        try:
            adocao.full_clean()
        except ValidationError as e:
            messages.error(request, e.messages[0])
        else:
            adocao.save()
            avisos = {
                'aprovada': f'Adoção de {adocao.animal.nome} aprovada! Os outros pedidos em análise foram recusados.',
                'recusada': f'Pedido de adoção de {adocao.animal.nome} recusado.',
                'analise': f'Pedido de adoção de {adocao.animal.nome} voltou para análise.',
            }
            messages.success(request, avisos[status])
    return voltar_para(request, 'adocoes')


@papel_required('adotante')
def adocao_cancelar(request, pk):
    adocao = get_object_or_404(Adocao, pk=pk, solicitante=request.user)
    if request.method == 'POST':
        if adocao.status == 'analise':
            adocao.delete()
            messages.success(request, 'Pedido de adoção cancelado.')
        else:
            messages.error(request, 'Só é possível cancelar pedidos que ainda estão em análise.')
    return redirect('adocoes')


class DoacaoListView(PapelMixin, ListView):
    papeis = EQUIPE
    template_name = 'doacoes.html'
    context_object_name = 'doacoes'
    paginate_by = 15

    def get_queryset(self):
        consulta = Doacao.objects.select_related('registrado_por')
        filtros = self.request.GET
        if filtros.get('tipo'):
            consulta = consulta.filter(tipo=filtros['tipo'])
        if filtros.get('q'):
            consulta = consulta.filter(Q(doador_nome__icontains=filtros['q']) | Q(descricao__icontains=filtros['q']))
        return consulta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'busca': self.request.GET,
            'filtros': filtros_da_busca(self.request),
            'tipos': Doacao.TIPO,
            'total': self.object_list.filter(tipo='dinheiro').aggregate(total=Sum('valor'))['total'] or 0,
        })
        return context


class DoacaoCreateView(PapelMixin, SuccessMessageMixin, CreateView):
    papeis = EQUIPE
    model = Doacao
    form_class = DoacaoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('doacoes')
    success_message = 'Doação registrada com sucesso!'
    extra_context = {
        'titulo': 'Nova doação',
        'icone': 'fa-gift',
        'voltar': reverse_lazy('doacoes'),
    }

    def get_initial(self):
        return {'data': timezone.localdate()}

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class DoacaoUpdateView(PapelMixin, SuccessMessageMixin, UpdateView):
    papeis = EQUIPE
    model = Doacao
    form_class = DoacaoForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('doacoes')
    success_message = 'Doação atualizada com sucesso!'
    extra_context = {
        'titulo': 'Editar doação',
        'icone': 'fa-gift',
        'voltar': reverse_lazy('doacoes'),
    }


class DoacaoDeleteView(PapelMixin, SuccessMessageMixin, DeleteView):
    papeis = ('gestor',)
    model = Doacao
    template_name = 'confirmar_exclusao.html'
    success_url = reverse_lazy('doacoes')
    success_message = 'Doação excluída com sucesso!'
    extra_context = {
        'voltar': reverse_lazy('doacoes'),
    }


class PessoaListView(PapelMixin, ListView):
    papeis = ('gestor',)
    template_name = 'pessoas.html'
    context_object_name = 'pessoas'
    paginate_by = 15

    def get_queryset(self):
        consulta = User.objects.select_related('perfil').order_by('first_name', 'username')
        filtros = self.request.GET
        if filtros.get('papel'):
            consulta = consulta.filter(perfil__papel=filtros['papel'])
        if filtros.get('q'):
            consulta = consulta.filter(
                Q(username__icontains=filtros['q'])
                | Q(first_name__icontains=filtros['q'])
                | Q(email__icontains=filtros['q'])
            )
        return consulta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'busca': self.request.GET,
            'filtros': filtros_da_busca(self.request),
            'papeis': Perfil.PAPEL,
        })
        return context


@papel_required('gestor')
def pessoa_nova(request):
    form = NovaPessoaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.salvar(papel=form.cleaned_data['papel'])
        messages.success(request, f'Conta de {user.first_name} criada com sucesso!')
        return redirect('pessoas')
    context = {
        'form': form,
        'titulo': 'Nova pessoa da equipe',
        'icone': 'fa-user-plus',
        'voltar': reverse('pessoas'),
    }
    return render(request, 'formulario.html', context)


@papel_required('gestor')
def pessoa_papel(request, pk):
    pessoa = get_object_or_404(User, pk=pk)
    papel = request.POST.get('papel')
    if request.method == 'POST' and papel in dict(Perfil.PAPEL):
        if pessoa == request.user:
            messages.error(request, 'Você não pode alterar o seu próprio papel.')
        else:
            Perfil.objects.update_or_create(usuario=pessoa, defaults={'papel': papel})
            messages.success(request, f'{pessoa.first_name or pessoa.username} agora é {dict(Perfil.PAPEL)[papel].lower()}.')
    return voltar_para(request, 'pessoas')
